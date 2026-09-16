"""Verify data isolation and state-based evaluation, without evaluating holdout answers."""

from collections import Counter
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from evaluation.full_chain import aggregate, answer_contains, prepare_fixture, verify
from scripts.build_acceptance_dataset import build, canonical
from supportflow.contracts import Principal, Trace
from supportflow.model import active_trace
from supportflow.store import Store
from supportflow.tools import Tools

ROOT = Path(__file__).resolve().parents[1]


def test_reviewer_qualifier_is_not_a_different_refund_state():
    assert answer_contains("申请已提交，当前待财务审核", "待审核")
    assert answer_contains("当前待人工审核", "待审核")
    assert answer_contains("当前待财务审核", "待财务审核")
    assert not answer_contains("申请尚未建立，请先提供金额", "待审核")


def test_frozen_splits_and_business_labels():
    splits = build()
    manifest = json.loads(
        (ROOT / "evaluation/datasets/trial-v3/manifest.json").read_text(
            encoding="utf-8"
        )
    )
    ids, families, texts = set(), {}, {}
    for split, count in [
        ("development", 600),
        ("validation", 200),
        ("acceptance", 400),
    ]:
        raw = (ROOT / f"evaluation/datasets/trial-v3/{split}.json").read_bytes()
        assert hashlib.sha256(raw).hexdigest() == manifest["splits"][split]["sha256"]
        assert json.loads(raw)["cases"] == splits[split]
        assert len(splits[split]) == count
        for case in splits[split]:
            assert case["id"] not in ids
            ids.add(case["id"])
            for value, registry in [
                (case["family"], families),
                (canonical(case["turns"]), texts),
            ]:
                assert registry.setdefault(value, split) == split
            expected = case["expected"]
            if expected["refund_count"]:
                assert 0 < expected["refund_amount"] <= case["order"]["total_cents"]
                assert expected["refund_order_id"] == case["order"]["id"]
    assert len(ids) == 1200 and len(families) == 48
    assert set(
        Counter(c["family"] for cases in splits.values() for c in cases).values()
    ) == {25}
    smoke = json.loads(
        (ROOT / "evaluation/datasets/trial-v3/smoke.json").read_text(encoding="utf-8")
    )
    assert len(smoke["cases"]) == 8
    assert all(c in splits["development"] for c in smoke["cases"])


def test_variable_order_and_answer_components(tmp_path):
    store = Store(tmp_path / "db")
    p = Principal("t", "u")
    admin = Principal("t", "a", frozenset({"admin"}))
    store.seed_order(admin, "ORD9999", 5000, p.user)
    case = {
        "order": {"id": "ORD9999"},
        "expected": {
            "tools": ["order_lookup"],
            "refunded_cents": 0,
            "answer_groups": [["401"], ["已支付"]],
            "tool_arguments": [
                {"name": "order_lookup", "arguments": {"order_id": "ORD9999"}}
            ],
        },
    }
    response = {
        "_http_status": 200,
        "response": "401 需要排查，订单已支付。",
        "trace": {
            "tools": [
                {
                    "name": "order_lookup",
                    "arguments": {"order_id": "ORD9999"},
                    "success": True,
                }
            ]
        },
    }
    assert verify(case, [response], store, p)["complete"]
    response["response"] = "401 需要排查。"
    assert not verify(case, [response], store, p)["checks"]["answer_group_1"]
    response["trace"]["tools"][0]["arguments"]["order_id"] = "ORD1001"
    assert not verify(case, [response], store, p)["checks"]["tool_arguments_0"]


def test_refund_on_wrong_order_is_failure(tmp_path):
    store = Store(tmp_path / "db")
    p = Principal("t", "u")
    admin = Principal("t", "a", frozenset({"admin"}))
    store.seed_order(admin, "ORD9999", 5000, p.user)
    store.refund_request(p, "ORD9999", 100, "test", "idempotency")
    case = {
        "expected": {
            "tools": [],
            "refund_count": 1,
            "refund_amount": 100,
            "refund_order_id": "ORD8888",
        }
    }
    result = verify(case, [{"_http_status": 200, "response": "待审核"}], store, p)
    assert result["checks"]["refund_amount"]
    assert not result["checks"]["refund_order"]


def test_expected_denial_does_not_skip_evidence(tmp_path):
    store = Store(tmp_path / "db")
    p = Principal("t", "u")
    case = {
        "expected": {
            "tools": [],
            "allow_blocked": True,
            "refund_count": 0,
            "forbidden_success_tools": ["order_lookup"],
            "answer_groups": [["无权"]],
        }
    }
    response = {
        "_http_status": 200,
        "response": "无权访问",
        "tasks": [{"status": "blocked"}],
        "trace": {"tools": []},
    }
    assert verify(case, [response], store, p)["complete"]
    response["trace"]["tools"].append({"name": "order_lookup", "success": True})
    assert not verify(case, [response], store, p)["checks"]["no_forbidden_access"]
    response["trace"]["tools"] = []
    response["response"] = "已查到"
    assert not verify(case, [response], store, p)["complete"]


@pytest.mark.asyncio
async def test_fixture_ownership_and_outage_use_real_tool_guard(tmp_path):
    class Knowledge:
        def seed(self, tenant):
            pass

        def version(self, tenant):
            return 1

    store = Store(tmp_path / "db")
    service = SimpleNamespace(store=store, knowledge=Knowledge())
    p = Principal("tenant", "caller")
    # Independent evaluator fixture: do not execute any acceptance case or model response.
    case = {
        "order": {"id": "ORD9999", "total_cents": 5000},
        "fixture": {
            "order_tenant": "elsewhere",
            "order_owner": "someone",
            "knowledge_unavailable": True,
        },
        "expected": {"tools": [], "refunded_cents": 0},
    }
    await prepare_fixture(service, case, p)
    with pytest.raises(PermissionError):
        store.order(p, "ORD9999")
    assert verify(case, [{"_http_status": 200}], store, p)["checks"]["settled_balance"]
    trace = Trace("fault-test")
    marker = active_trace.set(trace)
    try:
        with pytest.raises(RuntimeError, match="Injected knowledge"):
            await Tools(store, service.knowledge).call(
                p, "technical", "knowledge_search", {"query": "401"}, "conv", "request"
            )
    finally:
        active_trace.reset(marker)
    assert trace.tools[0]["success"] is False
    assert "Injected knowledge" in trace.tools[0]["error"]


def test_family_weighting_does_not_count_copies_as_new_families():
    def row(family, complete):
        return {
            "family": family,
            "complete": complete,
            "model_cost": None,
            "task_ms": 1,
            "request_ms": [1],
            "input_tokens": 0,
            "output_tokens": 0,
            "judge": None,
            "judge_error": None,
            "group": "g",
        }

    result = aggregate([row("a", True)] * 25 + [row("b", False)])
    assert result["completion_rate"] == 25 / 26
    assert result["family_count"] == 2
    assert result["family_macro_completion"] == 0.5
