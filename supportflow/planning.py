"""Request-owned task ledger. Only observed evidence can complete an executable task.

Rules cover the supported service domains, independently of benchmark cases. A plan is
not permission: write authorization always uses the original authenticated request.
Final rendering preserves every task verbatim, so synthesis cannot erase a result.
"""

from dataclasses import dataclass, field
import re
from supportflow.refunds import resolve_refund

# Error numbers require HTTP/error context so a 500-yuan refund is not a failure code.
TECHNICAL_PATTERN = (
    r"登录|登陆|报错|崩溃|无法打开|闪退|故障|超时|login|error|crash"
    r"|(?:HTTP|接口|返回|弹出|提示|出现|遇到|报(?:错)?|错误(?:码)?|status)\s*[:：]?\s*[45]\d{2}(?!\d|\s*元)"
    r"|(?<!\d)[45]\d{2}\s*(?:错误|报错)"
)


@dataclass
class Subtask:
    id: str
    kind: str
    agent: str
    title: str
    instruction: str
    required_tools: list[str] = field(default_factory=list)
    status: str = "pending"
    answer: str = ""
    observations: list[dict] = field(default_factory=list)
    attempts: int = 0
    missing: list[str] = field(default_factory=list)
    started_ms: float = 0
    duration_ms: float = 0
    input: dict = field(default_factory=dict)
    repairs: list[dict] = field(default_factory=list)

    def gaps(self, answer):
        successful = [o for o in self.observations if o.get("success")]
        names = {o["name"] for o in successful}
        gaps = ["缺少成功工具证据：" + n for n in self.required_tools if n not in names]
        if self.denied and re.search(r"超出|超过|不足|不能|无法|拒绝", answer):
            gaps = []
        if "knowledge_search" in self.required_tools and not any(
            o["name"] == "knowledge_search" and o["result"].get("items")
            for o in successful
        ):
            gaps.append("没有可用知识来源")
        if len(answer.strip()) < 10 or answer.strip() in {
            "给用户的回答",
            "处理完成",
            "已完成",
        }:
            gaps.append("没有实质答复")
        if self.kind == "technical" and not re.search(
            r"检查|尝试|重新|清除|更新|确认|配置|重试|重启|保留|记录|联系|提供|check|retry",
            answer,
            re.I,
        ):
            gaps.append("技术问题缺少可执行排查步骤")
        if self.kind == "technical" and re.search(r"订单|退款|工单", answer):
            gaps.append("仅回答技术排查，不要处理或代其他子任务承诺订单、退款、工单")
        if (
            self.kind == "refund"
            and "refund_request" in names
            and not re.search(
                r"待审核|待审批|等待审核|pending|申请已提交|已提交.*申请", answer, re.I
            )
        ):
            gaps.append("必须说明退款申请待审核，不能宣称款项已到账")
        return gaps

    @property
    def denied(self):
        return any(
            o.get("rejection_code") == "insufficient_refundable_balance"
            for o in self.observations
        )

    @property
    def allowed_tools(self):
        return {
            "technical": {"knowledge_search"},
            "order": {"order_lookup", "knowledge_search"},
            "order_list": {"order_list"},
            "product_order": {"order_lookup"},
            "refund": {"order_lookup", "refund_request", "knowledge_search"},
            "refund_details": {"order_lookup"},
            "refund_policy": {"knowledge_search"},
            "refund_status": {"refund_status"},
            "handoff": {"ticket_create"},
        }.get(self.kind)


