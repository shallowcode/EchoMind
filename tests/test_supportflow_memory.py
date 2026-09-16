import json
import pytest
import httpx
import fakeredis.aioredis
from supportflow.api import create_app
from supportflow.contracts import Settings, Principal
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
        cached = json.loads(await svc.redis.get("sf:t:longconv"))
        assert cached["turn"] == 9
        assert svc.store.profile(p) == {"language": "zh", "verbosity": "brief"}
        assert svc.store.profile(Principal("other", "alice")) == {}
        # A human result arriving after cache creation must remain visible in the source of truth.
        with svc.store.tx() as db:
            db.execute(
                "INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)",
                ("t", "longconv", "system", "人工解决回写", 0),
            )
        assert svc.store.history(p, "longconv")[-1]["content"] == "人工解决回写"
