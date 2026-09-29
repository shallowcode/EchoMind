"""Provider-neutral completion API with real usage accounting and no implicit paid fallback."""

import contextvars
import copy
import json
import re
import time
from types import SimpleNamespace
import httpx
from supportflow.contracts import Settings, Trace
from supportflow.pricing import estimate_call

active_trace: contextvars.ContextVar[Trace | None] = contextvars.ContextVar(
    "trace", default=None
)


class Model:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=settings.model_timeout)
        self.messages = self  # adapter for the existing IntentRecognizer / BaseAgent

    async def close(self):
        await self.client.aclose()

    async def complete(self, messages, system="", max_tokens=384, json_mode=False, purpose="模型调用"):
        s = self.settings
        if s.model_backend == "fixture":
            raise RuntimeError(
                "Fixture backend requires an explicitly injected test double"
            )
        start = time.perf_counter()
        trace = active_trace.get()
        if trace:
            trace.model_calls += 1
        captured = None

        def capture(payload):
            if not trace:
                return None
            record = {"index": len(trace.model_inputs) + 1, "purpose": purpose,
                      "provider": s.model_backend, "request": copy.deepcopy(payload), "status": "running"}
            trace.model_inputs.append(record)
            return record
        try:
            if s.model_backend == "compatible":
                data = {
                    "model": s.model_name,
                    "messages": (
                        [{"role": "system", "content": system}] if system else []
                    )
                    + messages,
                    "temperature": 0,
                    "max_tokens": max_tokens,
                    "stream": False,
                }
                if s.local_chat_template:
                    data["chat_template_kwargs"] = {"enable_thinking": False}
                if s.model_thinking:
                    data["thinking"] = {"type": s.model_thinking}
                if isinstance(json_mode, dict) and not s.supports_json_schema:
                    data["messages"] = [
                        {
                            "role": "system",
                            "content": system
                            + "\n只输出符合以下 JSON Schema 的 JSON 对象："
                            + json.dumps(json_mode, ensure_ascii=False),
                        }
                    ] + messages
                    data["response_format"] = {"type": "json_object"}
                elif isinstance(json_mode, dict):
                    data["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "response",
                            "strict": True,
                            "schema": json_mode,
                        },
                    }
                elif json_mode:
                    data["response_format"] = {"type": "json_object"}
                captured = capture(data)
                r = await self.client.post(
                    s.model_url.rstrip("/") + "/chat/completions",
                    json=data,
                    headers={"Authorization": "Bearer " + s.model_key}
                    if s.model_key
                    else {},
                )
                r.raise_for_status()
                body = r.json()
                text = body["choices"][0]["message"]["content"] or ""
                usage = body.get("usage", {})
                inp = usage.get("prompt_tokens", 0)
                out = usage.get("completion_tokens", 0)
            else:
                data = {"model": s.model_name, "system": system, "messages": messages,
                        "max_tokens": max_tokens, "temperature": 0}
                captured = capture(data)
                r = await self.client.post(
                    s.model_url.rstrip("/") + "/messages",
                    headers={
                        "x-api-key": s.model_key,
                        "anthropic-version": "2023-06-01",
                    },
                    json=data,
                )
                r.raise_for_status()
                body = r.json()
                text = "\n".join(
                    x["text"] for x in body["content"] if x.get("type") == "text"
                )
                usage = body.get("usage", {})
                inp = usage.get("input_tokens", 0)
                out = usage.get("output_tokens", 0)
            if captured is not None:
                captured["status"] = "completed"
            if trace:
                trace.input_tokens += inp
                trace.output_tokens += out
                trace.usage.append(
                    {
                        "input_tokens": inp,
                        "output_tokens": out,
                        "uncached_cost_estimate": estimate_call(s, inp, out)
                        if usage
                        else None,
                    }
                )
                if not usage:
                    trace.failures.append("usage_unavailable")
            return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
        except Exception as e:
            if captured is not None:
                captured.update(status="failed", error=type(e).__name__)
            if trace:
                trace.failures.append("model:" + type(e).__name__)
            raise
        finally:
            if captured is not None:
                captured["duration_ms"] = round((time.perf_counter() - start) * 1000, 1)
            if trace:
                trace.spans.append(
                    {"name": "llm", "duration_ms": (time.perf_counter() - start) * 1000}
                )

    async def create(
        self, model=None, messages=None, system="", max_tokens=384, **kwargs
    ):
        content = await self.complete(
            messages or [], system, max_tokens, json_mode=False, purpose="识别意图"
        )
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=content)])


def parse_json(text):
    # Accept fenced JSON but do not silently repair model choices or inject expected answers.
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    return json.loads(text)
