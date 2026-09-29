"""Launch the configured GLM sandbox in a hidden process on a separate local port."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.start_local import occupied, launch, wait_ready


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8002)
    parser.add_argument("--env-file", default=".runtime/glm.env")
    args = parser.parse_args()
    config = (ROOT / args.env_file).resolve()
    if not config.is_file():
        raise RuntimeError(
            "Create the private GLM configuration from .env.supportflow.example first"
        )
    if occupied(args.port):
        raise RuntimeError(
            f"Port {args.port} is already occupied; use that service or choose another port"
        )
    env = {
        **os.environ,
        "SF_ENV_FILE": str(config),
        "SF_DB_PATH": "data/supportflow-glm.sqlite3",
        "SF_CHROMA_PATH": "data/supportflow-glm-chroma",
        "SF_PUBLIC_URL": f"http://localhost:{args.port}",
        "SF_LOCAL_DEMO_ACCESS": "true",
    }
    # Use the selected file rather than stale model settings inherited from a local run.
    for field in [
        "MODEL_BACKEND",
        "MODEL_URL",
        "MODEL_NAME",
        "MODEL_KEY",
        "LOCAL_CHAT_TEMPLATE",
        "SUPPORTS_JSON_SCHEMA",
        "MODEL_THINKING",
        "PRICING_PROFILE",
    ]:
        env.pop("SF_" + field, None)
    subprocess.run(
        [
            sys.executable,
            "scripts/bootstrap_supportflow.py",
            "--output",
            ".runtime/glm-demo-tokens.json",
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )
    pid = launch(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.port),
        ],
        "glm-api",
        env,
    )
    wait_ready(f"http://127.0.0.1:{args.port}/health")
    (ROOT / ".runtime/glm-service.json").write_text(
        json.dumps({"pid": pid, "port": args.port}), encoding="utf-8"
    )
    print(f"EchoMind ready: http://127.0.0.1:{args.port}/; PID {pid}")


if __name__ == "__main__":
    if '--legacy' in sys.argv:
        sys.argv.remove('--legacy')
        main()
    else:
        from scripts.start_product import main as product_main
        product_main()
