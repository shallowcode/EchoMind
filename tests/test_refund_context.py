from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from supportflow.api import create_app
from supportflow.contracts import Settings, Principal, BusinessRejection
from supportflow.refunds import resolve_refund, validate_refund_call
from supportflow.store import Store
from tests.test_supportflow import ScriptedModel


@pytest.mark.parametrize("phrase", ["全退给我", "全部退给我", "全额退款", "请全额退还", "refund it all"])
def test_full_refund_continues_pending_user_order(phrase):
    state = {}
    resolve_refund("我买的内裤怎么还不到，我不要了，我要退款", state, [])
    context = resolve_refund("ORD1001", state, [])
    assert context["active"] and context["order_ids"] == ["ORD1001"]
    context = resolve_refund(phrase, state, [])
    assert context["full"] and context["consent"]
    validate_refund_call(context, {"order_id": "ORD1001", "full_refund": True})
    with pytest.raises(PermissionError):
        validate_refund_call(context, {"order_id": "ORD1001", "amount_cents": 5000})


@pytest.mark.parametrize("message", ["能全退吗？", "全额退款有什么条件", "如果全退会怎样", "别全退", "不要退款", "我没说全退", "不能全退", '他说“全退给我”', "thanks", "我没说我要退款ORD1001 20元", "我还买了20元的袜子"])
def test_questions_cancellation_and_unrelated_text_do_not_authorize(message):
    state = {}
    resolve_refund("我要退款 ORD1001", state, [])
    assert not resolve_refund(message, state, []).get("active")


def test_amount_before_order_and_new_order_invalidate_old_amount():
    state = {}
    resolve_refund("我要退款20元", state, [])
    assert resolve_refund("ORD1001", state, [])["amount_cents"] == 2000
    assert resolve_refund("ORD1002", state, [])["amount_cents"] is None
    resolve_refund("全退", state, [])
    assert not resolve_refund("我现在想查询物流", state, []).get("active")
    assert not resolve_refund("20元", state, []).get("active")


def test_full_before_order_and_legacy_user_history_only():
    state = {}
    resolve_refund("我要全退", state, [])
    assert resolve_refund("ORD1001", state, [])["full"]
    assert resolve_refund("全退给我", {}, [{"role": "user", "content": "ORD1001"}])["order_ids"] == ["ORD1001"]
    assert not resolve_refund("全退给我", {}, [{"role": "assistant", "content": "ORD1001"}])["order_ids"]
    assert resolve_refund("我要退款-20元", {}, [])["amount_cents"] is None


def test_full_refund_subtracts_reserved_and_settled_and_replays(tmp_path):
    store = Store(tmp_path / "ledger")
    p, admin = Principal("t", "alice"), Principal("t", "admin", frozenset({"admin"}))
    store.seed_order(admin, "ORD1001", 5000, "alice")
    settled = store.refund_request(p, "ORD1001", 1000, "partial", "one")
    store.approve_refund(admin, settled["id"])
    store.settle_refund(admin, settled["id"])
    store.refund_request(p, "ORD1001", 500, "pending", "two")
    assert store.order(p, "ORD1001")["refundable"] == 3500
    result = store.refund_request(p, "ORD1001", None, "全退", "all", full=True)
    assert result["amount"] == 3500 and result["status"] == "pending"
    assert store.refund_request(p, "ORD1001", None, "全退", "all", full=True) == result
    assert store.order(p, "ORD1001")["refundable"] == 0
    with pytest.raises(BusinessRejection):
        store.refund_request(p, "ORD1001", None, "全退", "another", full=True)
    with pytest.raises(PermissionError):
        store.refund_request(Principal("t", "bob"), "ORD1001", None, "全退", "bob", full=True)
    with pytest.raises(PermissionError):
        store.refund_request(Principal("other", "alice"), "ORD1001", None, "全退", "tenant", full=True)


def test_concurrent_full_refunds_reserve_once(tmp_path):
    store = Store(tmp_path / "ledger")
    p = Principal("t", "alice")
    store.seed_order(Principal("t", "admin", frozenset({"admin"})), "ORD1001", 5000, "alice")
    def request(index):
        try:
            return store.refund_request(p, "ORD1001", None, "全退", str(index), full=True)
        except BusinessRejection:
            return None
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(request, range(2)))
    assert sum(result["amount"] for result in results if result) == 5000


@pytest.mark.asyncio
async def test_exact_three_turn_refund_flow_and_replay(tmp_path):
    settings = Settings(db_path=str(tmp_path / "http"), model_backend="fixture")
    app = create_app(settings, ScriptedModel(settings))
    store = app.state.store
    p = Principal("t", "alice")
    store.seed_order(Principal("t", "admin", frozenset({"admin"})), "ORD1001", 5000, "alice")
    headers = {"Authorization": "Bearer " + store.issue_token(p)}
    async with app.router.lifespan_context(app), httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost") as client:
        conv = None
        for index, message in enumerate(["我买的内裤怎么还不到，我不要了，我要退款", "ORD1001", "全退给我"]):
            body = {"message": message, "conv_id": conv, "request_id": f"refund-turn-{index}"}
            response = await client.post("/chat", json=body, headers=headers)
            assert response.status_code == 200, response.text
            result = response.json()
            conv = result["conv_id"]
            if index < 2:
                assert result["status"] == "awaiting_input"
                assert "refund_request" not in result["tools_used"]
            else:
                assert result["status"] == "completed"
                assert "refund_request" in result["tools_used"]
                assert "50.00" in result["response"] and "待财务审核" in result["response"]
        replay = (await client.post("/chat", json=body, headers=headers)).json()
        assert replay["replayed"] and replay["response"] == result["response"]
        refunds = (await client.get("/refunds", headers=headers)).json()
        assert len(refunds) == 1 and refunds[0]["amount"] == 5000
        assert store.order(p, "ORD1001")["refunded"] == 0
