package app

import (
	"context"
	"encoding/json"
	"strings"
	"testing"

	"supportflow/backend/internal/llm"
	"supportflow/backend/internal/store"
)

var operator = store.Principal{Tenant: "demo", User: "operator", Roles: []string{"staff", "admin"}}

func seedConversation(t *testing.T, a *Server) {
	t.Helper()
	for _, q := range []string{
		"INSERT INTO conversations(tenant,id,user,state) VALUES('demo','c1','alice','idle')",
		"INSERT INTO messages(tenant,conv,role,content,created) VALUES('demo','c1','user','我的退款到哪一步了？',1)",
	} {
		if _, err := a.Store.DB.Exec(q); err != nil {
			t.Fatal(err)
		}
	}
}
func events(body string) map[string][]string {
	out := map[string][]string{}
	for _, block := range strings.Split(strings.TrimSpace(body), "\n\n") {
		var name, data string
		for _, line := range strings.Split(block, "\n") {
			if v, ok := strings.CutPrefix(line, "event: "); ok {
				name = v
			}
			if v, ok := strings.CutPrefix(line, "data: "); ok {
				data = v
			}
		}
		out[name] = append(out[name], data)
	}
	return out
}
func TestCopilotSuggestStreamsServerSentEvents(t *testing.T) {
	a, _ := testServer(t, false)
	a.Config.Router = llm.NewRouter(llm.Fixture{})
	a.Copilot.Router = a.Config.Router
	seedConversation(t, a)
	staff := token(t, a, operator)
	w := req(a, "POST", "/copilot/conversations/c1/suggest", staff, "", nil)
	requireStatus(t, w, 200)
	if w.Header().Get("Content-Type") != "text/event-stream" {
		t.Fatal("suggest must stream SSE")
	}
	got := events(w.Body.String())
	text := ""
	for _, raw := range got["delta"] {
		var d struct{ Text string }
		_ = json.Unmarshal([]byte(raw), &d)
		text += d.Text
	}
	if len(got["delta"]) < 2 || !strings.HasPrefix(text, "您好") || len(got["done"]) != 1 || !strings.Contains(got["done"][0], `"provider":"fixture"`) {
		t.Fatalf("unexpected stream: %s", w.Body.String())
	}
	cached := events(req(a, "POST", "/copilot/conversations/c1/suggest", staff, "", nil).Body.String())
	if !strings.Contains(cached["done"][0], `"cached":true`) {
		t.Fatal("repeat suggestion should be a cache replay")
	}
	w = req(a, "POST", "/copilot/conversations/c1/summary", staff, "", nil)
	requireStatus(t, w, 200)
	if !strings.Contains(w.Body.String(), `"sentiment":"neutral"`) {
		t.Fatal(w.Body.String())
	}
	customer := token(t, a, store.Principal{Tenant: "demo", User: "alice", Roles: []string{"customer"}})
	if w = req(a, "POST", "/copilot/conversations/c1/suggest", customer, "", nil); w.Code != 403 || w.Header().Get("Content-Type") == "text/event-stream" {
		t.Fatal("errors before the first event must be plain JSON")
	}
	usage := req(a, "GET", "/usage?days=1", staff, "", nil)
	requireStatus(t, usage, 200)
	var report struct {
		Total  map[string]any
		Budget map[string]any
	}
	_ = json.Unmarshal(usage.Body.Bytes(), &report)
	if report.Total["requests"].(float64) != 3 || report.Total["cached"].(float64) != 1 {
		t.Fatalf("usage report: %s", usage.Body.String())
	}
	metrics := req(a, "GET", "/metrics", staff, "", nil).Body.String()
	if !strings.Contains(metrics, `supportflow_llm_cache_lookups_total{result="hit"} 1`) || !strings.Contains(metrics, "supportflow_ingest_jobs") {
		t.Fatal(metrics)
	}
}
func TestCopilotUnconfiguredGatewayReturns503(t *testing.T) {
	a, _ := testServer(t, false)
	seedConversation(t, a)
	w := req(a, "POST", "/copilot/conversations/c1/suggest", token(t, a, operator), "", nil)
	requireStatus(t, w, 503)
	if !strings.Contains(w.Body.String(), "llm_unconfigured") {
		t.Fatal(w.Body.String())
	}
}
func TestKnowledgeJobIsIndexedThroughAIWorker(t *testing.T) {
	a, count := testServer(t, false)
	admin := token(t, a, operator)
	body := `{"doc_id":"returns","title":"退货政策","content":"七天无理由退货。\n\n运费由商家承担。"}`
	w := req(a, "POST", "/knowledge/jobs", admin, body, nil)
	requireStatus(t, w, 202)
	requireStatus(t, req(a, "POST", "/knowledge/jobs", admin, body, nil), 200)
	var created struct{ Job map[string]any }
	_ = json.Unmarshal(w.Body.Bytes(), &created)
	id := created.Job["id"].(string)
	job, err := a.Store.ClaimIngest(context.Background(), a.Ingest.Lease)
	if err != nil || job == nil {
		t.Fatal("job should be claimable", err)
	}
	a.Ingest.Process(context.Background(), job)
	if count.Load() != 1 {
		t.Fatalf("worker should index once, got %d calls", count.Load())
	}
	got := req(a, "GET", "/knowledge/jobs/"+id, admin, "", nil)
	if !strings.Contains(got.Body.String(), `"status":"succeeded"`) {
		t.Fatal(got.Body.String())
	}
	var revoked int
	_ = a.Store.DB.QueryRow("SELECT COUNT(*) FROM tokens WHERE revoked=1").Scan(&revoked)
	if revoked != 1 {
		t.Fatal("the worker's short-lived token must be revoked after use")
	}
	staffOnly := token(t, a, store.Principal{Tenant: "demo", User: "s", Roles: []string{"staff"}})
	requireStatus(t, req(a, "POST", "/knowledge/jobs", staffOnly, body, nil), 403)
}
