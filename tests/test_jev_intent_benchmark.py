import asyncio
import json
import pytest
from evaluation.jev_intent_benchmark import (
    Budget, BudgetStop, IntentCategory, Wire, build_dataset,
    jev_payload, metrics, paired_stats, validate_jev,
)
import httpx


def test_fixed_balanced_dataset_and_no_gold_in_payload():
    rows = build_dataset()["examples"]
    assert len(rows) == 48
    for language in ["zh", "en"]:
        for label in ["refund", "invoice", "order_status", "human_handoff"]:
            assert sum(r["language"] == language and r["expected"] == label for r in rows) == 6
    payload = asyncio.run(jev_payload({**rows[0], "expected": "GOLD_CANARY"}))
    assert "GOLD_CANARY" not in json.dumps(payload)
    assert len(payload["questions"]["intent"]["criteria"]) == 19


def test_error_stays_in_accuracy_and_f1_denominators():
    rows = [{"expected":"refund","predicted":"refund","total_ms":10},
            {"expected":"refund","predicted":"ERROR","total_ms":90,"error":"timeout"}]
    m = metrics(rows)
    assert m["accuracy"] == .5
    assert m["per_class_f1"]["refund"] == pytest.approx(2/3)
    assert m["failure_rate"] == .5 and m["p95_ms"] == 90


def test_budget_rejects_before_network(tmp_path):
    budget = Budget(tmp_path/"budget.json")
    budget.data["calls"] = [{"reserved_usd":.449999}]
    with pytest.raises(BudgetStop):
        budget.reserve("glm","case",{"messages":[]})
    assert len(budget.data["calls"]) == 1


def test_ambiguous_timeout_keeps_reservation(tmp_path):
    async def run():
        def handler(request):
            raise httpx.ReadTimeout("test")
        budget = Budget(tmp_path/"budget.json")
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            wire = Wire(client,budget,"jev","case",tmp_path)
            with pytest.raises(httpx.ReadTimeout):
                await wire.post("https://example.test",json={"state":"test"},headers={})
        restored = Budget(tmp_path/"budget.json")
        assert restored.used() > 0
        assert restored.data["calls"][0]["status"] == "uncertain_reserved"
    asyncio.run(run())


def test_observed_cost_and_missing_usage(tmp_path):
    budget = Budget(tmp_path/"budget.json")
    record = budget.reserve("jev","one",{})
    budget.settle(record,{"usage":{"input_tokens":100,"output_tokens":10,"cost":.00001}})
    assert budget.used() == .00001
    missing = budget.reserve("glm","two",{})
    reserved = missing["reserved_usd"]
    budget.settle(missing,{})
    assert budget.used() == pytest.approx(.00001+reserved)


def test_bad_decision_distribution_is_rejected():
    probs = {c.value:0 for c in IntentCategory}
    probs["refund"] = 1
    body = {"answers":{"intent":{"type":"choice","choice":"refund","probabilities":probs,"confidence":1}}}
    assert validate_jev(body)["choice"] == "refund"
    probs["refund"] = float("nan")
    with pytest.raises(ValueError):
        validate_jev(body)


def test_paired_stats_uses_only_matched_cases():
    rows = [{"id":"a","arm":"glm","expected":"refund","predicted":"other"},
            {"id":"a","arm":"jev","expected":"refund","predicted":"refund"},
            {"id":"b","arm":"glm","expected":"refund","predicted":"refund"}]
    assert paired_stats(rows)["n_pairs"] == 1
    assert paired_stats(rows)["jev_only_correct"] == 1
