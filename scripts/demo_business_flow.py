"""Exercise synthetic samples through real HTTP routes without an LLM or payments."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from supportflow.api import create_app
from supportflow.contracts import ChatInput, Principal, Settings
from supportflow.knowledge import Knowledge
from supportflow.store import Store


def sample(name):
    return json.loads(
        (ROOT / "data/demo_supportflow" / name).read_text(encoding="utf-8")
    )


def main():
    with TemporaryDirectory(prefix="supportflow-demo-") as folder:
        settings = Settings(
            db_path=str(Path(folder) / "demo.sqlite3"),
            model_backend="fixture",
            storage="sqlite",
            skills_dir=str(ROOT / "skills"),
            business_mode="sandbox",
        )
        store = Store(settings.db_path)
        admin = Principal("demo", "admin", frozenset({"admin"}))
        alice = Principal("demo", "alice")
        finance = Principal("demo", "finance", frozenset({"finance"}))
        headers = {
            p.user: {"Authorization": "Bearer " + store.issue_token(p)}
            for p in (admin, alice, finance)
        }
        store.seed_order(admin, "ORD1001", 5000, "alice")
        Knowledge(store, settings, None).seed("demo")
        ChatInput.model_validate(sample("chat.request.json"))
        app = create_app(settings)
        with TestClient(app) as client:

            def request(method, path, user="alice", body=None):
                response = client.request(
                    method, path, headers=headers[user], json=body
                )
                if response.status_code != 200:
                    raise RuntimeError(
                        f"{method} {path}: {response.status_code} {response.text}"
                    )
                return response.json()

            initial_order = request("GET", "/orders/ORD1001")
            if initial_order != sample("order.response.json"):
                raise RuntimeError(
                    "Order response no longer matches the checked-in sample"
                )
            request("POST", "/knowledge", "admin", sample("knowledge.request.json"))
            refund = request("POST", "/refunds", body=sample("refund.request.json"))
            if refund["status"] != "pending":
                raise RuntimeError("New refund must await approval")
            repeated = request("POST", "/refunds", body=sample("refund.request.json"))
            if repeated["id"] != refund["id"]:
                raise RuntimeError("Retry created a duplicate refund")
            request(
                "POST",
                f"/refunds/{refund['id']}/approval",
                "finance",
                {"approve": True},
            )
            request("POST", f"/refunds/{refund['id']}/settle", "finance")
            final_order = request("GET", "/orders/ORD1001")
            if final_order["refunded"] != sample("refund.request.json")["amount_cents"]:
                raise RuntimeError(
                    "Sandbox settlement amount did not match the request"
                )
            print(
                json.dumps(
                    {
                        "result": "passed",
                        "mode": "synthetic sandbox; no LLM or external payment calls",
                        "checks": [
                            "chat schema",
                            "order sample",
                            "knowledge import",
                            "refund idempotency",
                            "finance approval",
                            "sandbox settlement",
                        ],
                        "order": final_order,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )


if __name__ == "__main__":
    main()
