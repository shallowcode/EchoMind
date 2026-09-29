// Package store owns the transactional business database. The AI service never opens it.
package store

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"database/sql"
	_ "embed"
	"encoding/hex"
	"encoding/json"

	"fmt"
	"os"
	"path/filepath"
	"strconv"

	"time"

	_ "modernc.org/sqlite"
)

//go:embed schema.sql
var schema string

type Data = map[string]any
type Principal struct {
	Tenant string   `json:"tenant"`
	User   string   `json:"user"`
	Roles  []string `json:"roles"`
}

func (p Principal) Has(roles ...string) bool {
	for _, own := range p.Roles {
		if own == "admin" {
			return true
		}
		for _, role := range roles {
			if own == role {
				return true
			}
		}
	}
	return false
}
func (p Principal) Demo() bool {
	if p.Tenant != "demo" {
		return false
	}
	for _, role := range p.Roles {
		if role == "demo_customer" {
			return true
		}
	}
	return false
}

type Error struct {
	Status        int
	Code, Message string
}

func (e *Error) Error() string      { return e.Message }
func Denied() error                 { return &Error{403, "forbidden", "当前身份无权访问此记录"} }
func Conflict(s string) error       { return &Error{409, "conflict", s} }
func Invalid(s string) error        { return &Error{422, "invalid", s} }
func Business(code, s string) error { return &Error{409, code, s} }
func Text(d Data, k string) string  { v, _ := d[k].(string); return v }
func Int(d Data, k string) int64 {
	switch v := d[k].(type) {
	case json.Number:
		n, _ := v.Int64()
		return n
	case float64:
		return int64(v)
	case int64:
		return v
	case int:
		return int64(v)
	}
	return 0
}
func Bool(d Data, k string) bool { v, _ := d[k].(bool); return v }
func JSON(v any) string          { b, _ := json.Marshal(v); return string(b) }
func object(v any) Data {
	if d, ok := v.(map[string]any); ok {
		return d
	}
	return Data{}
}
func Parse(s string) Data { d := Data{}; _ = json.Unmarshal([]byte(s), &d); return d }
func ID(prefix string) string {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil {
		panic(err)
	}
	return prefix + hex.EncodeToString(b)
}
func Hash(s string) string { v := sha256.Sum256([]byte(s)); return hex.EncodeToString(v[:]) }
func Now() float64         { return float64(time.Now().UnixMilli()) / 1000 }

type Store struct{ DB *sql.DB }

func Open(path string) (*Store, error) {
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		return nil, err
	}
	db, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(1)
	if _, err = db.Exec("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=10000;" + schema); err != nil {
		db.Close()
		return nil, err
	}
	return &Store{db}, nil
}
func (s *Store) Close() error { return s.DB.Close() }

type transaction struct {
	tx  *sql.Tx
	ctx context.Context
	err error
}

func (t *transaction) exec(q string, a ...any) int64 {
	if t.err != nil {
		return 0
	}
	r, err := t.tx.ExecContext(t.ctx, q, a...)
	if err != nil {
		t.err = err
		return 0
	}
	n, _ := r.RowsAffected()
	return n
}
func (t *transaction) rows(q string, a ...any) []Data {
	out := []Data{}
	if t.err != nil {
		return out
	}
	rows, err := t.tx.QueryContext(t.ctx, q, a...)
	if err != nil {
		t.err = err
		return out
	}
	defer rows.Close()
	cols, err := rows.Columns()
	if err != nil {
		t.err = err
		return out
	}
	for rows.Next() {
		vals := make([]any, len(cols))
		ptrs := make([]any, len(cols))
		for i := range vals {
			ptrs[i] = &vals[i]
		}
		if err := rows.Scan(ptrs...); err != nil {
			t.err = err
			return out
		}
		r := Data{}
		for i, c := range cols {
			if b, ok := vals[i].([]byte); ok {
				r[c] = string(b)
			} else {
				r[c] = vals[i]
			}
		}
		out = append(out, r)
	}
	t.err = rows.Err()
	return out
}
func (t *transaction) one(q string, a ...any) Data {
	rows := t.rows(q, a...)
	if len(rows) == 0 {
		return nil
	}
	return rows[0]
}
func (t *transaction) audit(p Principal, action, target string, detail any) {
	t.exec("INSERT INTO audit(tenant,actor,action,target,detail,created) VALUES(?,?,?,?,?,?)", p.Tenant, p.User, action, target, JSON(detail), Now())
	t.event(p.Tenant, "", action, Data{"target": target})
}
func (t *transaction) event(tenant, conv, kind string, payload any) {
	t.exec("INSERT INTO events(tenant,conv,kind,payload,created) VALUES(?,?,?,?,?)", tenant, conv, kind, JSON(payload), Now())
}
func (t *transaction) mode(p Principal, conv string) Data {
	r := t.one("SELECT * FROM conversation_modes WHERE tenant=? AND conv=?", p.Tenant, conv)
	if r == nil {
		return Data{"mode": "ai", "assignee": "", "version": int64(0)}
	}
	return r
}
func (s *Store) Run(ctx context.Context, p Principal, op string, a Data) (any, error) {
	tx, err := s.DB.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()
	t := &transaction{tx: tx, ctx: ctx}
	v, err := t.run(p, op, a)
	if err != nil {
		return nil, err
	}
	if t.err != nil {
		return nil, fmt.Errorf("database operation: %w", t.err)
	}
	if err = tx.Commit(); err != nil {
		return nil, err
	}
	return v, nil
}
func (s *Store) Authenticate(ctx context.Context, token string) (Principal, error) {
	v, err := s.Run(ctx, Principal{}, "authenticate", Data{"token": token})
	if err != nil {
		return Principal{}, err
	}
	return v.(Principal), nil
}
func Integer(raw string, fallback int64) int64 {
	n, err := strconv.ParseInt(raw, 10, 64)
	if err != nil {
		return fallback
	}
	return n
}
func limit(a Data) (int64, int64) {
	n := Int(a, "limit")
	if n <= 0 {
		n = 20
	}
	if n > 100 {
		n = 100
	}
	o := Int(a, "offset")
	if o < 0 {
		o = 0
	}
	return n, o
}
func allowedID(s string) bool {
	if len(s) < 1 || len(s) > 100 {
		return false
	}
	for _, r := range s {
		if !(r >= 'a' && r <= 'z' || r >= 'A' && r <= 'Z' || r >= '0' && r <= '9' || r == '_' || r == '-') {
			return false
		}
	}
	return true
}
