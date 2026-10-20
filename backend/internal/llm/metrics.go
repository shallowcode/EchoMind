package llm

import (
	"cmp"
	"fmt"
	"io"
	"slices"
	"sync"
	"time"
)

var buckets = []float64{0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60}

type histogram struct {
	counts []int64
	sum    float64
	n      int64
}

func (h *histogram) observe(v float64) {
	if h.counts == nil {
		h.counts = make([]int64, len(buckets))
	}
	for i, b := range buckets {
		if v <= b {
			h.counts[i]++
		}
	}
	h.sum += v
	h.n++
}

// Metrics is a small Prometheus text exporter for gateway outcomes, latency, time-to-first-token and tokens.
type Metrics struct {
	mu       sync.Mutex
	outcomes map[[2]string]int64
	tokens   map[[2]string]int64
	latency  map[string]*histogram
	ttft     map[string]*histogram
	cache    map[string]int64
}

func NewMetrics() *Metrics {
	return &Metrics{outcomes: map[[2]string]int64{}, tokens: map[[2]string]int64{}, latency: map[string]*histogram{}, ttft: map[string]*histogram{}, cache: map[string]int64{}}
}
func (m *Metrics) Count(provider, outcome string) {
	m.mu.Lock()
	m.outcomes[[2]string{provider, outcome}]++
	m.mu.Unlock()
}
func (m *Metrics) CacheLookup(hit bool) {
	m.mu.Lock()
	if hit {
		m.cache["hit"]++
	} else {
		m.cache["miss"]++
	}
	m.mu.Unlock()
}
func (m *Metrics) Observe(provider string, r Result) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.outcomes[[2]string{provider, "success"}]++
	m.tokens[[2]string{provider, "prompt"}] += int64(r.Usage.PromptTokens)
	m.tokens[[2]string{provider, "completion"}] += int64(r.Usage.CompletionTokens)
	for _, pair := range []struct {
		h map[string]*histogram
		d time.Duration
	}{{m.latency, r.Latency}, {m.ttft, r.TTFT}} {
		if pair.h[provider] == nil {
			pair.h[provider] = &histogram{}
		}
		pair.h[provider].observe(pair.d.Seconds())
	}
}
func (m *Metrics) Write(w io.Writer) {
	m.mu.Lock()
	defer m.mu.Unlock()
	fmt.Fprint(w, "# TYPE supportflow_llm_requests_total counter\n")
	for _, k := range sortedKeys(m.outcomes) {
		fmt.Fprintf(w, "supportflow_llm_requests_total{provider=%q,outcome=%q} %d\n", k[0], k[1], m.outcomes[k])
	}
	fmt.Fprint(w, "# TYPE supportflow_llm_tokens_total counter\n")
	for _, k := range sortedKeys(m.tokens) {
		fmt.Fprintf(w, "supportflow_llm_tokens_total{provider=%q,kind=%q} %d\n", k[0], k[1], m.tokens[k])
	}
	fmt.Fprint(w, "# TYPE supportflow_llm_cache_lookups_total counter\n")
	for _, k := range []string{"hit", "miss"} {
		fmt.Fprintf(w, "supportflow_llm_cache_lookups_total{result=%q} %d\n", k, m.cache[k])
	}
	for _, family := range []struct {
		name   string
		series map[string]*histogram
	}{{"supportflow_llm_latency_seconds", m.latency}, {"supportflow_llm_ttft_seconds", m.ttft}} {
		name, series := family.name, family.series
		fmt.Fprintf(w, "# TYPE %s histogram\n", name)
		providers := make([]string, 0, len(series))
		for p := range series {
			providers = append(providers, p)
		}
		slices.Sort(providers)
		for _, p := range providers {
			h := series[p]
			for i, b := range buckets {
				fmt.Fprintf(w, "%s_bucket{provider=%q,le=\"%g\"} %d\n", name, p, b, h.counts[i])
			}
			fmt.Fprintf(w, "%s_bucket{provider=%q,le=\"+Inf\"} %d\n%s_sum{provider=%q} %g\n%s_count{provider=%q} %d\n", name, p, h.n, name, p, h.sum, name, p, h.n)
		}
	}
}
func sortedKeys(m map[[2]string]int64) [][2]string {
	keys := make([][2]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	slices.SortFunc(keys, func(a, b [2]string) int { return cmp.Or(cmp.Compare(a[0], b[0]), cmp.Compare(a[1], b[1])) })
	return keys
}
