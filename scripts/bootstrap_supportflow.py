"""Offline administrator provisioning; token file is ignored, never embedded in docs."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from supportflow.contracts import Settings, Principal
from supportflow.store import Store
from supportflow.knowledge import Knowledge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--output", default=".runtime/demo-tokens.json")
    args = parser.parse_args()
    s = Settings.from_env()
    store = Store(s.db_path)
    roles = {
        "alice": {"customer"},
        "bob": {"customer"},
        "operator": {"staff"},
        "finance": {"finance"},
        "admin": {"admin"},
    }
    tokens = {
        u: store.issue_token(Principal(args.tenant, u, frozenset(r)), s.token_ttl)
        for u, r in roles.items()
    }
    admin = Principal(args.tenant, "admin", frozenset({"admin"}))
    try:
        store.seed_order(admin, "ORD1001", 5000, "alice")
    except __import__("sqlite3").IntegrityError:
        pass
    Knowledge(store, s, None).seed(args.tenant)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tokens, indent=2), encoding="utf-8")
    print(
        f"Provisioned {len(tokens)} identities; token file: {path}; expires in {s.token_ttl}s"
    )


if __name__ == "__main__":
    main()
