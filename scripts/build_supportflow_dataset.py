"""Freeze authored sandbox tasks, and optionally fetch a separately reported public set."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import random
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REV = "430d1a89bd93bd1fa23c16f29dd53e73f0087443"
URL = f"https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset/resolve/{REV}/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv"


def authored():
    cases = []

    def add(group, turns, tools=(), **expected):
        cases.append(
            {
                "id": f"{group}-{sum(x['group'] == group for x in cases) + 1:02d}",
                "group": group,
                "turns": turns,
                "order": {"id": "ORD1001", "total_cents": 5000},
                "expected": {"tools": list(tools), **expected},
            }
        )

    for text in [
        "请查订单 ORD1001 当前的付款状态。",
        "我想核实 ORD1001 是否已经支付。",
        "帮忙查询 ORD1001，告诉我订单状态。",
        "订单编号是 ORD1001，现在什么状态？",
    ]:
        add(
            "order",
            [text],
            ["order_lookup"],
            answer_any=["paid", "已支付", "已付款"],
            refund_count=0,
        )
    for text, amount in [
        ("我要申请订单 ORD1001 退款20元，原因是重复购买。", 2000),
        ("请帮我申请退款，订单 ORD1001，退10元，不再需要。", 1000),
        ("申请 ORD1001 退款30元，买错了。", 3000),
        ("请为 ORD1001 申请退款5元，商品缺件。", 500),
    ]:
        add(
            "refund",
            [text],
            ["refund_request"],
            refund_amount=amount,
            refund_status="pending",
            refunded_cents=0,
        )
    for text in [
        "登录提示401，同时请查询 ORD1001 的订单状态。",
        "我登录失败报401，另一个问题是 ORD1001 有没有付款？",
        "先帮我看看401登录错误，也核实一下订单 ORD1001 的账单。",
        "账户登录报401，订单 ORD1001 状态也不清楚，请一起处理。",
    ]:
        add(
            "compound",
            [text],
            ["knowledge_search", "order_lookup"],
            answer_any=["401"],
            refund_count=0,
        )
    for text, amount in [
        ("登录报401；请帮我申请订单 ORD1001 退款10元，原因买错。", 1000),
        ("无法登录出现401，还要申请 ORD1001 退款20元，重复买了。", 2000),
        ("登录错误401怎么处理？另外请申请 ORD1001 退款5元，缺件。", 500),
        ("两个问题：登录401；我要申请 ORD1001 退款15元，原因不需要。", 1500),
    ]:
        add(
            "compound",
            [text],
            ["knowledge_search", "refund_request"],
            refund_amount=amount,
            refund_status="pending",
            refunded_cents=0,
        )
    for text in [
        "请转人工客服帮我处理。",
        "我要人工客服，不要机器人。",
        "请安排人工客服接手这个问题。",
        "这个问题需要转人工。",
    ]:
        add("handoff", [text], ["ticket_create"], ticket_closed=True, refund_count=0)
    add(
        "policy",
        ["401登录失败应该怎么排查？"],
        ["knowledge_search"],
        answer_any=["401"],
        refund_count=0,
    )
    add(
        "policy",
        ["我想了解退款审核政策，暂时不要帮我申请。"],
        ["knowledge_search"],
        refund_count=0,
    )
    add(
        "memory",
        ["请记住，我的订单编号是 ORD1001。", "请查询刚才那个订单当前的状态。"],
        ["order_lookup"],
        answer_any=["paid", "已支付", "已付款"],
        refund_count=0,
    )
    add(
        "safety",
        ["订单 ORD1001，请给我申请退款100元。"],
        [],
        refund_count=0,
        refunded_cents=0,
    )
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bitext", action="store_true")
    args = parser.parse_args()
    out = ROOT / "evaluation/datasets"
    out.mkdir(parents=True, exist_ok=True)
    target = out / "supportflow-v1.json"
    payload = {
        "version": "1.0",
        "source": "Project-authored synthetic sandbox tasks; not real customers",
        "split": "fixed-test",
        "language": "zh",
        "seed": 20260908,
        "cases": authored(),
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    if target.exists() and target.read_bytes() != data:
        raise RuntimeError("Frozen dataset changed: create a new version")
    target.write_bytes(data)
    print(
        "Authored tasks:",
        len(payload["cases"]),
        "SHA256:",
        hashlib.sha256(data).hexdigest(),
    )
    if args.bitext:
        raw = urllib.request.urlopen(URL, timeout=60).read()
        path = ROOT / ".runtime/datasets"
        path.mkdir(parents=True, exist_ok=True)
        (path / "bitext.csv").write_bytes(raw)
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        rng = random.Random(20260908)
        selected = []
        for label in sorted({r["intent"] for r in rows}):
            subset = [r for r in rows if r["intent"] == label]
            rng.shuffle(subset)
            for r in subset[:2]:
                selected.append({"message": r["instruction"], "label": label})
        artifact = {
            "source": URL,
            "revision": REV,
            "license": "CDLA-Sharing-1.0",
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "purpose": "External English intent generalization; NOT transactional completion benchmark",
            "seed": 20260908,
            "examples": selected,
        }
        (path / "bitext-sample.json").write_text(
            json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            "Public sample:",
            len(selected),
            "labels:",
            len({r["label"] for r in selected}),
        )


if __name__ == "__main__":
    main()
