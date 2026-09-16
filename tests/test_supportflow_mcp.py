import asyncio
import socket
import httpx
import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from supportflow.api import create_app
from supportflow.contracts import Principal, Settings


@pytest.mark.asyncio
async def test_real_mcp_http_handshake_tools_and_auth(tmp_path):
    app = create_app(
        Settings(db_path=str(tmp_path / "mcp.sqlite"), model_backend="fixture")
    )
    store = app.state.store
    p = Principal("t", "alice")
    admin = Principal("t", "admin", frozenset({"admin"}))
    store.seed_order(admin, "ORD1001", 5000, "alice")
    token = store.issue_token(p)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    )
    task = asyncio.create_task(server.serve(sockets=[sock]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                await asyncio.sleep(0.02)
        url = f"http://127.0.0.1:{port}/mcp/"
        async with httpx.AsyncClient() as unauth:
            r = await unauth.post(
                url, json={"jsonrpc": "2.0", "id": 1, "method": "initialize"}
            )
            assert r.status_code == 401
        async with httpx.AsyncClient(
            headers={"Authorization": "Bearer " + token}
        ) as client:
            async with streamable_http_client(url, http_client=client) as (
                read,
                write,
                _,
            ):
                async with ClientSession(read, write) as session:
                    info = await session.initialize()
                    assert info.serverInfo.name == "SupportFlow"
                    listing = await session.list_tools()
                    assert {"order_lookup", "refund_request", "ticket_create"} <= {
                        t.name for t in listing.tools
                    }
                    result = await session.call_tool(
                        "order_lookup", {"order_id": "ORD1001"}
                    )
                    assert not result.isError and "paid" in str(result)
                    rejected = await session.call_tool(
                        "order_lookup", {"order_id": "OTHER"}
                    )
                    assert rejected.isError
    finally:
        server.should_exit = True
        await task
        sock.close()
