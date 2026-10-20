package store

import (
	"context"
	"encoding/json"
	"time"
)

const ingestColumns = "id,tenant,actor,doc_id,title,content_hash,parts,done_parts,status,attempts,last_error,created,updated"

// EnqueueIngest persists a knowledge ingestion job. Resubmitting identical content for the same
// document while a job is pending or has succeeded returns that job instead of a duplicate.
func (s *Store) EnqueueIngest(ctx context.Context, p Principal, docID, title, content string, parts int) (Data, bool, error) {
	if !p.Has("admin") {
		return nil, false, Denied()
	}
	created := false
	v, err := s.within(ctx, func(t *transaction) (any, error) {
		hash := Hash(title + "\x00" + content)
		if r := t.one("SELECT "+ingestColumns+" FROM ingest_jobs WHERE tenant=? AND doc_id=? AND content_hash=? AND status IN ('queued','running','succeeded') ORDER BY created DESC LIMIT 1", p.Tenant, docID, hash); r != nil {
			return r, nil
		}
		id, now := ID("job_"), Now()
		t.exec("INSERT INTO ingest_jobs(id,tenant,actor,principal,doc_id,title,content,content_hash,parts,status,next_run,created,updated) VALUES(?,?,?,?,?,?,?,?,?,'queued',?,?,?)",
			id, p.Tenant, p.User, JSON(p), docID, title, content, hash, parts, now, now, now)
		t.audit(p, "knowledge_job_submit", id, Data{"doc_id": docID, "parts": parts})
		t.event(p.Tenant, "", "knowledge_job", Data{"id": id, "status": "queued"})
		created = true
		return t.one("SELECT "+ingestColumns+" FROM ingest_jobs WHERE id=?", id), nil
	})
	if err != nil {
		return nil, false, err
	}
	return v.(Data), created, nil
}

// IngestJob is a claimed job as seen by a worker, including the content and submitting principal.
type IngestJob struct {
	ID, DocID, Title, Content string
	Principal                 Principal
	Parts, DoneParts          int
	Attempts                  int
}

// ClaimIngest leases the oldest runnable job. Expired leases (a crashed worker) become runnable again.
func (s *Store) ClaimIngest(ctx context.Context, lease time.Duration) (*IngestJob, error) {
	v, err := s.within(ctx, func(t *transaction) (any, error) {
		now := Now()
		ready := "((status='queued' AND next_run<=?) OR (status='running' AND lease_until<?))"
		r := t.one("SELECT id,doc_id,title,content,principal,parts,done_parts,attempts FROM ingest_jobs WHERE "+ready+" ORDER BY created LIMIT 1", now, now)
		if r == nil {
			return nil, nil
		}
		if t.exec("UPDATE ingest_jobs SET status='running',lease_until=?,attempts=attempts+1,updated=? WHERE id=? AND "+ready, now+lease.Seconds(), now, r["id"], now, now) != 1 {
			return nil, nil
		}
		job := &IngestJob{ID: Text(r, "id"), DocID: Text(r, "doc_id"), Title: Text(r, "title"), Content: Text(r, "content"),
			Parts: int(Int(r, "parts")), DoneParts: int(Int(r, "done_parts")), Attempts: int(Int(r, "attempts")) + 1}
		_ = json.Unmarshal([]byte(Text(r, "principal")), &job.Principal)
		return job, nil
	})
	if v == nil || err != nil {
		return nil, err
	}
	return v.(*IngestJob), nil
}

// IngestProgress checkpoints completed parts and extends the lease, so a retry resumes after the last good part.
func (s *Store) IngestProgress(ctx context.Context, id string, done int, lease time.Duration) error {
	_, err := s.DB.ExecContext(ctx, "UPDATE ingest_jobs SET done_parts=?,lease_until=?,updated=? WHERE id=? AND status='running'", done, Now()+lease.Seconds(), Now(), id)
	return err
}

// FinishIngest records the outcome. A failed job is retried at retryAt, or dead-lettered when retryAt is zero.
func (s *Store) FinishIngest(ctx context.Context, id string, failure error, retryAt time.Time) error {
	_, err := s.within(ctx, func(t *transaction) (any, error) {
		r := t.one("SELECT tenant,actor,parts,done_parts FROM ingest_jobs WHERE id=?", id)
		if r == nil {
			return nil, nil
		}
		status, message := "succeeded", ""
		switch {
		case failure == nil:
			// Content is no longer needed once indexed; the hash still deduplicates resubmissions.
			t.exec("UPDATE ingest_jobs SET status='succeeded',done_parts=parts,content='',last_error='',lease_until=0,updated=? WHERE id=?", Now(), id)
		case retryAt.IsZero():
			status, message = "failed", failure.Error()
			t.exec("UPDATE ingest_jobs SET status='failed',last_error=?,lease_until=0,updated=? WHERE id=?", message, Now(), id)
		default:
			status, message = "queued", failure.Error()
			t.exec("UPDATE ingest_jobs SET status='queued',last_error=?,next_run=?,lease_until=0,updated=? WHERE id=?", message, float64(retryAt.UnixMilli())/1000, Now(), id)
		}
		t.event(Text(r, "tenant"), "", "knowledge_job", Data{"id": id, "status": status, "error": message})
		return nil, nil
	})
	return err
}
func (s *Store) IngestJobs(ctx context.Context, p Principal, id string) (any, error) {
	if !p.Has("admin", "staff") {
		return nil, Denied()
	}
	return s.within(ctx, func(t *transaction) (any, error) {
		if id == "" {
			return Data{"items": t.rows("SELECT "+ingestColumns+" FROM ingest_jobs WHERE tenant=? ORDER BY created DESC LIMIT 50", p.Tenant),
				"queue": t.rows("SELECT status,COUNT(*) count FROM ingest_jobs WHERE tenant=? GROUP BY status", p.Tenant)}, nil
		}
		r := t.one("SELECT "+ingestColumns+" FROM ingest_jobs WHERE tenant=? AND id=?", p.Tenant, id)
		if r == nil {
			return nil, &Error{404, "not_found", "任务不存在"}
		}
		return r, nil
	})
}

// RetryIngest re-queues a dead-lettered job with a fresh attempt budget.
func (s *Store) RetryIngest(ctx context.Context, p Principal, id string) (Data, error) {
	if !p.Has("admin") {
		return nil, Denied()
	}
	v, err := s.within(ctx, func(t *transaction) (any, error) {
		if t.exec("UPDATE ingest_jobs SET status='queued',attempts=0,next_run=?,updated=? WHERE tenant=? AND id=? AND status='failed'", Now(), Now(), p.Tenant, id) != 1 {
			return nil, Conflict("只有失败的任务可以重试")
		}
		t.audit(p, "knowledge_job_retry", id, Data{})
		return t.one("SELECT "+ingestColumns+" FROM ingest_jobs WHERE id=?", id), nil
	})
	if err != nil {
		return nil, err
	}
	return v.(Data), nil
}

// QueueDepth counts jobs per status across tenants for operational metrics.
func (s *Store) QueueDepth(ctx context.Context) (map[string]int64, error) {
	rows, err := s.DB.QueryContext(ctx, "SELECT status,COUNT(*) FROM ingest_jobs GROUP BY status")
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	out := map[string]int64{}
	for rows.Next() {
		var status string
		var n int64
		if err := rows.Scan(&status, &n); err != nil {
			return nil, err
		}
		out[status] = n
	}
	return out, rows.Err()
}
