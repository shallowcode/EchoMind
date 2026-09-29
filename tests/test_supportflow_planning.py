import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from agents.agent_orchestrator import AgentType, Request
from supportflow.contracts import Settings, Principal, ToolCall, Trace
from supportflow.model import Model, active_trace
from supportflow.planning import plan_tasks, render_tasks, scope_message
from supportflow.service import ToolAgent, job
from supportflow.store import Store
from supportflow.tools import Tools
from evaluation.full_chain import verify
from supportflow.pricing import estimate_call


def test_glm_cost_uses_each_call_output_tier():
    s = Settings(pricing_profile="glm-air-20260908")
    assert estimate_call(s, 1000, 199) == pytest.approx((800 + 398) / 1e6)
    assert estimate_call(s, 1000, 200) == pytest.approx((800 + 1200) / 1e6)
    assert estimate_call(s, 32000, 200) == pytest.approx((38400 + 1600) / 1e6)


def test_compound_plan_covers_order_and_technical():
    tasks = plan_tasks(
        "登录报401，帮我查订单 ORD1001 是否支付",
        {"order_id": ["ORD1001"]},
        "technical",
        False,
    )
    assert [(t.kind, t.required_tools) for t in tasks] == [
        ("technical", ["knowledge_search"]),
        ("order", ["order_lookup"]),
    ]
    assert "ticket_create" not in tasks[0].allowed_tools
    scoped = scope_message("登录报401，帮我查订单 ORD1001 是否支付", tasks[0])
    assert "401" in scoped and "ORD1001" not in scoped and "支付" not in scoped


def test_handoff_does_not_erase_other_tasks():
    tasks = plan_tasks(
        "登录401，申请订单 ORD1001 退款10元，也转人工",
        {"order_id": ["ORD1001"]},
        "escalation",
        True,
    )
    assert [t.kind for t in tasks] == ["technical", "refund", "handoff"]


@pytest.mark.parametrize(
    "message",
    [
        "接口报500，查询订单 ORD1001 状态",
        "返回502错误，同时查订单 ORD1001",
        "HTTP 404，查询订单 ORD1001",
        "进入账号时弹出401。另请核实订单 ORD1001 的支付状态。",
        "提示403，查询订单 ORD1001",
    ],
)
def test_http_server_and_client_errors_are_technical_tasks(message):
    tasks = plan_tasks(message, {"order_id": ["ORD1001"]}, "billing", False)
    assert tasks[0].kind == "technical"
    assert "ORD1001" not in scope_message(message, tasks[0])


def test_refund_amount_is_not_an_http_error():
    tasks = plan_tasks(
        "请申请订单 ORD1001 退款500元", {"order_id": ["ORD1001"]}, "billing", True
    )
    assert [t.kind for t in tasks] == ["refund"]


def test_completion_requires_own_evidence_and_keeps_failed_section():
    tasks = plan_tasks(
        "登录401并查询订单 ORD1001", {"order_id": ["ORD1001"]}, "technical", False
    )
    assert tasks[0].gaps("请检查 Token 是否过期并重新登录。")
    tasks[0].status = "blocked"
    tasks[0].answer = "尚未获得知识来源，无法确认。"
    tasks[0].missing = ["知识库不可用"]
    tasks[1].status = "completed"
    tasks[1].answer = "订单 ORD1001 已支付。"
    rendered = render_tasks(tasks)
    assert all(t.title in rendered and t.answer in rendered for t in tasks)
    assert "知识库不可用" in rendered


def test_business_refusal_is_terminal_but_backend_failure_is_not():
    task = plan_tasks(
        "申请订单 ORD1001 退款100元", {"order_id": ["ORD1001"]}, "billing", True
    )[0]
    answer = "申请金额超过订单可退余额，不能提交退款申请。"
    task.observations = [
        {"name": "refund_request", "success": False, "error": "timeout"}
    ]
    assert task.gaps(answer) and not task.denied
    task.observations[0]["rejection_code"] = "insufficient_refundable_balance"
    assert task.denied and not task.gaps(answer)


