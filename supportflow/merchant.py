"""Tenant-scoped merchant operations over the same transactional order ledger."""

import sqlite3
import time


ORDER_STATES = {"pending_payment", "paid", "shipped", "completed", "cancelled"}
TRANSITIONS = {"pending_payment": {"paid", "cancelled"}, "paid": {"shipped"}, "shipped": {"completed"}}


class Merchant:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def reader(p):
        if not p.roles.intersection({"admin", "staff", "finance"}):
            raise PermissionError("需要商户权限")

    def overview(self, p):
        self.reader(p)
        with self.store.tx() as db:
            orders = db.execute("SELECT COUNT(*),COALESCE(SUM(CASE WHEN status NOT IN ('pending_payment','cancelled') THEN total-refunded ELSE 0 END),0) FROM orders o WHERE tenant=? AND NOT EXISTS (SELECT 1 FROM deleted_orders x WHERE x.tenant=o.tenant AND x.order_id=o.id)", (p.tenant,)).fetchone()
            refunds = db.execute("SELECT COALESCE(SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END),0),COALESCE(SUM(CASE WHEN status='settled' THEN amount ELSE 0 END),0) FROM refunds WHERE tenant=?", (p.tenant,)).fetchone()
        return {"orders": orders[0], "net_cents": orders[1], "pending_refunds": refunds[0], "refunded_cents": refunds[1]}

    def orders(self, p, search="", status="", offset=0, limit=20):
        self.reader(p)
        where, args = "o.tenant=?", [p.tenant]
        deleted = status == "deleted"
        where += " AND " + ("" if deleted else "NOT ") + "EXISTS (SELECT 1 FROM deleted_orders x WHERE x.tenant=o.tenant AND x.order_id=o.id)"
        if search:
            where += " AND (o.id LIKE ? OR o.user LIKE ? OR d.product LIKE ?)"
            args += ["%" + search + "%"] * 3
        if status and not deleted:
            where += " AND o.status=?"
            args.append(status)
        join = " FROM orders o LEFT JOIN order_details d ON d.tenant=o.tenant AND d.order_id=o.id "
        with self.store.tx() as db:
            total = db.execute("SELECT COUNT(*)" + join + "WHERE " + where, args).fetchone()[0]
            rows = db.execute("""SELECT o.*, COALESCE(d.product,'演示订单') product,COALESCE(d.quantity,1) quantity,
                d.created,COALESCE(d.version,0) version,
                (SELECT COALESCE(SUM(r.amount),0) FROM refunds r WHERE r.tenant=o.tenant AND r.order_id=o.id AND r.status IN ('pending','approved','processing')) reserved,
                (SELECT r.status FROM refunds r WHERE r.tenant=o.tenant AND r.order_id=o.id AND r.status IN ('pending','approved','processing') ORDER BY CASE r.status WHEN 'pending' THEN 0 WHEN 'processing' THEN 1 ELSE 2 END LIMIT 1) refund_stage
                """ + join + "WHERE " + where + " ORDER BY COALESCE(d.created,0) DESC,o.id DESC LIMIT ? OFFSET ?", [*args, limit, offset]).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["deleted"] = deleted
            item["refundable"] = max(0, item["total"]-item["refunded"]-item["reserved"]) if item["status"] not in {"pending_payment", "cancelled"} else 0
            item["refund_status"] = "refunded" if item["refunded"] >= item["total"] else item["refund_stage"] if item["reserved"] else "partial" if item["refunded"] else "none"
            items.append(item)
        return {"items": items, "total": total, "offset": offset, "limit": limit}

    def create_order(self, p, order_id, customer, product, quantity, total_cents, status):
        p.require("staff")
        if status not in ORDER_STATES - {"cancelled"}:
            raise ValueError("无效的初始订单状态")
        try:
            with self.store.tx() as db:
                db.execute("INSERT INTO orders(tenant,id,user,total,status) VALUES(?,?,?,?,?)", (p.tenant, order_id, customer, total_cents, status))
                now = time.time()
                db.execute("INSERT INTO order_details VALUES(?,?,?,?,?,?,0)", (p.tenant, order_id, product, quantity, now, now))
                self.store.audit(db, p, "order.create", order_id, {"customer": customer, "product": product, "quantity": quantity, "total_cents": total_cents, "status": status})
        except sqlite3.IntegrityError as exc:
            raise ValueError("订单号已存在，请更换订单号") from exc
        return {"id": order_id, "status": status, "version": 0}

    def delete_order(self, p, order_id, version):
        p.require("staff")
        with self.store.tx() as db:
            row = db.execute("SELECT COALESCE(d.version,0) version FROM orders o LEFT JOIN order_details d ON d.tenant=o.tenant AND d.order_id=o.id WHERE o.tenant=? AND o.id=?", (p.tenant, order_id)).fetchone()
            if not row:
                raise PermissionError("订单不可访问")
            if db.execute("SELECT 1 FROM deleted_orders WHERE tenant=? AND order_id=?", (p.tenant, order_id)).fetchone():
                return {"id": order_id, "deleted": True}
            if row["version"] != version:
                raise ValueError("订单已更新，请刷新后重试")
            if db.execute("SELECT 1 FROM refunds WHERE tenant=? AND order_id=? AND status IN ('pending','approved','processing')", (p.tenant, order_id)).fetchone():
                raise ValueError("请先处理该订单的退款申请，再删除订单")
            db.execute("INSERT INTO deleted_orders VALUES(?,?,?)", (p.tenant, order_id, time.time()))
            self.store.audit(db, p, "order.delete", order_id, {})
        return {"id": order_id, "deleted": True}

    def restore_order(self, p, order_id):
        p.require("staff")
        with self.store.tx() as db:
            if not db.execute("SELECT 1 FROM deleted_orders WHERE tenant=? AND order_id=?", (p.tenant, order_id)).fetchone():
                raise ValueError("未找到已删除订单")
            db.execute("DELETE FROM deleted_orders WHERE tenant=? AND order_id=?", (p.tenant, order_id))
            now = time.time()
            db.execute("INSERT OR IGNORE INTO order_details VALUES(?,?,?,1,?,?,0)", (p.tenant, order_id, "演示订单", now, now))
            db.execute("UPDATE order_details SET version=version+1,updated=? WHERE tenant=? AND order_id=?", (now, p.tenant, order_id))
            self.store.audit(db, p, "order.restore", order_id, {})
        return {"id": order_id, "deleted": False}

    def update_order(self, p, order_id, status, version):
        p.require("staff")
        with self.store.tx() as db:
            if db.execute("SELECT 1 FROM deleted_orders WHERE tenant=? AND order_id=?", (p.tenant, order_id)).fetchone():
                raise ValueError("订单已删除，请先恢复")
            row = db.execute("SELECT o.*,COALESCE(d.version,0) version FROM orders o LEFT JOIN order_details d ON d.tenant=o.tenant AND d.order_id=o.id WHERE o.tenant=? AND o.id=?", (p.tenant, order_id)).fetchone()
            if not row:
                raise PermissionError("订单不可访问")
            if row["version"] != version:
                raise ValueError("订单已更新，请刷新后重试")
            if status not in TRANSITIONS.get(row["status"], set()):
                raise ValueError("不支持此订单状态变更")
            reserved = db.execute("SELECT COALESCE(SUM(amount),0) FROM refunds WHERE tenant=? AND order_id=? AND status IN ('pending','approved','processing')", (p.tenant, order_id)).fetchone()[0]
            if status in {"shipped", "completed"} and (reserved or row["refunded"] >= row["total"]):
                raise ValueError("订单存在退款处理中或已全额退款，不能继续履约")
            now = time.time()
            db.execute("INSERT OR IGNORE INTO order_details VALUES(?,?,?,1,?,?,0)", (p.tenant, order_id, "演示订单", now, now))
            db.execute("UPDATE orders SET status=? WHERE tenant=? AND id=?", (status, p.tenant, order_id))
            db.execute("UPDATE order_details SET version=version+1,updated=? WHERE tenant=? AND order_id=?", (now, p.tenant, order_id))
            self.store.audit(db, p, "order.status", order_id, {"from": row["status"], "to": status})
        return {"id": order_id, "status": status, "version": version+1}

    def refunds(self, p, status="", search="", offset=0, limit=20):
        p.require("finance")
        where, args = "r.tenant=?", [p.tenant]
        if status:
            where += " AND r.status=?"
            args.append(status)
        if search:
            where += " AND (r.order_id LIKE ? OR r.user LIKE ? OR r.id LIKE ?)"
            args += ["%"+search+"%"]*3
        with self.store.tx() as db:
            total = db.execute("SELECT COUNT(*) FROM refunds r WHERE " + where, args).fetchone()[0]
            rows = db.execute("SELECT r.*,COALESCE(d.product,'演示订单') product FROM refunds r LEFT JOIN order_details d ON d.tenant=r.tenant AND d.order_id=r.order_id WHERE " + where + " ORDER BY r.rowid DESC LIMIT ? OFFSET ?", [*args, limit, offset]).fetchall()
        return {"items": [dict(row) for row in rows], "total": total, "offset": offset, "limit": limit}
