import pytest
from jsonschema import ValidationError
from supportflow.contracts import Principal, Trace
from supportflow.store import Store
from supportflow.tools import Tools
from supportflow.model import active_trace


class FakeKnowledge:
    def __init__(self):
        self.revision = "v1"
        self.calls = 0
        self.fail = False

    def version(self, tenant):
        return self.revision

    async def retrieve(self, tenant, query, advanced=True):
        self.calls += 1
        if self.fail:
            raise RuntimeError("backend unavailable")
        return {"items": [{"id": tenant, "content": query}], "degraded": []}


@pytest.mark.asyncio
async def test_cache_scoping_copy_and_version(tmp_path):
    k = FakeKnowledge()
    tools = Tools(Store(tmp_path / "tools.sqlite"), k)
    p = Principal("t", "u")
    args = {"query": "test"}
    a = await tools.call(p, "general", "knowledge_search", args, "c", "request01")
    a["items"].clear()
    b = await tools.call(p, "general", "knowledge_search", args, "c", "request02")
    assert b["items"] and k.calls == 1
    await tools.call(
        Principal("other", "u"), "general", "knowledge_search", args, "c", "request03"
    )
    assert k.calls == 2
    k.revision = "v2"
    await tools.call(p, "general", "knowledge_search", args, "c", "request04")
    assert k.calls == 3


@pytest.mark.asyncio
async def test_bad_args_do_not_trip_breaker_and_denied_tools(tmp_path):
    tools = Tools(Store(tmp_path / "tools.sqlite"), FakeKnowledge())
    p = Principal("t", "u")
    for _ in range(4):
        with pytest.raises(ValidationError):
            await tools.call(
                p, "general", "knowledge_search", {"query": 42}, "c", "request01"
            )
    assert not tools.breakers
    with pytest.raises(PermissionError):
        await tools.call(p, "technical", "refund_request", {}, "c", "request02")
    with pytest.raises(PermissionError):
        await tools.call(
            p,
            "billing",
            "refund_request",
            {"order_id": "ORD1", "amount_cents": 100, "reason": "x"},
            "c",
            "request03",
        )


@pytest.mark.asyncio
async def test_breaker_outage_and_trace(tmp_path):
    k = FakeKnowledge()
    k.fail = True
    tools = Tools(Store(tmp_path / "tools.sqlite"), k)
    p = Principal("t", "u")
    trace = Trace("trace1")
    ctx = active_trace.set(trace)
    try:
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await tools.call(
                    p, "general", "knowledge_search", {"query": "q"}, "c", "request1"
                )
        with pytest.raises(RuntimeError, match="circuit_open"):
            await tools.call(
                p, "general", "knowledge_search", {"query": "q"}, "c", "request1"
            )
        assert (
            k.calls == 3
            and len(trace.tools) == 4
            and not any(t["success"] for t in trace.tools)
        )
    finally:
        active_trace.reset(ctx)


@pytest.mark.asyncio
async def test_same_mcp_idempotency_key_cannot_change_refund_payload(tmp_path):
    store = Store(tmp_path / "tools.sqlite")
    k = FakeKnowledge()
    tools = Tools(store, k)
    p = Principal("t", "u")
    a = Principal("t", "a", frozenset({"admin"}))
    store.seed_order(a, "ORD1", 5000, "u")
    args = {"order_id": "ORD1", "amount_cents": 100, "reason": "x"}
    first = await tools.call(
        p, "billing", "refund_request", args, "c", "request123", consent=True
    )
    again = await tools.call(
        p, "billing", "refund_request", args, "c", "request123", consent=True
    )
    assert first["id"] == again["id"]
    with pytest.raises(ValueError):
        await tools.call(
            p,
            "billing",
            "refund_request",
            {**args, "amount_cents": 101},
            "c",
            "request123",
            consent=True,
        )
