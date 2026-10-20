package llm

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

type fake struct {
	name   string
	calls  atomic.Int32
	script func(ctx context.Context, call int, emit func(string) error) (Usage, error)
}

func (f *fake) Name() string  { return f.name }
func (f *fake) Model() string { return f.name + "-model" }
func (f *fake) Stream(ctx context.Context, _ Request, emit func(string) error) (Usage, error) {
	return f.script(ctx, int(f.calls.Add(1)), emit)
}
func ok(text string) func(context.Context, int, func(string) error) (Usage, error) {
	return func(_ context.Context, _ int, emit func(string) error) (Usage, error) {
		return Usage{PromptTokens: 10, CompletionTokens: 5}, emit(text)
	}
}
func failing(status int) func(context.Context, int, func(string) error) (Usage, error) {
	return func(context.Context, int, func(string) error) (Usage, error) {
		return Usage{}, &StatusError{Status: status}
	}
}
func router(ps ...Provider) *Router {
	r := NewRouter(ps...)
	r.Backoff = time.Millisecond
	return r
}
func collect(t *testing.T, r *Router) (Result, string, error) {
	t.Helper()
	var b strings.Builder
	res, err := r.Stream(context.Background(), Request{}, func(s string) error { b.WriteString(s); return nil })
	return res, b.String(), err
}

