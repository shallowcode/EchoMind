"""Container worker entry point. Seed knowledge on first install, never business data."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from supportflow.contracts import Settings
from supportflow.store import Store
from supportflow.knowledge import Knowledge

settings = Settings.from_env()
if not settings.business_url:
    raise RuntimeError('SF_BUSINESS_URL is required for the private worker')
store = Store(settings.db_path)
tenant = os.environ.get('SF_ADMIN_TENANT', 'demo')
with store.tx() as db:
    empty = not db.execute('SELECT 1 FROM knowledge WHERE tenant=? LIMIT 1', (tenant,)).fetchone()
if empty:
    Knowledge(store, settings, None).seed(tenant)
os.execv(sys.executable, [sys.executable, '-m', 'uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000', '--no-proxy-headers'])
