"""Build and launch the Go business API + private Python AI worker."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import subprocess
import sys
import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.start_local import occupied, launch, wait_ready, get


def migrate_databases(source, directory):
    """One-time, consistent SQLite snapshots. Never overwrite an existing database."""
    directory.mkdir(parents=True, exist_ok=True)
    business, ai = directory / 'supportflow-business.sqlite3', directory / 'supportflow-ai.sqlite3'
    if business.exists() and ai.exists():
        return business, ai
    snapshot = None
    if source.is_file():
        backups = directory / 'backups'
        backups.mkdir(exist_ok=True)
        snapshot = backups / ('before-go-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '.sqlite3')
        with sqlite3.connect(source) as src, sqlite3.connect(snapshot) as dst:
            src.backup(dst)
        if not business.exists():
            with sqlite3.connect(snapshot) as src, sqlite3.connect(business) as dst:
                src.backup(dst)
    from supportflow.store import Store
    Store(str(business))
    if not ai.exists():
        Store(str(ai))
        if snapshot:
            with sqlite3.connect(snapshot) as src, sqlite3.connect(ai) as dst:
                dst.executemany('INSERT INTO knowledge VALUES(?,?,?,?,?)', src.execute('SELECT * FROM knowledge').fetchall())
    manifest = {'source': str(source), 'snapshot': str(snapshot) if snapshot else None,
                'business': str(business), 'ai': str(ai), 'migrated_at': datetime.now(timezone.utc).isoformat()}
    (directory / 'go-migration.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return business, ai


def stop_managed(path):
    """Only stop processes whose command and working directory still match this launch."""
    import psutil
    metadata = json.loads(path.read_text(encoding='utf-8'))
    processes = []
    for name, pid in metadata['pids'].items():
        try:
            process = psutil.Process(pid)
            command = process.cmdline()
            matches = ('uvicorn' in command and any(entry in command for entry in ('api.main:app', 'scripts.fixture_worker:app'))) if name == 'ai' else Path(command[0]).resolve() == Path(metadata['binary']).resolve()
            if not matches or Path(process.cwd()).resolve() != ROOT or abs(process.create_time() - metadata['started'][name]) > 1:
                raise RuntimeError(f'Process {pid} no longer matches the managed {name} service')
            # Windows venv launchers can spawn a second python.exe. Stop the
            # verified worker before its launcher so no listening child is left.
            if name == 'ai':
                for child in process.children(recursive=True):
                    args = child.cmdline()
                    if ('uvicorn' in args and any(entry in args for entry in ('api.main:app', 'scripts.fixture_worker:app'))
                            and Path(child.cwd()).resolve() == ROOT):
                        processes.append(child)
            processes.append(process)
        except psutil.NoSuchProcess:
            continue
    for process in processes:
        try:
            process.terminate()
        except psutil.NoSuchProcess:
            pass
    _, alive = psutil.wait_procs(processes, timeout=20)
    if alive:
        raise RuntimeError('Service is still stopping; retry after active requests finish')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8002)
    parser.add_argument('--ai-port', type=int, default=8003)
    parser.add_argument('--env-file', default='.runtime/glm.env')
    parser.add_argument('--data-dir', default='data')
    parser.add_argument('--source-db', default='data/supportflow-glm.sqlite3')
    parser.add_argument('--fixture', action='store_true', help='Offline deterministic model for tests')
    parser.add_argument('--no-demo', action='store_true', help='Require real accounts; set SF_ADMIN_PASSWORD on first launch')
    parser.add_argument('--restart', action='store_true')
    args = parser.parse_args()
    runtime = ROOT / '.runtime'
    runtime.mkdir(exist_ok=True)
    meta_path = runtime / f'product-{args.port}.json'
    if args.restart and meta_path.exists():
        stop_managed(meta_path)
    if args.port == args.ai_port:
        raise RuntimeError('Public and private ports must differ')
    if occupied(args.port) or occupied(args.ai_port):
        health = get(f'http://127.0.0.1:{args.port}/ready') or {}
        if health.get('runtime', {}).get('backend') == 'Go' and not args.restart:
            print(f'supportFlow is already running: http://127.0.0.1:{args.port}/')
            return
        raise RuntimeError('Port already occupied; stop the previous service or choose unused ports')
    go = shutil.which('go') or str(runtime / 'toolchains/go/bin' / ('go.exe' if sys.platform == 'win32' else 'go'))
    if not Path(go).is_file():
        raise RuntimeError('Install Go 1.27+ from https://go.dev/dl/ and retry')
    config = (ROOT / args.env_file).resolve()
    if not args.fixture and not config.is_file():
        raise RuntimeError('Create a private model configuration using .env.supportflow.example')
    binary = runtime / (f'supportflow-go-{args.port}' + ('.exe' if sys.platform == 'win32' else ''))
    subprocess.run([go, 'build', '-o', str(binary), './cmd/server'], cwd=ROOT / 'backend', check=True)
    business, ai = migrate_databases((ROOT / args.source_db).resolve(), (ROOT / args.data_dir).resolve())
    key_path = runtime / 'product-service.key'
    if not key_path.exists():
        key_path.write_text(secrets.token_urlsafe(48), encoding='utf-8')
        key_path.chmod(0o600)
    from dotenv import dotenv_values
    config_values = {k: v for k, v in dotenv_values(config).items() if v is not None} if config.is_file() else {}
    env = {**os.environ, **config_values, 'SF_ENV_FILE': str(config),
           'SF_DB_PATH': str(ai), 'SF_BUSINESS_DB': str(business),
           'SF_BUSINESS_URL': f'http://127.0.0.1:{args.port}', 'SF_AI_URL': f'http://127.0.0.1:{args.ai_port}',
           'SF_PUBLIC_URL': f'http://localhost:{args.port}', 'SF_SERVICE_KEY': key_path.read_text(encoding='utf-8'),
           'SF_FRONTEND': str(ROOT / 'frontend'), 'SF_LOCAL_DEMO_ACCESS': str(not args.no_demo).lower(),
           'SF_BUSINESS_MODE': 'sandbox', 'SF_CHROMA_PATH': str(ROOT / 'data/supportflow-glm-chroma')}
    if args.fixture:
        env.update(SF_MODEL_BACKEND='fixture', SF_STORAGE='sqlite', SF_MODEL_NAME='fixture', SF_MODEL_KEY='')
    # Fresh installations get knowledge only. Existing merchant orders are never reseeded.
    with sqlite3.connect(ai) as db:
        needs_knowledge = db.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0] == 0
    if needs_knowledge:
        subprocess.run([sys.executable, '-c', "from supportflow.contracts import Settings; from supportflow.store import Store; from supportflow.knowledge import Knowledge; import os; s=Settings.from_env(); Knowledge(Store(s.db_path),s,None).seed(os.environ.get('SF_ADMIN_TENANT','demo'))"], cwd=ROOT, env=env, check=True)
    pids = {}
    try:
        pids['go'] = launch([str(binary), '-addr', f'127.0.0.1:{args.port}'], f'product-go-{args.port}', env)
        wait_ready(f'http://127.0.0.1:{args.port}/health', seconds=20)
        pids['ai'] = launch([sys.executable, '-m', 'uvicorn', 'scripts.fixture_worker:app' if args.fixture else 'api.main:app', '--host', '127.0.0.1', '--port', str(args.ai_port), '--no-proxy-headers'], f'product-ai-{args.port}', env)
        wait_ready(f'http://127.0.0.1:{args.port}/ready', seconds=90)
    finally:
        import psutil
        started = {}
        for name,pid in pids.items():
            try:
                started[name] = psutil.Process(pid).create_time()
            except psutil.NoSuchProcess:
                started[name] = 0
        meta_path.write_text(json.dumps({'pids': pids, 'started': started, 'binary': str(binary), 'port': args.port, 'ai_port': args.ai_port}, indent=2), encoding='utf-8')
    print(f'supportFlow ready: http://127.0.0.1:{args.port}/ | /admin | /desk | /lab')
    print('Business: Go; AI: Python; local demo: ' + str(not args.no_demo))


if __name__ == '__main__':
    main()
