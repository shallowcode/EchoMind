package quota

import (
	"context"
	"errors"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"supportflow/backend/internal/store"
)

func code(err error) string {
	var e *store.Error
	if errors.As(err, &e) {
		return e.Code
	}
	return ""
}
func TestConcurrentReservationsNeverExceedDailyBudget(t *testing.T) {
	l := New(0, 1000, func(context.Context, string, time.Time) (int64, error) { return 100, nil })
	var granted atomic.Int64
	var wg sync.WaitGroup
	for range 50 {
		wg.Go(func() {
			if _, err := l.Acquire(context.Background(), "acme", 100); err == nil {
				granted.Add(1)
			} else if code(err) != "token_budget_exceeded" {
				t.Error(err)
			}
		})
	}
	wg.Wait()
	if granted.Load() != 9 {
		t.Fatalf("900 tokens remain after 100 used: want 9 leases, got %d", granted.Load())
	}
}
func TestSettleBooksActualUsageAndFreesReservation(t *testing.T) {
	l := New(0, 1000, nil)
	lease, err := l.Acquire(context.Background(), "acme", 800)
	if err != nil {
		t.Fatal(err)
	}
	if _, err = l.Acquire(context.Background(), "acme", 300); code(err) != "token_budget_exceeded" {
		t.Fatal("reservation must block overspending")
	}
	lease.Settle(150)
	lease.Settle(150)
	if spent, reserved := l.Snapshot("acme"); spent != 150 || reserved != 0 {
		t.Fatalf("spent=%d reserved=%d", spent, reserved)
	}
	if _, err = l.Acquire(context.Background(), "acme", 800); err != nil {
		t.Fatal(err)
	}
	if _, err = l.Acquire(context.Background(), "other", 900); err != nil {
		t.Fatal("tenants have independent budgets")
	}
}
func TestRateLimitRefillsOverTime(t *testing.T) {
	now := time.Now()
	l := New(2, 0, nil)
	l.now = func() time.Time { return now }
	for range 2 {
		if _, err := l.Acquire(context.Background(), "acme", 1); err != nil {
			t.Fatal(err)
		}
	}
	if _, err := l.Acquire(context.Background(), "acme", 1); code(err) != "rate_limited" {
		t.Fatal("burst should be limited to RPM")
	}
	now = now.Add(30 * time.Second)
	if _, err := l.Acquire(context.Background(), "acme", 1); err != nil {
		t.Fatal("half a minute refills one request at 2 RPM")
	}
}
func TestNewDayReloadsPersistedUsage(t *testing.T) {
	now := time.Date(2026, 10, 20, 23, 59, 0, 0, time.UTC)
	loads := 0
	l := New(0, 100, func(_ context.Context, _ string, since time.Time) (int64, error) {
		loads++
		if since.Day() == 20 {
			return 95, nil
		}
		return 0, nil
	})
	l.now = func() time.Time { return now }
	if _, err := l.Acquire(context.Background(), "acme", 10); err == nil {
		t.Fatal("persisted usage counts toward the budget")
	}
	now = now.Add(2 * time.Minute)
	if _, err := l.Acquire(context.Background(), "acme", 10); err != nil || loads != 2 {
		t.Fatalf("new UTC day starts a fresh budget: %v loads=%d", err, loads)
	}
}
