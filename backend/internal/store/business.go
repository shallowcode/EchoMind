package store

import "strings"

func (t *transaction) order(p Principal, id string) (Data, error) {
	r := t.one(`SELECT o.*,COALESCE(d.product,'演示订单') product,COALESCE(d.quantity,1) quantity,COALESCE(d.version,0) version FROM orders o LEFT JOIN order_details d ON d.tenant=o.tenant AND d.order_id=o.id WHERE o.tenant=? AND o.id=? AND NOT EXISTS(SELECT 1 FROM deleted_orders x WHERE x.tenant=o.tenant AND x.order_id=o.id)`, p.Tenant, id)
	if r == nil || Text(r, "user") != p.User && !p.Demo() && !p.Has("staff", "finance") {
		return nil, Denied()
	}
	reserved := t.one("SELECT COALESCE(SUM(amount),0) n FROM refunds WHERE tenant=? AND order_id=? AND status IN ('pending','approved','processing')", p.Tenant, id)
	r["reserved"] = Int(reserved, "n")
	r["refundable"] = max(int64(0), Int(r, "total")-Int(r, "refunded")-Int(r, "reserved"))
	if Text(r, "status") == "pending_payment" || Text(r, "status") == "cancelled" {
		r["refundable"] = int64(0)
	}
	r["refunds"] = t.rows("SELECT id,order_id,amount,status FROM refunds WHERE tenant=? AND order_id=? ORDER BY rowid DESC", p.Tenant, id)
	return r, nil
}
func (t *transaction) business(p Principal, op string, a Data) (any, error) {
	id := Text(a, "order_id")
	switch op {
	case "order":
		return t.order(p, id)
	case "order_list":
		q := `SELECT o.id,o.status,o.total,o.refunded,COALESCE(d.product,'演示订单') product FROM orders o LEFT JOIN order_details d ON d.tenant=o.tenant AND d.order_id=o.id WHERE o.tenant=? AND NOT EXISTS(SELECT 1 FROM deleted_orders x WHERE x.tenant=o.tenant AND x.order_id=o.id)`
		args := []any{p.Tenant}
		if !p.Demo() && !p.Has("staff", "finance") {
			q += " AND o.user=?"
			args = append(args, p.User)
		}
		rows := t.rows(q+" ORDER BY o.rowid DESC", args...)
		return Data{"items": rows, "total": len(rows)}, nil
	case "merchant_overview":
		if !p.Has("staff", "finance") {
			return nil, Denied()
		}
		r := t.one("SELECT COUNT(*) orders,COALESCE(SUM(CASE WHEN status NOT IN ('pending_payment','cancelled') THEN total-refunded ELSE 0 END),0) net_cents FROM orders o WHERE tenant=? AND NOT EXISTS(SELECT 1 FROM deleted_orders x WHERE x.tenant=o.tenant AND x.order_id=o.id)", p.Tenant)
		f := t.one("SELECT COALESCE(SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END),0) pending_refunds,COALESCE(SUM(CASE WHEN status='settled' THEN amount ELSE 0 END),0) refunded_cents FROM refunds WHERE tenant=?", p.Tenant)
		for k, v := range f {
			r[k] = v
		}
		return r, nil
	case "merchant_orders":
		if !p.Has("staff", "finance") {
			return nil, Denied()
		}
		n, offset := limit(a)
		where := "o.tenant=?"
		args := []any{p.Tenant}
		deleted := Text(a, "status") == "deleted"
		if !deleted {
			where += " AND NOT"
		} else {
			where += " AND"
		}
		where += " EXISTS(SELECT 1 FROM deleted_orders x WHERE x.tenant=o.tenant AND x.order_id=o.id)"
		if q := Text(a, "search"); q != "" {
			where += " AND (o.id LIKE ? OR o.user LIKE ? OR d.product LIKE ?)"
			args = append(args, "%"+q+"%", "%"+q+"%", "%"+q+"%")
		}
		if st := Text(a, "status"); st != "" && !deleted {
			where += " AND o.status=?"
			args = append(args, st)
		}
		join := " FROM orders o LEFT JOIN order_details d ON d.tenant=o.tenant AND d.order_id=o.id WHERE "
		total := t.one("SELECT COUNT(*) total"+join+where, args...)
		rows := t.rows(`SELECT o.*,COALESCE(d.product,'演示订单') product,COALESCE(d.quantity,1) quantity,d.created,COALESCE(d.version,0) version,(SELECT COALESCE(SUM(amount),0) FROM refunds r WHERE r.tenant=o.tenant AND r.order_id=o.id AND status IN ('pending','approved','processing')) reserved,(SELECT status FROM refunds r WHERE r.tenant=o.tenant AND r.order_id=o.id AND status IN ('pending','approved','processing') ORDER BY CASE status WHEN 'pending' THEN 0 WHEN 'processing' THEN 1 ELSE 2 END LIMIT 1) refund_stage`+join+where+" ORDER BY COALESCE(d.created,0) DESC,o.id DESC LIMIT ? OFFSET ?", append(args, n, offset)...)
		for _, r := range rows {
			r["deleted"] = deleted
			r["refundable"] = max(int64(0), Int(r, "total")-Int(r, "refunded")-Int(r, "reserved"))
			if Text(r, "status") == "pending_payment" || Text(r, "status") == "cancelled" {
				r["refundable"] = 0
			}
			r["refund_status"] = "none"
			if Int(r, "refunded") > 0 {
				r["refund_status"] = "partial"
			}
			if Int(r, "reserved") > 0 {
				r["refund_status"] = r["refund_stage"]
			}
			if Int(r, "refunded") >= Int(r, "total") {
				r["refund_status"] = "refunded"
			}
		}
		return Data{"items": rows, "total": Int(total, "total"), "offset": offset, "limit": n}, nil
	case "create_order":
		if !p.Has("staff") {
			return nil, Denied()
		}
		product := strings.TrimSpace(Text(a, "product"))
		customer := Text(a, "customer")
		amount := Int(a, "total_cents")
		qty := Int(a, "quantity")
		st := Text(a, "status")
		if !allowedID(id) || len(id) < 4 || len(id) > 32 || !allowedID(customer) || product == "" || len([]rune(product)) > 120 || amount <= 0 || amount > 100000000 || qty <= 0 || qty > 10000 {
			return nil, Invalid("请检查订单号、商品、客户、数量及金额")
		}
		if st != "paid" && st != "pending_payment" && st != "shipped" && st != "completed" {
			return nil, Invalid("无效的初始状态")
		}
		if t.one("SELECT id FROM orders WHERE tenant=? AND id=?", p.Tenant, id) != nil {
			return nil, Conflict("订单号已存在")
		}
		t.exec("INSERT INTO orders(tenant,id,user,total,status) VALUES(?,?,?,?,?)", p.Tenant, id, customer, amount, st)
		t.exec("INSERT INTO order_details VALUES(?,?,?,?,?,?,0)", p.Tenant, id, product, qty, Now(), Now())
		t.audit(p, "order.create", id, a)
		return Data{"id": id, "status": st, "version": 0}, nil
	case "update_order", "delete_order", "restore_order":
		if !p.Has("staff") {
			return nil, Denied()
		}
		r := t.one("SELECT o.*,COALESCE(d.version,0) version FROM orders o LEFT JOIN order_details d ON d.tenant=o.tenant AND d.order_id=o.id WHERE o.tenant=? AND o.id=?", p.Tenant, id)
		if r == nil {
			return nil, Denied()
		}
		deleted := t.one("SELECT order_id FROM deleted_orders WHERE tenant=? AND order_id=?", p.Tenant, id) != nil
		if op == "restore_order" {
			if !deleted {
				return nil, Conflict("未找到已删除订单")
			}
			t.exec("DELETE FROM deleted_orders WHERE tenant=? AND order_id=?", p.Tenant, id)
			t.exec("INSERT OR IGNORE INTO order_details VALUES(?,?,?,1,?,?,0)", p.Tenant, id, "演示订单", Now(), Now())
			t.exec("UPDATE order_details SET version=version+1,updated=? WHERE tenant=? AND order_id=?", Now(), p.Tenant, id)
			t.audit(p, "order.restore", id, Data{})
			return Data{"id": id, "deleted": false}, nil
		}
		if deleted {
			if op == "delete_order" {
				return Data{"id": id, "deleted": true}, nil
			}
			return nil, Conflict("订单已删除，请先恢复")
		}
		if Int(a, "version") != Int(r, "version") {
			return nil, Conflict("订单已更新，请刷新后重试")
		}
		reserved := Int(t.one("SELECT COALESCE(SUM(amount),0) n FROM refunds WHERE tenant=? AND order_id=? AND status IN ('pending','approved','processing')", p.Tenant, id), "n")
		if op == "delete_order" {
			if reserved > 0 {
				return nil, Conflict("请先处理退款申请再删除订单")
			}
			t.exec("INSERT INTO deleted_orders VALUES(?,?,?)", p.Tenant, id, Now())
			t.audit(p, "order.delete", id, Data{})
			return Data{"id": id, "deleted": true}, nil
		}
		st := Text(a, "status")
		old := Text(r, "status")
		if !(old == "pending_payment" && (st == "paid" || st == "cancelled") || old == "paid" && st == "shipped" || old == "shipped" && st == "completed") {
			return nil, Conflict("不支持此订单状态变更")
		}
		if (st == "shipped" || st == "completed") && (reserved > 0 || Int(r, "refunded") >= Int(r, "total")) {
			return nil, Conflict("退款处理中或已全额退款，不能继续履约")
		}
		t.exec("INSERT OR IGNORE INTO order_details VALUES(?,?,?,1,?,?,0)", p.Tenant, id, "演示订单", Now(), Now())
		t.exec("UPDATE orders SET status=? WHERE tenant=? AND id=?", st, p.Tenant, id)
		t.exec("UPDATE order_details SET version=version+1,updated=? WHERE tenant=? AND order_id=?", Now(), p.Tenant, id)
		t.audit(p, "order.status", id, Data{"from": old, "to": st})
		return Data{"id": id, "status": st, "version": Int(r, "version") + 1}, nil
	case "refund_status":
		if id != "" {
			r, err := t.order(p, id)
			if err != nil {
				return nil, err
			}
			items := r["refunds"].([]Data)
			if rid := Text(a, "refund_id"); rid != "" {
				filtered := []Data{}
				for _, item := range items {
					if Text(item, "id") == rid {
						filtered = append(filtered, item)
					}
				}
				items = filtered
			}
			return Data{"order_id": id, "items": items}, nil
		}
		r := t.one("SELECT * FROM refunds WHERE tenant=? AND id=?", p.Tenant, Text(a, "refund_id"))
		if r == nil || Text(r, "user") != p.User && !p.Demo() && !p.Has("staff", "finance") {
			return nil, Denied()
		}
		return Data{"order_id": r["order_id"], "items": []Data{r}}, nil
	case "refund_request":
		amount := Int(a, "amount")
		full := Bool(a, "full")
		if full && a["amount"] != nil {
			return nil, Invalid("全额退款金额由账本计算")
		}
		reason := strings.TrimSpace(Text(a, "reason"))
		idem := Text(a, "idem")
		if reason == "" || len([]rune(reason)) > 500 || idem == "" || len(idem) > 150 || !full && (amount <= 0 || amount > 100000000) {
			return nil, Invalid("退款参数无效")
		}
		if full {
			idem = "full:" + idem
		}
		if t.one("SELECT 1 FROM deleted_orders WHERE tenant=? AND order_id=?", p.Tenant, id) != nil {
			return nil, Denied()
		}
		old := t.one("SELECT * FROM refunds WHERE tenant=? AND user=? AND idem=?", p.Tenant, p.User, idem)
		if old != nil {
			if Text(old, "order_id") != id || Text(old, "reason") != reason || !full && Int(old, "amount") != amount {
				return nil, Conflict("幂等键对应的请求内容不同")
			}
			return old, nil
		}
		r, err := t.order(p, id)
		if err != nil {
			return nil, err
		}
		if Text(r, "user") != p.User && !p.Demo() {
			return nil, Denied()
		}
		if Text(r, "status") == "pending_payment" || Text(r, "status") == "cancelled" {
			return nil, Business("order_not_paid", "订单尚未支付")
		}
		if full {
			amount = Int(r, "refundable")
		}
		if amount <= 0 || amount > Int(r, "refundable") {
			return nil, Business("insufficient_refundable_balance", "申请金额超出未占用的可退款余额")
		}
		rid := ID("rf_")
		t.exec("INSERT INTO refunds(id,tenant,user,order_id,amount,status,idem,reason) VALUES(?,?,?,?,?,'pending',?,?)", rid, p.Tenant, p.User, id, amount, idem, reason)
		t.audit(p, "refund.request", rid, Data{"amount_cents": amount, "mode": "sandbox"})
		return t.one("SELECT * FROM refunds WHERE id=?", rid), nil
	case "approve_refund", "settle_refund":
		if !p.Has("finance") {
			return nil, Denied()
		}
		rid := Text(a, "rid")
		r := t.one("SELECT * FROM refunds WHERE tenant=? AND id=?", p.Tenant, rid)
		if r == nil || Text(r, "user") == p.User {
			return nil, Denied()
		}
		st := Text(r, "status")
		if op == "approve_refund" {
			if st != "pending" {
				return nil, Conflict("退款必须处于待审核状态")
			}
			next := "approved"
			if !Bool(a, "approve") {
				next = "rejected"
			}
			t.exec("UPDATE refunds SET status=? WHERE tenant=? AND id=?", next, p.Tenant, rid)
			t.audit(p, "refund."+next, rid, Data{})
			return Data{"id": rid, "status": next}, nil
		}
		if st == "settled" {
			return r, nil
		}
		if st != "approved" {
			return nil, Conflict("退款须先审批通过")
		}
		t.exec("UPDATE orders SET refunded=refunded+? WHERE tenant=? AND id=?", r["amount"], p.Tenant, r["order_id"])
		t.exec("UPDATE refunds SET status='settled',payment_ref=? WHERE tenant=? AND id=?", "sandbox_"+rid, p.Tenant, rid)
		t.audit(p, "refund.settle", rid, Data{"mode": "sandbox"})
		return t.one("SELECT * FROM refunds WHERE id=?", rid), nil
	case "refunds", "merchant_refunds":
		where := "r.tenant=?"
		args := []any{p.Tenant}
		if op == "merchant_refunds" && !p.Has("finance") {
			return nil, Denied()
		}
		if op == "refunds" && !p.Demo() && !p.Has("finance") {
			where += " AND r.user=?"
			args = append(args, p.User)
		}
		if st := Text(a, "status"); st != "" {
			where += " AND r.status=?"
			args = append(args, st)
		}
		if q := Text(a, "search"); q != "" {
			where += " AND (r.order_id LIKE ? OR r.user LIKE ? OR r.id LIKE ?)"
			args = append(args, "%"+q+"%", "%"+q+"%", "%"+q+"%")
		}
		n, o := limit(a)
		total := t.one("SELECT COUNT(*) n FROM refunds r WHERE "+where, args...)
		q := `SELECT r.*,COALESCE(d.product,'演示订单') product FROM refunds r LEFT JOIN order_details d ON d.tenant=r.tenant AND d.order_id=r.order_id WHERE ` + where + " ORDER BY r.rowid DESC"
		if op == "merchant_refunds" {
			q += " LIMIT ? OFFSET ?"
			args = append(args, n, o)
		}
		rows := t.rows(q, args...)
		if op == "refunds" {
			return rows, nil
		}
		return Data{"items": rows, "total": Int(total, "n"), "limit": n, "offset": o}, nil
	}
	return nil, Invalid("未知业务操作")
}
