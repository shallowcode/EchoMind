package llm

import (
	"context"
	"encoding/json"
	"strings"
	"time"
)

// Fixture is an explicit offline double for CI and demos. Its output is never a model quality result.
type Fixture struct{ Delay time.Duration }

func (Fixture) Name() string  { return "fixture" }
func (Fixture) Model() string { return "fixture" }
func (f Fixture) Stream(ctx context.Context, req Request, emit func(string) error) (Usage, error) {
	last := ""
	for _, m := range req.Messages {
		if m.Role == "user" {
			last = m.Content
		}
	}
	text := "您好，已收到您的问题，我们正在核实相关信息，稍后为您同步处理结果。"
	if req.JSON {
		raw, _ := json.Marshal(map[string]string{"summary": "离线摘要：" + firstRunes(last, 40), "intent": "other", "sentiment": "neutral", "next_action": "人工核实后回复客户"})
		text = string(raw)
	}
	runes := []rune(text)
	for i := 0; i < len(runes); i += 6 {
		if err := ctx.Err(); err != nil {
			return Usage{}, err
		}
		if f.Delay > 0 {
			time.Sleep(f.Delay)
		}
		if err := emit(string(runes[i:min(i+6, len(runes))])); err != nil {
			return Usage{}, err
		}
	}
	return Usage{PromptTokens: EstimateMessages(req.Messages), CompletionTokens: EstimateTokens(text), Estimated: true}, nil
}
func firstRunes(s string, n int) string {
	r := []rune(strings.TrimSpace(s))
	if len(r) > n {
		r = r[:n]
	}
	return string(r)
}
