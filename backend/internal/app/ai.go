package app

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"supportflow/backend/internal/copilot"
	"supportflow/backend/internal/ingest"
	"supportflow/backend/internal/llm"
	"supportflow/backend/internal/store"
)

func meta(res llm.Result, version string) store.Data {
	return store.Data{"provider": res.Provider, "model": res.Model, "prompt_version": version, "cached": res.Cached, "attempts": res.Attempts,
		"usage": res.Usage, "ttft_ms": res.TTFT.Milliseconds(), "latency_ms": res.Latency.Milliseconds()}
}

// sse writes Server-Sent Events. Headers are sent lazily so errors raised before the first
// event (permissions, quota, an unavailable gateway) still return a normal JSON error response.
type sse struct {
	w       http.ResponseWriter
	flusher http.Flusher
	started bool
}

func (s *sse) send(event string, data any) error {
	if !s.started {
		s.started = true
		h := s.w.Header()
		h.Set("Content-Type", "text/event-stream")
		h.Set("Cache-Control", "no-cache")
		h.Set("X-Accel-Buffering", "no")
		s.w.WriteHeader(200)
	}
	if _, err := fmt.Fprintf(s.w, "event: %s\ndata: %s\n\n", event, store.JSON(data)); err != nil {
		return err
	}
	s.flusher.Flush()
	return nil
}

// copilot serves POST /copilot/conversations/{id}/suggest (SSE) and /summary (JSON).
func (a *Server) copilot(w http.ResponseWriter, r *http.Request, p store.Principal) error {
	parts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	if len(parts) != 4 || parts[1] != "conversations" || (parts[3] != "suggest" && parts[3] != "summary") {
		return &store.Error{Status: 404, Code: "not_found", Message: "接口不存在"}
	}
	if r.Method != "POST" {
		return &store.Error{Status: 405, Code: "method", Message: "不支持此方法"}
	}
	conv := parts[2]
	if !conversationID.MatchString(conv) {
		return store.Invalid("会话编号无效")
	}
	ctx, cancel := context.WithTimeout(r.Context(), 90*time.Second)
	defer cancel()
	if parts[3] == "summary" {
		summary, res, err := a.Copilot.Summarize(ctx, p, conv)
		if err != nil {
			return copilot.HTTPError(err)
		}
		jsonOut(w, 200, store.Data{"summary": summary, "meta": meta(res, copilot.SummaryVersion)})
		return nil
	}
	flusher, ok := w.(http.Flusher)
	if !ok {
		return fmt.Errorf("streaming unsupported")
	}
	plan, err := a.Copilot.Suggest(ctx, p, conv, r.URL.Query().Get("fresh") == "1")
	if err != nil {
		return err
	}
	stream := &sse{w: w, flusher: flusher}
	res, err := a.Copilot.Run(ctx, plan, func(delta string) error { return stream.send("delta", store.Data{"text": delta}) })
	if err != nil {
		if !stream.started {
			return copilot.HTTPError(err)
		}
		a.failures.Add(1)
		typed := copilot.HTTPError(err)
		_ = stream.send("error", store.Data{"code": typed.Code, "detail": typed.Message, "partial": res.Text != ""})
		return nil
	}
	return stream.send("done", meta(res, plan.Version))
}

// knowledgeJobs exposes the asynchronous ingestion queue.
func (a *Server) knowledgeJobs(w http.ResponseWriter, r *http.Request, p store.Principal) error {
	parts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	switch {
	case len(parts) == 2 && r.Method == "GET":
		v, err := a.Store.IngestJobs(r.Context(), p, "")
		if err != nil {
			return err
		}
		jsonOut(w, 200, v)
		return nil
	case len(parts) == 2 && r.Method == "POST":
		b, err := readBody(w, r)
		if err != nil {
			return err
		}
		if err = strict(b, "doc_id title content"); err != nil {
			return err
		}
		job, created, err := a.Ingest.Submit(r.Context(), p, store.Text(b, "doc_id"), store.Text(b, "title"), store.Text(b, "content"))
		if err != nil {
			return err
		}
		status := 202
		if !created {
			status = 200
		}
		jsonOut(w, status, store.Data{"job": job, "deduplicated": !created})
		return nil
	case len(parts) == 3 && r.Method == "GET":
		v, err := a.Store.IngestJobs(r.Context(), p, parts[2])
		if err != nil {
			return err
		}
		jsonOut(w, 200, v)
		return nil
	case len(parts) == 4 && parts[3] == "retry" && r.Method == "POST":
		v, err := a.Store.RetryIngest(r.Context(), p, parts[2])
		if err != nil {
			return err
		}
		a.Ingest.Notify()
		jsonOut(w, 200, v)
		return nil
	}
	return &store.Error{Status: 404, Code: "not_found", Message: "接口不存在"}
}

// sendKnowledge indexes one document part in the AI worker as the job's submitter, using a
// short-lived token that is revoked right after the call.
func (a *Server) sendKnowledge(ctx context.Context, p store.Principal, d ingest.Document) error {
	v, err := a.Store.Run(ctx, p, "issue_token", store.Data{"ttl": 300})
	if err != nil {
		return ingest.Permanent{Err: err}
	}
	token := v.(string)
	defer a.Store.Run(context.WithoutCancel(ctx), p, "revoke", store.Data{"token": token})
	body, _ := json.Marshal(map[string]string{"id": d.ID, "title": d.Title, "content": d.Content})
	req, err := http.NewRequestWithContext(ctx, "POST", strings.TrimRight(a.Config.AIURL, "/")+"/knowledge", bytes.NewReader(body))
	if err != nil {
		return ingest.Permanent{Err: err}
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("X-SupportFlow-Service-Key", a.Config.ServiceKey)
	resp, err := a.aiClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	detail, _ := io.ReadAll(io.LimitReader(resp.Body, 512))
	switch {
	case resp.StatusCode == 200:
		return nil
	case resp.StatusCode == 401 || resp.StatusCode == 403 || resp.StatusCode == 404 || resp.StatusCode == 413 || resp.StatusCode == 422:
		return ingest.Permanent{Err: fmt.Errorf("AI 服务拒绝索引 %s：HTTP %d %s", d.ID, resp.StatusCode, detail)}
	}
	return fmt.Errorf("AI 服务索引 %s 失败：HTTP %d", d.ID, resp.StatusCode)
}
