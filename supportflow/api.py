"""Authenticated primary HTTP API; business writes have strict schemas and persistent state."""

from contextlib import asynccontextmanager
from pathlib import Path
import hashlib
import hmac
import time
from fastapi import FastAPI, Depends, Request, HTTPException, Query
from typing import Literal
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
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
from supportflow.merchant import Merchant


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RefundInput(Strict):
    order_id: str = Field(min_length=1, max_length=100)
    amount_cents: int = Field(strict=True, gt=0)
    reason: str = Field(min_length=1, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=100)


class Approval(Strict):
    approve: bool = True


class MerchantOrderInput(Strict):
    order_id: str = Field(pattern=r"^[A-Za-z0-9_-]{4,32}$")
    customer: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    product: str = Field(min_length=1, max_length=120)
    quantity: int = Field(strict=True, ge=1, le=10000)
    total_cents: int = Field(strict=True, ge=1, le=100000000)
    status: Literal["pending_payment", "paid", "shipped", "completed"] = "paid"


class MerchantOrderUpdate(Strict):
    status: Literal["paid", "shipped", "completed", "cancelled"]
    version: int = Field(strict=True, ge=0)


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
    knowledge_store = Store(settings.db_path)
    store = knowledge_store
    if settings.business_url:
        from supportflow.remote_store import RemoteStore
        store = RemoteStore(settings.business_url, settings.service_key)
    merchant = Merchant(store)
    model = model or Model(settings)
    kb = Knowledge(knowledge_store, settings, model)
    service = ChatService(store, settings, model, kb, Tools(store, kb))
    mcp = build_mcp(service)

    @asynccontextmanager
    async def lifespan(app):
        try:
            if settings.require_memory_services and not (await service.memory_status())["ready"]:
                raise RuntimeError("Resume profile requires reachable ChromaDB and Redis services")
            async with mcp.session_manager.run():
                yield
        finally:
            await service.close()
            if settings.business_url:
                store.close()

    app = FastAPI(title="SupportFlow", version="3.0.0" if settings.business_url else "2.0.0", lifespan=lifespan)
    source_root = Path(__file__).resolve().parents[1]
    build_files = sorted((source_root / "supportflow").glob("*.py")) + sorted((source_root / "frontend").glob("*"))
    runtime_info = {
        "application": app.title, "version": app.version,
        "model": settings.model_name, "thinking": settings.model_thinking,
        "orchestration": variant,
        "storage": settings.storage,
        "chroma_mode": settings.chroma_mode if settings.storage == "chroma" else None,
        "working_memory": "redis" if settings.redis_url else "sql",
        "build": hashlib.sha256(b"".join(p.read_bytes() for p in build_files if p.is_file())).hexdigest()[:12],
    }
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
        if settings.business_url and request.url.path != '/health':
            if not hmac.compare_digest(request.headers.get('X-SupportFlow-Service-Key', ''), settings.service_key):
                return JSONResponse({'detail': 'Internal service only'}, status_code=403)
            path = request.url.path
            if not (path in {'/chat', '/intents', '/knowledge', '/skills/reload'}
                    or path.startswith('/lab/') or path.startswith('/mcp/')):
                return JSONResponse({'detail': 'Business API is served by Go'}, status_code=404)
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
            principal = store.authenticate(credentials.credentials)
            if principal.demo_customer and (not settings.local_demo_access or settings.business_mode != "sandbox"):
                raise PermissionError("Demo mode disabled")
            return principal
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
        return {"status": "alive", "business_mode": settings.business_mode, "runtime": runtime_info}

    @app.get("/ready")
    async def ready():
        memory = await service.memory_status()
        return JSONResponse({"status": "ready" if memory["ready"] else "unavailable",
                             "memory": memory, "runtime": runtime_info},
                            status_code=200 if memory["ready"] else 503)

    @app.get("/auth/me")
    async def me(p=Depends(identity)):
        return {"user": p.user, "tenant": p.tenant, "roles": sorted(p.roles)}

    def require_local_demo(request: Request, audience: str):
        # Opt-in localhost sandbox only. No CORS: the custom header prevents
        # another website from silently obtaining this local demo identity.
        local_hosts = {"127.0.0.1", "::1", "localhost"}
        if not settings.local_demo_access or settings.business_mode != "sandbox":
            raise HTTPException(404, "Not found")
        if settings.business_url:
            # The authenticated Go gateway already checked the original socket,
            # Host and Origin before forwarding this local-only route.
            if request.headers.get('X-SupportFlow-Demo') != audience:
                raise HTTPException(403, 'Local sandbox only')
            return
        if (not request.client or request.client.host not in local_hosts
                or request.url.hostname not in local_hosts
                or request.headers.get("X-SupportFlow-Demo") != audience
                or request.headers.get("Sec-Fetch-Site") == "cross-site"
                or (request.headers.get("Origin") and request.headers["Origin"] != str(request.base_url).rstrip("/"))):
            raise HTTPException(403, "Local sandbox only")

    @app.post("/auth/demo-customer")
    async def demo_customer(request: Request):
        require_local_demo(request, "customer")
        token = store.issue_token(Principal("demo", "alice", frozenset({"customer", "demo_customer"})), settings.token_ttl)
        return JSONResponse({"token": token}, headers={"Cache-Control": "no-store"})

    from supportflow.showcase import install_showcase
    install_showcase(app, service, identity, require_local_demo, source_root)

    @app.post("/auth/demo-merchant")
    async def demo_merchant(request: Request):
        require_local_demo(request, "merchant")
        token = store.issue_token(Principal("demo", "merchant", frozenset({"staff", "finance"})), settings.token_ttl)
        return JSONResponse({"token": token}, headers={"Cache-Control": "no-store"})

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

    @app.get("/orders")
    async def orders(p=Depends(identity)):
        return store.order_list(p)

    @app.get("/merchant/overview")
    async def merchant_overview(p=Depends(identity)):
        return merchant.overview(p)

    @app.get("/merchant/orders")
    async def merchant_orders(search: str = Query(default="", max_length=100), status: str = "", offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), p=Depends(identity)):
        return merchant.orders(p, search, status, offset, limit)

    @app.post("/merchant/orders", status_code=201)
    async def merchant_create(body: MerchantOrderInput, p=Depends(identity)):
        if settings.business_mode != "sandbox":
            raise HTTPException(403, "模拟订单仅在沙箱模式下开放")
        if not body.product.strip():
            raise HTTPException(422, "请输入商品名称")
        data = body.model_dump()
        if settings.local_demo_access:
            data["customer"] = "alice"
        return merchant.create_order(p, **data)

    @app.delete("/merchant/orders/{order_id}")
    async def merchant_delete(order_id: str, version: int = Query(ge=0), p=Depends(identity)):
        if settings.business_mode != "sandbox":
            raise HTTPException(403, "模拟订单仅在沙箱模式下开放")
        return merchant.delete_order(p, order_id, version)

    @app.post("/merchant/orders/{order_id}/restore")
    async def merchant_restore(order_id: str, p=Depends(identity)):
        if settings.business_mode != "sandbox":
            raise HTTPException(403, "模拟订单仅在沙箱模式下开放")
        return merchant.restore_order(p, order_id)

    @app.patch("/merchant/orders/{order_id}")
    async def merchant_update(order_id: str, body: MerchantOrderUpdate, p=Depends(identity)):
        if settings.business_mode != "sandbox":
            raise HTTPException(403, "模拟订单仅在沙箱模式下开放")
        return merchant.update_order(p, order_id, **body.model_dump())

    @app.get("/merchant/refunds")
    async def merchant_refunds(status: str = "", search: str = Query(default="", max_length=100), offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), p=Depends(identity)):
        return merchant.refunds(p, status, search, offset, limit)

    @app.post("/refunds")
    async def refund(body: RefundInput, p=Depends(identity)):
        return store.refund_request(
            p, body.order_id, body.amount_cents, body.reason, body.idempotency_key
        )

    @app.get("/refunds")
    async def refunds(p=Depends(identity)):
        with store.tx() as c:
            if p.demo_customer or p.roles.intersection({"finance", "admin"}):
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
    frontend = Path(__file__).resolve().parents[1] / "frontend"
    app.mount("/assets", StaticFiles(directory=frontend), name="frontend")

    @app.get("/", include_in_schema=False)
    async def home():
        return FileResponse(frontend / "index.html", headers={"Cache-Control": "no-cache"})

    @app.get("/admin", include_in_schema=False)
    async def merchant_home():
        return FileResponse(frontend / "admin.html", headers={"Cache-Control": "no-cache"})

    return app