@pytest.mark.asyncio
async def test_glm_json_object_adapter_and_usage():
    settings = Settings(
        model_url="https://open.bigmodel.cn/api/paas/v4",
        model_name="glm-4.5-air",
        model_key="test-only",
        local_chat_template=False,
        supports_json_schema=False,
        model_thinking="disabled",
    )
    model = Model(settings)
    await model.client.aclose()

    def handle(request):
        body = json.loads(request.content)
        assert body["response_format"] == {"type": "json_object"}
        assert body["thinking"] == {"type": "disabled"}
        assert "chat_template_kwargs" not in body
        assert "JSON Schema" in body["messages"][0]["content"]
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"ok":true}'}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            },
        )

    model.client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
    trace = Trace("test-glm")
    token = active_trace.set(trace)
    try:
        assert await model.complete([], json_mode={"type": "object"}) == '{"ok":true}'
        assert (trace.input_tokens, trace.output_tokens) == (10, 5)
    finally:
        active_trace.reset(token)
        await model.close()


@pytest.mark.asyncio
async def test_parallel_ticket_reuses_canonical_request_and_keeps_store_guard(tmp_path):
    store = Store(tmp_path / "ledger")
    p = Principal("t", "alice")
    store.acquire_conversation(p, "conv", "lease", 60)
    tools = Tools(store, None)
    model = SimpleNamespace(settings=Settings())
    skills = SimpleNamespace(prompt_for=lambda *a: "")
    agent = ToolAgent(AgentType.GENERAL, model, skills, tools)
    req = Request("登录和订单都要人工处理", p.user, "conv", request_id="request-test")
    j = {
        "p": p,
        "variant": "multi",
        "original": req.message,
        "consent": False,
        "shared": {},
        "locks": {},
    }
    first, second = await asyncio.gather(
        *[
            agent._execute_tool(
                j,
                "general",
                ToolCall(name="ticket_create", arguments={"summary": summary}),
                req,
            )
            for summary in ["技术摘要", "账单摘要"]
        ]
    )
    assert first["id"] == second["id"]
    assert first["summary"] == req.message
    assert tools.counts["ticket_create"]["total"] == 1
    with pytest.raises(ValueError):
        store.create_ticket(p, "conv", "changed", "request-test:ticket")


@pytest.mark.asyncio
async def test_missing_evidence_repairs_same_task_before_completion(tmp_path):
    class ModelFixture:
        settings = Settings(max_tool_rounds=3)
        calls = 0

        async def complete(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 2:
                return json.dumps(
                    {
                        "answer": "",
                        "tool_calls": [
                            {
                                "name": "order_lookup",
                                "arguments": {"order_id": "ORD1001"},
                            }
                        ],
                    }
                )
            return json.dumps(
                {"answer": "订单 ORD1001 已支付（paid）。", "tool_calls": []}
            )

    store = Store(tmp_path / "db")
    p = Principal("t", "alice")
    store.seed_order(
        Principal("t", "admin", frozenset({"admin"})), "ORD1001", 1000, p.user
    )
    tools = Tools(store, None)
    model = ModelFixture()
    agent = ToolAgent(
        AgentType.BILLING, model, SimpleNamespace(prompt_for=lambda *a: ""), tools
    )
    # Order status now renders deterministically from the tool. Exercise the
    # generic evidence-repair loop with an agent-owned task instead.
    from supportflow.planning import Subtask
    task = Subtask("task-1", "general", "billing", "核验信息", "先核验业务信息", ["order_lookup"])
    token = job.set(
        {
            "p": p,
            "variant": "multi",
            "task": task,
            "consent": False,
            "shared": {},
            "locks": {},
        }
    )
    try:
        await agent._call_llm(
            Request(
                "查询订单 ORD1001",
                p.user,
                "conv",
                entities={"order_id": ["ORD1001"]},
                request_id="request-repair",
            )
        )
        assert task.status == "completed" and task.attempts == 3
        assert task.repairs[0]["action"] == "补齐缺项，保留成功操作"
        assert tools.counts["order_lookup"]["total"] == 1
    finally:
        job.reset(token)


@pytest.mark.parametrize(
    "answer,valid",
    [
        ("已退款0分。", True),
        ("已退款金额为0分。", True),
        ("已退款金额为10分。", False),
        ("退款成功0元。", False),
        ("已退款0.00元。", True),
        ("已退款10元。", False),
        ("已退款0.01元。", False),
        ("退款成功。", False),
    ],
)
def test_zero_refund_is_not_a_settlement_claim(tmp_path, answer, valid):
    store = Store(tmp_path / "db")
    result = verify(
        {"expected": {"tools": []}},
        [{"_http_status": 200, "response": answer}],
        store,
        Principal("t", "u"),
    )
    assert result["checks"]["no_false_settlement_claim"] is valid
