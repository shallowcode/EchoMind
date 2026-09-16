import hashlib
import hmac
import json
import time
import httpx
import pytest
from supportflow.contracts import Principal, Settings
from supportflow.store import Store
from supportflow.payments import Payments


@pytest.mark.asyncio
async def test_outbox_signed_settlement_and_replay(tmp_path):
    s = Store(tmp_path / "payments.sqlite")
    a = Principal("t", "admin", frozenset({"admin"}))
    p = Principal("t", "alice")
    s.seed_order(a, "ORD1", 1000, "alice")
    r = s.refund_request(p, "ORD1", 500, "test", "key")
    s.approve_refund(a, r["id"])
    cfg = Settings(
        business_mode="external",
        payment_url="https://provider.test",
        payment_key="test",
        payment_webhook_secret="test-secret",
    )
    pay = Payments(s, cfg)
    pay.enqueue(a, r["id"])
    with pytest.raises(ValueError):
        s.refund_request(p, "ORD1", 600, "test", "other")

    def respond(req):
        assert req.headers["Idempotency-Key"] == r["id"]
        return httpx.Response(202, json={"accepted": True})

    assert (await pay.dispatch(a, httpx.MockTransport(respond)))[0]["sent"]
    assert s.order(p, "ORD1")["refunded"] == 0
    event = {
        "event_id": "evt1",
        "refund_id": r["id"],
        "tenant": "t",
        "order_id": "ORD1",
        "amount_cents": 500,
        "currency": "CNY",
        "status": "settled",
        "payment_ref": "test-ref",
    }
    raw = json.dumps(event).encode()
    ts = str(int(time.time()))
    sig = hmac.new(b"test-secret", ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
    with pytest.raises(PermissionError):
        pay.event(raw, ts, "bad")
    assert pay.event(raw, ts, sig)["status"] == "settled"
    assert pay.event(raw, ts, sig)["duplicate"]
    assert s.order(p, "ORD1")["refunded"] == 500
    bad = json.dumps({**event, "event_id": "evt2", "amount_cents": 400}).encode()
    sign = hmac.new(
        b"test-secret", ts.encode() + b"." + bad, hashlib.sha256
    ).hexdigest()
    with pytest.raises(ValueError):
        pay.event(bad, ts, sign)


@pytest.mark.asyncio
async def test_lost_callback_reconciliation(tmp_path):
    s = Store(tmp_path / "reconcile.sqlite")
    a = Principal("t", "admin", frozenset({"admin"}))
    p = Principal("t", "alice")
    s.seed_order(a, "ORD1", 1000, "alice")
    r = s.refund_request(p, "ORD1", 100, "test", "key")
    s.approve_refund(a, r["id"])
    pay = Payments(
        s,
        Settings(
            business_mode="external",
            payment_url="https://provider.test",
            payment_key="test",
            payment_webhook_secret="secret",
        ),
    )
    pay.enqueue(a, r["id"])
    await pay.dispatch(a, httpx.MockTransport(lambda req: httpx.Response(202)))
    event = {
        "event_id": "lost-event",
        "refund_id": r["id"],
        "tenant": "t",
        "order_id": "ORD1",
        "amount_cents": 100,
        "currency": "CNY",
        "status": "settled",
        "payment_ref": "provider-ref",
    }
    raw = json.dumps(event).encode()
    ts = str(int(time.time()))
    sig = hmac.new(b"secret", ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
    result = await pay.reconcile(
        a,
        httpx.MockTransport(
            lambda req: httpx.Response(
                200, content=raw, headers={"x-timestamp": ts, "x-signature": sig}
            )
        ),
    )
    assert result[0]["status"] == "settled" and s.order(p, "ORD1")["refunded"] == 100
