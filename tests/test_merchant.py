import pytest
from fastapi.testclient import TestClient
from supportflow.api import create_app
from supportflow.contracts import Principal, Settings


@pytest.fixture
def merchant(tmp_path):
    app = create_app(Settings(db_path=str(tmp_path / "merchant.sqlite"), model_backend="fixture"))
    headers = {}
    for user, tenant, role in [("admin", "demo", "admin"), ("alice", "demo", "customer"), ("staff", "demo", "staff"), ("finance", "demo", "finance"), ("other", "other", "admin")]:
        headers[user] = {"Authorization": "Bearer " + app.state.store.issue_token(Principal(tenant, user, frozenset({role})))}
    with TestClient(app) as client:
        yield client, headers, app.state.store


def order(order_id="ORD2001", status="paid"):
    return {"order_id": order_id, "customer": "alice", "product": "纯棉家居套装", "quantity": 2, "total_cents": 6800, "status": status}


def test_local_demo_merchant_session(tmp_path):
    app = create_app(Settings(db_path=str(tmp_path / "demo.sqlite"), model_backend="fixture", local_demo_access=True))
    with TestClient(app, base_url="http://127.0.0.1:8002", client=("127.0.0.1", 50000)) as c:
        headers = {"X-SupportFlow-Demo": "merchant", "Origin": "http://127.0.0.1:8002"}
        assert c.post("/auth/demo-merchant").status_code == 403
        assert c.post("/auth/demo-merchant", headers={**headers, "Origin": "https://elsewhere.test"}).status_code == 403
        response = c.post("/auth/demo-merchant", headers=headers)
        assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
        auth = {"Authorization": "Bearer " + response.json()["token"]}
        assert c.get("/auth/me", headers=auth).json() == {"tenant": "demo", "user": "merchant", "roles": ["finance", "staff"]}
        assert c.post("/merchant/orders", headers=auth, json=order()).status_code == 201
        assert c.get("/merchant/orders", headers=auth).json()["total"] == 1
    remote = create_app(Settings(db_path=str(tmp_path / "remote.sqlite"), model_backend="fixture", local_demo_access=True))
    with TestClient(remote, base_url="http://127.0.0.1:8002", client=("192.0.2.1", 50000)) as c:
        assert c.post("/auth/demo-merchant", headers=headers).status_code == 403
    for enabled, mode in [(False, "sandbox"), (True, "external")]:
        disabled = create_app(Settings(db_path=str(tmp_path / "disabled.sqlite"), model_backend="fixture", local_demo_access=enabled, business_mode=mode))
        with TestClient(disabled, base_url="http://127.0.0.1:8002", client=("127.0.0.1", 50000)) as c:
            assert c.post("/auth/demo-merchant", headers=headers).status_code == 404


def test_merchant_permissions_and_tenant_isolation(merchant):
    c, h, _ = merchant
    assert c.get("/admin").status_code == 200
    assert c.get("/merchant/orders").status_code == 401
    for path in ["/merchant/orders", "/merchant/refunds", "/merchant/overview"]:
        assert c.get(path, headers=h["alice"]).status_code == 403
    assert c.post("/merchant/orders", headers=h["alice"], json=order()).status_code == 403
    assert c.post("/merchant/orders", headers=h["finance"], json=order()).status_code == 403
    assert c.post("/merchant/orders", headers=h["staff"], json=order()).status_code == 201
    assert c.get("/merchant/orders", headers=h["finance"]).json()["total"] == 1
    assert c.get("/merchant/refunds", headers=h["staff"]).status_code == 403
    assert c.get("/merchant/orders", headers=h["other"]).json()["total"] == 0
    assert c.patch("/merchant/orders/ORD2001", headers=h["other"], json={"status": "shipped", "version": 0}).status_code == 403
    assert c.get("/orders/ORD2001", headers=h["alice"]).json()["product"] == "纯棉家居套装"


