
            CREATE TABLE IF NOT EXISTS tokens (hash TEXT PRIMARY KEY, tenant TEXT, user TEXT, roles TEXT, expires REAL, revoked INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS orders (tenant TEXT, id TEXT, user TEXT, total INTEGER, refunded INTEGER DEFAULT 0, status TEXT, PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS deleted_orders (tenant TEXT, order_id TEXT, deleted REAL NOT NULL, PRIMARY KEY(tenant,order_id));
            CREATE TABLE IF NOT EXISTS order_details (tenant TEXT, order_id TEXT, product TEXT NOT NULL, quantity INTEGER NOT NULL, created REAL NOT NULL, updated REAL NOT NULL, version INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(tenant,order_id));
            CREATE TABLE IF NOT EXISTS refunds (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, order_id TEXT, amount INTEGER, status TEXT, idem TEXT, reason TEXT, payment_ref TEXT, UNIQUE(tenant,user,idem));
            CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, conv TEXT, summary TEXT, status TEXT, assignee TEXT, resolution TEXT, idem TEXT, version INTEGER DEFAULT 0, UNIQUE(tenant,user,idem));
            CREATE TABLE IF NOT EXISTS conversations (tenant TEXT, id TEXT, user TEXT, state TEXT, version INTEGER DEFAULT 0, lease_owner TEXT, lease_until REAL DEFAULT 0, PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS messages (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, conv TEXT, role TEXT, content TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS requests (tenant TEXT, user TEXT, id TEXT, fingerprint TEXT, response TEXT, PRIMARY KEY(tenant,user,id));
            CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, actor TEXT, action TEXT, target TEXT, detail TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS knowledge (tenant TEXT, id TEXT, title TEXT, content TEXT, version TEXT, PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS traces (tenant TEXT, user TEXT, id TEXT PRIMARY KEY, payload TEXT);
            CREATE TABLE IF NOT EXISTS payment_outbox (refund_id TEXT PRIMARY KEY, tenant TEXT, payload TEXT, status TEXT, attempts INTEGER DEFAULT 0, lease_until REAL DEFAULT 0, last_error TEXT);
            CREATE TABLE IF NOT EXISTS payment_events (id TEXT PRIMARY KEY, refund_id TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS profiles (tenant TEXT, user TEXT, payload TEXT, PRIMARY KEY(tenant,user));
            
CREATE TABLE IF NOT EXISTS users (tenant TEXT NOT NULL,id TEXT NOT NULL,name TEXT NOT NULL,password_hash TEXT NOT NULL,roles TEXT NOT NULL,disabled INTEGER NOT NULL DEFAULT 0,created REAL NOT NULL,PRIMARY KEY(tenant,id));
CREATE TABLE IF NOT EXISTS conversation_modes (tenant TEXT NOT NULL,conv TEXT NOT NULL,mode TEXT NOT NULL DEFAULT 'ai',assignee TEXT NOT NULL DEFAULT '',version INTEGER NOT NULL DEFAULT 0,updated REAL NOT NULL,PRIMARY KEY(tenant,conv));
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT,tenant TEXT NOT NULL,conv TEXT NOT NULL DEFAULT '',kind TEXT NOT NULL,payload TEXT NOT NULL,created REAL NOT NULL);
CREATE INDEX IF NOT EXISTS events_tenant_id ON events(tenant,id);
CREATE INDEX IF NOT EXISTS messages_conv ON messages(tenant,conv,seq);
CREATE INDEX IF NOT EXISTS refunds_order_status ON refunds(tenant,order_id,status);
CREATE INDEX IF NOT EXISTS tickets_queue ON tickets(tenant,status);
CREATE TABLE IF NOT EXISTS human_requests (tenant TEXT NOT NULL,actor TEXT NOT NULL,id TEXT NOT NULL,fingerprint TEXT NOT NULL,response TEXT NOT NULL,PRIMARY KEY(tenant,actor,id));
CREATE TABLE IF NOT EXISTS message_details (seq INTEGER PRIMARY KEY,tenant TEXT NOT NULL,conv TEXT NOT NULL,actor TEXT NOT NULL,request_id TEXT NOT NULL,execution TEXT NOT NULL DEFAULT '{}');
CREATE INDEX IF NOT EXISTS message_details_request ON message_details(tenant,actor,request_id);
CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY,applied REAL NOT NULL);
INSERT OR IGNORE INTO schema_migrations VALUES(1,unixepoch());
-- Upgrade legacy open tickets into the reception queue without changing existing modes.
INSERT OR IGNORE INTO conversation_modes(tenant,conv,mode,assignee,version,updated)
SELECT DISTINCT tenant,conv,'waiting','',0,unixepoch() FROM tickets
WHERE status IN ('open','assigned') AND NOT EXISTS(SELECT 1 FROM schema_migrations WHERE version=2);
INSERT OR IGNORE INTO schema_migrations VALUES(2,unixepoch());
