# supportflow\model.py

## 输入输出流

标准 messages/system 与输出预算进入供应商适配器；输出文本并累计真实 usage、耗时和失败。

## 先理解设计

不通过异常自动切换付费模型。ContextVar 让并行 Agent 的模型调用回到同一个请求 trace。

源码 SHA256：`e8050a636d30f9cf02f7c9dbf97fd037b83141ce9b79c380e3747a25302070b7`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Provider-neutral completion API with real usage accounting and no implicit paid fallback."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import contextvars
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import re
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
from types import SimpleNamespace
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
import httpx
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from supportflow.contracts import Settings, Trace
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
from supportflow.pricing import estimate_call
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
active_trace: contextvars.ContextVar[Trace | None] = contextvars.ContextVar(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```python
    "trace", default=None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L14**

```python
)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```python
class Model:
```

定义一组状态和行为，或定义可校验的数据契约。

### L18 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L18**

```python
    def __init__(self, settings: Settings):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L19**

```python
        self.settings = settings
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L20**

```python
        self.client = httpx.AsyncClient(timeout=settings.model_timeout)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L21**

```python
        self.messages = self  # adapter for the existing IntentRecognizer / BaseAgent
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L23 · close

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L23**

```python
    async def close(self):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L24**

```python
        await self.client.aclose()
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

### L26 · complete

执行一次真实模型 HTTP 请求；把供应商返回的 usage 累加到当前请求 trace。

**L26**

```python
    async def complete(self, messages, system="", max_tokens=384, json_mode=False):
```

执行一次真实模型 HTTP 请求；把供应商返回的 usage 累加到当前请求 trace。

**L27**

```python
        s = self.settings
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L28**

```python
        if s.model_backend == "fixture":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L29**

```python
            raise RuntimeError(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L30**

```python
                "Fixture backend requires an explicitly injected test double"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
        start = time.perf_counter()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
        trace = active_trace.get()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L34**

```python
        if trace:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L35**

```python
            trace.model_calls += 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
            if s.model_backend == "compatible":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L38**

```python
                data = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
                    "model": s.model_name,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
                    "messages": (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
                        [{"role": "system", "content": system}] if system else []
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L42**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
                    + messages,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
                    "temperature": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
                    "max_tokens": max_tokens,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
                    "stream": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
                if s.local_chat_template:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L49**

```python
                    data["chat_template_kwargs"] = {"enable_thinking": False}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
                if s.model_thinking:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L51**

```python
                    data["thinking"] = {"type": s.model_thinking}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L52**

```python
                if isinstance(json_mode, dict) and not s.supports_json_schema:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L53**

```python
                    data["messages"] = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L54**

```python
                        {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
                            "role": "system",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L56**

```python
                            "content": system
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
                            + "\n只输出符合以下 JSON Schema 的 JSON 对象："
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
                            + json.dumps(json_mode, ensure_ascii=False),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L59**

```python
                        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
                    ] + messages
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
                    data["response_format"] = {"type": "json_object"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L62**

```python
                elif isinstance(json_mode, dict):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L63**

```python
                    data["response_format"] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L64**

```python
                        "type": "json_schema",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
                        "json_schema": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
                            "name": "response",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
                            "strict": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
                            "schema": json_mode,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
                        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```python
                    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L71**

```python
                elif json_mode:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L72**

```python
                    data["response_format"] = {"type": "json_object"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
                r = await self.client.post(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L74**

```python
                    s.model_url.rstrip("/") + "/chat/completions",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
                    json=data,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L76**

```python
                    headers={"Authorization": "Bearer " + s.model_key}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L77**

```python
                    if s.model_key
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L78**

```python
                    else {},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
                r.raise_for_status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
                body = r.json()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L82**

```python
                text = body["choices"][0]["message"]["content"] or ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L83**

```python
                usage = body.get("usage", {})
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
                inp = usage.get("prompt_tokens", 0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L85**

```python
                out = usage.get("completion_tokens", 0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L86**

```python
            else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L87**

```python
                r = await self.client.post(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L88**

```python
                    s.model_url.rstrip("/") + "/messages",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
                    headers={
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L90**

```python
                        "x-api-key": s.model_key,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
                        "anthropic-version": "2023-06-01",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
                    },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
                    json={
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L94**

```python
                        "model": s.model_name,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
                        "system": system,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
                        "messages": messages,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
                        "max_tokens": max_tokens,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
                        "temperature": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
                    },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L100**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
                r.raise_for_status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
                body = r.json()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L103**

```python
                text = "\n".join(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L104**

```python
                    x["text"] for x in body["content"] if x.get("type") == "text"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L105**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
                usage = body.get("usage", {})
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L107**

```python
                inp = usage.get("input_tokens", 0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L108**

```python
                out = usage.get("output_tokens", 0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L109**

```python
            if trace:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L110**

```python
                trace.input_tokens += inp
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L111**

```python
                trace.output_tokens += out
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L112**

```python
                trace.usage.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L113**

```python
                    {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
                        "input_tokens": inp,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
                        "output_tokens": out,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
                        "uncached_cost_estimate": estimate_call(s, inp, out)
```

使用单次调用长度选择版本化费率；未配置单价返回 None，不把未知费用写成零。

**L117**

```python
                        if usage
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L118**

```python
                        else None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L119**

```python
                    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L121**

```python
                if not usage:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L122**

```python
                    trace.failures.append("usage_unavailable")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L123**

```python
            return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
```

结束当前函数并把本行构造的结果交给调用方。

**L124**

```python
        except Exception as e:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L125**

```python
            if trace:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L126**

```python
                trace.failures.append("model:" + type(e).__name__)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L127**

```python
            raise
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
        finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L129**

```python
            if trace:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L130**

```python
                trace.spans.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L131**

```python
                    {"name": "llm", "duration_ms": (time.perf_counter() - start) * 1000}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L132**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L134 · create

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L134**

```python
    async def create(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L135**

```python
        self, model=None, messages=None, system="", max_tokens=384, **kwargs
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L136**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L137**

```python
        content = await self.complete(
```

执行一次真实模型 HTTP 请求；把供应商返回的 usage 累加到当前请求 trace。

**L138**

```python
            messages or [], system, max_tokens, json_mode=False
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L139**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=content)])
```

结束当前函数并把本行构造的结果交给调用方。

### L143 · parse_json

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L143**

```python
def parse_json(text):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L144**

```python
    # Accept fenced JSON but do not silently repair model choices or inject expected answers.
```

作者注释，说明约束或设计意图；本行不执行。

**L145**

```python
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L146**

```python
    return json.loads(text)
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

GLM JSON object 适配与真实 usage 已验证，评委用量已单列；其他供应商契约、截断恢复及账单校准仍可增强。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