def test_order_transitions_conflicts_and_unpaid_refund(merchant):
    c, h, store = merchant
    assert c.post("/merchant/orders", headers=h["admin"], json=order(status="pending_payment")).status_code == 201
    refund = {"order_id": "ORD2001", "amount_cents": 6800, "reason": "测试", "idempotency_key": "merchant-test-refund"}
    assert c.post("/refunds", headers=h["alice"], json=refund).status_code == 409
    assert store.order(Principal("demo", "alice"), "ORD2001")["refundable"] == 0
    assert c.patch("/merchant/orders/ORD2001", headers=h["admin"], json={"status": "shipped", "version": 0}).status_code == 409
    for version, status in enumerate(["paid", "shipped", "completed"]):
        assert c.patch("/merchant/orders/ORD2001", headers=h["admin"], json={"status": status, "version": version}).status_code == 200
    assert c.patch("/merchant/orders/ORD2001", headers=h["admin"], json={"status": "paid", "version": 0}).status_code == 409
    assert c.post("/merchant/orders", headers=h["admin"], json=order("ORD2002", "pending_payment")).status_code == 201
    assert c.patch("/merchant/orders/ORD2002", headers=h["staff"], json={"status": "cancelled", "version": 0}).status_code == 200


def test_create_apply_approve_settle_and_dashboard(merchant):
    c, h, store = merchant
    assert c.post("/merchant/orders", headers=h["admin"], json=order()).status_code == 201
    refund = c.post("/refunds", headers=h["alice"], json={"order_id": "ORD2001", "amount_cents": 6800, "reason": "客户申请", "idempotency_key": "merchant-refund-one"}).json()
    rid = refund["id"]
    assert c.get("/merchant/overview", headers=h["admin"]).json()["pending_refunds"] == 1
    assert c.patch("/merchant/orders/ORD2001", headers=h["admin"], json={"status": "shipped", "version": 0}).status_code == 409
    assert c.post(f"/refunds/{rid}/settle", headers=h["finance"]).status_code == 409
    assert c.post(f"/refunds/{rid}/approval", headers=h["alice"], json={"approve": True}).status_code == 403
    assert c.post(f"/refunds/{rid}/approval", headers=h["finance"], json={"approve": True}).status_code == 200
    assert c.get("/merchant/orders", headers=h["admin"]).json()["items"][0]["refund_status"] == "approved"
    assert c.post(f"/refunds/{rid}/settle", headers=h["finance"]).json()["status"] == "settled"
    assert c.post(f"/refunds/{rid}/settle", headers=h["finance"]).status_code == 200
    assert store.order(Principal("demo", "alice"), "ORD2001")["refunded"] == 6800
    assert c.get("/merchant/overview", headers=h["admin"]).json() == {"orders": 1, "net_cents": 0, "pending_refunds": 0, "refunded_cents": 6800}
    item = c.get("/merchant/orders", headers=h["admin"]).json()["items"][0]
    assert item["refund_status"] == "refunded" and item["refundable"] == 0
    assert c.get("/merchant/refunds?status=settled", headers=h["finance"]).json()["total"] == 1
    assert c.get("/merchant/refunds", headers=h["other"]).json()["total"] == 0


def test_validation_duplicate_order_search_and_rejection(merchant):
    c, h, store = merchant
    for body in [{**order(), "total_cents": -1}, {**order(), "quantity": True}, {**order(), "product": "  "}]:
        assert c.post("/merchant/orders", headers=h["admin"], json=body).status_code == 422
    assert c.post("/merchant/orders", headers=h["admin"], json=order()).status_code == 201
    assert c.post("/merchant/orders", headers=h["admin"], json=order()).status_code == 409
    assert c.get("/merchant/orders?search=家居&limit=1", headers=h["admin"]).json()["total"] == 1
    assert c.get("/merchant/orders?status=shipped", headers=h["admin"]).json()["items"] == []
    assert c.get("/merchant/orders?offset=-1", headers=h["admin"]).status_code == 422
    rid = c.post("/refunds", headers=h["alice"], json={"order_id": "ORD2001", "amount_cents": 1000, "reason": "测试", "idempotency_key": "merchant-refund-two"}).json()["id"]
    assert c.post(f"/refunds/{rid}/approval", headers=h["admin"], json={"approve": False}).status_code == 200
    assert store.order(Principal("demo", "alice"), "ORD2001")["refundable"] == 6800
