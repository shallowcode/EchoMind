package store

import (
	"encoding/json"
	"strings"
)

func (t *transaction) run(p Principal, op string, a Data) (any, error) {
	switch op {
	case "authenticate":
		r := t.one("SELECT * FROM tokens WHERE hash=? AND revoked=0 AND expires>?", Hash(Text(a, "token")), Now())
		if r == nil {
			return nil, &Error{401, "unauthorized", "连接已失效，请重新登录"}
		}
		roles := []string{}
		_ = json.Unmarshal([]byte(Text(r, "roles")), &roles)
		if u := t.one("SELECT disabled,roles FROM users WHERE tenant=? AND id=?", r["tenant"], r["user"]); u != nil {
			if Int(u, "disabled") != 0 {
				return nil, Denied()
			}
			_ = json.Unmarshal([]byte(Text(u, "roles")), &roles)
		}
		return Principal{Text(r, "tenant"), Text(r, "user"), roles}, nil
	case "issue_token":
		if p.Tenant == "" || p.User == "" {
			return nil, Denied()
		}
		token := ID("") + ID("")
		ttl := Int(a, "ttl")
		if ttl <= 0 || ttl > 86400 {
			ttl = 3600
		}
		t.exec("INSERT INTO tokens(hash,tenant,user,roles,expires) VALUES(?,?,?,?,?)", Hash(token), p.Tenant, p.User, JSON(p.Roles), Now()+float64(ttl))
		return token, nil
	case "revoke":
		t.exec("UPDATE tokens SET revoked=1 WHERE tenant=? AND user=? AND hash=?", p.Tenant, p.User, Hash(Text(a, "token")))
		return Data{"revoked": true}, nil
	case "profile":
		r := t.one("SELECT payload FROM profiles WHERE tenant=? AND user=?", p.Tenant, p.User)
		return Parse(Text(r, "payload")), nil
	case "history", "conversation":
		conv := Text(a, "conv")
		r := t.one("SELECT * FROM conversations WHERE tenant=? AND id=?", p.Tenant, conv)
		if r == nil {
			if op == "conversation" {
				return nil, &Error{404, "not_found", "会话不存在"}
			}
			return []Data{}, nil
		}
		if Text(r, "user") != p.User && !(op == "conversation" && p.Has("staff")) {
			return nil, Denied()
		}
		n := Int(a, "limit")
		if n <= 0 {
			n = 20
		}
		if n > 200 {
			n = 200
		}
		cols := "role,content"
		if op == "conversation" {
			cols = "seq,role,content,created,(SELECT actor FROM message_details d WHERE d.seq=messages.seq) author,(SELECT execution FROM message_details d WHERE d.seq=messages.seq) execution"
		}
		rows := t.rows("SELECT "+cols+" FROM messages WHERE tenant=? AND conv=? ORDER BY seq DESC LIMIT ?", p.Tenant, conv, n)
		if op == "conversation" {
			for _, m := range rows {
				m["execution"] = Parse(Text(m, "execution"))
			}
		}
		for i, j := 0, len(rows)-1; i < j; i, j = i+1, j-1 {
			rows[i], rows[j] = rows[j], rows[i]
		}
		if op == "history" {
			return rows, nil
		}
		mode := t.mode(p, conv)
		return Data{"id": conv, "customer": r["user"], "messages": rows, "mode": mode["mode"], "assignee": mode["assignee"], "version": mode["version"], "tickets": t.rows("SELECT * FROM tickets WHERE tenant=? AND conv=? ORDER BY rowid DESC", p.Tenant, conv)}, nil
	case "conversations":
		where := "c.tenant=?"
		args := []any{p.Tenant}
		if !p.Has("staff") {
			where += " AND c.user=?"
			args = append(args, p.User)
		}
		if st := Text(a, "mode"); st != "" {
			where += " AND COALESCE(m.mode,'ai')=?"
			args = append(args, st)
		}
		rows := t.rows(`SELECT c.id,c.user,COALESCE(m.mode,'ai') mode,COALESCE(m.assignee,'') assignee,COALESCE(m.version,0) version,(SELECT content FROM messages WHERE tenant=c.tenant AND conv=c.id ORDER BY seq ASC LIMIT 1) title,(SELECT content FROM messages WHERE tenant=c.tenant AND conv=c.id ORDER BY seq DESC LIMIT 1) preview,(SELECT MAX(created) FROM messages WHERE tenant=c.tenant AND conv=c.id) updated FROM conversations c LEFT JOIN conversation_modes m ON m.tenant=c.tenant AND m.conv=c.id WHERE `+where+" ORDER BY updated DESC LIMIT 100", args...)
		return Data{"items": rows}, nil
	case "mode":
		conv := Text(a, "conv")
		r := t.one("SELECT user,lease_until FROM conversations WHERE tenant=? AND id=?", p.Tenant, conv)
		if r == nil || Text(r, "user") != p.User && !p.Has("staff") {
			return nil, Denied()
		}
		return t.mode(p, conv), nil
	case "takeover", "resume_ai":
		if !p.Has("staff") {
			return nil, Denied()
		}
		conv := Text(a, "conv")
		r := t.one("SELECT * FROM conversations WHERE tenant=? AND id=?", p.Tenant, conv)
		if r == nil {
			return nil, Denied()
		}
		if value, ok := r["lease_until"].(float64); ok && value > Now() {
			return nil, Conflict("AI 正在完成本轮处理，请稍后接管")
		}
		old := t.mode(p, conv)
		if Int(a, "version") != Int(old, "version") {
			return nil, Conflict("会话已更新，请刷新")
		}
		if Text(old, "assignee") != "" && Text(old, "assignee") != p.User && !p.Has("admin") {
			return nil, Denied()
		}
		mode := "human"
		assignee := p.User
		if op == "resume_ai" {
			mode = "ai"
			assignee = ""
		}
		t.exec("INSERT INTO conversation_modes VALUES(?,?,?,?,?,?) ON CONFLICT(tenant,conv) DO UPDATE SET mode=excluded.mode,assignee=excluded.assignee,version=excluded.version,updated=excluded.updated", p.Tenant, conv, mode, assignee, Int(old, "version")+1, Now())
		t.event(p.Tenant, conv, "conversation.mode", Data{"mode": mode})
		t.audit(p, "conversation."+op, conv, Data{})
		return t.mode(p, conv), nil
	case "acquire_conversation":
		conv := Text(a, "conv")
		if !allowedID(conv) {
			return nil, Invalid("会话编号无效")
		}
		t.exec("INSERT OR IGNORE INTO conversations(tenant,id,user,state) VALUES(?,?,?,'{}')", p.Tenant, conv, p.User)
		r := t.one("SELECT * FROM conversations WHERE tenant=? AND id=?", p.Tenant, conv)
		if Text(r, "user") != p.User {
			return nil, Denied()
		}
		if v, ok := r["lease_until"].(float64); ok && v > Now() {
			return nil, Conflict("会话正在处理中，请重试同一请求")
		}
		if Text(t.mode(p, conv), "mode") != "ai" {
			return nil, Conflict("会话已转人工")
		}
		t.exec("UPDATE conversations SET lease_owner=?,lease_until=? WHERE tenant=? AND id=?", Text(a, "owner"), Now()+float64(Int(a, "ttl")), p.Tenant, conv)
		return Parse(Text(r, "state")), nil
	case "release":
		t.exec("UPDATE conversations SET lease_until=0 WHERE tenant=? AND id=? AND lease_owner=?", p.Tenant, Text(a, "conv"), Text(a, "owner"))
		return true, nil
	case "cached_request":
		r := t.one("SELECT * FROM requests WHERE tenant=? AND user=? AND id=?", p.Tenant, p.User, Text(a, "rid"))
		if r == nil && Bool(a, "include_human") {
			r = t.one("SELECT * FROM human_requests WHERE tenant=? AND actor=? AND id=?", p.Tenant, p.User, Text(a, "rid"))
		}
		if r == nil {
			return nil, nil
		}
		if Text(r, "fingerprint") != Text(a, "fingerprint") {
			return nil, Conflict("请求编号对应的内容不同")
		}
		return Parse(Text(r, "response")), nil
	case "commit_turn":
		conv := Text(a, "conv")
		r := t.one("SELECT * FROM conversations WHERE tenant=? AND id=?", p.Tenant, conv)
		if r == nil || Text(r, "user") != p.User || Text(r, "lease_owner") != Text(a, "owner") {
			return nil, Conflict("会话租约已失效")
		}
		response := object(a["response"])
		state := object(a["state"])
		for _, msg := range []Data{{"role": "user", "content": a["message"]}, {"role": "assistant", "content": response["response"]}} {
			t.exec("INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)", p.Tenant, conv, msg["role"], msg["content"], Now())
			if msg["role"] == "assistant" {
				t.exec("INSERT INTO message_details(seq,tenant,conv,actor,request_id,execution) VALUES(last_insert_rowid(),?,?,?,?,?)", p.Tenant, conv, p.User, a["rid"], JSON(response["execution"]))
			}
		}
		t.exec("UPDATE conversations SET state=?,version=version+1 WHERE tenant=? AND id=?", JSON(state), p.Tenant, conv)
		t.exec("INSERT INTO profiles VALUES(?,?,?) ON CONFLICT(tenant,user) DO UPDATE SET payload=excluded.payload", p.Tenant, p.User, JSON(state["profile"]))
		t.exec("INSERT INTO requests VALUES(?,?,?,?,?)", p.Tenant, p.User, a["rid"], a["fingerprint"], JSON(response))
		t.exec("INSERT INTO traces VALUES(?,?,?,?)", p.Tenant, p.User, p.Tenant+":"+p.User+":"+Text(a, "rid"), JSON(response["trace"]))
		t.event(p.Tenant, conv, "message.created", Data{"role": "assistant"})
		return true, nil
	case "finalize_turn":
		response := object(a["response"])
		t.exec("UPDATE requests SET response=? WHERE tenant=? AND user=? AND id=?", JSON(response), p.Tenant, p.User, a["rid"])
		t.exec("UPDATE traces SET payload=? WHERE id=?", JSON(response["trace"]), p.Tenant+":"+p.User+":"+Text(a, "rid"))
		t.exec("UPDATE message_details SET execution=? WHERE tenant=? AND actor=? AND request_id=?", JSON(response["execution"]), p.Tenant, p.User, a["rid"])
		t.event(p.Tenant, Text(response, "conv_id"), "execution.updated", Data{})
		return true, nil
	case "human_message", "staff_reply":
		conv := Text(a, "conv")
		message := strings.TrimSpace(Text(a, "message"))
		rid := Text(a, "request_id")
		if message == "" || len([]rune(message)) > 6000 || !allowedID(rid) {
			return nil, Invalid("消息或请求编号无效")
		}
		r := t.one("SELECT user,lease_until FROM conversations WHERE tenant=? AND id=?", p.Tenant, conv)
		if r == nil {
			return nil, Denied()
		}
		mode := t.mode(p, conv)
		if until, ok := r["lease_until"].(float64); ok && until > Now() {
			return nil, Conflict("本轮仍在处理中，请稍后重试")
		}
		role := "user"
		if op == "staff_reply" {
			if !p.Has("staff") || Text(mode, "mode") != "human" || Text(mode, "assignee") != p.User {
				return nil, Denied()
			}
			role = "assistant"
		} else if Text(r, "user") != p.User || Text(mode, "mode") == "ai" {
			return nil, Denied()
		}
		fingerprint := Hash(conv + "\n" + message + "\n" + op)
		if op == "human_message" {
			fingerprint = Text(a, "fingerprint")
		}
		old := t.one("SELECT * FROM human_requests WHERE tenant=? AND actor=? AND id=?", p.Tenant, p.User, rid)
		if old != nil {
			if Text(old, "fingerprint") != fingerprint {
				return nil, Conflict("消息幂等键冲突")
			}
			return Parse(Text(old, "response")), nil
		}
		t.exec("INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)", p.Tenant, conv, role, message, Now())
		if op == "staff_reply" {
			t.exec("INSERT INTO message_details(seq,tenant,conv,actor,request_id) VALUES(last_insert_rowid(),?,?,?,?)", p.Tenant, conv, p.User, rid)
		}
		result := Data{"conv_id": conv, "request_id": rid, "response": "消息已送达，等待人工客服回复。", "status": "awaiting_human", "mode": mode["mode"]}
		if op == "staff_reply" {
			result["response"] = message
			result["status"] = "completed"
		}
		t.exec("INSERT INTO human_requests VALUES(?,?,?,?,?)", p.Tenant, p.User, rid, fingerprint, JSON(result))
		t.event(p.Tenant, conv, "message.created", Data{"role": role})
		return result, nil
	case "create_ticket", "ticket", "tickets", "update_ticket":
		return t.tickets(p, op, a)
	case "audit_log":
		if !p.Has("staff", "ops") {
			return nil, Denied()
		}
		return t.rows("SELECT * FROM audit WHERE tenant=? ORDER BY seq DESC LIMIT 200", p.Tenant), nil
	case "append_audit":
		if !p.Has("staff") {
			return nil, Denied()
		}
		t.audit(p, Text(a, "action"), Text(a, "target"), a["detail"])
		return true, nil
	case "events":
		where := "tenant=? AND id>?"
		args := []any{p.Tenant, Int(a, "after")}
		if !p.Has("staff") {
			where += " AND conv IN (SELECT id FROM conversations WHERE tenant=? AND user=?)"
			args = append(args, p.Tenant, p.User)
		}
		return t.rows("SELECT * FROM events WHERE "+where+" ORDER BY id LIMIT 100", args...), nil
	case "stats":
		if !p.Has("staff", "ops") {
			return nil, Denied()
		}
		r := t.one("SELECT COUNT(*) conversations FROM conversations WHERE tenant=?", p.Tenant)
		r["messages"] = Int(t.one("SELECT COUNT(*) n FROM messages WHERE tenant=?", p.Tenant), "n")
		r["waiting"] = Int(t.one("SELECT COUNT(*) n FROM conversation_modes WHERE tenant=? AND mode='waiting'", p.Tenant), "n")
		r["human"] = Int(t.one("SELECT COUNT(*) n FROM conversation_modes WHERE tenant=? AND mode='human'", p.Tenant), "n")
		r["tickets"] = t.rows("SELECT status,COUNT(*) count FROM tickets WHERE tenant=? GROUP BY status", p.Tenant)
		r["refunds"] = t.rows("SELECT status,COUNT(*) count,COALESCE(SUM(amount),0) amount FROM refunds WHERE tenant=? GROUP BY status", p.Tenant)
		return r, nil
	}
	return t.business(p, op, a)
}

