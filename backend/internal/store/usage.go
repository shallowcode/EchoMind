package store

import (
	"context"
	"slices"
	"time"
)

// Usage is one model gateway call. Cached replays are recorded with zero tokens so hit rate is measurable.
type Usage struct {
	Tenant, Actor, Feature, Provider, Model, PromptVersion, Status string
	PromptTokens, CompletionTokens, LatencyMS, TTFTMS              int64
	Cached, Estimated                                              bool
}

func flag(b bool) int {
	if b {
		return 1
	}
	return 0
}
func (s *Store) RecordUsage(ctx context.Context, u Usage) error {
	_, err := s.DB.ExecContext(ctx, "INSERT INTO llm_usage(tenant,actor,feature,provider,model,prompt_version,status,prompt_tokens,completion_tokens,latency_ms,ttft_ms,cached,estimated,created) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
		u.Tenant, u.Actor, u.Feature, u.Provider, u.Model, u.PromptVersion, u.Status, u.PromptTokens, u.CompletionTokens, u.LatencyMS, u.TTFTMS, flag(u.Cached), flag(u.Estimated), Now())
	return err
}
func (s *Store) TokensSince(ctx context.Context, tenant string, since time.Time) (int64, error) {
	var n int64
	err := s.DB.QueryRowContext(ctx, "SELECT COALESCE(SUM(prompt_tokens+completion_tokens),0) FROM llm_usage WHERE tenant=? AND created>=?", tenant, float64(since.Unix())).Scan(&n)
	return n, err
}

// UsageReport aggregates the tenant's model usage: totals, per day, per feature (with latency percentiles) and per model.
func (s *Store) UsageReport(ctx context.Context, p Principal, days int) (Data, error) {
	if !p.Has("staff", "ops") {
		return nil, Denied()
	}
	days = min(max(days, 1), 90)
	since := Now() - float64(days*86400)
	v, err := s.within(ctx, func(t *transaction) (any, error) {
		where := " FROM llm_usage WHERE tenant=? AND created>=?"
		total := t.one("SELECT COUNT(*) requests,COALESCE(SUM(prompt_tokens),0) prompt_tokens,COALESCE(SUM(completion_tokens),0) completion_tokens,COALESCE(SUM(cached),0) cached,COALESCE(SUM(status<>'ok'),0) errors"+where, p.Tenant, since)
		if n := Int(total, "requests"); n > 0 {
			total["cache_hit_rate"] = float64(Int(total, "cached")) / float64(n)
		}
		features := t.rows("SELECT feature,COUNT(*) requests,COALESCE(SUM(prompt_tokens+completion_tokens),0) tokens,COALESCE(SUM(cached),0) cached,COALESCE(SUM(status<>'ok'),0) errors"+where+" GROUP BY feature ORDER BY feature", p.Tenant, since)
		for _, f := range features {
			// Percentiles cover real model calls only; cache replays would hide upstream latency.
			rows := t.rows("SELECT latency_ms,ttft_ms"+where+" AND feature=? AND status='ok' AND cached=0", p.Tenant, since, f["feature"])
			latency, ttft := []int64{}, []int64{}
			for _, r := range rows {
				latency, ttft = append(latency, Int(r, "latency_ms")), append(ttft, Int(r, "ttft_ms"))
			}
			f["p50_latency_ms"], f["p95_latency_ms"], f["p95_ttft_ms"] = percentile(latency, 50), percentile(latency, 95), percentile(ttft, 95)
		}
		return Data{
			"days":       days,
			"total":      total,
			"by_day":     t.rows("SELECT date(created,'unixepoch') day,COUNT(*) requests,COALESCE(SUM(prompt_tokens+completion_tokens),0) tokens"+where+" GROUP BY day ORDER BY day", p.Tenant, since),
			"by_feature": features,
			"by_model":   t.rows("SELECT provider,model,COUNT(*) requests,COALESCE(SUM(prompt_tokens+completion_tokens),0) tokens,COALESCE(SUM(estimated),0) estimated"+where+" AND cached=0 GROUP BY provider,model ORDER BY requests DESC", p.Tenant, since),
		}, nil
	})
	if err != nil {
		return nil, err
	}
	return v.(Data), nil
}

// percentile uses the nearest-rank method; it returns nil when there is no sample.
func percentile(values []int64, p int) any {
	if len(values) == 0 {
		return nil
	}
	slices.Sort(values)
	rank := (p*len(values) + 99) / 100
	return values[max(rank, 1)-1]
}
