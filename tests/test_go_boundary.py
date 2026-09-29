"""Worker isolation and one-time migration can run without the Go toolchain."""
import sqlite3
from fastapi.testclient import TestClient
from supportflow.api import create_app
from supportflow.contracts import Settings, Principal
from supportflow.store import Store
from scripts.start_product import migrate_databases
from tests.test_supportflow import ScriptedModel


def test_private_ai_worker_rejects_direct_business_and_chat(tmp_path):
    settings = Settings(db_path=str(tmp_path / 'ai.sqlite3'), model_backend='fixture',
                        business_url='http://127.0.0.1:1', service_key='k' * 40)
    with TestClient(create_app(settings, ScriptedModel(settings))) as client:
        assert client.get('/health').status_code == 200
        assert client.post('/chat', json={}).status_code == 403
        assert client.post('/auth/demo-customer').status_code == 403
        for route in ['/merchant/orders', '/orders', '/auth/me', '/tickets', '/docs']:
            assert client.get(route, headers={'X-SupportFlow-Service-Key': settings.service_key}).status_code == 404


def test_migration_keeps_business_and_separates_knowledge_without_overwrite(tmp_path):
    source = tmp_path / 'legacy.sqlite3'
    legacy = Store(source)
    legacy.seed_order(Principal('demo', 'admin', frozenset({'admin'})), 'ORD1001', 8800, 'alice')
    with legacy.tx() as db:
        db.execute('INSERT INTO knowledge VALUES(?,?,?,?,?)', ('demo', 'doc', '标题', '内容', 'v1'))
    business, ai = migrate_databases(source, tmp_path / 'new')
    with sqlite3.connect(business) as db:
        assert db.execute('SELECT total FROM orders').fetchone()[0] == 8800
        db.execute("UPDATE orders SET status='shipped'")
    with sqlite3.connect(ai) as db:
        assert db.execute('SELECT COUNT(*) FROM orders').fetchone()[0] == 0
        assert db.execute('SELECT content FROM knowledge').fetchone()[0] == '内容'
    migrate_databases(source, tmp_path / 'new')
    with sqlite3.connect(business) as db:
        assert db.execute('SELECT status FROM orders').fetchone()[0] == 'shipped'
    with sqlite3.connect(source) as db:
        assert db.execute('SELECT status FROM orders').fetchone()[0] == 'paid'
    assert len(list((tmp_path / 'new/backups').glob('*.sqlite3'))) == 1
