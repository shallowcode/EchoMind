package app

import (
	"encoding/json"
	"net/http"
	"strings"
	"supportflow/backend/internal/store"
)

func strict(a store.Data, fields string) error {
	allowed := map[string]bool{}
	for _, f := range strings.Fields(fields) {
		allowed[f] = true
	}
	for k := range a {
		if !allowed[k] {
			return store.Invalid("未知字段：" + k)
		}
	}
	return nil
}
func integers(a store.Data, fields string) error {
	for _, key := range strings.Fields(fields) {
		n, ok := a[key].(json.Number)
		if !ok {
			return store.Invalid("需要整数字段：" + key)
		}
		if v, e := n.Int64(); e != nil || v < 0 {
			return store.Invalid("整数无效：" + key)
		}
	}
	return nil
}
func (a *Server) conversations(w http.ResponseWriter, r *http.Request, p store.Principal) error {
	parts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	if len(parts) == 1 && r.Method == "GET" {
		return a.run(w, r, p, "conversations", store.Data{"mode": r.URL.Query().Get("mode")})
	}
	if len(parts) == 2 && r.Method == "GET" {
		return a.run(w, r, p, "conversation", store.Data{"conv": parts[1], "limit": 200})
	}
	if len(parts) == 3 && r.Method == "POST" {
		b, e := readBody(w, r)
		if e != nil {
			return e
		}
		op := ""
		switch parts[2] {
		case "takeover":
			op = "takeover"
		case "resume-ai":
			op = "resume_ai"
		case "messages":
			op = "staff_reply"
		}
		if op == "" {
			return &store.Error{Status: 404, Code: "not_found", Message: "接口不存在"}
		}
		if op == "staff_reply" {
			if e = strict(b, "message request_id"); e != nil {
				return e
			}
		} else {
			if e = strict(b, "version"); e != nil {
				return e
			}
			if e = integers(b, "version"); e != nil {
				return e
			}
		}
		b["conv"] = parts[1]
		return a.run(w, r, p, op, b)
	}
	return &store.Error{Status: 405, Code: "method", Message: "不支持此操作"}
}
func (a *Server) business(w http.ResponseWriter, r *http.Request, p store.Principal) error {
	path := strings.Trim(r.URL.Path, "/")
	parts := strings.Split(path, "/")
	q := r.URL.Query()
	args := store.Data{"status": q.Get("status"), "search": q.Get("search"), "offset": store.Integer(q.Get("offset"), 0), "limit": store.Integer(q.Get("limit"), 20)}
	if r.Method == "GET" {
		op := ""
		switch path {
		case "merchant/overview":
			op = "merchant_overview"
		case "merchant/orders":
			op = "merchant_orders"
		case "merchant/refunds":
			op = "merchant_refunds"
		case "orders":
			op = "order_list"
		case "refunds":
			op = "refunds"
		case "tickets":
			op = "tickets"
		}
		if len(parts) == 2 && parts[0] == "orders" {
			op = "order"
			args["order_id"] = parts[1]
		}
		if len(parts) == 2 && parts[0] == "tickets" {
			op = "ticket"
			args["tid"] = parts[1]
		}
		if op != "" {
			return a.run(w, r, p, op, args)
		}
	}
	if r.Method == "DELETE" && len(parts) == 3 && parts[0] == "merchant" && parts[1] == "orders" {
		v := store.Integer(q.Get("version"), -1)
		if v < 0 {
			return store.Invalid("需要订单版本")
		}
		return a.run(w, r, p, "delete_order", store.Data{"order_id": parts[2], "version": v})
	}
	if r.Method == "POST" && len(parts) == 4 && parts[0] == "merchant" && parts[1] == "orders" && parts[3] == "restore" {
		return a.run(w, r, p, "restore_order", store.Data{"order_id": parts[2]})
	}
	if r.Method == "POST" && len(parts) == 3 && parts[0] == "refunds" && parts[2] == "settle" {
		return a.run(w, r, p, "settle_refund", store.Data{"rid": parts[1]})
	}
	if r.Method != "POST" && r.Method != "PATCH" {
		return &store.Error{Status: 405, Code: "method", Message: "不支持此操作"}
	}
	b, e := readBody(w, r)
	if e != nil {
		return e
	}
	op, fields, nums := "", "", ""
	switch {
	case path == "merchant/orders" && r.Method == "POST":
		op = "create_order"
		fields = "order_id customer product quantity total_cents status"
		nums = "quantity total_cents"
		if _, ok := b["status"]; !ok {
			b["status"] = "paid"
		}
	case len(parts) == 3 && parts[0] == "merchant" && parts[1] == "orders" && r.Method == "PATCH":
		op = "update_order"
		fields = "status version"
		nums = "version"
	case path == "refunds" && r.Method == "POST":
		op = "refund_request"
		fields = "order_id amount_cents reason idempotency_key"
		nums = "amount_cents"
	case len(parts) == 3 && parts[0] == "refunds" && parts[2] == "approval" && r.Method == "POST":
		op = "approve_refund"
		fields = "approve"
		if _, ok := b["approve"]; !ok {
			b["approve"] = true
		}
		if _, ok := b["approve"].(bool); !ok {
			return store.Invalid("审核决定必须为布尔值")
		}
	case path == "tickets" && r.Method == "POST":
		op = "create_ticket"
		fields = "conv_id summary idempotency_key"
	case len(parts) == 2 && parts[0] == "tickets" && r.Method == "PATCH":
		op = "update_ticket"
		fields = "status assignee resolution version"
		nums = "version"
	default:
		return &store.Error{Status: 404, Code: "not_found", Message: "接口不存在"}
	}
	if e = strict(b, fields); e != nil {
		return e
	}
	if e = integers(b, nums); e != nil {
		return e
	}
	switch op {
	case "update_order":
		b["order_id"] = parts[2]
	case "refund_request":
		b["amount"] = b["amount_cents"]
		b["idem"] = b["idempotency_key"]
	case "approve_refund":
		b["rid"] = parts[1]
	case "create_ticket":
		b["conv"] = b["conv_id"]
		b["idem"] = b["idempotency_key"]
	case "update_ticket":
		b["tid"] = parts[1]
	}
	if op == "create_order" {
		v, e := a.Store.Run(r.Context(), p, op, b)
		if e != nil {
			return e
		}
		jsonOut(w, 201, v)
		return nil
	}
	return a.run(w, r, p, op, b)
}
