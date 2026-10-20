// Package app is the public Go API and the authenticated boundary to the AI worker.
package app

import (
	"bytes"
	"context"
	"crypto/subtle"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"supportflow/backend/internal/copilot"
	"supportflow/backend/internal/ingest"
	"supportflow/backend/internal/llm"
	"supportflow/backend/internal/quota"
	"supportflow/backend/internal/store"
)

type Config struct {
	AIURL, ServiceKey, Frontend string
	Demo                        bool
	// Router is the Go model gateway used by Copilot; nil disables AI-assist endpoints.
	Router      *llm.Router
	RPM         int
	DailyTokens int64
}
type Server struct {
	Store     *store.Store
	Config    Config
	Copilot   *copilot.Service
	Ingest    *ingest.Queue
	proxy     *httputil.ReverseProxy
	requests  atomic.Int64
	failures  atomic.Int64
	mu        sync.Mutex
	logins    map[string]attempt
	chatSlots chan struct{}
	aiClient  *http.Client
}
type attempt struct {
	n     int
	until time.Time
}

func New(s *store.Store, c Config) (*Server, error) {
	u, err := url.Parse(c.AIURL)
	if err != nil || u.Scheme != "http" || u.Host == "" {
		return nil, fmt.Errorf("invalid AI worker URL")
	}
	if len(c.ServiceKey) < 32 {
		return nil, fmt.Errorf("service key must contain at least 32 characters")
	}
	a := &Server{Store: s, Config: c, logins: map[string]attempt{}, chatSlots: make(chan struct{}, 8)}
	p := httputil.NewSingleHostReverseProxy(u)
	base := p.Director
	p.Director = func(r *http.Request) {
		base(r)
		r.Header.Set("X-SupportFlow-Service-Key", c.ServiceKey)
		r.Header.Del("X-SupportFlow-Principal")
	}
	p.Transport = &http.Transport{Proxy: http.ProxyFromEnvironment, ResponseHeaderTimeout: 240 * time.Second, IdleConnTimeout: 60 * time.Second, MaxIdleConnsPerHost: 16}
	a.aiClient = &http.Client{Transport: p.Transport}
	p.ErrorHandler = func(w http.ResponseWriter, r *http.Request, e error) {
		a.failures.Add(1)
		writeError(w, &store.Error{Status: 503, Code: "ai_unavailable", Message: "AI 服务暂不可用，可重试或转人工"})
	}
	a.proxy = p
	if c.Router == nil {
		c.Router = llm.NewRouter()
		a.Config.Router = c.Router
	}
	a.Copilot = copilot.New(s, c.Router, quota.New(c.RPM, c.DailyTokens, s.TokensSince))
	a.Ingest = ingest.New(s, a.sendKnowledge)
	return a, nil
}
func jsonOut(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
func writeError(w http.ResponseWriter, err error) {
	var e *store.Error
	if errors.As(err, &e) {
		jsonOut(w, e.Status, store.Data{"detail": e.Message, "code": e.Code})
		return
	}
	slog.Error("request failed", "error", err)
	jsonOut(w, 500, store.Data{"detail": "服务暂不可用", "code": "internal_error"})
}
func readBody(w http.ResponseWriter, r *http.Request) (store.Data, error) {
	d := json.NewDecoder(http.MaxBytesReader(w, r.Body, 4<<20))
	d.UseNumber()
	var a store.Data
	if err := d.Decode(&a); err != nil || a == nil {
		return nil, store.Invalid("JSON 请求格式错误")
	}
	if d.Decode(new(any)) != io.EOF {
		return nil, store.Invalid("只允许一个 JSON 对象")
	}
	return a, nil
}
func bearer(r *http.Request) string {
	return strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer ")
}
func (a *Server) principal(r *http.Request) (store.Principal, error) {
	return a.Store.Authenticate(r.Context(), bearer(r))
}
func (a *Server) local(r *http.Request, audience string) bool {
	if !a.Config.Demo {
		return false
	}
	host, _, _ := net.SplitHostPort(r.RemoteAddr)
	ip := net.ParseIP(host)
	if ip == nil || !ip.IsLoopback() {
		return false
	}
	h := r.URL.Hostname()
	if h == "" {
		h, _, _ = net.SplitHostPort(r.Host)
		if h == "" {
			h = r.Host
		}
	}
	if h != "127.0.0.1" && h != "localhost" && h != "::1" {
		return false
	}
	origin := r.Header.Get("Origin")
	return r.Header.Get("X-SupportFlow-Demo") == audience && r.Header.Get("Sec-Fetch-Site") != "cross-site" && (origin == "" || origin == "http://"+r.Host)
}
func (a *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	a.requests.Add(1)
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.Header().Set("Referrer-Policy", "same-origin")
	w.Header().Set("X-Request-ID", store.ID("req_"))
	defer func() {
		if v := recover(); v != nil {
			slog.Error("panic", "value", v)
			jsonOut(w, 500, store.Data{"detail": "服务内部错误"})
		}
		slog.Info("http", "method", r.Method, "path", r.URL.Path, "duration_ms", time.Since(start).Milliseconds())
	}()
	if err := a.route(w, r); err != nil {
		a.failures.Add(1)
		writeError(w, err)
	}
}
func (a *Server) route(w http.ResponseWriter, r *http.Request) error {
	path := r.URL.Path
	if path == "/internal/store" {
		return a.internal(w, r)
	}
	if path == "/health" || path == "/ready" {
		if r.Method != "GET" {
			return &store.Error{Status: 405, Code: "method", Message: "不支持此方法"}
		}
		ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
		defer cancel()
		req, _ := http.NewRequestWithContext(ctx, "GET", a.Config.AIURL+"/health", nil)
		resp, err := http.DefaultClient.Do(req)
		v := store.Data{"status": "alive", "business_mode": "sandbox", "demo": a.Config.Demo, "ai_status": "unavailable", "llm_gateway": a.Config.Router.Status(), "runtime": store.Data{"application": "supportFlow", "version": "3.1.0", "backend": "Go", "ai": "Python"}}
		if err == nil {
			defer resp.Body.Close()
			var worker store.Data
			if json.NewDecoder(resp.Body).Decode(&worker) == nil && resp.StatusCode == 200 && store.Text(worker, "status") == "alive" {
				if info, ok := worker["runtime"].(map[string]any); ok {
					info["backend"] = "Go"
					info["ai"] = "Python"
					info["version"] = "3.1.0"
					v["runtime"] = info
				}
				v["ai_status"] = "ready"
			}
		} else {
			v["ai_status"] = "unavailable"
		}
		if path == "/ready" && (store.Text(v, "ai_status") != "ready" || a.Store.DB.PingContext(ctx) != nil) {
			jsonOut(w, 503, v)
		} else {
			jsonOut(w, 200, v)
		}
		return nil
	}
	if strings.HasPrefix(path, "/assets/") {
		if r.Method != "GET" && r.Method != "HEAD" {
			return &store.Error{Status: 405, Code: "method", Message: "不支持此方法"}
		}
		http.StripPrefix("/assets/", http.FileServer(http.Dir(a.Config.Frontend))).ServeHTTP(w, r)
		return nil
	}
	pages := map[string]string{"/": "index.html", "/admin": "admin.html", "/lab": "lab.html", "/desk": "desk.html", "/login": "login.html"}
	if file, ok := pages[path]; ok {
		w.Header().Set("Cache-Control", "no-cache")
		http.ServeFile(w, r, filepath.Join(a.Config.Frontend, file))
		return nil
	}
	if strings.HasPrefix(path, "/auth/demo-") {
		if r.Method != "POST" {
			return &store.Error{Status: 405, Code: "method", Message: "不支持此方法"}
		}
		audience := strings.TrimPrefix(path, "/auth/demo-")
		if !a.local(r, audience) {
			return &store.Error{Status: 403, Code: "local_demo_only", Message: "本机演示模式未开放"}
		}
		p := store.Principal{Tenant: "demo"}
		switch audience {
		case "customer":
			p.User = "alice"
			p.Roles = []string{"customer", "demo_customer"}
		case "merchant":
			p.User = "merchant"
			p.Roles = []string{"staff", "finance"}
		case "operator":
			p.User = "operator"
			p.Roles = []string{"staff", "admin"}
		default:
			return &store.Error{Status: 404, Code: "not_found", Message: "入口不存在"}
		}
		v, err := a.Store.Run(r.Context(), p, "issue_token", store.Data{"ttl": 3600})
		if err != nil {
			return err
		}
		jsonOut(w, 200, store.Data{"token": v})
		return nil
	}
	if path == "/auth/login" {
		return a.login(w, r)
	}
	p, err := a.principal(r)
	if err != nil {
		return err
	}
	if p.Demo() && !a.Config.Demo {
		return store.Denied()
	}
	if path == "/auth/me" && r.Method == "GET" {
		jsonOut(w, 200, p)
		return nil
	}
	if path == "/auth/logout" && r.Method == "POST" {
		return a.run(w, r, p, "revoke", store.Data{"token": bearer(r)})
	}
	if path == "/users" {
		if r.Method == "GET" {
			v, err := a.Store.Users(r.Context(), p)
			if err != nil {
				return err
			}
			jsonOut(w, 200, v)
			return nil
		}
		if r.Method == "POST" {
			b, err := readBody(w, r)
			if err != nil {
				return err
			}
			v, err := a.Store.CreateUser(r.Context(), p, b)
			if err != nil {
				return err
			}
			jsonOut(w, 201, v)
			return nil
		}
	}
	if strings.HasPrefix(path, "/users/") && r.Method == "PATCH" {
		b, e := readBody(w, r)
		if e != nil {
			return e
		}
		if e = strict(b, "disabled"); e != nil {
			return e
		}
		disabled, ok := b["disabled"].(bool)
		if !ok {
			return store.Invalid("需要 disabled 字段")
		}
		v, e := a.Store.SetUserDisabled(r.Context(), p, strings.TrimPrefix(path, "/users/"), disabled)
		if e != nil {
			return e
		}
		jsonOut(w, 200, v)
		return nil
	}
	if path == "/events" && r.Method == "GET" {
		return a.events(w, r, p)
	}
	if path == "/metrics" && r.Method == "GET" {
		if !p.Has("ops", "staff") {
			return store.Denied()
		}
		w.Header().Set("Content-Type", "text/plain; version=0.0.4")
		fmt.Fprintf(w, "# TYPE supportflow_go_requests_total counter\nsupportflow_go_requests_total %d\n# TYPE supportflow_go_failures_total counter\nsupportflow_go_failures_total %d\n", a.requests.Load(), a.failures.Load())
		a.Config.Router.WriteMetrics(w)
		if depth, err := a.Store.QueueDepth(r.Context()); err == nil {
			fmt.Fprint(w, "# TYPE supportflow_ingest_jobs gauge\n")
			for _, status := range []string{"queued", "running", "succeeded", "failed"} {
				fmt.Fprintf(w, "supportflow_ingest_jobs{status=%q} %d\n", status, depth[status])
			}
		}
		return nil
	}
	if path == "/chat" && r.Method == "POST" {
		return a.chat(w, r, p)
	}
	if strings.HasPrefix(path, "/copilot/") {
		return a.copilot(w, r, p)
	}
	if path == "/usage" && r.Method == "GET" {
		v, err := a.Store.UsageReport(r.Context(), p, int(store.Integer(r.URL.Query().Get("days"), 7)))
		if err != nil {
			return err
		}
		spent, reserved := a.Copilot.Limiter.Snapshot(p.Tenant)
		v["budget"] = store.Data{"daily_tokens": a.Config.DailyTokens, "spent_today": spent, "reserved": reserved, "rpm": a.Config.RPM}
		v["gateway"] = a.Config.Router.Status()
		jsonOut(w, 200, v)
		return nil
	}
	if path == "/knowledge/jobs" || strings.HasPrefix(path, "/knowledge/jobs/") {
		return a.knowledgeJobs(w, r, p)
	}
	if path == "/stats" && r.Method == "GET" {
		return a.run(w, r, p, "stats", store.Data{})
	}
	if path == "/audit" && r.Method == "GET" {
		return a.run(w, r, p, "audit_log", store.Data{})
	}
	if strings.HasPrefix(path, "/conversations") {
		return a.conversations(w, r, p)
	}
	if strings.HasPrefix(path, "/merchant/") || strings.HasPrefix(path, "/orders") || strings.HasPrefix(path, "/refunds") || strings.HasPrefix(path, "/tickets") {
		return a.business(w, r, p)
	}
	if path == "/intents" || strings.HasPrefix(path, "/mcp/") || strings.HasPrefix(path, "/lab/") || path == "/knowledge" || path == "/skills/reload" {
		if strings.HasPrefix(path, "/lab/") && !a.local(r, "merchant") {
			return store.Denied()
		}
		a.proxy.ServeHTTP(w, r)
		return nil
	}
	return &store.Error{Status: 404, Code: "not_found", Message: "接口不存在"}
}
func (a *Server) run(w http.ResponseWriter, r *http.Request, p store.Principal, op string, b store.Data) error {
	v, err := a.Store.Run(r.Context(), p, op, b)
	if err != nil {
		return err
	}
	jsonOut(w, 200, v)
	return nil
}
func (a *Server) login(w http.ResponseWriter, r *http.Request) error {
	if r.Method != "POST" {
		return &store.Error{Status: 405, Code: "method", Message: "不支持此方法"}
	}
	b, err := readBody(w, r)
	if err != nil {
		return err
	}
	ip, _, _ := net.SplitHostPort(r.RemoteAddr)
	a.mu.Lock()
	entry := a.logins[ip]
	if time.Now().After(entry.until) {
		entry = attempt{until: time.Now().Add(time.Minute)}
	}
	entry.n++
	a.logins[ip] = entry
	if len(a.logins) > 10000 {
		for key, v := range a.logins {
			if time.Now().After(v.until) {
				delete(a.logins, key)
			}
		}
	}
	a.mu.Unlock()
	if entry.n > 20 {
		return &store.Error{Status: 429, Code: "rate_limited", Message: "登录尝试过多，请稍后重试"}
	}
	p, err := a.Store.Login(r.Context(), store.Text(b, "tenant"), store.Text(b, "user"), store.Text(b, "password"))
	if err != nil {
		return err
	}
	v, err := a.Store.Run(r.Context(), p, "issue_token", store.Data{"ttl": 3600})
	if err != nil {
		return err
	}
	jsonOut(w, 200, store.Data{"token": v, "principal": p})
	return nil
}
func (a *Server) internal(w http.ResponseWriter, r *http.Request) error {
	if r.Method != "POST" || subtle.ConstantTimeCompare([]byte(r.Header.Get("X-SupportFlow-Service-Key")), []byte(a.Config.ServiceKey)) != 1 {
		return store.Denied()
	}
	b, err := readBody(w, r)
	if err != nil {
		return err
	}
	var p store.Principal
	_ = json.Unmarshal([]byte(store.JSON(b["principal"])), &p)
	op := store.Text(b, "operation")
	args, _ := b["arguments"].(map[string]any)
	allowed := map[string]bool{}
	for _, name := range strings.Fields("authenticate history profile cached_request acquire_conversation release commit_turn finalize_turn order order_list refund_status refund_request create_ticket ticket audit_log append_audit") {
		allowed[name] = true
	}
	if !allowed[op] || (op != "authenticate" && (p.Tenant == "" || p.User == "")) {
		return store.Denied()
	}
	return a.run(w, r, p, op, args)
}
func (a *Server) chat(w http.ResponseWriter, r *http.Request, p store.Principal) error {
	raw, err := io.ReadAll(http.MaxBytesReader(w, r.Body, 40000))
	if err != nil {
		return store.Invalid("消息过长")
	}
	var b store.Data
	if json.Unmarshal(raw, &b) != nil {
		return store.Invalid("消息格式错误")
	}
	if err = strict(b, "message conv_id request_id"); err != nil {
		return err
	}
	message, rid, conv := store.Text(b, "message"), store.Text(b, "request_id"), store.Text(b, "conv_id")
	if strings.TrimSpace(message) == "" || len([]rune(message)) > 6000 || !requestID.MatchString(rid) {
		return store.Invalid("消息或请求编号无效")
	}
	if b["conv_id"] != nil && !conversationID.MatchString(conv) {
		return store.Invalid("会话编号无效")
	}
	var encoded bytes.Buffer
	encoder := json.NewEncoder(&encoded)
	encoder.SetEscapeHTML(false)
	_ = encoder.Encode([]any{message, b["conv_id"], "multi"})
	fingerprint := store.Hash(strings.TrimSuffix(encoded.String(), "\n"))
	cached, err := a.Store.Run(r.Context(), p, "cached_request", store.Data{"rid": rid, "fingerprint": fingerprint, "include_human": true})
	if err != nil {
		return err
	}
	if cached != nil {
		result := cached.(map[string]any)
		result["replayed"] = true
		jsonOut(w, 200, result)
		return nil
	}
	if conv := store.Text(b, "conv_id"); conv != "" {
		v, err := a.Store.Run(r.Context(), p, "mode", store.Data{"conv": conv})
		if err != nil {
			return err
		}
		if store.Text(v.(map[string]any), "mode") != "ai" {
			b["conv"] = conv
			b["fingerprint"] = fingerprint
			return a.run(w, r, p, "human_message", b)
		}
	}
	select {
	case a.chatSlots <- struct{}{}:
		defer func() { <-a.chatSlots }()
	default:
		return &store.Error{Status: 429, Code: "busy", Message: "当前请求较多，请稍后重试"}
	}
	r.Body = io.NopCloser(strings.NewReader(string(raw)))
	a.proxy.ServeHTTP(w, r)
	return nil
}
func (a *Server) events(w http.ResponseWriter, r *http.Request, p store.Principal) error {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("X-Accel-Buffering", "no")
	flusher, ok := w.(http.Flusher)
	if !ok {
		return fmt.Errorf("streaming unsupported")
	}
	cursor := store.Integer(r.URL.Query().Get("after"), 0)
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()
	deadline := time.NewTimer(55 * time.Second)
	defer deadline.Stop()
	for {
		v, err := a.Store.Run(r.Context(), p, "events", store.Data{"after": cursor})
		if err != nil {
			return nil
		}
		for _, e := range v.([]map[string]any) {
			cursor = store.Int(e, "id")
			fmt.Fprintf(w, "id: %d\ndata: %s\n\n", cursor, store.JSON(e))
		}
		fmt.Fprint(w, ": heartbeat\n\n")
		flusher.Flush()
		select {
		case <-r.Context().Done():
			return nil
		case <-deadline.C:
			return nil
		case <-ticker.C:
		}
	}
}

var requestID = regexp.MustCompile(`^[a-zA-Z0-9_-]{8,100}$`)
var conversationID = regexp.MustCompile(`^[a-zA-Z0-9_-]{1,80}$`)
