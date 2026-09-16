"""Provider-neutral outbox contract; activation requires explicit external configuration.

POST /refunds must honor Idempotency-Key and return no assumption of settlement.
Only a signed terminal event matching tenant/order/amount can book settled funds.
Network ambiguity retains the reservation. Never retry with a new business key.
"""

import hashlib
import hmac
import json
import time
import httpx
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class PaymentEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(min_length=1, max_length=200)
    refund_id: str = Field(min_length=1, max_length=100)
    tenant: str = Field(min_length=1, max_length=100)
    order_id: str = Field(min_length=1, max_length=100)
    amount_cents: int = Field(strict=True, gt=0)
    currency: Literal["CNY"]
    status: Literal["settled", "rejected"]
    payment_ref: str = Field(min_length=1, max_length=200)


class Payments:
    def __init__(self, store, settings):
        self.store = store
        self.settings = settings

    def enqueue(self, p, rid):
        p.require("finance")
        if (
            not self.settings.payment_url.startswith("https://")
            or not self.settings.payment_key
            or not self.settings.payment_webhook_secret
        ):
            raise ValueError(
                "External payment provider must be configured before execution"
            )
        with self.store.tx() as c:
            row = c.execute(
                "SELECT * FROM refunds WHERE tenant=? AND id=?", (p.tenant, rid)
            ).fetchone()
            if not row:
                raise PermissionError("Refund not accessible")
            if row["user"] == p.user:
                raise PermissionError("Requester cannot execute own refund")
            if row["status"] in {"processing", "settled"}:
                return dict(row)
            if row["status"] != "approved":
                raise ValueError("Approval required")
            payload = {
                "refund_id": rid,
                "tenant": p.tenant,
                "order_id": row["order_id"],
                "amount_cents": row["amount"],
                "currency": self.settings.business_currency,
            }
            c.execute(
                "INSERT INTO payment_outbox(refund_id,tenant,payload,status) VALUES(?,?,?,?)",
                (rid, p.tenant, json.dumps(payload), "pending"),
            )
            c.execute("UPDATE refunds SET status='processing' WHERE id=?", (rid,))
            self.store.audit(c, p, "payment.enqueue", rid, payload)
            return {"id": rid, "status": "processing"}

    async def dispatch(self, p, transport=None):
        p.require("ops")
        now = time.time()
        with self.store.tx() as c:
            rows = [
                dict(r)
                for r in c.execute(
                    "SELECT * FROM payment_outbox WHERE tenant=? AND status='pending' AND lease_until<? LIMIT 20",
                    (p.tenant, now),
                )
            ]
            for r in rows:
                c.execute(
                    "UPDATE payment_outbox SET lease_until=?,attempts=attempts+1 WHERE refund_id=?",
                    (now + 15 * len(rows) + 30, r["refund_id"]),
                )
        results = []
        async with httpx.AsyncClient(
            timeout=15, transport=transport, follow_redirects=False
        ) as client:
            for row in rows:
                try:
                    response = await client.post(
                        self.settings.payment_url.rstrip("/") + "/refunds",
                        json=json.loads(row["payload"]),
                        headers={
                            "Authorization": "Bearer " + self.settings.payment_key,
                            "Idempotency-Key": row["refund_id"],
                        },
                    )
                    response.raise_for_status()
                    # Accepted is deliberately not settled. Query/callback reconciles eventual result.
                    results.append({"id": row["refund_id"], "sent": True})
                    with self.store.tx() as c:
                        c.execute(
                            "UPDATE payment_outbox SET status='accepted',last_error=NULL WHERE refund_id=? AND status='pending'",
                            (row["refund_id"],),
                        )
                except Exception as e:
                    results.append(
                        {
                            "id": row["refund_id"],
                            "sent": False,
                            "error": type(e).__name__,
                        }
                    )
                    with self.store.tx() as c:
                        c.execute(
                            "UPDATE payment_outbox SET last_error=? WHERE refund_id=?",
                            (type(e).__name__, row["refund_id"]),
                        )
        return results

    async def reconcile(self, p, transport=None):
        """Query accepted operations whose final callback may have been lost.

        Provider GET /refunds/{id} returns the same signed event contract as webhooks.
        Pending (202) is not treated as failure or success. Authentication/signature and
        exact amount/order checks are identical to the push callback path.
        """
        p.require("ops")
        with self.store.tx() as c:
            rows = [
                dict(r)
                for r in c.execute(
                    "SELECT * FROM payment_outbox WHERE tenant=? AND status='accepted' LIMIT 20",
                    (p.tenant,),
                )
            ]
        results = []
        async with httpx.AsyncClient(
            timeout=15, transport=transport, follow_redirects=False
        ) as client:
            for row in rows:
                try:
                    response = await client.get(
                        self.settings.payment_url.rstrip("/")
                        + "/refunds/"
                        + row["refund_id"],
                        headers={
                            "Authorization": "Bearer " + self.settings.payment_key
                        },
                    )
                    if response.status_code == 202:
                        results.append({"id": row["refund_id"], "status": "pending"})
                        continue
                    response.raise_for_status()
                    event = json.loads(response.content)
                    if (
                        event.get("refund_id") != row["refund_id"]
                        or event.get("tenant") != p.tenant
                    ):
                        raise ValueError("Reconciliation identity mismatch")
                    result = self.event(
                        response.content,
                        response.headers.get("x-timestamp", ""),
                        response.headers.get("x-signature", ""),
                    )
                    results.append({"id": row["refund_id"], **result})
                except Exception as e:
                    results.append({"id": row["refund_id"], "error": type(e).__name__})
        return results

    def event(self, raw, timestamp, signature):
        if not self.settings.payment_webhook_secret:
            raise PermissionError("Webhook not configured")
        try:
            if abs(time.time() - int(timestamp)) > 300:
                raise PermissionError("Webhook expired")
        except (ValueError, TypeError):
            raise PermissionError("Invalid timestamp")
        expected = hmac.new(
            self.settings.payment_webhook_secret.encode(),
            timestamp.encode() + b"." + raw,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise PermissionError("Invalid webhook signature")
        event = PaymentEvent.model_validate_json(raw).model_dump()
        with self.store.tx() as c:
            prior = c.execute(
                "SELECT refund_id FROM payment_events WHERE id=?", (event["event_id"],)
            ).fetchone()
            if prior:
                if prior["refund_id"] != event["refund_id"]:
                    raise ValueError("Event id conflict")
                return {"duplicate": True}
            r = c.execute(
                "SELECT * FROM refunds WHERE id=? AND tenant=?",
                (event["refund_id"], event["tenant"]),
            ).fetchone()
            if not r:
                raise PermissionError("Refund not accessible")
            if (
                r["order_id"] != event["order_id"]
                or type(event["amount_cents"]) is not int
                or r["amount"] != event["amount_cents"]
            ):
                raise ValueError("Payment event amount/order mismatch")
            if r["status"] not in {"processing", event["status"]}:
                raise ValueError("Unexpected refund state")
            if event["status"] == "settled" and r["status"] != "settled":
                c.execute(
                    "UPDATE orders SET refunded=refunded+? WHERE tenant=? AND id=?",
                    (r["amount"], r["tenant"], r["order_id"]),
                )
            c.execute(
                "UPDATE refunds SET status=?,payment_ref=? WHERE id=?",
                (event["status"], event["payment_ref"], r["id"]),
            )
            c.execute(
                "UPDATE payment_outbox SET status='completed' WHERE refund_id=?",
                (r["id"],),
            )
            c.execute(
                "INSERT INTO payment_events VALUES(?,?,?)",
                (event["event_id"], r["id"], time.time()),
            )
            from supportflow.contracts import Principal

            self.store.audit(
                c,
                Principal(r["tenant"], "payment-provider"),
                "payment." + event["status"],
                r["id"],
                event,
            )
        return {"status": event["status"]}
