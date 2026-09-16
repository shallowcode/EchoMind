-- Schema snapshot; authoritative initializer: supportflow/store.py

CREATE TABLE audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, actor TEXT, action TEXT, target TEXT, detail TEXT, created REAL);

CREATE TABLE conversations (tenant TEXT, id TEXT, user TEXT, state TEXT, version INTEGER DEFAULT 0, lease_owner TEXT, lease_until REAL DEFAULT 0, PRIMARY KEY(tenant,id));

CREATE TABLE knowledge (tenant TEXT, id TEXT, title TEXT, content TEXT, version TEXT, PRIMARY KEY(tenant,id));

CREATE TABLE messages (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, conv TEXT, role TEXT, content TEXT, created REAL);

CREATE TABLE orders (tenant TEXT, id TEXT, user TEXT, total INTEGER, refunded INTEGER DEFAULT 0, status TEXT, PRIMARY KEY(tenant,id));

CREATE TABLE payment_events (id TEXT PRIMARY KEY, refund_id TEXT, created REAL);

CREATE TABLE payment_outbox (refund_id TEXT PRIMARY KEY, tenant TEXT, payload TEXT, status TEXT, attempts INTEGER DEFAULT 0, lease_until REAL DEFAULT 0, last_error TEXT);

CREATE TABLE profiles (tenant TEXT, user TEXT, payload TEXT, PRIMARY KEY(tenant,user));

CREATE TABLE refunds (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, order_id TEXT, amount INTEGER, status TEXT, idem TEXT, reason TEXT, payment_ref TEXT, UNIQUE(tenant,user,idem));

CREATE TABLE requests (tenant TEXT, user TEXT, id TEXT, fingerprint TEXT, response TEXT, PRIMARY KEY(tenant,user,id));

CREATE TABLE tickets (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, conv TEXT, summary TEXT, status TEXT, assignee TEXT, resolution TEXT, idem TEXT, version INTEGER DEFAULT 0, UNIQUE(tenant,user,idem));

CREATE TABLE tokens (hash TEXT PRIMARY KEY, tenant TEXT, user TEXT, roles TEXT, expires REAL, revoked INTEGER DEFAULT 0);

CREATE TABLE traces (tenant TEXT, user TEXT, id TEXT PRIMARY KEY, payload TEXT);
