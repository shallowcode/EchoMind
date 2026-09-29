from supportflow.contracts import Trace, Settings
from supportflow.presentation import clean_answer, execution_view


def test_answer_removes_source_ids_but_keeps_business_status():
    ident = "a" * 64
    answer = f"根据退款政策（知识ID: {ident}），申请 R001 待审核。沙箱只更新测试账本，不发生真实资金转移。"
    cleaned = clean_answer(answer, [{"id": ident}])
    assert ident not in cleaned and "知识ID" not in cleaned
    assert "申请 R001 待审核" in cleaned
    assert "不发生真实资金转移" in cleaned
    assert clean_answer("余额不足，退款未提交。", []) == "余额不足，退款未提交。"


def test_execution_uses_observed_outcomes_and_separates_sources():
    trace = Trace("request-id")
    trace.events = [{"title": "识别意图", "detail": "refund", "status": "completed"}]
    trace.model_calls = 3
    trace.tools = [
        {"name": "knowledge_search", "agent": "billing", "success": True, "duration_ms": 120,
         "result": {"items": [{"id": "doc1"}], "queries": ["退款政策"], "rerank_applied": False, "backend": "sqlite"}},
        {"name": "refund_request", "agent": "billing", "success": False, "error": "private backend diagnostic", "result": None},
    ]
    result = {"status": "partial", "latency_ms": 500, "sources": [{"id": "doc1", "title": "退款政策", "content": "需审核"}]}
    result["tasks"] = [{"title": "退款申请", "agent": "billing", "status": "blocked", "attempts": 2}]
    view = execution_view(result, trace, Settings(model_name="test-model"))
    assert view["tools"][0]["queries"] == ["退款政策"]
    assert view["tools"][0]["reranked"] is False
    assert view["tools"][1]["success"] is False
    assert "private backend diagnostic" not in str(view)
    assert view["tasks"][0]["status"] == "blocked"
    assert view["sources"][0]["title"] == "退款政策"
    assert view["model_calls"] == 3
    assert view["steps"] == trace.events


def test_no_tools_or_sources_are_invented():
    view = execution_view({"status": "completed", "latency_ms": 10}, Trace("id"), Settings())
    assert view["steps"] == []
    assert view["tools"] == []
    assert view["sources"] == []
