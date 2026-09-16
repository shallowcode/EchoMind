"""Capability filtering, complete JSON Schema validation, scoped cache and single probe breaker."""

import asyncio
import copy
import hashlib
import json
import time
from dataclasses import dataclass
from jsonschema import Draft202012Validator
from supportflow.model import active_trace


def schema(properties, required=None):
    return {
        "type": "object",
        "properties": properties,
        "required": required or list(properties),
        "additionalProperties": False,
    }


STR = {"type": "string", "minLength": 1, "maxLength": 100}


@dataclass
class Breaker:
    threshold: int = 3
    recovery: float = 10
    failures: int = 0
    opened: float = 0
    probe: bool = False

    def enter(self):
        if self.opened:
            if time.monotonic() - self.opened < self.recovery or self.probe:
                return False
            self.probe = True
        return True

    def finish(self, success):
        self.probe = False
        if success:
            self.failures = 0
            self.opened = 0
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened = time.monotonic()


class Tools:
    specs = {
        "knowledge_search": schema(
            {"query": {"type": "string", "minLength": 1, "maxLength": 1500}}
        ),
        "order_lookup": schema({"order_id": STR}),
        "refund_request": schema(
            {
                "order_id": STR,
                "amount_cents": {"type": "integer", "minimum": 1, "maximum": 100000000},
                "reason": {"type": "string", "minLength": 1, "maxLength": 500},
            }
        ),
        "ticket_create": schema(
            {"summary": {"type": "string", "minLength": 1, "maxLength": 1500}}
        ),
        "ticket_status": schema({"ticket_id": STR}),
    }
    descriptions = {
        "knowledge_search": "检索企业政策与排障文档",
        "order_lookup": "查询当前用户订单真实状态",
        "refund_request": "提交待财务审核的退款申请，不会直接付款",
        "ticket_create": "创建人工客服工单",
        "ticket_status": "查看本人已有工单处理状态",
    }
    capabilities = {
        "general": {
            "knowledge_search",
            "order_lookup",
            "ticket_create",
            "ticket_status",
        },
        "technical": {"knowledge_search", "ticket_create", "ticket_status"},
        "billing": set(specs),
        "escalation": {"ticket_create", "ticket_status"},
    }

    def __init__(self, store, knowledge):
        self.store = store
        self.knowledge = knowledge
        self.cache = {}
        self.breakers = {}
        self.counts = {}

    def available(self, agent):
        return [
            {
                "name": n,
                "description": self.descriptions[n],
                "parameters": self.specs[n],
            }
            for n in sorted(self.capabilities[agent])
        ]

    async def call(self, p, agent, name, args, conv, rid, advanced=True, consent=False):
        start = time.perf_counter()
        result = None
        cached = False
        error = None
        trace = active_trace.get()
        try:
            if name not in self.capabilities.get(agent, set()):
                raise PermissionError("Tool outside agent capability")
            Draft202012Validator(self.specs[name]).validate(args)
            if name == "refund_request" and not consent:
                raise PermissionError("Explicit user refund request required")
            if name == "knowledge_search":
                version = await asyncio.to_thread(self.knowledge.version, p.tenant)
                key = hashlib.sha256(
                    json.dumps(
                        [p.tenant, p.user, sorted(p.roles), args, advanced, version],
                        sort_keys=True,
                    ).encode()
                ).hexdigest()
                hit = self.cache.get(key)
                if hit and hit[0] > time.monotonic():
                    cached = True
                    result = copy.deepcopy(hit[1])
                    return result
            breaker = self.breakers.setdefault((p.tenant, name), Breaker())
            if not breaker.enter():
                raise RuntimeError("circuit_open")
            try:
                async with asyncio.timeout(90 if name == "knowledge_search" else 10):
                    if name == "knowledge_search":
                        result = await self.knowledge.retrieve(
                            p.tenant, args["query"], advanced=advanced
                        )
                    elif name == "order_lookup":
                        result = await asyncio.to_thread(
                            self.store.order, p, args["order_id"]
                        )
                    elif name == "refund_request":
                        idem = hashlib.sha256(
                            (rid + name + args["order_id"]).encode()
                        ).hexdigest()
                        result = await asyncio.to_thread(
                            self.store.refund_request,
                            p,
                            args["order_id"],
                            args["amount_cents"],
                            args["reason"],
                            idem,
                        )
                    elif name == "ticket_create":
                        result = await asyncio.to_thread(
                            self.store.create_ticket,
                            p,
                            conv,
                            args["summary"],
                            rid + ":ticket",
                        )
                    else:
                        result = await asyncio.to_thread(
                            self.store.ticket, p, args["ticket_id"]
                        )
            except (PermissionError, ValueError):
                breaker.probe = False  # user errors are not backend outages
                raise
            except BaseException:
                breaker.finish(False)
                raise
            else:
                breaker.finish(True)
            if name == "knowledge_search":
                if len(self.cache) > 1000:
                    self.cache.clear()
                self.cache[key] = (time.monotonic() + 300, copy.deepcopy(result))
            return result
        except BaseException as e:
            error = type(e).__name__ + ": " + str(e)
            raise
        finally:
            ok = result is not None
            c = self.counts.setdefault(
                name, {"total": 0, "success": 0, "latency_ms": 0}
            )
            c["total"] += 1
            c["success"] += int(ok)
            c["latency_ms"] += (time.perf_counter() - start) * 1000
            if trace:
                trace.tools.append(
                    {
                        "name": name,
                        "agent": agent,
                        "success": ok,
                        "cached": cached,
                        "duration_ms": (time.perf_counter() - start) * 1000,
                        "arguments": args,
                        "result": result,
                        "error": error,
                    }
                )
