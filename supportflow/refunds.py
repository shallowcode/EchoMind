"""Refund slots come from user turns; monetary authority stays in the ledger."""

from decimal import Decimal
import re

FULL = r"全(?:额|部)?(?:都)?退(?:款|还)?|退(?:还)?全部|full refund|refund (?:it )?all"
CANCEL = r"(?:不要|不用|不想|暂不|别|取消|撤销)(?:再|给我|帮我|申请|这个|这笔|全部|全额|全|的|了|办理|\s){0,5}(?:退款|退还|退)|不(?:能|要|想)?(?:全额|全部|全)?退(?:了|款)?|do not.{0,8}refund"
QUESTION = r"吗|么|如何|怎么|能否|是否|能不能|什么|规则|条件|流程|[?？]|如果|假如|比如|例如"


def orders_in(message):
    return list(dict.fromkeys(re.findall(r"(?:订单(?:编号|号)?(?:是)?|order(?:_id)?|#)\s*[:：#]?\s*([A-Za-z0-9_-]{4,32})", message, re.I) + re.findall(r"\bORD\d{3,20}\b", message, re.I)))


def resolve_refund_status(message, state, history):
    """Read-only follow-ups use user references; assistant text cannot invent an ID."""
    topic = bool(re.search(r"退款|退钱|退费|退到|退了|退完|rf_[a-f0-9]{32}|refund", message, re.I))
    progress = bool(re.search(r"进度|状态|审核|审批|批准|到账|退到|退了|退完|完成|成功|怎么样|结果|查.{0,8}(?:退款|退钱|退费|rf_)|处理.{0,5}(?:了|吗)|有.{0,3}消息|status", message, re.I))
    policy = bool(re.search(r"规则|条件|政策|流程|如何申请|怎么申请|怎样申请|怎么退款|能不能退|能退吗", message))
    prior = state.get("last_refund") or state.get("refund_flow") or {}
    recent_refund = bool(prior) or any(re.search(r"退款|退钱|退费|全.{0,2}退", turn.get("content", "")) for turn in history[-6:])
    identifiers = re.findall(r"\brf_[a-f0-9]{32}\b", message, re.I)
    orders = orders_in(message)
    if state.get("refund_status_pending") and (orders or identifiers) and re.fullmatch(r"\s*(?:(?:订单|退款申请)(?:编号|号)?[：:\s]*)?[A-Za-z0-9_-]+\s*", message):
        return {"active": True, "order_ids": orders, "refund_ids": identifiers}
    if policy or not progress or not (topic or (recent_refund and "订单" not in message)):
        return {"active": False}
    # Explicit fresh requests are still handled by the refund authorization path.
    if re.search(r"(?:我要|我想|请|帮我|给我|重新|再)(?:申请|办理)?退款\s*(?:\d|[。！!]|$)", message):
        return {"active": False}
    if not orders and not identifiers:
        orders = state.get("order_reference", {}).get("ids", [])
    if not orders and not identifiers:
        for turn in reversed(history):
            if turn.get("role") == "user":
                orders = orders_in(turn.get("content", ""))
                if orders:
                    break
        if not orders and prior.get("order_id"):
            orders = [prior["order_id"]]
        if not orders:
            orders = prior.get("order_ids", [])
    return {"active": True, "order_ids": orders, "refund_ids": identifiers}


def resolve_refund(message, state, history, resolved_order_ids=None):
    previous = dict(state.get("refund_flow") or {})
    if previous.get("status") != "collecting":
        previous = {}
    if re.search(CANCEL, message, re.I):
        state.pop("refund_flow", None)
        return {"active": False, "consent": False, "cancelled": True}
    clauses = re.split(r"[，,。；;！!\n]", message)
    full = any(re.search(FULL, clause, re.I) and not re.search(QUESTION + r"|不|没|别|取消|撤销|他说|她说|示例|例子|[\"“”「」]", clause, re.I) for clause in clauses)
    question = bool(re.search(QUESTION, message, re.I))
    explicit = any(re.search(r"(?:申请|我要|我想|请|帮我|给我|确认|want|please|request).{0,16}(?:退款|退还|refund)|(?:退款|refund).{0,12}(?:申请|确认|please|给我|吧)", clause, re.I) and not re.search(QUESTION + r"|没(?:有)?说|并非|不是|示例|例子|他说|她说|[\"“”「」]", clause, re.I) for clause in clauses)
    # A policy/hypothetical question cannot authorize a money operation.
    explicit = bool(explicit or full)
    orders = orders_in(message) or resolved_order_ids or []
    amounts = re.findall(r"(?<![\d.\-−])(\d+(?:\.\d{1,2})?)\s*元", message)
    if previous and re.fullmatch(r"\s*\d+(?:\.\d{1,2})?\s*", message):
        amounts = [message.strip()]
    order_reply = bool(orders) and bool(re.fullmatch(r"\s*(?:我的)?(?:订单(?:号)?(?:是)?\s*[:：]?\s*)?[A-Za-z0-9_-]{4,32}\s*[。.]?", message))
    amount_reply = bool(amounts) and bool(re.fullmatch(r"\s*(?:退款金额|金额|只退|就退|退给我|给我退|退我|退款|退还|退)?(?:是|为)?\s*\d+(?:\.\d{1,2})?\s*元?\s*(?:吧|就行|就好)?[。.]?\s*", message))
    slot_reply = order_reply or amount_reply or bool(resolved_order_ids)
    if not explicit and (not previous or not slot_reply or question):
        state.pop("refund_flow", None)
        return {"active": False, "consent": False}
    flow = previous or {"order_ids": [], "amount_cents": None, "full": False}
    if orders:
        if flow.get("order_ids") and orders != flow.get("order_ids"):
            flow.update(amount_cents=None, full=False)
        flow["order_ids"] = orders
    elif full and not flow.get("order_ids"):
        # Supports an already-open conversation from before refund slots existed.
        # Only the user's own order reference is eligible, never an assistant claim.
        for turn in reversed(history):
            if turn.get("role") == "user":
                referenced = orders_in(turn.get("content", ""))
                if referenced:
                    flow["order_ids"] = referenced
                    break
    if full:
        flow.update(full=True, amount_cents=None)
    elif amounts:
        values = {int(Decimal(value) * 100) for value in amounts}
        flow.update(full=False, amount_cents=values.pop() if len(values) == 1 else None)
    flow.update(status="collecting", active=True, consent=True)
    state["refund_flow"] = flow
    return flow


def validate_refund_call(flow, arguments):
    if not flow.get("active") or not flow.get("consent"):
        raise PermissionError("缺少用户明确的退款申请")
    if len(flow.get("order_ids", [])) != 1 or arguments.get("order_id") != flow["order_ids"][0]:
        raise PermissionError("退款订单尚未明确或与用户选择不符")
    if flow.get("full"):
        if arguments.get("full_refund") is not True or "amount_cents" in arguments:
            raise PermissionError("全退必须由账本计算当前可退余额")
    elif flow.get("amount_cents") is None or arguments.get("amount_cents") != flow["amount_cents"] or arguments.get("full_refund"):
        raise PermissionError("退款金额必须与用户明确提供的金额一致")
