"""Explicit real Chroma integration check; downloads default ONNX embedding on first use."""

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from supportflow.contracts import Principal, Settings
from supportflow.knowledge import Knowledge
from supportflow.store import Store


async def main(args):
    root = Path(".runtime") / ("chroma-check-" + str(time.time_ns()))
    s = Settings(
        db_path=str(root / "db.sqlite"),
        storage="chroma",
        chroma_path=str(root / "vectors"),
        chroma_mode="http" if args.http else "embedded",
        chroma_host=args.host,
        chroma_port=args.port,
    )
    kb = Knowledge(Store(s.db_path), s, None)
    tenant = "chroma-check-" + str(time.time_ns())
    other = tenant + "-other"
    kb.add(tenant, "login", "Login", "401 login token expired, sign in again.")
    kb.add(other, "private", "Private", "TENANT_B_PRIVATE_RECORD")
    first = kb.search(tenant, "401 login", 3)
    assert first and all("PRIVATE" not in r["content"] for r in first)
    old = first[0]["id"]
    kb.add(tenant, "login", "Login", "401 authentication expired; renew the session.")
    assert all(r["id"] != old for r in kb.search(tenant, "401 login", 3))
    kb.reindex(tenant)
    assert kb.search(tenant, "401 login", 3)
    p = Principal(tenant, "alice")
    await kb.archive(p, "conv", "Order ORD1001 remains pending.", 1)
    assert await kb.recall(p, "order")
    assert not await kb.recall(Principal(other, "alice"), "order")
    await kb.project_profile(p, {"language": "zh"})
    print(
        "REAL CHROMA PASS:", s.chroma_mode,
        "tenant isolation, version replacement, reindex, episodic recall, profile projection"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8001)
    asyncio.run(main(parser.parse_args()))
