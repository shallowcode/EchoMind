import json

import fakeredis.aioredis
import httpx
import pytest

from supportflow.api import create_app
from supportflow.contracts import Principal, Settings
from supportflow.working_memory import WorkingMemory
from tests.test_supportflow import ScriptedModel


@pytest.mark.asyncio
async def test_working_memory_projection_profile_and_raw_order(tmp_path):
    s = Settings(db_path=str(tmp_path / "memory.sqlite"), model_backend="fixture")
    app = create_app(s, ScriptedModel(s))
    svc = app.state.service
    svc.redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    p = Principal("t", "alice")
    a = Principal("t", "admin", frozenset({"admin"}))
    svc.store.seed_order(a, "ORD1001", 5000, "alice")
    token = svc.store.issue_token(p)
    h = {"Authorization": "Bearer " + token}
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost"
        ) as c,
    ):
        for i in range(9):
            message = (
                "请用中文，简短回答。查询订单 ORD1001"
                if i == 0
                else f"第{i}轮，查询订单 ORD1001"
            )
            r = await c.post(
                "/chat",
                headers=h,
                json={
                    "message": message,
                    "conv_id": "longconv",
                    "request_id": f"memory-{i:03d}",
                },
            )
            assert r.status_code == 200, r.text
        history = svc.store.history(p, "longconv", 100)
        assert (
            len(history) == 18
            and history[0]["role"] == "user"
            and "第8轮" in history[-2]["content"]
        )
        cached = json.loads(await svc.redis.get(WorkingMemory.key(p, "longconv")))
        assert cached["turn"] == 9
        assert cached["summary"] and cached["profile"] == {"language": "zh", "verbosity": "brief"}
        assert r.json()["trace"]["memory"]["redis_cache"] == "hit"
        assert r.json()["trace"]["memory"]["working_backend"] == "redis"
        assert 0 < await svc.redis.ttl(WorkingMemory.key(p, "longconv")) <= 86400
        assert svc.store.profile(p) == {"language": "zh", "verbosity": "brief"}
        assert svc.store.profile(Principal("other", "alice")) == {}
        # A human result arriving after cache creation must remain visible in the source of truth.
        with svc.store.tx() as db:
            db.execute(
                "INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)",
                ("t", "longconv", "system", "人工解决回写", 0),
            )
        assert svc.store.history(p, "longconv")[-1]["content"] == "人工解决回写"
        r = await c.post("/chat", headers=h, json={"message": "查询订单 ORD1001",
                         "conv_id": "longconv", "request_id": "memory-human-result"})
        assert r.status_code == 200
        assert r.json()["trace"]["memory"]["redis_cache"] == "stale"
        assert any("人工解决回写" in m["content"] for m in r.json()["trace"]["memory"]["history"])


@pytest.mark.asyncio
async def test_cache_isolation_and_expiry_fall_back_to_sql():
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    p = Principal("a:b", "alice")
    other = Principal("a", "b:alice")
    state = {"turn": 1, "summary": "待处理", "profile": {"language": "zh"}}
    history = [{"role": "user", "content": "私有历史"}]
    try:
        await WorkingMemory.save(redis, p, "conv", state, history)
        assert (await WorkingMemory.read(redis, p, "conv", state, history))[1] == "hit"
        assert (await WorkingMemory.read(redis, other, "conv", state, history))[1] == "miss"
        assert (await WorkingMemory.read(redis, Principal("a:b", "bob"), "conv", state, history))[1] == "miss"
        assert (await WorkingMemory.read(redis, p, "conv", {**state, "turn": 2}, history))[1] == "stale"
        await redis.delete(WorkingMemory.key(p, "conv"))
        assert await WorkingMemory.read(redis, p, "conv", state, history) == (history, "miss")
    finally:
        await redis.aclose()


@pytest.mark.asyncio
async def test_redis_failure_is_visible_without_losing_committed_reply(tmp_path):
    class UnavailableRedis:
        async def get(self, key):
            raise ConnectionError("unavailable")

        async def setex(self, *args):
            raise ConnectionError("unavailable")

        async def ping(self):
            raise ConnectionError("unavailable")

        async def aclose(self):
            pass

    s = Settings(db_path=str(tmp_path / "db.sqlite"), model_backend="fixture")
    app = create_app(s, ScriptedModel(s))
    svc = app.state.service
    svc.redis = UnavailableRedis()
    p = Principal("t", "alice")
    svc.store.seed_order(Principal("t", "admin", frozenset({"admin"})), "ORD1001", 5000, p.user)
    token = svc.store.issue_token(p)
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://localhost"
    ) as c:
        assert (await c.get("/ready")).status_code == 503
        body = {"message": "查询订单 ORD1001", "conv_id": "conv", "request_id": "redis-unavailable"}
        result = await c.post("/chat", headers={"Authorization": "Bearer " + token}, json=body)
        assert result.status_code == 200
        data = result.json()
        assert data["status"] == "degraded"
        assert {"redis_read", "redis_projection"} <= set(data["trace"]["failures"])
        assert len(svc.store.history(p, "conv")) == 2
        replay = await c.post("/chat", headers={"Authorization": "Bearer " + token}, json=body)
        assert replay.json()["replayed"] and replay.json()["response"] == data["response"]


@pytest.mark.asyncio
async def test_resume_profile_refuses_missing_dependencies(tmp_path):
    s = Settings(db_path=str(tmp_path / "db.sqlite"), model_backend="fixture", require_memory_services=True)
    app = create_app(s, ScriptedModel(s))
    with pytest.raises(RuntimeError, match="requires reachable"):
        async with app.router.lifespan_context(app):
            pytest.fail("Missing dependencies must not start a resume service")
