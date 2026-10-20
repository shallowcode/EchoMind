// Package quota enforces per-tenant request rate and daily token budgets for model calls.
//
// Budgets use the same reserve-then-settle pattern as refunds: a request reserves its worst-case
// token cost before calling the model and settles the actual usage afterwards, so concurrent
// requests cannot jointly overspend. State is per process; the deployment runs one Go instance.
package quota

import (
	"context"
	"sync"
	"time"

	"supportflow/backend/internal/store"
)

type Limiter struct {
	RPM   int
	Daily int64
	// Used loads tokens already spent since the start of the UTC day (from persisted usage).
	Used    func(ctx context.Context, tenant string, since time.Time) (int64, error)
	mu      sync.Mutex
	tenants map[string]*tenantState
	now     func() time.Time
}
type tenantState struct {
	tokens   float64
	refilled time.Time
	day      string
	loaded   bool
	spent    int64
	reserved int64
}
type Lease struct {
	l      *Limiter
	tenant string
	amount int64
	once   sync.Once
}

func New(rpm int, daily int64, used func(context.Context, string, time.Time) (int64, error)) *Limiter {
	return &Limiter{RPM: rpm, Daily: daily, Used: used, tenants: map[string]*tenantState{}, now: time.Now}
}
func (l *Limiter) state(tenant string, now time.Time) *tenantState {
	s := l.tenants[tenant]
	if s == nil {
		s = &tenantState{tokens: float64(l.RPM), refilled: now}
		l.tenants[tenant] = s
	}
	if day := now.UTC().Format(time.DateOnly); s.day != day {
		s.day, s.loaded, s.spent = day, false, 0
	}
	return s
}

// Acquire takes one request token and reserves estimate tokens of today's budget.
func (l *Limiter) Acquire(ctx context.Context, tenant string, estimate int64) (*Lease, error) {
	now := l.now()
	l.mu.Lock()
	s := l.state(tenant, now)
	loaded, day := s.loaded, s.day
	l.mu.Unlock()
	if !loaded && l.Used != nil {
		start, _ := time.Parse(time.DateOnly, day)
		used, err := l.Used(ctx, tenant, start)
		if err != nil {
			return nil, err
		}
		l.mu.Lock()
		if s = l.state(tenant, now); !s.loaded && s.day == day {
			s.spent, s.loaded = used, true
		}
		l.mu.Unlock()
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	s = l.state(tenant, now)
	if l.RPM > 0 {
		s.tokens = min(float64(l.RPM), s.tokens+now.Sub(s.refilled).Minutes()*float64(l.RPM))
		s.refilled = now
		if s.tokens < 1 {
			return nil, &store.Error{Status: 429, Code: "rate_limited", Message: "AI 助手请求过于频繁，请稍后重试"}
		}
	}
	if l.Daily > 0 && s.spent+s.reserved+estimate > l.Daily {
		return nil, &store.Error{Status: 429, Code: "token_budget_exceeded", Message: "今日 AI 用量已达租户上限"}
	}
	s.tokens--
	s.reserved += estimate
	return &Lease{l: l, tenant: tenant, amount: estimate}, nil
}

// Settle releases the reservation and books the actual tokens. It is safe to call more than once.
func (lease *Lease) Settle(actual int64) {
	lease.once.Do(func() {
		l := lease.l
		l.mu.Lock()
		defer l.mu.Unlock()
		s := l.state(lease.tenant, l.now())
		s.reserved = max(0, s.reserved-lease.amount)
		s.spent += actual
	})
}

// Snapshot reports today's spent and reserved tokens for one tenant.
func (l *Limiter) Snapshot(tenant string) (spent, reserved int64) {
	l.mu.Lock()
	defer l.mu.Unlock()
	s := l.state(tenant, l.now())
	return s.spent, s.reserved
}
