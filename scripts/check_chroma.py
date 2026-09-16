"""Explicit real Chroma integration check; downloads default ONNX embedding on first use."""

import asyncio
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from supportflow.contracts import Settings, Principal
from supportflow.store import Store
from supportflow.knowledge import Knowledge


async def main():
    root = Path(".runtime") / ("chroma-check-" + str(time.time_ns()))
    s = Settings(
        db_path=str(root / "db.sqlite"),
        storage="chroma",
        chroma_path=str(root / "vectors"),
    )
    kb = Knowledge(Store(s.db_path), s, None)
    kb.add("a", "login", "Login", "401 login token expired, sign in again.")
    kb.add("b", "private", "Private", "TENANT_B_PRIVATE_RECORD")
    first = kb.search("a", "401 login", 3)
    assert first and all("PRIVATE" not in r["content"] for r in first)
    old = first[0]["id"]
    kb.add("a", "login", "Login", "401 authentication expired; renew the session.")
    assert all(r["id"] != old for r in kb.search("a", "401 login", 3))
    p = Principal("a", "alice")
    await kb.archive(p, "conv", "Order ORD1001 remains pending.", 1)
    assert await kb.recall(p, "order")
    assert not await kb.recall(Principal("b", "alice"), "order")
    await kb.project_profile(p, {"language": "zh"})
    print(
        "REAL CHROMA PASS: tenant isolation, version replacement, episodic recall, profile projection"
    )


if __name__ == "__main__":
    asyncio.run(main())
