package llm

import (
	"sync"
	"time"
)

// Breaker opens after consecutive failures and lets a single probe through after the cooldown.
type Breaker struct {
	mu        sync.Mutex
	threshold int
	cooldown  time.Duration
	failures  int
	openUntil time.Time
	probing   bool
	now       func() time.Time
}

func NewBreaker(threshold int, cooldown time.Duration) *Breaker {
	return &Breaker{threshold: threshold, cooldown: cooldown, now: time.Now}
}
func (b *Breaker) Allow() bool {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.openUntil.IsZero() {
		return true
	}
	if b.now().Before(b.openUntil) || b.probing {
		return false
	}
	b.probing = true
	return true
}
func (b *Breaker) Success() {
	b.mu.Lock()
	b.failures, b.openUntil, b.probing = 0, time.Time{}, false
	b.mu.Unlock()
}
func (b *Breaker) Failure() {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.failures++
	if b.probing || b.failures >= b.threshold {
		b.openUntil, b.probing = b.now().Add(b.cooldown), false
	}
}

// Release returns an unused half-open probe slot, e.g. when the caller disconnected mid-attempt.
func (b *Breaker) Release() {
	b.mu.Lock()
	b.probing = false
	b.mu.Unlock()
}
func (b *Breaker) State() string {
	b.mu.Lock()
	defer b.mu.Unlock()
	switch {
	case b.openUntil.IsZero():
		return "closed"
	case b.now().Before(b.openUntil):
		return "open"
	}
	return "half_open"
}
