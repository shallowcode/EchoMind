package store

import (
	"context"
	"errors"
	"path/filepath"
	"sync"
	"sync/atomic"
	"testing"
)

var ctx = context.Background()
var customer = Principal{"acme", "alice", []string{"customer"}}
var admin = Principal{"acme", "admin", []string{"admin"}}
var staff = Principal{"acme", "operator", []string{"staff"}}

func setup(t *testing.T) *Store {
	t.Helper()
	s, e := Open(filepath.Join(t.TempDir(), "business.sqlite3"))
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(func() { s.Close() })
	run(t, s, admin, "create_order", Data{"order_id": "ORD1001", "customer": "alice", "product": "棉袜", "total_cents": 5000, "quantity": 1, "status": "paid"})
	return s
}
func run(t *testing.T, s *Store, p Principal, op string, args Data) any {
	t.Helper()
	v, e := s.Run(ctx, p, op, args)
	if e != nil {
		t.Fatalf("%s: %v", op, e)
	}
	return v
}
func fails(t *testing.T, s *Store, p Principal, op string, args Data, status int) {
	t.Helper()
	_, e := s.Run(ctx, p, op, args)
	var typed *Error
	if !errors.As(e, &typed) || typed.Status != status {
		t.Fatalf("%s: want %d got %v", op, status, e)
	}
}
func request(amount int, idem string) Data {
	return Data{"order_id": "ORD1001", "amount": amount, "reason": "退货", "idem": idem}
}