func TestOpenAIStreamParsesDeltasAndUsage(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/chat/completions" || r.Header.Get("Authorization") != "Bearer secret" {
			t.Errorf("unexpected request %s %s", r.URL.Path, r.Header.Get("Authorization"))
		}
		for _, part := range []string{"您好", "，已为您", "查询"} {
			fmt.Fprintf(w, "data: {\"choices\":[{\"delta\":{\"content\":%q}}]}\n\n", part)
		}
		fmt.Fprint(w, "data: {\"choices\":[],\"usage\":{\"prompt_tokens\":21,\"completion_tokens\":7}}\n\ndata: [DONE]\n\n")
	}))
	defer server.Close()
	deltas := []string{}
	usage, err := NewOpenAI("glm", server.URL+"/v1/", "secret", "glm-4.5-air").Stream(context.Background(), Request{Messages: []Message{{"user", "hi"}}}, func(s string) error { deltas = append(deltas, s); return nil })
	if err != nil || strings.Join(deltas, "") != "您好，已为您查询" || len(deltas) != 3 || usage.PromptTokens != 21 || usage.CompletionTokens != 7 || usage.Estimated {
		t.Fatalf("got %v %v %+v", err, deltas, usage)
	}
}
func TestOpenAIStreamEstimatesMissingUsageAndRejectsTruncation(t *testing.T) {
	done := true
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "data: {\"choices\":[{\"delta\":{\"content\":\"退款处理中\"}}]}\n\n")
		if done {
			fmt.Fprint(w, "data: [DONE]\n\n")
		}
	}))
	defer server.Close()
	p := NewOpenAI("x", server.URL, "", "m")
	usage, err := p.Stream(context.Background(), Request{Messages: []Message{{"user", "进度"}}}, func(string) error { return nil })
	if err != nil || !usage.Estimated || usage.CompletionTokens != 5 {
		t.Fatalf("estimate: %v %+v", err, usage)
	}
	done = false
	if _, err = p.Stream(context.Background(), Request{}, func(string) error { return nil }); !errors.Is(err, ErrBadStream) || !Retryable(err) {
		t.Fatalf("truncated stream must be a retryable error, got %v", err)
	}
}
func TestRouterRetriesThenFailsOver(t *testing.T) {
	primary, backup := &fake{name: "primary", script: failing(503)}, &fake{name: "backup", script: ok("答复")}
	res, text, err := collect(t, router(primary, backup))
	if err != nil || text != "答复" || res.Provider != "backup" || res.Attempts != 3 || primary.calls.Load() != 2 {
		t.Fatalf("got %v %q %+v primary=%d", err, text, res, primary.calls.Load())
	}
}
func TestRouterDoesNotRetryClientErrorsOnSameProvider(t *testing.T) {
	primary, backup := &fake{name: "primary", script: failing(401)}, &fake{name: "backup", script: ok("ok")}
	if res, _, err := collect(t, router(primary, backup)); err != nil || primary.calls.Load() != 1 || res.Attempts != 2 {
		t.Fatalf("401 should fail over without retry: %v primary=%d", err, primary.calls.Load())
	}
}
func TestRouterCircuitBreakerShortCircuitsUnhealthyProvider(t *testing.T) {
	primary, backup := &fake{name: "primary", script: failing(500)}, &fake{name: "backup", script: ok("ok")}
	r := router(primary, backup)
	r.Retries = 0
	for range 3 {
		if _, _, err := collect(t, r); err != nil {
			t.Fatal(err)
		}
	}
	if _, _, err := collect(t, r); err != nil || primary.calls.Load() != 3 || r.Status()[0]["breaker"] != "open" {
		t.Fatalf("breaker should skip primary: calls=%d status=%v err=%v", primary.calls.Load(), r.Status(), err)
	}
}
func TestRouterFirstTokenTimeoutFailsOver(t *testing.T) {
	slow := &fake{name: "slow", script: func(ctx context.Context, _ int, emit func(string) error) (Usage, error) {
		<-ctx.Done()
		return Usage{}, ctx.Err()
	}}
	r := router(slow, &fake{name: "fast", script: ok("fast")})
	r.Retries, r.FirstTokenTimeout = 0, 20*time.Millisecond
	if res, _, err := collect(t, r); err != nil || res.Provider != "fast" {
		t.Fatalf("first-token timeout should fail over: %v %+v", err, res)
	}
}
func TestRouterNeverFailsOverAfterPartialOutput(t *testing.T) {
	broken := &fake{name: "broken", script: func(_ context.Context, _ int, emit func(string) error) (Usage, error) {
		_ = emit("部分")
		return Usage{}, &StatusError{Status: 502}
	}}
	backup := &fake{name: "backup", script: ok("完整")}
	res, text, err := collect(t, router(broken, backup))
	if !errors.Is(err, ErrInterrupted) || text != "部分" || res.Text != "部分" || backup.calls.Load() != 0 {
		t.Fatalf("got %v %q backup=%d", err, text, backup.calls.Load())
	}
}
func TestRouterStopsWhenClientDisconnects(t *testing.T) {
	p := &fake{name: "p", script: ok("x")}
	r := router(p)
	gone := errors.New("client gone")
	if _, err := r.Stream(context.Background(), Request{}, func(string) error { return gone }); !errors.Is(err, gone) || p.calls.Load() != 1 || r.Status()[0]["breaker"] != "closed" {
		t.Fatalf("disconnect must not retry or trip the breaker: %v", err)
	}
}
func TestBreakerHalfOpenAllowsSingleProbe(t *testing.T) {
	now := time.Now()
	b := NewBreaker(1, time.Minute)
	b.now = func() time.Time { return now }
	b.Failure()
	if b.Allow() || b.State() != "open" {
		t.Fatal("breaker should be open")
	}
	now = now.Add(2 * time.Minute)
	if !b.Allow() || b.Allow() {
		t.Fatal("exactly one half-open probe expected")
	}
	b.Failure()
	if b.State() != "open" {
		t.Fatal("failed probe reopens the breaker")
	}
	now = now.Add(2 * time.Minute)
	b.Allow()
	b.Success()
	if b.State() != "closed" || !b.Allow() {
		t.Fatal("successful probe closes the breaker")
	}
}
func TestCacheEvictsLeastRecentlyUsedAndExpires(t *testing.T) {
	now := time.Now()
	c := NewCache(2, time.Minute)
	c.now = func() time.Time { return now }
	c.Put("a", Result{Text: "a"})
	c.Put("b", Result{Text: "b"})
	c.Get("a")
	c.Put("c", Result{Text: "c"})
	if _, ok := c.Get("b"); ok {
		t.Fatal("b should be evicted")
	}
	if v, ok := c.Get("a"); !ok || v.Text != "a" {
		t.Fatal("a should survive")
	}
	now = now.Add(2 * time.Minute)
	if _, ok := c.Get("a"); ok || c.Len() != 1 {
		t.Fatal("expired entries must not be served")
	}
}
func TestMetricsExposition(t *testing.T) {
	r := router(&fake{name: "p", script: ok("x")})
	collect(t, r)
	var b strings.Builder
	r.WriteMetrics(&b)
	for _, want := range []string{`supportflow_llm_requests_total{provider="p",outcome="success"} 1`, `supportflow_llm_tokens_total{provider="p",kind="prompt"} 10`, `supportflow_llm_ttft_seconds_count{provider="p"} 1`, `supportflow_llm_breaker_open{provider="p"} 0`} {
		if !strings.Contains(b.String(), want) {
			t.Fatalf("missing %s in\n%s", want, b.String())
		}
	}
}
