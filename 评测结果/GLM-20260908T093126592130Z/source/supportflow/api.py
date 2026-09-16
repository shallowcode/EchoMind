"""Authenticated primary HTTP API; business writes have strict schemas and persistent state."""

from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, Field
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from supportflow.contracts import Settings, ChatInput, Principal
from supportflow.store import Store
from supportflow.model import Model
from supportflow.knowledge import Knowledge
from supportflow.tools import Tools
from supportflow.service import ChatService
from supportflow.protocol import build_mcp
from supportflow.payments import Payments


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RefundInput(Strict):
    order_id: str = Field(min_length=1, max_length=100)
    amount_cents: int = Field(strict=True, gt=0)
    reason: str = Field(min_length=1, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=100)


class Approval(Strict):
    approve: bool = True


class TicketInput(Strict):
    conv_id: str = Field(min_length=1, max_length=80)
    summary: str = Field(min_length=1, max_length=1500)
    idempotency_key: str = Field(min_length=8, max_length=100)


class TicketUpdate(Strict):
    status: str
    assignee: str = ""
    resolution: str = Field(default="", max_length=4000)
    version: int = Field(ge=0)


class Document(Strict):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=100000)


class Revoke(Strict):
    token: str


class TokenInput(Strict):
    user: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    roles: list[str] = Field(min_length=1, max_length=5)
    ttl: int = Field(default=3600, ge=60, le=86400)


