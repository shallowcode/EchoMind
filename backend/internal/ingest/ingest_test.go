package ingest

import (
	"context"
	"errors"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"supportflow/backend/internal/store"
)

var admin = store.Principal{Tenant: "acme", User: "admin", Roles: []string{"admin"}}

func queue(t *testing.T, send Sender) *Queue {
	t.Helper()
	s, err := store.Open(filepath.Join(t.TempDir(), "business.sqlite3"))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { s.Close() })
	q := New(s, send)
	q.PartRunes, q.BaseBackoff = 10, time.Millisecond
	return q
}
func status(t *testing.T, q *Queue, id string) store.Data {
	t.Helper()
	v, err := q.Store.IngestJobs(context.Background(), admin, id)
	if err != nil {
		t.Fatal(err)
	}
	return v.(store.Data)
}

// drain claims and processes jobs, sleeping past retry backoffs, until nothing is runnable.
func drain(t *testing.T, q *Queue) {
	t.Helper()
	for range 20 {
		job, err := q.Store.ClaimIngest(context.Background(), q.Lease)
		if err != nil {
			t.Fatal(err)
		}
		if job == nil {
			time.Sleep(20 * time.Millisecond)
			if job, _ = q.Store.ClaimIngest(context.Background(), q.Lease); job == nil {
				return
			}
		}
		q.Process(context.Background(), job)
	}
}
func TestSplitPrefersParagraphsAndIsDeterministic(t *testing.T) {
	parts := Split("第一段内容\n\n第二段内容\n\n这是一段很长很长很长的第三段内容", 10)
	if len(parts) != 4 || parts[0] != "第一段内容" || parts[1] != "第二段内容" {
		t.Fatalf("%q", parts)
	}
	for _, p := range parts {
		if len([]rune(p)) > 10 {
			t.Fatalf("part too long: %q", p)
		}
	}
	if strings.Join(Split("a\n\nb", 10), "|") != "a\n\nb" {
		t.Fatal("small paragraphs are merged into one part")
	}
}
func TestRetryResumesFromCheckpointAfterTransientFailure(t *testing.T) {
	sent, failOnce := []string{}, true
	q := queue(t, func(_ context.Context, p store.Principal, d Document) error {
		if p.User != "admin" {
			t.Errorf("sent as %+v", p)
		}
		if d.ID == "faq-p2" && failOnce {
			failOnce = false
			return errors.New("connection reset")
		}
		sent = append(sent, d.ID)
		return nil
	})
	job, created, err := q.Submit(context.Background(), admin, "faq", "常见问题", "退货政策七天无理由\n\n运费由商家承担")
	if err != nil || !created || store.Int(job, "parts") != 2 {
		t.Fatalf("%v %v %v", job, created, err)
	}
	drain(t, q)
	got := status(t, q, store.Text(job, "id"))
	if strings.Join(sent, ",") != "faq-p1,faq-p2" || store.Text(got, "status") != "succeeded" || store.Int(got, "attempts") != 2 {
		t.Fatalf("sent=%v job=%v", sent, got)
	}
	again, created, _ := q.Submit(context.Background(), admin, "faq", "常见问题", "退货政策七天无理由\n\n运费由商家承担")
	if created || store.Text(again, "id") != store.Text(job, "id") {
		t.Fatal("identical resubmission must be deduplicated")
	}
}
func TestPermanentAndExhaustedFailuresAreDeadLettered(t *testing.T) {
	calls := 0
	q := queue(t, func(context.Context, store.Principal, Document) error {
		calls++
		return errors.New("upstream 503")
	})
	q.MaxAttempts = 3
	job, _, _ := q.Submit(context.Background(), admin, "doc", "标题", "正文")
	drain(t, q)
	got := status(t, q, store.Text(job, "id"))
	if store.Text(got, "status") != "failed" || calls != 3 || !strings.Contains(store.Text(got, "last_error"), "503") {
		t.Fatalf("calls=%d job=%v", calls, got)
	}
	q.Send = func(context.Context, store.Principal, Document) error { return nil }
	if _, err := q.Store.RetryIngest(context.Background(), admin, store.Text(job, "id")); err != nil {
		t.Fatal(err)
	}
	drain(t, q)
	if store.Text(status(t, q, store.Text(job, "id")), "status") != "succeeded" {
		t.Fatal("manual retry should recover a dead-lettered job")
	}
	q.Send = func(context.Context, store.Principal, Document) error { return Permanent{errors.New("403")} }
	job, _, _ = q.Submit(context.Background(), admin, "doc2", "标题", "正文")
	drain(t, q)
	if got = status(t, q, store.Text(job, "id")); store.Text(got, "status") != "failed" || store.Int(got, "attempts") != 1 {
		t.Fatalf("permanent errors are not retried: %v", got)
	}
}
func TestExpiredLeaseIsReclaimed(t *testing.T) {
	q := queue(t, func(context.Context, store.Principal, Document) error { return nil })
	q.Submit(context.Background(), admin, "doc", "标题", "正文")
	if job, _ := q.Store.ClaimIngest(context.Background(), -time.Second); job == nil {
		t.Fatal("job should be claimable")
	}
	job, _ := q.Store.ClaimIngest(context.Background(), time.Minute)
	if job == nil || job.Attempts != 2 {
		t.Fatalf("a crashed worker's expired lease must be reclaimed: %+v", job)
	}
	if again, _ := q.Store.ClaimIngest(context.Background(), time.Minute); again != nil {
		t.Fatal("a live lease must not be claimed twice")
	}
}
func TestSubmitRequiresAdminAndValidDocument(t *testing.T) {
	q := queue(t, nil)
	if _, _, err := q.Submit(context.Background(), store.Principal{Tenant: "acme", User: "u", Roles: []string{"staff"}}, "doc", "t", "c"); err == nil {
		t.Fatal("staff cannot submit")
	}
	if _, _, err := q.Submit(context.Background(), admin, "bad id", "t", "c"); err == nil {
		t.Fatal("invalid document id accepted")
	}
}
