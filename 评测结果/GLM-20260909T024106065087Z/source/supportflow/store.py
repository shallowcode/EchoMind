"""Transactional business source of truth. No credentials or money leave this sandbox ledger.

SQLite WAL transactions reserve pending refunds, enforce ownership and persist idempotency,
conversation state and audit events. Redis/Chroma are optional projections, never the authority.
"""

import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager
from supportflow.contracts import Principal, BusinessRejection


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.tx() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS tokens (hash TEXT PRIMARY KEY, tenant TEXT, user TEXT, roles TEXT, expires REAL, revoked INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS orders (tenant TEXT, id TEXT, user TEXT, total INTEGER, refunded INTEGER DEFAULT 0, status TEXT, PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS refunds (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, order_id TEXT, amount INTEGER, status TEXT, idem TEXT, reason TEXT, payment_ref TEXT, UNIQUE(tenant,user,idem));
            CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, conv TEXT, summary TEXT, status TEXT, assignee TEXT, resolution TEXT, idem TEXT, version INTEGER DEFAULT 0, UNIQUE(tenant,user,idem));
            CREATE TABLE IF NOT EXISTS conversations (tenant TEXT, id TEXT, user TEXT, state TEXT, version INTEGER DEFAULT 0, lease_owner TEXT, lease_until REAL DEFAULT 0, PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS messages (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, conv TEXT, role TEXT, content TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS requests (tenant TEXT, user TEXT, id TEXT, fingerprint TEXT, response TEXT, PRIMARY KEY(tenant,user,id));
            CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, actor TEXT, action TEXT, target TEXT, detail TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS knowledge (tenant TEXT, id TEXT, title TEXT, content TEXT, version TEXT, PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS traces (tenant TEXT, user TEXT, id TEXT PRIMARY KEY, payload TEXT);
            CREATE TABLE IF NOT EXISTS payment_outbox (refund_id TEXT PRIMARY KEY, tenant TEXT, payload TEXT, status TEXT, attempts INTEGER DEFAULT 0, lease_until REAL DEFAULT 0, last_error TEXT);
            CREATE TABLE IF NOT EXISTS payment_events (id TEXT PRIMARY KEY, refund_id TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS profiles (tenant TEXT, user TEXT, payload TEXT, PRIMARY KEY(tenant,user));
            """)

    @contextmanager
    def tx(self):
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA foreign_keys=ON")
        try:
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.commit()
        except BaseException:
            c.rollback()
            raise
        finally:
            c.close()

    def audit(self, c, p, action, target, detail):
        c.execute(
            "INSERT INTO audit(tenant,actor,action,target,detail,created) VALUES(?,?,?,?,?,?)",
            (
                p.tenant,
                p.user,
                action,
                target,
                json.dumps(detail, ensure_ascii=False),
                time.time(),
            ),
        )

    def issue_token(self, p, ttl=3600):
        token = secrets.token_urlsafe(32)
        with self.tx() as c:
            c.execute(
                "INSERT INTO tokens(hash,tenant,user,roles,expires) VALUES(?,?,?,?,?)",
                (
                    hashlib.sha256(token.encode()).hexdigest(),
                    p.tenant,
                    p.user,
                    json.dumps(sorted(p.roles)),
                    time.time() + ttl,
                ),
            )
        return token

    def authenticate(self, token):
        with self.tx() as c:
            r = c.execute(
                "SELECT * FROM tokens WHERE hash=?",
                (hashlib.sha256(token.encode()).hexdigest(),),
            ).fetchone()
        if not r or r["revoked"] or r["expires"] <= time.time():
            raise PermissionError("Invalid or expired token")
        return Principal(r["tenant"], r["user"], frozenset(json.loads(r["roles"])))

    def revoke(self, p, token):
        p.require("admin")
        with self.tx() as c:
            c.execute(
                "UPDATE tokens SET revoked=1 WHERE tenant=? AND hash=?",
                (p.tenant, hashlib.sha256(token.encode()).hexdigest()),
            )

    def seed_order(self, p, order_id, total=5000, user=None):
        p.require("admin")
        with self.tx() as c:
            c.execute(
                "INSERT INTO orders(tenant,id,user,total,status) VALUES(?,?,?,?,?)",
                (p.tenant, order_id, user or p.user, total, "paid"),
            )

    def order(self, p, order_id):
        with self.tx() as c:
            r = c.execute(
                "SELECT * FROM orders WHERE tenant=? AND id=?", (p.tenant, order_id)
            ).fetchone()
        if not r or (
            r["user"] != p.user
            and not p.roles.intersection({"staff", "finance", "admin"})
        ):
            raise PermissionError("Order not accessible")
        return dict(r)

    def refund_request(self, p, order_id, amount, reason, idem):
        if type(amount) is not int or amount <= 0:
            raise ValueError("amount_cents must be positive integer")
        with self.tx() as c:
            old = c.execute(
                "SELECT * FROM refunds WHERE tenant=? AND user=? AND idem=?",
                (p.tenant, p.user, idem),
            ).fetchone()
            if old:
                if (
                    old["order_id"] != order_id
                    or old["amount"] != amount
                    or old["reason"] != reason
                ):
                    raise ValueError("Idempotency key payload mismatch")
                return dict(old)
            order = c.execute(
                "SELECT * FROM orders WHERE tenant=? AND id=? AND user=?",
                (p.tenant, order_id, p.user),
            ).fetchone()
            if not order:
                raise PermissionError("Order not accessible")
            reserved = c.execute(
                "SELECT COALESCE(SUM(amount),0) FROM refunds WHERE tenant=? AND order_id=? AND status IN ('pending','approved','processing')",
                (p.tenant, order_id),
            ).fetchone()[0]
            if order["refunded"] + reserved + amount > order["total"]:
                raise BusinessRejection(
                    "insufficient_refundable_balance",
                    "Refund exceeds unreserved balance",
                )
            rid = "rf_" + uuid.uuid4().hex
            c.execute(
                "INSERT INTO refunds VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    rid,
                    p.tenant,
                    p.user,
                    order_id,
                    amount,
                    "pending",
                    idem,
                    reason,
                    None,
                ),
            )
            self.audit(
                c, p, "refund.request", rid, {"amount_cents": amount, "mode": "sandbox"}
            )
            return dict(
                c.execute("SELECT * FROM refunds WHERE id=?", (rid,)).fetchone()
            )

    def approve_refund(self, p, rid, approve=True):
        p.require("finance")
        with self.tx() as c:
            r = c.execute(
                "SELECT * FROM refunds WHERE tenant=? AND id=?", (p.tenant, rid)
            ).fetchone()
            if not r:
                raise PermissionError("Refund not accessible")
            if r["status"] != "pending":
                raise ValueError("Refund must be pending")
            if r["user"] == p.user:
                raise PermissionError("Requester cannot approve own refund")
            status = "approved" if approve else "rejected"
            c.execute("UPDATE refunds SET status=? WHERE id=?", (status, rid))
            self.audit(c, p, "refund." + status, rid, {})
        return {"id": rid, "status": status}

    def settle_refund(self, p, rid):
        p.require("finance")
        with self.tx() as c:
            r = c.execute(
                "SELECT * FROM refunds WHERE tenant=? AND id=?", (p.tenant, rid)
            ).fetchone()
            if not r:
                raise PermissionError("Refund not accessible")
            if r["status"] == "settled":
                return dict(r)
            if r["status"] != "approved":
                raise ValueError("Approval required")
            if r["user"] == p.user:
                raise PermissionError("Requester cannot settle own refund")
            c.execute(
                "UPDATE orders SET refunded=refunded+? WHERE tenant=? AND id=?",
                (r["amount"], p.tenant, r["order_id"]),
            )
            ref = "sandbox_" + rid
            c.execute(
                "UPDATE refunds SET status='settled',payment_ref=? WHERE id=?",
                (ref, rid),
            )
            self.audit(
                c, p, "refund.settle", rid, {"mode": "sandbox", "payment_ref": ref}
            )
            return dict(
                c.execute("SELECT * FROM refunds WHERE id=?", (rid,)).fetchone()
            )

    def create_ticket(self, p, conv, summary, idem):
        with self.tx() as c:
            conversation = c.execute(
                "SELECT user FROM conversations WHERE tenant=? AND id=?",
                (p.tenant, conv),
            ).fetchone()
            if not conversation or conversation["user"] != p.user:
                raise PermissionError("Owned conversation required")
            old = c.execute(
                "SELECT * FROM tickets WHERE tenant=? AND user=? AND idem=?",
                (p.tenant, p.user, idem),
            ).fetchone()
            if old:
                if old["conv"] != conv or old["summary"] != summary:
                    raise ValueError("Ticket idempotency payload mismatch")
                return dict(old)
            tid = "tk_" + uuid.uuid4().hex
            c.execute(
                "INSERT INTO tickets(id,tenant,user,conv,summary,status,idem) VALUES(?,?,?,?,?,?,?)",
                (tid, p.tenant, p.user, conv, summary, "open", idem),
            )
            self.audit(c, p, "ticket.create", tid, {"conv": conv})
            return dict(
                c.execute("SELECT * FROM tickets WHERE id=?", (tid,)).fetchone()
            )

    def ticket(self, p, tid):
        with self.tx() as c:
            r = c.execute(
                "SELECT * FROM tickets WHERE tenant=? AND id=?", (p.tenant, tid)
            ).fetchone()
        if not r or (
            r["user"] != p.user and not p.roles.intersection({"staff", "admin"})
        ):
            raise PermissionError("Ticket not accessible")
        return dict(r)

    def update_ticket(self, p, tid, status, assignee="", resolution="", version=0):
        p.require("staff")
        with self.tx() as c:
            r = c.execute(
                "SELECT * FROM tickets WHERE tenant=? AND id=?", (p.tenant, tid)
            ).fetchone()
            if not r:
                raise PermissionError("Ticket not accessible")
            transitions = {
                "open": {"assigned"},
                "assigned": {"resolved"},
                "resolved": {"closed"},
                "closed": set(),
            }
            if status not in transitions[r["status"]]:
                raise ValueError("Invalid ticket transition")
            if status == "assigned" and not assignee:
                raise ValueError("Assignee required")
            if status == "resolved" and (
                not resolution or (r["assignee"] != p.user and "admin" not in p.roles)
            ):
                raise PermissionError("Assigned staff and resolution required")
            cur = c.execute(
                "UPDATE tickets SET status=?,assignee=?,resolution=?,version=version+1 WHERE id=? AND version=?",
                (
                    status,
                    assignee or r["assignee"],
                    resolution or r["resolution"],
                    tid,
                    version,
                ),
            )
            if cur.rowcount != 1:
                raise ValueError("Ticket version conflict")
            if status == "resolved":
                c.execute(
                    "INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)",
                    (
                        p.tenant,
                        r["conv"],
                        "system",
                        f"工单 {tid} 已解决：{resolution}",
                        time.time(),
                    ),
                )
            self.audit(c, p, "ticket." + status, tid, {"resolution": resolution})
        return self.ticket(p, tid)

    def acquire_conversation(self, p, conv, owner, ttl):
        with self.tx() as c:
            c.execute(
                "INSERT OR IGNORE INTO conversations(tenant,id,user,state) VALUES(?,?,?,?)",
                (p.tenant, conv, p.user, "{}"),
            )
            row = c.execute(
                "SELECT * FROM conversations WHERE tenant=? AND id=?", (p.tenant, conv)
            ).fetchone()
            if row["user"] != p.user:
                raise PermissionError("Conversation belongs to another user")
            if row["lease_until"] > time.time():
                raise ValueError("Conversation busy; retry with same request_id")
            c.execute(
                "UPDATE conversations SET lease_owner=?,lease_until=? WHERE tenant=? AND id=?",
                (owner, time.time() + ttl, p.tenant, conv),
            )
            return json.loads(row["state"])

    def release(self, p, conv, owner):
        with self.tx() as c:
            c.execute(
                "UPDATE conversations SET lease_until=0 WHERE tenant=? AND id=? AND lease_owner=?",
                (p.tenant, conv, owner),
            )

    def history(self, p, conv, limit=20):
        with self.tx() as c:
            row = c.execute(
                "SELECT user FROM conversations WHERE tenant=? AND id=?",
                (p.tenant, conv),
            ).fetchone()
            if row and row["user"] != p.user:
                raise PermissionError("Conversation not accessible")
            rows = c.execute(
                "SELECT role,content FROM messages WHERE tenant=? AND conv=? ORDER BY seq DESC LIMIT ?",
                (p.tenant, conv, limit),
            ).fetchall()
        return [dict(x) for x in reversed(rows)]

    def cached_request(self, p, rid, fingerprint):
        with self.tx() as c:
            r = c.execute(
                "SELECT * FROM requests WHERE tenant=? AND user=? AND id=?",
                (p.tenant, p.user, rid),
            ).fetchone()
        if r and r["fingerprint"] != fingerprint:
            raise ValueError("request_id reused with different payload")
        return json.loads(r["response"]) if r else None

    def commit_turn(self, p, conv, owner, rid, fingerprint, message, response, state):
        with self.tx() as c:
            row = c.execute(
                "SELECT lease_owner FROM conversations WHERE tenant=? AND id=?",
                (p.tenant, conv),
            ).fetchone()
            if not row or row["lease_owner"] != owner:
                raise ValueError("Conversation lease lost")
            for role, content in [
                ("user", message),
                ("assistant", response["response"]),
            ]:
                c.execute(
                    "INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)",
                    (p.tenant, conv, role, content, time.time()),
                )
            c.execute(
                "UPDATE conversations SET state=?,version=version+1 WHERE tenant=? AND id=?",
                (json.dumps(state, ensure_ascii=False), p.tenant, conv),
            )
            c.execute(
                "INSERT INTO profiles VALUES(?,?,?) ON CONFLICT(tenant,user) DO UPDATE SET payload=excluded.payload",
                (p.tenant, p.user, json.dumps(state.get("profile", {}))),
            )
            c.execute(
                "INSERT INTO requests VALUES(?,?,?,?,?)",
                (
                    p.tenant,
                    p.user,
                    rid,
                    fingerprint,
                    json.dumps(response, ensure_ascii=False),
                ),
            )
            c.execute(
                "INSERT INTO traces VALUES(?,?,?,?)",
                (
                    p.tenant,
                    p.user,
                    p.tenant + ":" + p.user + ":" + rid,
                    json.dumps(response["trace"], ensure_ascii=False),
                ),
            )

    def audit_log(self, p):
        p.require("admin")
        with self.tx() as c:
            return [
                dict(x)
                for x in c.execute(
                    "SELECT * FROM audit WHERE tenant=? ORDER BY seq DESC LIMIT 200",
                    (p.tenant,),
                )
            ]

    def profile(self, p):
        with self.tx() as c:
            r = c.execute(
                "SELECT payload FROM profiles WHERE tenant=? AND user=?",
                (p.tenant, p.user),
            ).fetchone()
        return json.loads(r["payload"]) if r else {}
