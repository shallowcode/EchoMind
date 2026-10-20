package llm

import (
	"context"
	"errors"
	"fmt"
	"io"
	"math/rand/v2"
	"strings"
	"time"
)

// Router tries providers in priority order. Retries and failover only happen before the first token
// reaches the caller; once text is streamed, switching provider would duplicate or contradict output.
type Router struct {
	routes            []*route
	Retries           int
	Backoff           time.Duration
	FirstTokenTimeout time.Duration
	Metrics           *Metrics
}
type route struct {
	provider Provider
	breaker  *Breaker
}
type emitError struct{ err error }

func (e *emitError) Error() string { return e.err.Error() }
func (e *emitError) Unwrap() error { return e.err }

func NewRouter(providers ...Provider) *Router {
	r := &Router{Retries: 1, Backoff: 300 * time.Millisecond, FirstTokenTimeout: 20 * time.Second, Metrics: NewMetrics()}
	for _, p := range providers {
		r.routes = append(r.routes, &route{p, NewBreaker(3, 30*time.Second)})
	}
	return r
}
func (r *Router) Enabled() bool { return len(r.routes) > 0 }

// Chain identifies the configured routes; it is part of cache keys so a config change never serves stale output.
func (r *Router) Chain() string {
	names := []string{}
	for _, rt := range r.routes {
		names = append(names, rt.provider.Name()+"/"+rt.provider.Model())
	}
	return strings.Join(names, ",")
}
func (r *Router) Status() []map[string]string {
	out := []map[string]string{}
	for _, rt := range r.routes {
		out = append(out, map[string]string{"provider": rt.provider.Name(), "model": rt.provider.Model(), "breaker": rt.breaker.State()})
	}
	return out
}
func (r *Router) Complete(ctx context.Context, req Request) (Result, error) {
	return r.Stream(ctx, req, func(string) error { return nil })
}
func (r *Router) Stream(ctx context.Context, req Request, emit func(string) error) (Result, error) {
	start := time.Now()
	attempts := 0
	var last error = ErrUnavailable
	for _, rt := range r.routes {
		name := rt.provider.Name()
		for try := 0; try <= r.Retries; try++ {
			if try > 0 {
				delay := r.Backoff<<(try-1) + time.Duration(rand.Int64N(int64(r.Backoff/2)+1))
				select {
				case <-ctx.Done():
					return Result{Attempts: attempts}, ctx.Err()
				case <-time.After(delay):
				}
			}
			if !rt.breaker.Allow() {
				r.Metrics.Count(name, "short_circuit")
				break
			}
			attempts++
			res, err := r.attempt(ctx, rt, req, emit)
			res.Attempts, res.Latency = attempts, time.Since(start)
			if err == nil {
				rt.breaker.Success()
				r.Metrics.Observe(name, res)
				return res, nil
			}
			var gone *emitError
			if errors.As(err, &gone) || ctx.Err() != nil {
				rt.breaker.Release()
				r.Metrics.Count(name, "cancelled")
				if ctx.Err() != nil {
					return res, ctx.Err()
				}
				return res, gone.err
			}
			rt.breaker.Failure()
			last = fmt.Errorf("%s: %w", name, err)
			if res.Text != "" {
				r.Metrics.Count(name, "interrupted")
				return res, fmt.Errorf("%w: %w", ErrInterrupted, last)
			}
			r.Metrics.Count(name, "error")
			if !Retryable(err) {
				break
			}
		}
	}
	return Result{Attempts: attempts, Latency: time.Since(start)}, fmt.Errorf("%w: %w", ErrUnavailable, last)
}
func (r *Router) attempt(ctx context.Context, rt *route, req Request, emit func(string) error) (Result, error) {
	actx, cancel := context.WithCancelCause(ctx)
	defer cancel(nil)
	begin := time.Now()
	timer := time.AfterFunc(r.FirstTokenTimeout, func() { cancel(ErrFirstToken) })
	defer timer.Stop()
	res := Result{Provider: rt.provider.Name(), Model: rt.provider.Model()}
	var text strings.Builder
	var emitErr error
	usage, err := rt.provider.Stream(actx, req, func(s string) error {
		if text.Len() == 0 {
			timer.Stop()
			res.TTFT = time.Since(begin)
		}
		text.WriteString(s)
		if e := emit(s); e != nil {
			emitErr = e
			return e
		}
		return nil
	})
	res.Text, res.Usage = text.String(), usage
	if emitErr != nil {
		return res, &emitError{emitErr}
	}
	if err != nil && ctx.Err() == nil && errors.Is(context.Cause(actx), ErrFirstToken) {
		err = ErrFirstToken
	}
	return res, err
}
func (r *Router) WriteMetrics(w io.Writer) {
	r.Metrics.Write(w)
	fmt.Fprint(w, "# TYPE supportflow_llm_breaker_open gauge\n")
	for _, rt := range r.routes {
		open := 0
		if rt.breaker.State() == "open" {
			open = 1
		}
		fmt.Fprintf(w, "supportflow_llm_breaker_open{provider=%q} %d\n", rt.provider.Name(), open)
	}
}
