"""Run the resume's Python service; real Redis and Chroma are required."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default=".env.resume")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--fixture", action="store_true", help="Offline model only; still uses real storage")
    args = parser.parse_args()
    os.chdir(ROOT)
    from dotenv import load_dotenv

    from supportflow.contracts import Settings

    os.environ["SF_ENV_FILE"] = str((ROOT / args.env_file).resolve())
    load_dotenv(os.environ["SF_ENV_FILE"], override=True)
    os.environ.setdefault("SF_DB_PATH", "data/supportflow-resume.sqlite3")
    os.environ["SF_REQUIRE_MEMORY_SERVICES"] = "true"
    if args.fixture:
        os.environ["SF_MODEL_BACKEND"] = "fixture"
        os.environ["SF_MODEL_NAME"] = "fixture"
    settings = Settings.from_env()
    if settings.business_url or settings.storage != "chroma" or not settings.redis_url:
        raise RuntimeError("Resume profile requires standalone FastAPI, SF_STORAGE=chroma and SF_REDIS_URL")
    if settings.model_backend != "fixture" and not settings.model_key:
        raise RuntimeError("Set SF_MODEL_KEY in the private resume configuration, or use --fixture for logic checks")
    subprocess.run([sys.executable, "scripts/bootstrap_supportflow.py", "--output",
                    ".runtime/resume-demo-tokens.json"], check=True)
    import uvicorn

    uvicorn.run("api.main:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