func TestRefundReservationApprovalAndIdempotentSettlement(t *testing.T) {
	s := setup(t)
	r := run(t, s, customer, "refund_request", request(3000, "key")).(Data)
	rid := Text(r, "id")
	if Text(run(t, s, customer, "refund_request", request(3000, "key")).(Data), "id") != rid {
		t.Fatal("duplicate refund")
	}
	fails(t, s, customer, "refund_request", request(3100, "key"), 409)
	fails(t, s, customer, "refund_request", request(3000, "second"), 409)
	fails(t, s, admin, "settle_refund", Data{"rid": rid}, 409)
	fails(t, s, Principal{"acme", "alice", []string{"finance"}}, "approve_refund", Data{"rid": rid, "approve": true}, 403)
	run(t, s, admin, "approve_refund", Data{"rid": rid, "approve": true})
	run(t, s, admin, "settle_refund", Data{"rid": rid})
	run(t, s, admin, "settle_refund", Data{"rid": rid})
	o := run(t, s, customer, "order", Data{"order_id": "ORD1001"}).(Data)
	if Int(o, "refunded") != 3000 || Int(o, "refundable") != 2000 {
		t.Fatal(o)
	}
}
func TestConcurrentFullRefundCannotOverspend(t *testing.T) {
	s := setup(t)
	var success atomic.Int32
	var wg sync.WaitGroup
	for i := 0; i < 12; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_, e := s.Run(ctx, customer, "refund_request", Data{"order_id": "ORD1001", "full": true, "reason": "退款", "idem": ID("")})
			if e == nil {
				success.Add(1)
			}
		}()
	}
	wg.Wait()
	if success.Load() != 1 {
		t.Fatalf("successful reservations = %d", success.Load())
	}
	o := run(t, s, customer, "order", Data{"order_id": "ORD1001"}).(Data)
	if Int(o, "reserved") != 5000 || Int(o, "refundable") != 0 {
		t.Fatal(o)
	}
}
func TestTenantOwnershipAndExplicitDemoRole(t *testing.T) {
	s := setup(t)
	for _, p := range []Principal{{"other", "alice", []string{"admin"}}, {"acme", "bob", []string{"customer"}}} {
		fails(t, s, p, "order", Data{"order_id": "ORD1001"}, 403)
		if len(run(t, s, p, "order_list", Data{}).(Data)["items"].([]Data)) != 0 {
			t.Fatal("order leaked")
		}
	}
	if (Principal{"demo", "admin", []string{"admin"}}).Demo() {
		t.Fatal("admin accidentally receives demo-customer semantics")
	}
}
func TestOrderOptimisticLockDeleteRestoreAndRefundGuard(t *testing.T) {
	s := setup(t)
	run(t, s, admin, "update_order", Data{"order_id": "ORD1001", "status": "shipped", "version": 0})
	fails(t, s, admin, "update_order", Data{"order_id": "ORD1001", "status": "completed", "version": 0}, 409)
	r := run(t, s, customer, "refund_request", request(100, "hold")).(Data)
	fails(t, s, admin, "delete_order", Data{"order_id": "ORD1001", "version": 1}, 409)
	run(t, s, admin, "approve_refund", Data{"rid": r["id"], "approve": false})
	run(t, s, admin, "delete_order", Data{"order_id": "ORD1001", "version": 1})
	fails(t, s, customer, "order", Data{"order_id": "ORD1001"}, 403)
	run(t, s, admin, "restore_order", Data{"order_id": "ORD1001"})
	if Int(run(t, s, customer, "order", Data{"order_id": "ORD1001"}).(Data), "version") != 2 {
		t.Fatal("version not advanced")
	}
}
func TestHumanTakeoverLeaseMessagesAndTickets(t *testing.T) {
	s := setup(t)
	run(t, s, customer, "acquire_conversation", Data{"conv": "conversation", "owner": "lease", "ttl": 120})
	fails(t, s, staff, "takeover", Data{"conv": "conversation", "version": 0}, 409)
	ticket := run(t, s, customer, "create_ticket", Data{"conv": "conversation", "summary": "需要人工", "idem": "ticket-key"}).(Data)
	run(t, s, customer, "release", Data{"conv": "conversation", "owner": "lease"})
	run(t, s, staff, "takeover", Data{"conv": "conversation", "version": 0})
	fails(t, s, customer, "acquire_conversation", Data{"conv": "conversation", "owner": "next", "ttl": 120}, 409)
	msg := Data{"conv": "conversation", "message": "我来帮您处理", "request_id": "staff-msg-1"}
	run(t, s, staff, "staff_reply", msg)
	run(t, s, staff, "staff_reply", msg)
	fails(t, s, Principal{"acme", "other", []string{"staff"}}, "staff_reply", msg, 403)
	detail := run(t, s, customer, "conversation", Data{"conv": "conversation"}).(Data)
	if len(detail["messages"].([]Data)) != 1 {
		t.Fatal("duplicate message")
	}
	run(t, s, staff, "update_ticket", Data{"tid": ticket["id"], "status": "assigned", "version": 0})
	run(t, s, staff, "update_ticket", Data{"tid": ticket["id"], "status": "resolved", "version": 1, "resolution": "已处理"})
	if len(run(t, s, customer, "history", Data{"conv": "conversation"}).([]Data)) != 2 {
		t.Fatal("resolution missing")
	}
	run(t, s, staff, "resume_ai", Data{"conv": "conversation", "version": 1})
	run(t, s, customer, "acquire_conversation", Data{"conv": "conversation", "owner": "next", "ttl": 120})
}
func TestTransactionRollbackOnAuditFailure(t *testing.T) {
	s := setup(t)
	_, e := s.DB.Exec("CREATE TRIGGER reject_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT,'audit unavailable'); END")
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.Run(ctx, customer, "refund_request", request(200, "rollback")); e == nil {
		t.Fatal("expected rollback")
	}
	if Int(run(t, s, customer, "order", Data{"order_id": "ORD1001"}).(Data), "reserved") != 0 {
		t.Fatal("orphan reservation")
	}
}
func TestCredentialsDisableRevocationAndTenantScope(t *testing.T) {
	s := setup(t)
	_, e := s.CreateUser(ctx, admin, Data{"user": "staff", "name": "客服", "password": "test-password-123", "roles": []any{"staff"}})
	if e != nil {
		t.Fatal(e)
	}
	p, e := s.Login(ctx, "acme", "staff", "test-password-123")
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.Login(ctx, "other", "staff", "test-password-123"); e == nil {
		t.Fatal("cross-tenant login")
	}
	token := run(t, s, p, "issue_token", Data{}).(string)
	if _, e = s.Authenticate(ctx, token); e != nil {
		t.Fatal(e)
	}
	if _, e = s.SetUserDisabled(ctx, admin, "staff", true); e != nil {
		t.Fatal(e)
	}
	if _, e = s.Authenticate(ctx, token); e == nil {
		t.Fatal("disabled token valid")
	}
	if _, e = s.SetUserDisabled(ctx, admin, "admin", true); e == nil {
		t.Fatal("self disable")
	}
}
func TestEventsOnlyReachOwningCustomer(t *testing.T) {
	s := setup(t)
	run(t, s, customer, "acquire_conversation", Data{"conv": "conversation", "owner": "lease", "ttl": 10})
	run(t, s, customer, "create_ticket", Data{"conv": "conversation", "summary": "人工", "idem": "ticket-key"})
	if len(run(t, s, customer, "events", Data{}).([]Data)) == 0 {
		t.Fatal("missing event")
	}
	if len(run(t, s, Principal{"acme", "bob", []string{"customer"}}, "events", Data{}).([]Data)) != 0 {
		t.Fatal("event leaked")
	}
	if len(run(t, s, Principal{"other", "admin", []string{"admin"}}, "events", Data{}).([]Data)) != 0 {
		t.Fatal("tenant event leaked")
	}
}

func TestLegacyTicketsEnterQueueOnlyOnce(t *testing.T) {
	path := filepath.Join(t.TempDir(), "legacy.sqlite3")
	s, e := Open(path)
	if e != nil {
		t.Fatal(e)
	}
	_, e = s.DB.Exec("DELETE FROM schema_migrations WHERE version=2; INSERT INTO conversations(tenant,id,user,state) VALUES('acme','old-conv','alice','{}'); INSERT INTO tickets(id,tenant,user,conv,summary,status,idem) VALUES('old-ticket','acme','alice','old-conv','help','open','old-key')")
	if e != nil {
		t.Fatal(e)
	}
	s.Close()
	s, e = Open(path)
	if e != nil {
		t.Fatal(e)
	}
	if Text(run(t, s, customer, "mode", Data{"conv": "old-conv"}).(Data), "mode") != "waiting" {
		t.Fatal("legacy queue missing")
	}
	run(t, s, staff, "resume_ai", Data{"conv": "old-conv", "version": 0})
	s.Close()
	s, e = Open(path)
	if e != nil {
		t.Fatal(e)
	}
	defer s.Close()
	if Text(run(t, s, customer, "mode", Data{"conv": "old-conv"}).(Data), "mode") != "ai" {
		t.Fatal("migration changed an existing mode")
	}
}
