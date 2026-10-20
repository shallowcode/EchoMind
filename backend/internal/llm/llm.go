// Package llm is the Go model gateway: providers, streaming, failover, circuit breaking and caching.
package llm

import (
	"context"
	"errors"
	"fmt"
	"net"
	"time"
	"unicode"
)

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}
type Request struct {
	Messages    []Message
	MaxTokens   int
	Temperature float64
	JSON        bool
}
type Usage struct {
	PromptTokens     int  `json:"prompt_tokens"`
	CompletionTokens int  `json:"completion_tokens"`
	Estimated        bool `json:"estimated"`
}

func (u Usage) Total() int { return u.PromptTokens + u.CompletionTokens }

// Result describes one completed generation, including which route actually served it.
type Result struct {
	Text     string        `json:"text"`
	Usage    Usage         `json:"usage"`
	Provider string        `json:"provider"`
	Model    string        `json:"model"`
	Attempts int           `json:"attempts"`
	TTFT     time.Duration `json:"-"`
	Latency  time.Duration `json:"-"`
	Cached   bool          `json:"cached"`
}

// Provider streams one completion. emit is called synchronously for each text delta.
type Provider interface {
	Name() string
	Model() string
	Stream(ctx context.Context, req Request, emit func(string) error) (Usage, error)
}

// StatusError carries the upstream HTTP status so the router can decide whether to fail over.
type StatusError struct {
	Status int
	Body   string
}

func (e *StatusError) Error() string { return fmt.Sprintf("model endpoint returned %d", e.Status) }

var (
	ErrFirstToken  = errors.New("model did not produce a first token in time")
	ErrBadStream   = errors.New("model stream was malformed")
	ErrUnavailable = errors.New("all model routes are unavailable")
	ErrInterrupted = errors.New("model stream interrupted after partial output")
)

// Retryable reports whether another attempt, possibly on another provider, may succeed.
func Retryable(err error) bool {
	var status *StatusError
	if errors.As(err, &status) {
		return status.Status == 408 || status.Status == 409 || status.Status == 429 || status.Status >= 500
	}
	if errors.Is(err, ErrFirstToken) || errors.Is(err, ErrBadStream) {
		return true
	}
	var netErr net.Error
	return errors.As(err, &netErr) || errors.Is(err, context.DeadlineExceeded)
}

// EstimateTokens is used only when a provider omits usage: CJK runes ~1 token, other text ~4 runes per token.
func EstimateTokens(s string) int {
	cjk, other := 0, 0
	for _, r := range s {
		if unicode.Is(unicode.Han, r) || unicode.Is(unicode.Hiragana, r) || unicode.Is(unicode.Katakana, r) || unicode.Is(unicode.Hangul, r) {
			cjk++
		} else {
			other++
		}
	}
	return cjk + (other+3)/4
}
func EstimateMessages(ms []Message) int {
	n := 0
	for _, m := range ms {
		n += EstimateTokens(m.Content) + 4
	}
	return n
}
