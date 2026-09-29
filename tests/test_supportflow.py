"""Behavior/security invariants. Doubles do not constitute model quality evidence."""

from concurrent.futures import ThreadPoolExecutor
import json
import pytest
import httpx
from supportflow.contracts import Principal, Settings
from supportflow.store import Store
from supportflow.api import create_app
from supportflow.tools import Breaker


@pytest.fixture
def ledger(tmp_path):
    s = Store(tmp_path / "db.sqlite")
    a = Principal("t", "admin", frozenset({"admin"}))
    p = Principal("t", "alice")
    s.seed_order(a, "ORD1001", 5000, p.user)
    return s, p, a


def test_refund_reservation_approval_settlement(ledger):
    s, p, a = ledger
    r = s.refund_request(p, "ORD1001", 3000, "test", "key")
    assert s.refund_request(p, "ORD1001", 3000, "test", "key")["id"] == r["id"]
    with pytest.raises(ValueError):
        s.refund_request(p, "ORD1001", 3000, "test", "other")
    with pytest.raises(PermissionError):
        s.approve_refund(p, r["id"])
    with pytest.raises(ValueError):
        s.settle_refund(a, r["id"])
    s.approve_refund(a, r["id"])
    s.settle_refund(a, r["id"])
    s.settle_refund(a, r["id"])
    assert s.order(p, "ORD1001")["refunded"] == 3000


def test_concurrent_refunds_cannot_overspend(ledger):
    s, p, a = ledger

    def attempt(i):
        try:
            return s.refund_request(p, "ORD1001", 3000, "test", str(i))
        except ValueError:
            return None

    with ThreadPoolExecutor(4) as pool:
        rows = list(pool.map(attempt, range(4)))
    assert sum(r is not None for r in rows) == 1


def test_tenant_owner_expiry_revocation(ledger):
    s, p, a = ledger
    for other in [Principal("other", "alice"), Principal("t", "bob")]:
        with pytest.raises(PermissionError):
            s.order(other, "ORD1001")
    expired = s.issue_token(p, -1)
    with pytest.raises(PermissionError):
        s.authenticate(expired)
    token = s.issue_token(p)
    assert s.authenticate(token) == p
    s.revoke(a, token)
    with pytest.raises(PermissionError):
        s.authenticate(token)


def test_self_approval_and_idempotency_payload(ledger):
    s, p, a = ledger
    r = s.refund_request(p, "ORD1001", 100, "why", "a")
    with pytest.raises(PermissionError):
        s.approve_refund(Principal("t", "alice", frozenset({"finance"})), r["id"])
    with pytest.raises(ValueError):
        s.refund_request(p, "ORD1001", 101, "why", "a")
    with pytest.raises(ValueError):
        s.refund_request(p, "ORD1001", True, "why", "b")


def test_ticket_closure_writes_conversation(ledger):
    s, p, a = ledger
    s.acquire_conversation(p, "conv", "lease", 100)
    s.release(p, "conv", "lease")
    ticket = s.create_ticket(p, "conv", "help", "key")
    tid = ticket["id"]
    staff = Principal("t", "operator", frozenset({"staff"}))
    with pytest.raises(ValueError):
        s.update_ticket(staff, tid, "closed")
    s.update_ticket(staff, tid, "assigned", assignee="operator")
    with pytest.raises(ValueError):
        s.update_ticket(staff, tid, "resolved", resolution="fixed", version=0)
    s.update_ticket(staff, tid, "resolved", resolution="fixed", version=1)
    assert "fixed" in s.history(p, "conv")[0]["content"]
    assert s.update_ticket(staff, tid, "closed", version=2)["status"] == "closed"
    with pytest.raises(PermissionError):
        s.ticket(Principal("t", "bob"), tid)


def test_conversation_lease_and_ownership(ledger):
    s, p, a = ledger
    s.acquire_conversation(p, "conv", "first", 100)
    with pytest.raises(ValueError):
        s.acquire_conversation(p, "conv", "second", 100)
    s.release(p, "conv", "wrong")
    with pytest.raises(ValueError):
        s.acquire_conversation(p, "conv", "second", 100)
    s.release(p, "conv", "first")
    with pytest.raises(PermissionError):
        s.acquire_conversation(Principal("t", "bob"), "conv", "second", 100)


def test_single_half_open_probe():
    b = Breaker(threshold=1, recovery=0)
    b.finish(False)
    assert b.enter()
    assert not b.enter()
    b.finish(True)
    assert b.enter()


class ScriptedModel:
    """Transparent fixture backend: deterministic tool execution only, no quality claims."""

    def __init__(self, s):
        self.settings = s
        self.messages = self

    async def close(self):
        pass

    async def create(self, **kwargs):
        from types import SimpleNamespace

        return SimpleNamespace(
            content=[
                SimpleNamespace(
                    type="text", text='{"intent":"order_status","confidence":0.99}'
                )
            ]
        )

    async def complete(self, messages, system="", **kwargs):
        if "工具执行结果" in messages[-1]["content"]:
            return json.dumps({"answer": "订单为 paid。", "tool_calls": []})
        return json.dumps(
            {
                "answer": "",
                "tool_calls": [
                    {"name": "order_lookup", "arguments": {"order_id": "ORD1001"}}
                ],
            }
        )


@pytest.mark.asyncio
async def test_http_full_chain_and_replay(tmp_path):
    s = Settings(db_path=str(tmp_path / "http.sqlite"), model_backend="fixture")
    app = create_app(s, ScriptedModel(s))
    store = app.state.store
    p = Principal("t", "alice")
    a = Principal("t", "admin", frozenset({"admin"}))
    store.seed_order(a, "ORD1001", 5000, "alice")
    token = store.issue_token(p)
    headers = {"Authorization": "Bearer " + token}
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost"
        ) as c,
    ):
        assert (
            await c.post("/chat", json={"message": "hi", "request_id": "request001"})
        ).status_code == 401
        body = {"message": "查询订单 ORD1001", "request_id": "request001"}
        r = await c.post("/chat", json=body, headers=headers)
        assert r.status_code == 200, r.text
        result = r.json()
        assert "order_lookup" in result["tools_used"]
        execution = result["execution"]
        assert execution["tools"][0]["name"] == "order_lookup"
        assert execution["steps"][-1]["title"] == "保存会话"
        assert execution["sources"] == []
        assert (await c.post("/chat", json=body, headers=headers)).json()["execution"] == execution
        assert (await c.post("/chat", json=body, headers=headers)).json()["replayed"]
        assert (
            await c.post("/chat", json={**body, "message": "changed"}, headers=headers)
        ).status_code == 409
        assert len(store.history(p, result["conv_id"])) == 2
        assert (await c.get("/metrics", headers=headers)).status_code == 403
        assert (
            await c.post(
                "/refunds",
                json={
                    "order_id": "ORD1001",
                    "amount_cents": True,
                    "reason": "x",
                    "idempotency_key": "abcdefghi",
                },
                headers=headers,
            )
        ).status_code == 422
