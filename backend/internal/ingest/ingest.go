// Package ingest runs the asynchronous knowledge ingestion pipeline: documents are accepted
// immediately, split into parts, and indexed by a worker pool with leases, checkpoints and retries.
package ingest

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"math/rand/v2"
	"regexp"
	"strings"
	"sync"
	"time"
	"unicode/utf8"

	"supportflow/backend/internal/store"
)

type Document struct{ ID, Title, Content string }

// Sender indexes one document part in the AI service. Re-sending a part must replace, not duplicate it.
type Sender func(ctx context.Context, p store.Principal, d Document) error

// Permanent marks errors that no retry can fix, such as a revoked submitter or rejected content.
type Permanent struct{ Err error }

func (e Permanent) Error() string { return e.Err.Error() }
func (e Permanent) Unwrap() error { return e.Err }

type Queue struct {
	Store       *store.Store
	Send        Sender
	Workers     int
	MaxAttempts int
	PartRunes   int
	Lease       time.Duration
	Poll        time.Duration
	BaseBackoff time.Duration
	wake        chan struct{}
}

func New(s *store.Store, send Sender) *Queue {
	return &Queue{Store: s, Send: send, Workers: 2, MaxAttempts: 5, PartRunes: 20000, Lease: 3 * time.Minute, Poll: 2 * time.Second, BaseBackoff: 2 * time.Second, wake: make(chan struct{}, 1)}
}

var docID = regexp.MustCompile(`^[a-zA-Z0-9_-]{1,72}$`)

const maxContentRunes = 1 << 20

func (q *Queue) Submit(ctx context.Context, p store.Principal, id, title, content string) (store.Data, bool, error) {
	title, content = strings.TrimSpace(title), strings.TrimSpace(content)
	if !docID.MatchString(id) || title == "" || utf8.RuneCountInString(title) > 160 || content == "" || utf8.RuneCountInString(content) > maxContentRunes {
		return nil, false, store.Invalid("文档编号为 1–72 位字母数字，标题 1–160 字，正文 1–1048576 字")
	}
	job, created, err := q.Store.EnqueueIngest(ctx, p, id, title, content, len(Split(content, q.PartRunes)))
	if created {
		q.Notify()
	}
	return job, created, err
}

// Notify wakes one idle worker without blocking; workers also poll for scheduled retries.
func (q *Queue) Notify() {
	select {
	case q.wake <- struct{}{}:
	default:
	}
}
func (q *Queue) Run(ctx context.Context) {
	var wg sync.WaitGroup
	for range q.Workers {
		wg.Go(func() { q.worker(ctx) })
	}
	wg.Wait()
}
func (q *Queue) worker(ctx context.Context) {
	ticker := time.NewTicker(q.Poll)
	defer ticker.Stop()
	for {
		job, err := q.Store.ClaimIngest(ctx, q.Lease)
		if err != nil && ctx.Err() == nil {
			slog.Error("ingest claim", "error", err)
		}
		if job != nil {
			q.Process(ctx, job)
			continue
		}
		select {
		case <-ctx.Done():
			return
		case <-q.wake:
		case <-ticker.C:
		}
	}
}

// Process indexes the remaining parts of a claimed job and records success, a scheduled retry or a dead letter.
func (q *Queue) Process(ctx context.Context, job *store.IngestJob) {
	parts := Split(job.Content, q.PartRunes)
	start := job.DoneParts
	if len(parts) != job.Parts || start > len(parts) {
		start = 0
	}
	var failure error
	for i := start; i < len(parts) && failure == nil; i++ {
		d := Document{ID: job.DocID, Title: job.Title, Content: parts[i]}
		if len(parts) > 1 {
			d.ID, d.Title = fmt.Sprintf("%s-p%d", job.DocID, i+1), fmt.Sprintf("%s（%d/%d）", job.Title, i+1, len(parts))
		}
		pctx, cancel := context.WithTimeout(ctx, q.Lease-10*time.Second)
		failure = q.Send(pctx, job.Principal, d)
		cancel()
		if failure == nil {
			failure = q.Store.IngestProgress(ctx, job.ID, i+1, q.Lease)
		}
	}
	if ctx.Err() != nil {
		return // shutting down: the lease expires and another worker resumes from the checkpoint
	}
	var retryAt time.Time
	if failure != nil && !errors.As(failure, new(Permanent)) && job.Attempts < q.MaxAttempts {
		delay := min(q.BaseBackoff<<(job.Attempts-1), 5*time.Minute)
		retryAt = time.Now().Add(delay + time.Duration(rand.Int64N(int64(delay/4)+1)))
	}
	if failure != nil {
		slog.Warn("ingest attempt failed", "job", job.ID, "attempt", job.Attempts, "retry", !retryAt.IsZero(), "error", failure)
	}
	if err := q.Store.FinishIngest(context.WithoutCancel(ctx), job.ID, failure, retryAt); err != nil {
		slog.Error("ingest finish", "job", job.ID, "error", err)
	}
}

// Split cuts content into parts of at most limit runes, preferring paragraph boundaries. It is
// deterministic so a retried job resumes at the same part boundaries.
func Split(content string, limit int) []string {
	parts, current := []string{}, []rune{}
	flush := func() {
		if s := strings.TrimSpace(string(current)); s != "" {
			parts = append(parts, s)
		}
		current = current[:0]
	}
	for _, paragraph := range strings.SplitAfter(content, "\n\n") {
		r := []rune(paragraph)
		if len(current)+len(r) > limit {
			flush()
		}
		for len(r) > limit {
			parts = append(parts, strings.TrimSpace(string(r[:limit])))
			r = r[limit:]
		}
		current = append(current, r...)
	}
	flush()
	return parts
}
