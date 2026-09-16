"""Run: uvicorn api.supportflow:app --host 127.0.0.1 --port 8000."""

from supportflow.api import create_app

app = create_app()
