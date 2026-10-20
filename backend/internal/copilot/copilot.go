// Package copilot implements the agent-assist features served directly by Go: streamed reply
// drafts and structured handoff summaries for human agents, on top of the llm gateway.
package copilot

import (
	"context"
	_ "embed"
	"encoding/json"
	"errors"
	"fmt"
	"regexp"
	"slices"
	"strings"
	"time"
	"unicode/utf8"

	"supportflow/backend/internal/llm"
	"supportflow/backend/internal/quota"
	"supportflow/backend/internal/store"
)

var (
	//go:embed prompts/suggest.txt
	suggestPrompt string
	//go:embed prompts/summary.txt
	summaryPrompt string
)

// Prompt versions are derived from the template content, so editing a prompt changes the version
// recorded with every call and automatically invalidates cached generations.
var (
	SuggestVersion = "suggest@" + store.Hash(suggestPrompt)[:8]
	SummaryVersion = "summary@" + store.Hash(summaryPrompt)[:8]
)
var ErrInvalidOutput = errors.New("model output failed schema validation")

type Service struct {
	Store         *store.Store
	Router        *llm.Router
	Cache         *llm.Cache
	Limiter       *quota.Limiter
	HistoryTokens int
}

func New(s *store.Store, r *llm.Router, l *quota.Limiter) *Service {
	return &Service{Store: s, Router: r, Cache: llm.NewCache(512, 10*time.Minute), Limiter: l, HistoryTokens: 3000}
}

// Plan is a fully prepared model call; preparing it performs every check that should fail before streaming starts.
type Plan struct {
	Principal store.Principal
	Feature   string
	Version   string
	Conv      string
	Request   llm.Request
	Fresh     bool
	key       string
	validate  func(string) error
}

func (s *Service) prepare(ctx context.Context, p store.Principal, conv, feature, version, system string, req llm.Request) (*Plan, error) {
	if !p.Has("staff") {
		return nil, store.Denied()
	}
	if !s.Router.Enabled() {
		return nil, &store.Error{Status: 503, Code: "llm_unconfigured", Message: "未配置模型服务，AI 助手不可用"}
	}
	v, err := s.Store.Run(ctx, p, "conversation", store.Data{"conv": conv, "limit": 60})
	if err != nil {
		return nil, err
	}
	detail := v.(store.Data)
	transcript := s.transcript(detail)
	if transcript == "" {
		return nil, store.Invalid("会话暂无消息")
	}
	tickets := []string{}
	for _, t := range detail["tickets"].([]store.Data) {
		line := fmt.Sprintf("- [%s] %s", store.Text(t, "status"), store.Text(t, "summary"))
		if r := store.Text(t, "resolution"); r != "" {
			line += "；处理结果：" + r
		}
		tickets = append(tickets, line)
	}
	if len(tickets) == 0 {
		tickets = append(tickets, "无")
	}
	user := "<transcript>\n" + transcript + "\n</transcript>\n<tickets>\n" + strings.Join(tickets, "\n") + "\n</tickets>"
	req.Messages = []llm.Message{{Role: "system", Content: system}, {Role: "user", Content: user}}
	plan := &Plan{Principal: p, Feature: feature, Version: version, Conv: conv, Request: req}
	plan.key = store.Hash(store.JSON([]any{p.Tenant, feature, version, s.Router.Chain(), req.Messages, req.MaxTokens, req.Temperature, req.JSON}))
	return plan, nil
}

// transcript keeps the newest messages that fit the history token budget, oldest first.
func (s *Service) transcript(detail store.Data) string {
	messages := detail["messages"].([]store.Data)
	lines, used := []string{}, 0
	for i := len(messages) - 1; i >= 0; i-- {
		m := messages[i]
		speaker := "客户"
		switch store.Text(m, "role") {
		case "assistant":
			speaker = "AI 客服"
			if exec, _ := m["execution"].(store.Data); exec["steps"] == nil && store.Text(m, "author") != "" {
				speaker = "人工客服"
			}
		case "system":
			speaker = "系统"
		}
		content := []rune(strings.TrimSpace(store.Text(m, "content")))
		if len(content) > 1500 {
			content = append(content[:1500], []rune("…")...)
		}
		line := speaker + "：" + string(content)
		cost := llm.EstimateTokens(line)
		if used+cost > s.HistoryTokens && len(lines) > 0 {
			break
		}
		lines, used = append(lines, line), used+cost
	}
	slices.Reverse(lines)
	return strings.Join(lines, "\n")
}
func (s *Service) Suggest(ctx context.Context, p store.Principal, conv string, fresh bool) (*Plan, error) {
	plan, err := s.prepare(ctx, p, conv, "suggest_reply", SuggestVersion, suggestPrompt, llm.Request{MaxTokens: 300, Temperature: 0.3})
	if plan != nil {
		plan.Fresh = fresh
	}
	return plan, err
}

