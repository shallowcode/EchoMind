package llm

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"time"
)

// OpenAI speaks the OpenAI-compatible /chat/completions streaming protocol (GLM, DeepSeek, vLLM, ...).
type OpenAI struct {
	name, url, key, model string
	client                *http.Client
}

func NewOpenAI(name, baseURL, key, model string) *OpenAI {
	transport := &http.Transport{Proxy: http.ProxyFromEnvironment, MaxIdleConnsPerHost: 32, IdleConnTimeout: 90 * time.Second, ResponseHeaderTimeout: 60 * time.Second}
	return &OpenAI{name: name, url: strings.TrimRight(baseURL, "/") + "/chat/completions", key: key, model: model, client: &http.Client{Transport: transport}}
}
func (o *OpenAI) Name() string  { return o.name }
func (o *OpenAI) Model() string { return o.model }

type chunk struct {
	Choices []struct {
		Delta struct {
			Content string `json:"content"`
		} `json:"delta"`
	} `json:"choices"`
	Usage *struct {
		PromptTokens     int `json:"prompt_tokens"`
		CompletionTokens int `json:"completion_tokens"`
	} `json:"usage"`
}

func (o *OpenAI) Stream(ctx context.Context, req Request, emit func(string) error) (Usage, error) {
	body := map[string]any{"model": o.model, "messages": req.Messages, "temperature": req.Temperature, "stream": true, "stream_options": map[string]any{"include_usage": true}}
	if req.MaxTokens > 0 {
		body["max_tokens"] = req.MaxTokens
	}
	if req.JSON {
		body["response_format"] = map[string]string{"type": "json_object"}
	}
	raw, _ := json.Marshal(body)
	r, err := http.NewRequestWithContext(ctx, "POST", o.url, bytes.NewReader(raw))
	if err != nil {
		return Usage{}, err
	}
	r.Header.Set("Content-Type", "application/json")
	r.Header.Set("Accept", "text/event-stream")
	if o.key != "" {
		r.Header.Set("Authorization", "Bearer "+o.key)
	}
	resp, err := o.client.Do(r)
	if err != nil {
		return Usage{}, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		detail, _ := io.ReadAll(io.LimitReader(resp.Body, 2048))
		return Usage{}, &StatusError{Status: resp.StatusCode, Body: string(detail)}
	}
	var usage Usage
	var out strings.Builder
	done := false
	scanner := bufio.NewScanner(resp.Body)
	scanner.Buffer(make([]byte, 64<<10), 1<<20)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if !strings.HasPrefix(line, "data:") {
			continue
		}
		payload := strings.TrimSpace(strings.TrimPrefix(line, "data:"))
		if payload == "[DONE]" {
			done = true
			break
		}
		var c chunk
		if json.Unmarshal([]byte(payload), &c) != nil {
			return usage, ErrBadStream
		}
		if c.Usage != nil {
			usage.PromptTokens, usage.CompletionTokens = c.Usage.PromptTokens, c.Usage.CompletionTokens
		}
		for _, choice := range c.Choices {
			if choice.Delta.Content == "" {
				continue
			}
			out.WriteString(choice.Delta.Content)
			if err := emit(choice.Delta.Content); err != nil {
				return usage, err
			}
		}
	}
	if err := scanner.Err(); err != nil {
		return usage, err
	}
	if !done {
		return usage, ErrBadStream
	}
	if usage.Total() == 0 {
		usage = Usage{PromptTokens: EstimateMessages(req.Messages), CompletionTokens: EstimateTokens(out.String()), Estimated: true}
	}
	return usage, nil
}
