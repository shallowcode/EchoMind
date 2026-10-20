package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log/slog"
	"net"
	"net/http"
	"os"
	"os/signal"
	"supportflow/backend/internal/app"
	"supportflow/backend/internal/llm"
	"supportflow/backend/internal/store"
	"syscall"
	"time"
)

func env(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// providers builds the model gateway routes in priority order. SF_LLM_PROVIDERS takes a JSON list
// such as [{"name":"glm","url":"https://...","model":"glm-4.5-air","key_env":"SF_MODEL_KEY"}];
// otherwise the AI worker's OpenAI-compatible model settings are reused as a single route.
func providers() ([]llm.Provider, error) {
	if os.Getenv("SF_MODEL_BACKEND") == "fixture" {
		return []llm.Provider{llm.Fixture{Delay: 30 * time.Millisecond}}, nil
	}
	if raw := os.Getenv("SF_LLM_PROVIDERS"); raw != "" {
		var parsed []map[string]string
		if err := json.Unmarshal([]byte(raw), &parsed); err != nil {
			return nil, fmt.Errorf("SF_LLM_PROVIDERS: %w", err)
		}
		out := []llm.Provider{}
		for _, r := range parsed {
			if r["name"] == "" || r["url"] == "" || r["model"] == "" {
				return nil, fmt.Errorf("SF_LLM_PROVIDERS entries need name, url and model")
			}
			out = append(out, llm.NewOpenAI(r["name"], r["url"], os.Getenv(r["key_env"]), r["model"]))
		}
		return out, nil
	}
	if os.Getenv("SF_MODEL_BACKEND") == "compatible" && os.Getenv("SF_MODEL_URL") != "" {
		return []llm.Provider{llm.NewOpenAI("primary", os.Getenv("SF_MODEL_URL"), os.Getenv("SF_MODEL_KEY"), env("SF_MODEL_NAME", "glm-4.5-air"))}, nil
	}
	return nil, nil
}
func main() {
	addr := flag.String("addr", env("SF_GO_ADDR", "127.0.0.1:8002"), "HTTP listen address")
	flag.Parse()
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, nil)))
	s, e := store.Open(env("SF_BUSINESS_DB", "data/supportflow-business.sqlite3"))
	if e != nil {
		slog.Error("database", "error", e)
		os.Exit(1)
	}
	defer s.DB.Close()
	if password := os.Getenv("SF_ADMIN_PASSWORD"); password != "" {
		p := store.Principal{Tenant: env("SF_ADMIN_TENANT", "demo"), User: env("SF_ADMIN_USER", "admin"), Roles: []string{"admin"}}
		var n int
		if e = s.DB.QueryRow("SELECT COUNT(*) FROM users WHERE tenant=? AND id=?", p.Tenant, p.User).Scan(&n); e != nil {
			slog.Error("bootstrap", "error", e)
			os.Exit(1)
		}
		if n == 0 {
			_, e = s.CreateUser(context.Background(), p, store.Data{"user": p.User, "name": "管理员", "password": password, "roles": []any{"admin", "staff", "finance", "ops"}})
			if e != nil {
				slog.Error("bootstrap", "error", e)
				os.Exit(1)
			}
		}
	}
	routes, e := providers()
	if e != nil {
		slog.Error("configuration", "error", e)
		os.Exit(1)
	}
	handler, e := app.New(s, app.Config{AIURL: env("SF_AI_URL", "http://127.0.0.1:8003"), ServiceKey: os.Getenv("SF_SERVICE_KEY"), Frontend: env("SF_FRONTEND", "frontend"), Demo: os.Getenv("SF_LOCAL_DEMO_ACCESS") == "true",
		Router: llm.NewRouter(routes...), RPM: int(store.Integer(os.Getenv("SF_LLM_RPM"), 30)), DailyTokens: store.Integer(os.Getenv("SF_LLM_DAILY_TOKENS"), 500000)})
	if e != nil {
		slog.Error("configuration", "error", e)
		os.Exit(1)
	}
	listener, e := net.Listen("tcp", *addr)
	if e != nil {
		slog.Error("listen", "error", e)
		os.Exit(1)
	}
	server := &http.Server{Handler: handler, ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 20 * time.Second, WriteTimeout: 300 * time.Second, IdleTimeout: 90 * time.Second, MaxHeaderBytes: 32768}
	stop, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()
	workers := make(chan struct{})
	go func() { handler.Ingest.Run(stop); close(workers) }()
	go func() {
		<-stop.Done()
		ctx, end := context.WithTimeout(context.Background(), 20*time.Second)
		defer end()
		_ = server.Shutdown(ctx)
	}()
	slog.Info("supportFlow ready", "address", listener.Addr().String(), "backend", "Go", "ai", "Python", "llm_routes", len(routes))
	if e = server.Serve(listener); e != nil && !errors.Is(e, http.ErrServerClosed) {
		slog.Error("serve", "error", e)
		os.Exit(1)
	}
	cancel()
	<-workers
}
