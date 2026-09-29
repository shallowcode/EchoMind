"""Explicit offline double for architecture smoke tests, never a model quality result."""
import json
from types import SimpleNamespace
from supportflow.api import create_app
from supportflow.contracts import Settings


class OfflineModel:
    def __init__(self, settings):
        self.settings = settings
        self.messages = self

    async def close(self):
        pass

    async def create(self, **kwargs):
        return SimpleNamespace(content=[SimpleNamespace(type='text', text=json.dumps({'intent': 'other', 'confidence': 1}))])

    async def complete(self, messages, system='', **kwargs):
        return json.dumps({'answer': '离线结构测试', 'tool_calls': []})


settings = Settings.from_env()
if settings.model_backend != 'fixture':
    raise RuntimeError('Fixture worker requires explicit SF_MODEL_BACKEND=fixture')
app = create_app(settings, OfflineModel(settings))
