"""Redis working context with bounded history and SQL-validated snapshots."""

import hashlib
import json


class WorkingMemory:
    TTL = 86400

    @staticmethod
    def key(p, conv):
        identity = json.dumps([p.tenant, p.user, conv], ensure_ascii=False)
        return "sf:wm:" + hashlib.sha256(identity.encode()).hexdigest()

    @classmethod
    async def save(cls, redis, p, conv, state, history):
        snapshot = {
            "turn": state["turn"], "history": history[-20:],
            "summary": state.get("summary", ""), "profile": state.get("profile", {}),
        }
        await redis.setex(cls.key(p, conv), cls.TTL, json.dumps(snapshot, ensure_ascii=False))

    @classmethod
    async def read(cls, redis, p, conv, state, history):
        raw = await redis.get(cls.key(p, conv))
        if not raw:
            return history, "miss"
        cached = json.loads(raw)
        # Human replies can arrive without incrementing the Agent's turn counter.
        if (cached.get("turn") == state.get("turn")
                and cached.get("history") == history
                and cached.get("summary", "") == state.get("summary", "")):
            return cached["history"], "hit"
        return history, "stale"