func (t *transaction) tickets(p Principal, op string, a Data) (any, error) {
	tid := Text(a, "tid")
	switch op {
	case "tickets":
		if !p.Has("staff") {
			return nil, Denied()
		}
		return t.rows("SELECT * FROM tickets WHERE tenant=? ORDER BY rowid DESC LIMIT 200", p.Tenant), nil
	case "ticket":
		r := t.one("SELECT * FROM tickets WHERE tenant=? AND id=?", p.Tenant, tid)
		if r == nil || Text(r, "user") != p.User && !p.Has("staff") {
			return nil, Denied()
		}
		return r, nil
	case "create_ticket":
		conv, summary, idem := Text(a, "conv"), strings.TrimSpace(Text(a, "summary")), Text(a, "idem")
		if summary == "" || len([]rune(summary)) > 1500 || idem == "" {
			return nil, Invalid("工单信息不完整")
		}
		r := t.one("SELECT user FROM conversations WHERE tenant=? AND id=?", p.Tenant, conv)
		if r == nil || Text(r, "user") != p.User {
			return nil, Denied()
		}
		old := t.one("SELECT * FROM tickets WHERE tenant=? AND user=? AND idem=?", p.Tenant, p.User, idem)
		if old != nil {
			if Text(old, "conv") != conv || Text(old, "summary") != summary {
				return nil, Conflict("工单幂等键冲突")
			}
			return old, nil
		}
		tid = ID("tk_")
		t.exec("INSERT INTO tickets(id,tenant,user,conv,summary,status,idem) VALUES(?,?,?,?,?,'open',?)", tid, p.Tenant, p.User, conv, summary, idem)
		t.exec("INSERT INTO conversation_modes VALUES(?,?,'waiting','',0,?) ON CONFLICT(tenant,conv) DO UPDATE SET mode=CASE WHEN mode='human' THEN 'human' ELSE 'waiting' END,version=version+1,updated=excluded.updated", p.Tenant, conv, Now())
		t.audit(p, "ticket.create", tid, Data{"conv": conv})
		t.event(p.Tenant, conv, "ticket.created", Data{"id": tid})
		return t.one("SELECT * FROM tickets WHERE id=?", tid), nil
	case "update_ticket":
		if !p.Has("staff") {
			return nil, Denied()
		}
		r := t.one("SELECT * FROM tickets WHERE tenant=? AND id=?", p.Tenant, tid)
		if r == nil {
			return nil, Denied()
		}
		st, assignee, resolution := Text(a, "status"), Text(a, "assignee"), strings.TrimSpace(Text(a, "resolution"))
		old := Text(r, "status")
		next := map[string]string{"open": "assigned", "assigned": "resolved", "resolved": "closed", "closed": "open"}
		if next[old] != st {
			return nil, Conflict("无效的工单状态变更")
		}
		if Int(a, "version") != Int(r, "version") {
			return nil, Conflict("工单已更新，请刷新")
		}
		if st == "assigned" {
			if assignee == "" {
				assignee = p.User
			}
			if assignee != p.User && !p.Has("admin") {
				return nil, Denied()
			}
		}
		if st == "resolved" && (resolution == "" || Text(r, "assignee") != p.User && !p.Has("admin")) {
			return nil, Denied()
		}
		if len([]rune(resolution)) > 4000 {
			return nil, Invalid("解决说明过长")
		}
		if assignee == "" {
			assignee = Text(r, "assignee")
		}
		if resolution == "" {
			resolution = Text(r, "resolution")
		}
		if st == "open" {
			assignee = ""
			resolution = ""
		}
		t.exec("UPDATE tickets SET status=?,assignee=?,resolution=?,version=version+1 WHERE tenant=? AND id=?", st, assignee, resolution, p.Tenant, tid)
		if st == "resolved" {
			t.exec("INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,'system',?,?)", p.Tenant, r["conv"], "工单 "+tid+" 已解决："+resolution, Now())
		}
		t.audit(p, "ticket."+st, tid, Data{"resolution": resolution})
		t.event(p.Tenant, Text(r, "conv"), "ticket.updated", Data{"status": st})
		return t.one("SELECT * FROM tickets WHERE id=?", tid), nil
	}
	return nil, Invalid("未知工单操作")
}
