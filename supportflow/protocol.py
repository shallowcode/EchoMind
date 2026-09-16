"""Official MCP SDK Streamable HTTP resource server sharing HTTP's identity and tools."""

import time
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.transport_security import TransportSecuritySettings
from urllib.parse import urlsplit


class TokenVerifier:
    def __init__(self, store):
        self.store = store

    async def verify_token(self, token):
        try:
            p = self.store.authenticate(token)
        except PermissionError:
            return None
        return AccessToken(
            token=token,
            client_id=p.user,
            scopes=["supportflow"],
            subject=p.user,
            claims={"tenant": p.tenant},
            expires_at=int(time.time()) + 60,
        )


def build_mcp(service):
    public = service.settings.public_url.rstrip("/")
    host = urlsplit(public).hostname
    if not host:
        raise ValueError("Valid public_url required")
    server = FastMCP(
        "SupportFlow",
        stateless_http=True,
        json_response=True,
        streamable_http_path="/",
        transport_security=TransportSecuritySettings(
            allowed_hosts=[host, host + ":*", "127.0.0.1:*", "localhost:*"],
            allowed_origins=[public, "http://127.0.0.1:*", "http://localhost:*"],
        ),
        token_verifier=TokenVerifier(service.store),
        auth=AuthSettings(
            issuer_url=public,
            resource_server_url=public + "/mcp",
            required_scopes=["supportflow"],
            validate_token_resource=False,
        ),
    )

    def principal():
        token = get_access_token()
        if not token:
            raise PermissionError("Authentication required")
        return service.store.authenticate(token.token)

    @server.tool()
    async def knowledge_search(query: str):
        """Search only the authenticated tenant's policy documents."""
        return await service.tools.call(
            principal(),
            "billing",
            "knowledge_search",
            {"query": query},
            "",
            "mcp-search",
        )

    @server.tool()
    async def order_lookup(order_id: str):
        """Read an order after ownership/role checks."""
        return await service.tools.call(
            principal(),
            "billing",
            "order_lookup",
            {"order_id": order_id},
            "",
            "mcp-order",
        )

    @server.tool()
    async def refund_request(
        order_id: str, amount_cents: int, reason: str, idempotency_key: str
    ):
        """Explicitly request a pending refund. Cannot approve or transfer money."""
        return await service.tools.call(
            principal(),
            "billing",
            "refund_request",
            {"order_id": order_id, "amount_cents": amount_cents, "reason": reason},
            "",
            idempotency_key,
            consent=True,
        )

    @server.tool()
    async def ticket_create(conv_id: str, summary: str, idempotency_key: str):
        """Create a human support ticket linked to an owned conversation."""
        p = principal()
        service.store.history(p, conv_id)
        return await service.tools.call(
            p,
            "billing",
            "ticket_create",
            {"summary": summary},
            conv_id,
            idempotency_key,
        )

    @server.tool()
    async def ticket_status(ticket_id: str):
        """Read an accessible support ticket."""
        return service.store.ticket(principal(), ticket_id)

    return server