def create_app(settings=None, model=None, variant="multi"):
    settings = settings or Settings.from_env()
    store = Store(settings.db_path)
    model = model or Model(settings)
    kb = Knowledge(store, settings, model)
    service = ChatService(store, settings, model, kb, Tools(store, kb))
    mcp = build_mcp(service)

    @asynccontextmanager
    async def lifespan(app):
        async with mcp.session_manager.run():
            yield
        await service.close()

    app = FastAPI(title="SupportFlow", version="2.0.0", lifespan=lifespan)
    app.state.service = service
    app.state.store = store
    payments = Payments(store, settings)
    reg = CollectorRegistry()
    count = Counter(
        "sf_http_requests", "HTTP requests", ["route", "status"], registry=reg
    )
    latency = Histogram(
        "sf_http_duration_seconds",
        "Actual completed HTTP duration",
        ["route"],
        registry=reg,
        buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 180, 300),
    )
    app.state.registry = reg

    @app.middleware("http")
    async def metrics(request, call_next):
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            route = getattr(request.scope.get("route"), "path", "unmatched")
            count.labels(route, str(status)).inc()
            latency.labels(route).observe(time.perf_counter() - start)

    bearer = HTTPBearer(auto_error=False)

    async def identity(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
        if not credentials:
            raise HTTPException(401, "Bearer token required")
        try:
            return store.authenticate(credentials.credentials)
        except PermissionError:
            raise HTTPException(401, "Invalid or expired token")

    @app.exception_handler(PermissionError)
    async def denied(req, exc):
        return JSONResponse({"detail": str(exc)}, status_code=403)

    @app.exception_handler(ValueError)
    async def conflict(req, exc):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(TimeoutError)
    async def timeout(req, exc):
        return JSONResponse(
            {"detail": "Request deadline exceeded; retry same request_id"},
            status_code=504,
        )

    @app.get("/health")
    async def health():
        return {"status": "alive", "business_mode": settings.business_mode}

    @app.post("/chat")
    async def chat(body: ChatInput, p=Depends(identity)):
        return await service.chat(p, body, variant)

    @app.post("/intents")
    async def intents(body: ChatInput, p=Depends(identity)):
        from dataclasses import asdict

        result = await service.router.recognize_intent(body.message, [])
        return {
            **asdict(result),
            "intent": result.intent.value,
            "urgency": result.urgency.value,
        }

    @app.get("/conversations/{conv_id}")
    async def history(conv_id: str, p=Depends(identity)):
        return {"messages": store.history(p, conv_id)}

    @app.get("/orders/{order_id}")
    async def order(order_id: str, p=Depends(identity)):
        return store.order(p, order_id)

    @app.post("/refunds")
    async def refund(body: RefundInput, p=Depends(identity)):
        return store.refund_request(
            p, body.order_id, body.amount_cents, body.reason, body.idempotency_key
        )

    @app.get("/refunds")
    async def refunds(p=Depends(identity)):
        with store.tx() as c:
            if p.roles.intersection({"finance", "admin"}):
                rows = c.execute("SELECT * FROM refunds WHERE tenant=?", (p.tenant,))
            else:
                rows = c.execute(
                    "SELECT * FROM refunds WHERE tenant=? AND user=?",
                    (p.tenant, p.user),
                )
            return [dict(r) for r in rows]

    @app.post("/refunds/{rid}/approval")
    async def approve(rid: str, body: Approval, p=Depends(identity)):
        return store.approve_refund(p, rid, body.approve)

    @app.post("/refunds/{rid}/settle")
    async def settle(rid: str, p=Depends(identity)):
        return (
            store.settle_refund(p, rid)
            if settings.business_mode == "sandbox"
            else payments.enqueue(p, rid)
        )

    @app.post("/ops/payments/dispatch")
    async def dispatch(p=Depends(identity)):
        return await payments.dispatch(p)

    @app.post("/ops/payments/reconcile")
    async def reconcile(p=Depends(identity)):
        return await payments.reconcile(p)

    @app.post("/payments/events")
    async def payment_event(request: Request):
        raw = await request.body()
        if len(raw) > 16384:
            raise HTTPException(413, "Event too large")
        return payments.event(
            raw,
            request.headers.get("x-timestamp", ""),
            request.headers.get("x-signature", ""),
        )

    @app.post("/tickets")
    async def ticket(body: TicketInput, p=Depends(identity)):
        store.history(p, body.conv_id)
        return store.create_ticket(p, body.conv_id, body.summary, body.idempotency_key)

    @app.get("/tickets")
    async def queue(p=Depends(identity)):
        p.require("staff")
        with store.tx() as c:
            return [
                dict(r)
                for r in c.execute(
                    "SELECT * FROM tickets WHERE tenant=? ORDER BY rowid DESC LIMIT 200",
                    (p.tenant,),
                )
            ]

    @app.get("/tickets/{tid}")
    async def ticket_get(tid: str, p=Depends(identity)):
        return store.ticket(p, tid)

    @app.patch("/tickets/{tid}")
    async def ticket_update(tid: str, body: TicketUpdate, p=Depends(identity)):
        return store.update_ticket(p, tid, **body.model_dump())

    @app.post("/knowledge")
    async def knowledge(body: Document, p=Depends(identity)):
        p.require("admin")
        kb.add(p.tenant, body.id, body.title, body.content)
        return {"version": kb.version(p.tenant)}

    @app.post("/skills/reload")
    async def reload(p=Depends(identity)):
        p.require("admin")
        service.skills.reload()
        return service.skills.summary()

    @app.get("/audit")
    async def audit(p=Depends(identity)):
        return store.audit_log(p)

    @app.post("/auth/revoke")
    async def revoke(body: Revoke, p=Depends(identity)):
        store.revoke(p, body.token)
        return {"revoked": True}

    @app.post("/auth/tokens")
    async def issue(body: TokenInput, p=Depends(identity)):
        p.require("admin")
        if not set(body.roles) <= {"customer", "staff", "finance", "ops", "admin"}:
            raise ValueError("Unknown role")
        target = Principal(p.tenant, body.user, frozenset(body.roles))
        token = store.issue_token(target, body.ttl)
        with store.tx() as c:
            store.audit(
                c, p, "auth.issue", body.user, {"roles": body.roles, "ttl": body.ttl}
            )
        return {"token": token, "expires_in": body.ttl}

    @app.get("/metrics")
    async def metrics_get(p=Depends(identity)):
        p.require("ops")
        return Response(generate_latest(reg), media_type=CONTENT_TYPE_LATEST)

    app.mount("/mcp", mcp.streamable_http_app())
    return app
