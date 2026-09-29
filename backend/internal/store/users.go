package store

import (
	"context"
	"encoding/json"
	"golang.org/x/crypto/bcrypt"
)

func (s *Store) Login(ctx context.Context, tenant, user, password string) (Principal, error) {
	var hash, roles string
	var disabled int
	err := s.DB.QueryRowContext(ctx, "SELECT password_hash,roles,disabled FROM users WHERE tenant=? AND id=?", tenant, user).Scan(&hash, &roles, &disabled)
	if err != nil || disabled != 0 || bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) != nil {
		return Principal{}, &Error{401, "invalid_credentials", "租户、账号或密码错误"}
	}
	p := Principal{Tenant: tenant, User: user}
	_ = json.Unmarshal([]byte(roles), &p.Roles)
	return p, nil
}
func (s *Store) CreateUser(ctx context.Context, p Principal, a Data) (Data, error) {
	if !p.Has("admin") {
		return nil, Denied()
	}
	user, password, name := Text(a, "user"), Text(a, "password"), Text(a, "name")
	if !allowedID(user) || len(user) > 80 || len(password) < 10 || len(password) > 72 || name == "" {
		return nil, Invalid("账号有效，名称必填，密码须为 10–72 字节")
	}
	roles := []string{}
	raw, ok := a["roles"].([]any)
	if !ok || len(raw) == 0 {
		return nil, Invalid("至少选择一个角色")
	}
	for _, v := range raw {
		role, ok := v.(string)
		if !ok || !(role == "customer" || role == "staff" || role == "finance" || role == "ops" || role == "admin") {
			return nil, Invalid("未知角色")
		}
		roles = append(roles, role)
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}
	tx, err := s.DB.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()
	t := &transaction{tx: tx, ctx: ctx}
	if t.one("SELECT id FROM users WHERE tenant=? AND id=?", p.Tenant, user) != nil {
		return nil, Conflict("账号已存在")
	}
	t.exec("INSERT INTO users VALUES(?,?,?,?,?,0,?)", p.Tenant, user, name, string(hash), JSON(roles), Now())
	t.audit(p, "user.create", user, Data{"roles": roles})
	if t.err != nil {
		return nil, t.err
	}
	if err = tx.Commit(); err != nil {
		return nil, err
	}
	return Data{"user": user, "name": name, "roles": roles}, nil
}
func (s *Store) Users(ctx context.Context, p Principal) ([]Data, error) {
	if !p.Has("admin") {
		return nil, Denied()
	}
	tx, err := s.DB.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()
	t := &transaction{tx: tx, ctx: ctx}
	r := t.rows("SELECT id user,name,roles,disabled,created FROM users WHERE tenant=? ORDER BY created DESC", p.Tenant)
	for _, u := range r {
		roles := []string{}
		_ = json.Unmarshal([]byte(Text(u, "roles")), &roles)
		u["roles"] = roles
	}
	return r, t.err
}

func (s *Store) SetUserDisabled(ctx context.Context, p Principal, user string, disabled bool) (Data, error) {
	if !p.Has("admin") || p.User == user {
		return nil, Denied()
	}
	tx, err := s.DB.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()
	t := &transaction{tx: tx, ctx: ctx}
	if t.one("SELECT id FROM users WHERE tenant=? AND id=?", p.Tenant, user) == nil {
		return nil, &Error{404, "not_found", "账号不存在"}
	}
	t.exec("UPDATE users SET disabled=? WHERE tenant=? AND id=?", disabled, p.Tenant, user)
	if disabled {
		t.exec("UPDATE tokens SET revoked=1 WHERE tenant=? AND user=?", p.Tenant, user)
	}
	t.audit(p, "user.access", user, Data{"disabled": disabled})
	if t.err != nil {
		return nil, t.err
	}
	if err = tx.Commit(); err != nil {
		return nil, err
	}
	return Data{"user": user, "disabled": disabled}, nil
}