// Run executes a plan: cache lookup, budget reservation, routed streaming, metering and cache fill.
func (s *Service) Run(ctx context.Context, plan *Plan, emit func(string) error) (llm.Result, error) {
	start := time.Now()
	if !plan.Fresh {
		if v, ok := s.Cache.Get(plan.key); ok {
			s.Router.Metrics.CacheLookup(true)
			v.Cached, v.Attempts, v.TTFT, v.Latency = true, 0, 0, time.Since(start)
			err := emit(v.Text)
			s.record(ctx, plan, v, "ok")
			return v, err
		}
		s.Router.Metrics.CacheLookup(false)
	}
	estimate := int64(llm.EstimateMessages(plan.Request.Messages) + plan.Request.MaxTokens)
	lease, err := s.Limiter.Acquire(ctx, plan.Principal.Tenant, estimate)
	if err != nil {
		return llm.Result{}, err
	}
	res, err := s.Router.Stream(ctx, plan.Request, emit)
	if res.Usage.Total() == 0 && res.Text != "" {
		res.Usage = llm.Usage{PromptTokens: llm.EstimateMessages(plan.Request.Messages), CompletionTokens: llm.EstimateTokens(res.Text), Estimated: true}
	}
	lease.Settle(int64(res.Usage.Total()))
	status := "ok"
	switch {
	case errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded):
		status = "cancelled"
	case errors.Is(err, llm.ErrInterrupted):
		status = "interrupted"
	case err != nil:
		status = "error"
	case plan.validate != nil:
		if verr := plan.validate(res.Text); verr != nil {
			status, err = "invalid_output", fmt.Errorf("%w: %w", ErrInvalidOutput, verr)
		}
	}
	s.record(ctx, plan, res, status)
	if err == nil {
		s.Cache.Put(plan.key, res)
	}
	return res, err
}
func (s *Service) record(ctx context.Context, plan *Plan, res llm.Result, status string) {
	provider, model := res.Provider, res.Model
	if provider == "" {
		provider, model = "none", "none"
	}
	usage := res.Usage
	if res.Cached {
		usage = llm.Usage{}
	}
	_ = s.Store.RecordUsage(context.WithoutCancel(ctx), store.Usage{Tenant: plan.Principal.Tenant, Actor: plan.Principal.User, Feature: plan.Feature,
		Provider: provider, Model: model, PromptVersion: plan.Version, Status: status, PromptTokens: int64(usage.PromptTokens), CompletionTokens: int64(usage.CompletionTokens),
		LatencyMS: res.Latency.Milliseconds(), TTFTMS: res.TTFT.Milliseconds(), Cached: res.Cached, Estimated: usage.Estimated})
}

type Summary struct {
	Summary    string `json:"summary"`
	Intent     string `json:"intent"`
	Sentiment  string `json:"sentiment"`
	NextAction string `json:"next_action"`
}

var fence = regexp.MustCompile("(?s)^```(?:json)?\\s*|\\s*```$")
var intents = strings.Fields("order_status refund payment logistics account technical complaint other")
var sentiments = strings.Fields("positive neutral negative")

// ParseSummary accepts a fenced JSON object but never repairs field values on the model's behalf.
func ParseSummary(text string) (Summary, error) {
	var s Summary
	if err := json.Unmarshal([]byte(fence.ReplaceAllString(strings.TrimSpace(text), "")), &s); err != nil {
		return s, fmt.Errorf("不是合法 JSON 对象: %w", err)
	}
	switch {
	case s.Summary == "" || utf8.RuneCountInString(s.Summary) > 120:
		return s, errors.New("summary 必填且不超过 120 字")
	case !slices.Contains(intents, s.Intent):
		return s, fmt.Errorf("intent 取值无效: %q", s.Intent)
	case !slices.Contains(sentiments, s.Sentiment):
		return s, fmt.Errorf("sentiment 取值无效: %q", s.Sentiment)
	case s.NextAction == "" || utf8.RuneCountInString(s.NextAction) > 60:
		return s, errors.New("next_action 必填且不超过 60 字")
	}
	return s, nil
}

// Summarize produces a validated handoff summary, giving the model one repair turn with the validation error.
func (s *Service) Summarize(ctx context.Context, p store.Principal, conv string) (Summary, llm.Result, error) {
	plan, err := s.prepare(ctx, p, conv, "summarize", SummaryVersion, summaryPrompt, llm.Request{MaxTokens: 400, JSON: true})
	if err != nil {
		return Summary{}, llm.Result{}, err
	}
	plan.validate = func(text string) error { _, err := ParseSummary(text); return err }
	noop := func(string) error { return nil }
	res, err := s.Run(ctx, plan, noop)
	if errors.Is(err, ErrInvalidOutput) {
		repair := *plan
		repair.Request.Messages = append(slices.Clone(plan.Request.Messages),
			llm.Message{Role: "assistant", Content: res.Text},
			llm.Message{Role: "user", Content: "上一次输出不符合要求：" + strings.TrimPrefix(err.Error(), ErrInvalidOutput.Error()+": ") + "。请只输出符合字段要求的 JSON 对象。"})
		repair.key = store.Hash(plan.key + "\x00repair\x00" + res.Text)
		res, err = s.Run(ctx, &repair, noop)
	}
	if err != nil {
		return Summary{}, res, err
	}
	summary, _ := ParseSummary(res.Text)
	return summary, res, nil
}

// HTTPError maps gateway failures to API errors; business errors pass through unchanged.
func HTTPError(err error) *store.Error {
	var typed *store.Error
	switch {
	case errors.As(err, &typed):
		return typed
	case errors.Is(err, ErrInvalidOutput):
		return &store.Error{Status: 502, Code: "model_output_invalid", Message: "模型输出未通过格式校验，请重试"}
	case errors.Is(err, llm.ErrInterrupted):
		return &store.Error{Status: 502, Code: "llm_interrupted", Message: "模型输出中断，请重试"}
	case errors.Is(err, context.DeadlineExceeded):
		return &store.Error{Status: 504, Code: "llm_timeout", Message: "模型响应超时，请重试"}
	}
	return &store.Error{Status: 503, Code: "llm_unavailable", Message: "模型服务暂不可用，请稍后重试或直接人工回复"}
}
