from evaluation.full_chain import aggregate, wilson, verify
from evaluation.compare_runs import compare
from supportflow.contracts import Principal
from supportflow.store import Store
import pytest


def test_metric_denominators_latency_cost_unknown():
    def row(ok, ms, cost):
        return {
            "complete": ok,
            "task_ms": ms,
            "request_ms": [ms],
            "input_tokens": 1,
            "output_tokens": 1,
            "model_cost": cost,
            "judge": None,
            "judge_error": None,
            "group": "g",
        }

    a = aggregate([row(True, 10, 0), row(False, 100, None)])
    assert (
        a["completion_rate"] == 0.5
        and a["request_p95_ms"] == 100
        and a["mean_model_cost"] is None
    )
    lo, hi = wilson(1, 2)
    assert lo < 0.5 < hi


def test_response_claim_does_not_substitute_for_database_state(tmp_path):
    s = Store(tmp_path / "db")
    p = Principal("t", "u")
    a = Principal("t", "a", frozenset({"admin"}))
    s.seed_order(a, "ORD1001", 5000, "u")
    case = {
        "expected": {
            "tools": ["refund_request"],
            "refund_amount": 2000,
            "refund_status": "pending",
        }
    }
    fake_response = {
        "response": "我已完成退款",
        "_http_status": 200,
        "trace": {"tools": []},
    }
    assert not verify(case, [fake_response], s, p)["complete"]
    refund = s.refund_request(p, "ORD1001", 2000, "test", "key")
    false_claim = {
        "response": "退款成功，已到账",
        "_http_status": 200,
        "trace": {
            "tools": [{"name": "refund_request", "success": True, "result": refund}]
        },
    }
    assert not verify(case, [false_claim], s, p)["checks"]["no_false_settlement_claim"]


def test_regression_does_not_overwrite_or_mix_datasets():
    def report(rate):
        return {
            "dataset_sha256": "same",
            "evaluated_tasks": 10,
            "transport": "http",
            "concurrency_tasks": 1,
            "settings": {"storage": "sqlite"},
            "summaries": {
                a: {
                    "completion_rate": rate,
                    "request_p95_ms": 10,
                    "mean_model_cost": None,
                }
                for a in ["single", "multi"]
            },
        }

    old = report(1)
    new = report(0.9)
    assert len(compare(old, new)) == 2
    assert old["summaries"]["single"]["completion_rate"] == 1
    new["dataset_sha256"] = "other"
    with pytest.raises(ValueError):
        compare(old, new)
