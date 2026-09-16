"""Start the local sandbox without a visible helper window; never stop occupied ports."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return json.load(response)
    except Exception:
        return None


def occupied(port):
    with socket.socket() as connection:
        connection.settimeout(0.5)
        return connection.connect_ex(("127.0.0.1", port)) == 0


def launch(args, name, env):
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    with (RUNTIME / f"{name}.log").open("ab") as output:
        return subprocess.Popen(
            args,
            cwd=ROOT,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
            creationflags=flags,
            start_new_session=sys.platform != "win32",
        ).pid


def wait_ready(url, seconds=60):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if get(url):
            return
        time.sleep(0.5)
    raise RuntimeError(f"Service not ready: {url}; inspect .runtime logs")


def main():
    RUNTIME.mkdir(exist_ok=True)
    model = RUNTIME / "Qwen3-1.7B-Q8_0.gguf"
    binary = RUNTIME / "llama/llama-server.exe"
    if not model.exists() or not binary.exists():
        raise RuntimeError("Run scripts/prepare_local_model.py --size 1.7B first")
    env = {
        **os.environ,
        "SF_MODEL_BACKEND": "compatible",
        "SF_MODEL_URL": "http://127.0.0.1:8081/v1",
        "SF_MODEL_NAME": "Qwen3-1.7B-Q8_0",
        "SF_MODEL_KEY": "",
        "SF_LOCAL_CHAT_TEMPLATE": "true",
        "SF_STORAGE": "chroma",
        "SF_BUSINESS_MODE": "sandbox",
        "SF_PUBLIC_URL": "http://localhost:8000",
    }
    pids = {}
    if occupied(8081):
        models = get("http://127.0.0.1:8081/v1/models") or {}
        if not any("1.7B" in m.get("id", "") for m in models.get("data", [])):
            raise RuntimeError(
                "Port 8081 is occupied by a different/unverified model server"
            )
    else:
        pids["model"] = launch(
            [
                str(binary),
                "-m",
                ".runtime/Qwen3-1.7B-Q8_0.gguf",
                "--host",
                "127.0.0.1",
                "--port",
                "8081",
                "-c",
                "16384",
                "-np",
                "2",
                "-t",
                "6",
                "--jinja",
            ],
            "local-model",
            env,
        )
    wait_ready("http://127.0.0.1:8081/health")
    if occupied(8000):
        info = get("http://127.0.0.1:8000/openapi.json") or {}
        if info.get("info", {}).get("title") != "SupportFlow":
            raise RuntimeError("Port 8000 is occupied by another service")
    else:
        subprocess.run(
            [sys.executable, "scripts/bootstrap_supportflow.py"],
            cwd=ROOT,
            env=env,
            check=True,
        )
        pids["api"] = launch(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            "local-api",
            env,
        )
    wait_ready("http://127.0.0.1:8000/health")
    (RUNTIME / "local-processes.json").write_text(
        json.dumps(pids, indent=2), encoding="utf-8"
    )
    print("SupportFlow ready: http://127.0.0.1:8000/docs")
    print(
        "Credentials: .runtime/demo-tokens.json (not printed); created process IDs:",
        pids,
    )


if __name__ == "__main__":
    main()
