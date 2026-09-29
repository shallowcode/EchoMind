"""Public execution facts and customer-facing answers, independent of model reasoning."""

import re

AGENTS = {"billing": "账单助手", "technical": "技术助手", "general": "通用助手", "escalation": "人工接管"}
TOOLS = {"knowledge_search": "知识检索", "order_lookup": "订单查询", "refund_request": "退款申请", "refund_status": "退款进度查询", "ticket_create": "创建工单", "ticket_lookup": "工单查询"}


def clean_answer(answer, sources):
    """Remove source identifiers, never rewrite business outcomes or failure text."""
    for source in sources:
        ident = re.escape(source["id"])
        answer = re.sub(r"[（(]\s*(?:知识\s*ID|来源\s*(?:ID|id)?|source\s*id)\s*[:：]?\s*" + ident + r"\s*[)）]", "", answer, flags=re.I)
        answer = re.sub(r"\[\s*" + ident + r"\s*\]", "", answer)
        answer = answer.replace(source["id"], "")
    return answer.strip()


def execution_view(result, trace, settings):
    """Only report observed stages, tool outcomes and retrieved documents."""
    tools = []
    for call in trace.tools:
        value = call.get("result") or {}
        if not isinstance(value, dict):
            value = {}
        item = {
            "name": call["name"], "title": TOOLS.get(call["name"], call["name"]),
            "agent": AGENTS.get(call.get("agent"), call.get("agent", "")),
            "success": bool(call.get("success")), "cached": bool(call.get("cached")),
            "duration_ms": round(call.get("duration_ms", 0), 1),
            "shared": bool(call.get("shared")), "arguments": call.get("arguments", {}),
            "result": call.get("result"), "error": "工具执行失败" if call.get("error") else None,
            "controls": call.get("controls", {}), "transport": call.get("transport", "shared_service"),
        }
        if not item["success"]:
            item["detail"] = "调用未成功，未据此确认业务完成"
        elif call["name"] == "knowledge_search":
            item.update({
                "detail": f"返回 {len(value.get('items', []))} 条资料",
                "queries": value.get("queries", []),
                "backend": value.get("backend", ""),
                "reranked": bool(value.get("rerank_applied")),
                "degraded": value.get("degraded", []),
            })
        elif call["name"] == "order_lookup":
            item["detail"] = f"{value.get('id', '')} · {value.get('status', '')}"
        elif call["name"] == "order_list":
            item["title"] = "查询全部订单"
            item["detail"] = f"返回 {value.get('total', 0)} 笔订单"
        elif call["name"] == "refund_status":
            labels = {"pending": "待审核", "approved": "已批准 · 待执行", "processing": "退款处理中", "settled": "已退款", "rejected": "已拒绝", "failed": "退款失败"}
            item["detail"] = value.get("order_id", "") + " · " + ("；".join(labels.get(r["status"], r["status"]) + f" {r['amount'] / 100:.2f} 元" for r in value.get("items", [])) or "无退款记录")
        else:
            item["detail"] = str(value.get("status", "已返回结果"))
        tools.append(item)
    return {
        "schema_version": 2,
        "model": settings.model_name,
        "thinking": settings.model_thinking,
        "status": result["status"],
        "duration_ms": round(result["latency_ms"], 1),
        "model_calls": trace.model_calls,
        "steps": list(trace.events),
        "tasks": [{**t, "agent": AGENTS.get(t["agent"], t["agent"])} for t in result.get("tasks", [])],
        "skills": trace.skills,
        "limits": {"max_tool_rounds": settings.max_tool_rounds, "request_timeout": settings.request_timeout},
        "tools": tools,
        "sources": [{"id": s["id"], "title": s.get("title", "知识文档"), "content": s.get("content", "")} for s in result.get("sources", [])],
        "memory": trace.memory,
        "knowledge": [{"query": call.get("arguments", {}).get("query", ""), "success": call.get("success", False),
                       "cached": call.get("cached", False), "result": call.get("result"), "error": call.get("error")}
                      for call in trace.tools if call["name"] == "knowledge_search"],
        "model_inputs": trace.model_inputs,
        "failures": list(trace.failures),
    }