def plan_tasks(message, entities, default_agent, consent, refund_context=None, refund_status_context=None, order_reference=None):
    if refund_context is None:
        refund_context = resolve_refund(message, {}, [])
        if not consent:
            refund_context["active"] = False
    tasks = []

    def add(kind, agent, title, instruction, tools):
        tasks.append(
            Subtask(f"task-{len(tasks) + 1}", kind, agent, title, instruction, tools)
        )

    technical = bool(
        re.search(
            TECHNICAL_PATTERN,
            message,
            re.I,
        )
    )
    collecting = bool(refund_context and refund_context.get("active"))
    refund = collecting or bool(re.search(r"退款|退还|refund", message, re.I))
    product_task = False
    ambiguous = False
    if order_reference and order_reference.get("active"):
        ambiguous = len(order_reference.get("ids", [])) != 1 or order_reference.get("uncertain")
        if ambiguous or (not refund and not (refund_status_context or {}).get("active")):
            add("product_order", "billing", "商品订单查询", "依据商品对应的真实订单回答；多笔匹配时询问用户选择，不猜测物流。", [] if ambiguous else ["order_lookup"])
            product_task = True
    order = bool(entities.get("order_id")) and bool(
        re.search(r"订单|付款|支付|扣款|账单|物流|发货|order|payment", message, re.I)
    )
    if product_task:
        order = False
    from supportflow.refunds import orders_in
    list_orders = not orders_in(message) and bool(re.search(r"订单|买了什么|买过什么", message)) and not refund and bool(re.search(r"全部|所有|有哪些|列表|我的订单|查.*订单|订单.*查|买了什么|买过什么", message)) and not re.search(r"这个|这笔|该订单|再查|它", message)
    if list_orders:
        order = False
        add("order_list", "billing", "订单列表", "读取并列出可查询的全部订单，不要求提供订单号。", ["order_list"])
    handoff = bool(re.search(r"转人工|人工客服|human agent|紧急", message, re.I))
    if technical:
        add(
            "technical",
            "technical",
            "技术问题",
            "只处理原始请求中的技术问题。检索相关知识，给出具体排查步骤并引用来源；不能承诺已修复。其他任务由同事负责。",
            ["knowledge_search"],
        )
    if order and (
        not refund or re.search(r"查询|查一下|核实|状态|是否.{0,4}支付", message)
    ):
        add(
            "order",
            "billing",
            "订单查询",
            "只核实原始请求中的订单状态，使用已提供订单号查询，并明确告知查得的状态。其他问题由同事负责。",
            ["order_lookup"],
        )
    if refund_status_context and refund_status_context.get("active"):
        add("refund_status", "billing", "退款进度", "读取退款账本当前审批和执行状态；不能依据历史答复或政策推测，不提交新申请。", ["refund_status"])
    elif refund and not (product_task and ambiguous):
        if collecting:
            ready = len(refund_context.get("order_ids", [])) == 1 and (
                refund_context.get("full") or refund_context.get("amount_cents") is not None
            )
            add(
                "refund" if ready else "refund_details", "billing",
                "退款申请" if ready else "补充退款信息",
                "承接当前退款申请，核验订单；全退金额由账本计算，缺少信息仅追问缺少的字段。",
                ["refund_request"] if ready else [],
            )
        else:
            add("refund_policy", "billing", "退款说明", "只查询并简洁说明退款规则，不提交退款。", ["knowledge_search"])
    if handoff:
        add(
            "handoff",
            "general",
            "人工工单",
            "为原始请求创建人工工单，并给出真实工单号和等待接单状态。",
            ["ticket_create"],
        )
    if re.search(r"发票|开票|invoice", message, re.I):
        add(
            "invoice",
            "billing",
            "发票办理",
            "只处理发票诉求，检索发票办理规则，明确当前需人工审核以及缺失信息，不得宣称已经开票。",
            ["knowledge_search"],
        )
    if not tasks:
        add(
            "general",
            default_agent if default_agent != "escalation" else "general",
            "处理结果",
            "完整处理用户请求；业务状态必须依据工具，缺失信息明确追问。",
            [],
        )
    return tasks


def render_tasks(tasks):
    """No freeform rewriting after validation: one section per task, including failures."""
    return "\n\n".join(
        (f"【{t.title}】\n" if len(tasks) > 1 else "") + t.answer
        + (
            "\n尚未完成：" + "；".join(t.missing)
            if t.status not in {"completed", "denied", "awaiting_input"}
            else ""
        )
        for t in tasks
    )


def scope_message(message, task):
    """Keep unrelated requests out of specialist prompts, not just an instruction to ignore.

    The full unmodified message stays in the request's authorization context. Technical
    agents receive the technical clauses; only billing receives order/amount entities.
    """
    if task.kind != "technical":
        return message
    clauses = re.split(r"[，,。；;\n]|同时|另外|而且|并且|顺便|还有", message)
    selected = []
    for clause in clauses:
        if re.search(
            TECHNICAL_PATTERN,
            clause,
            re.I,
        ):
            clause = re.split(r"订单|退款|扣款|账单|ORD\d+", clause, flags=re.I)[0]
            if clause.strip():
                selected.append(clause.strip())
    return "；".join(selected) or "排查用户报告的技术故障：" + "、".join(
        re.findall(TECHNICAL_PATTERN, message, re.I)
    )
