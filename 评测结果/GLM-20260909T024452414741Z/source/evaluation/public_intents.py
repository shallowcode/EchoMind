"""Public dataset intent evaluation only; never merge with transaction success metrics."""

import argparse
import asyncio
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from supportflow.api import create_app
from supportflow.contracts import Settings, Principal

# Explicit many-to-one ontology mapping; ambiguous labels excluded rather than relabelled OTHER.
MAP = {
    "cancel_order": "request",
    "change_order": "request",
    "change_shipping_address": "request",
    "check_cancellation_fee": "billing",
    "check_invoice": "invoice",
    "check_payment_methods": "billing",
    "check_refund_policy": "refund",
    "complaint": "complaint",
    "contact_human_agent": "human_handoff",
    "create_account": "account",
    "delete_account": "account",
    "delivery_options": "logistics",
    "delivery_period": "logistics",
    "edit_account": "account",
    "get_invoice": "invoice",
    "get_refund": "refund",
    "payment_issue": "payment_issue",
    "place_order": "request",
    "recover_password": "account_security",
    "registration_problems": "account",
    "set_up_shipping_address": "request",
    "switch_account": "account",
    "track_order": "order_status",
    "track_refund": "refund",
}


async def main(args):
    raw = Path(args.dataset).read_bytes()
    dataset = json.loads(raw)
    out = Path("artifacts") / ("public-intents-" + str(time.time_ns()))
    out.mkdir(parents=True)
    s = Settings.from_env().model_copy(update={"db_path": str(out / "state.sqlite")})
    if s.model_backend == "fixture":
        raise ValueError("Public evaluation requires a real model")
    app = create_app(s)
    token = app.state.store.issue_token(Principal("external-eval", "evaluator"))
    records = []
    excluded = []
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://localhost",
        ) as client,
    ):
        for i, row in enumerate(dataset["examples"]):
            if row["label"] not in MAP:
                excluded.append(row)
                continue
            r = await client.post(
                "/intents",
                headers={"Authorization": "Bearer " + token},
                json={"message": row["message"], "request_id": f"public-{i:04d}"},
            )
            pred = r.json().get("intent", "ERROR") if r.status_code == 200 else "ERROR"
            records.append(
                {
                    **row,
                    "expected": MAP[row["label"]],
                    "predicted": pred,
                    "http_status": r.status_code,
                }
            )
            print(i, row["label"], pred, flush=True)
    labels = sorted(set(MAP.values()))
    f1 = {}
    confusion = Counter((r["expected"], r["predicted"]) for r in records)
    for label in labels:
        tp = sum(r["expected"] == r["predicted"] == label for r in records)
        fp = sum(r["expected"] != label and r["predicted"] == label for r in records)
        fn = sum(r["expected"] == label and r["predicted"] != label for r in records)
        f1[label] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0
    report = {
        "type": "external-intent-only",
        "model": s.model_name,
        "source": dataset["source"],
        "license": dataset["license"],
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "source_sha256": dataset["source_sha256"],
        "mapping": MAP,
        "sampled": len(dataset["examples"]),
        "evaluated": len(records),
        "excluded_labels": sorted({r["label"] for r in excluded}),
        "accuracy": sum(r["expected"] == r["predicted"] for r in records)
        / len(records),
        "macro_f1": sum(f1.values()) / len(f1),
        "per_class_f1": f1,
        "confusion": [
            {"expected": a, "predicted": b, "n": n} for (a, b), n in confusion.items()
        ],
        "records": records,
        "limitations": [
            "Synthetic English public training corpus, not live production traffic",
            "Many-to-one ontology mapping disclosed",
            "No refund/order execution score in this report",
        ],
    }
    (out / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("REPORT", out, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=".runtime/datasets/bitext-sample.json")
    asyncio.run(main(parser.parse_args()))
