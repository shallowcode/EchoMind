package app

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"strings"
	"supportflow/backend/internal/store"
	"sync/atomic"
	"testing"
)

func testServer(t *testing.T, demo bool) (*Server, *atomic.Int32) {
	t.Helper()
	count := &atomic.Int32{}
	worker := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/health" {
			jsonOut(w, 200, store.Data{"status": "alive"})
			return
		}
		count.Add(1)
		if r.Header.Get("X-SupportFlow-Service-Key") != strings.Repeat("k", 40) {
			t.Error("missing service authentication")
		}
		jsonOut(w, 200, store.Data{"proxied": true})
	}))
	t.Cleanup(worker.Close)
	s, e := store.Open(filepath.Join(t.TempDir(), "store.sqlite3"))
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(func() { s.Close() })
	a, e := New(s, Config{AIURL: worker.URL, ServiceKey: strings.Repeat("k", 40), Demo: demo, Frontend: t.TempDir()})
	if e != nil {
		t.Fatal(e)
	}
	return a, count
}
func req(a *Server, method, path, token, body string, headers map[string]string) *httptest.ResponseRecorder {
	r := httptest.NewRequest(method, "http://127.0.0.1:8002"+path, strings.NewReader(body))
	r.RemoteAddr = "127.0.0.1:50000"
	if token != "" {
		r.Header.Set("Authorization", "Bearer "+token)
	}
	for k, v := range headers {
		r.Header.Set(k, v)
	}
	w := httptest.NewRecorder()
	a.ServeHTTP(w, r)
	return w
}
func token(t *testing.T, a *Server, p store.Principal) string {
	t.Helper()
	v, e := a.Store.Run(context.Background(), p, "issue_token", store.Data{})
	if e != nil {
		t.Fatal(e)
	}
	return v.(string)
}
func requireStatus(t *testing.T, r *httptest.ResponseRecorder, status int) {
	t.Helper()
	if r.Code != status {
		t.Fatalf("want %d got %d: %s", status, r.Code, r.Body.String())
	}
}
func TestLocalDemoBoundary(t *testing.T) {
	a, _ := testServer(t, true)
	requireStatus(t, req(a, "POST", "/auth/demo-operator", "", "", nil), 403)
	requireStatus(t, req(a, "POST", "/auth/demo-operator", "", "", map[string]string{"X-SupportFlow-Demo": "operator", "Origin": "https://evil.example"}), 403)
	requireStatus(t, req(a, "POST", "/auth/demo-operator", "", "", map[string]string{"X-SupportFlow-Demo": "operator"}), 200)
	a.Config.Demo = false
	requireStatus(t, req(a, "POST", "/auth/demo-operator", "", "", map[string]string{"X-SupportFlow-Demo": "operator"}), 403)
}
func TestRPCRequiresSharedKeyAndOperationAllowlist(t *testing.T) {
	a, _ := testServer(t, true)
	body := `{"operation":"authenticate","arguments":{"token":"invalid"}}`
	requireStatus(t, req(a, "POST", "/internal/store", "", body, nil), 403)
	requireStatus(t, req(a, "POST", "/internal/store", "", body, map[string]string{"X-SupportFlow-Service-Key": a.Config.ServiceKey}), 401)
	body = `{"operation":"settle_refund","principal":{"tenant":"demo","user":"admin","roles":["admin"]}}`
	requireStatus(t, req(a, "POST", "/internal/store", "", body, map[string]string{"X-SupportFlow-Service-Key": a.Config.ServiceKey}), 403)
}
func TestHTTPStrictMoneyAndRoleChecks(t *testing.T) {
	a, _ := testServer(t, true)
	customer := token(t, a, store.Principal{Tenant: "demo", User: "alice", Roles: []string{"customer"}})
	admin := token(t, a, store.Principal{Tenant: "demo", User: "admin", Roles: []string{"admin"}})
	base := `{"order_id":"ORD1001","customer":"alice","product":"棉袜","quantity":1,"total_cents":5000,"status":"paid"}`
	requireStatus(t, req(a, "POST", "/merchant/orders", customer, base, nil), 403)
	for _, body := range []string{strings.Replace(base, "5000", "1.2", 1), strings.Replace(base, "5000", "true", 1), strings.Replace(base, `"product"`, `"unknown"`, 1), base + base} {
		requireStatus(t, req(a, "POST", "/merchant/orders", admin, body, nil), 422)
	}
	requireStatus(t, req(a, "POST", "/merchant/orders", admin, base, nil), 201)
	requireStatus(t, req(a, "GET", "/stats", customer, "", nil), 403)
	requireStatus(t, req(a, "GET", "/merchant/orders", "", "", nil), 401)
}
func TestHumanMessageBypassesAIAndReplaysAfterResume(t *testing.T) {
	a, calls := testServer(t, true)
	p := store.Principal{Tenant: "demo", User: "alice", Roles: []string{"customer"}}
	staff := store.Principal{Tenant: "demo", User: "operator", Roles: []string{"staff"}}
	c := token(t, a, p)
	op := token(t, a, staff)
	for _, step := range []struct {
		op   string
		args store.Data
	}{{"acquire_conversation", store.Data{"conv": "conv1", "owner": "lease", "ttl": 1}}, {"release", store.Data{"conv": "conv1", "owner": "lease"}}} {
		if _, e := a.Store.Run(context.Background(), p, step.op, step.args); e != nil {
			t.Fatal(e)
		}
	}
	requireStatus(t, req(a, "POST", "/conversations/conv1/takeover", op, `{"version":0}`, nil), 200)
	body := `{"message":"你好 <>& 😀","conv_id":"conv1","request_id":"human-001"}`
	requireStatus(t, req(a, "POST", "/chat", c, body, nil), 200)
	requireStatus(t, req(a, "POST", "/chat", c, body, nil), 200)
	requireStatus(t, req(a, "POST", "/conversations/conv1/resume-ai", op, `{"version":1}`, nil), 200)
	requireStatus(t, req(a, "POST", "/chat", c, body, nil), 200)
	if calls.Load() != 0 {
		t.Fatal("AI called during human/replayed turn")
	}
	requireStatus(t, req(a, "POST", "/chat", c, strings.Replace(body, "你好", "变更", 1), nil), 409)
	detail := req(a, "GET", "/conversations/conv1", c, "", nil)
	var data store.Data
	_ = json.Unmarshal(detail.Body.Bytes(), &data)
	if len(data["messages"].([]any)) != 1 {
		t.Fatal("duplicate human message")
	}
	requireStatus(t, req(a, "POST", "/chat", c, strings.Replace(body, "human-001", "human-002", 1), nil), 200)
	if calls.Load() != 1 {
		t.Fatal("AI did not resume")
	}
}
func TestReadyReportsWorkerFailure(t *testing.T) {
	a, _ := testServer(t, true)
	requireStatus(t, req(a, "GET", "/ready", "", "", nil), 200)
	bad := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(500)
		io.WriteString(w, `{"status":"alive"}`)
	}))
	defer bad.Close()
	a.Config.AIURL = bad.URL
	requireStatus(t, req(a, "GET", "/ready", "", "", nil), 503)
	requireStatus(t, req(a, "GET", "/health", "", "", nil), 200)
}
