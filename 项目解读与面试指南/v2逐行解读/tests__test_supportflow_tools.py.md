# tests\test_supportflow_tools.py

## 输入输出流

隔离的测试目录、身份、请求或模拟依赖进入测试；输出断言通过/失败与 pytest 结果。

## 先理解设计

测试替身验证工程行为，不能充当真实模型准确率或生产性能证据。

源码 SHA256：`75808f4b5eebf67fc5023e1b752c9353dd8dbf36f6fe32fc2d2770ab0e7abe79`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
import pytest
```

导入本段使用的标准库、依赖或项目组件。

**L2**

```python
from jsonschema import ValidationError
```

导入本段使用的标准库、依赖或项目组件。

**L3**

```python
from supportflow.contracts import Principal, Trace
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
from supportflow.store import Store
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
from supportflow.tools import Tools
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from supportflow.model import active_trace
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
class FakeKnowledge:
```

定义一组状态和行为，或定义可校验的数据契约。

### L10 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L10**

```python
    def __init__(self):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L11**

```python
        self.revision = "v1"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L12**

```python
        self.calls = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```python
        self.fail = False
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L15 · version

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L15**

```python
    def version(self, tenant):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L16**

```python
        return self.revision
```

结束当前函数并把本行构造的结果交给调用方。

### L18 · retrieve

把查询改写、并发检索、按稳定 ID 去重和重排接成一条可降级链路。

**L18**

```python
    async def retrieve(self, tenant, query, advanced=True):
```

把查询改写、并发检索、按稳定 ID 去重和重排接成一条可降级链路。

**L19**

```python
        self.calls += 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L20**

```python
        if self.fail:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L21**

```python
            raise RuntimeError("backend unavailable")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L22**

```python
        return {"items": [{"id": tenant, "content": query}], "degraded": []}
```

结束当前函数并把本行构造的结果交给调用方。

**L25**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L26 · test_cache_scoping_copy_and_version

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L26**

```python
async def test_cache_scoping_copy_and_version(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L27**

```python
    k = FakeKnowledge()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L28**

```python
    tools = Tools(Store(tmp_path / "tools.sqlite"), k)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
    args = {"query": "test"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L31**

```python
    a = await tools.call(p, "general", "knowledge_search", args, "c", "request01")
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L32**

```python
    a["items"].clear()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```python
    b = await tools.call(p, "general", "knowledge_search", args, "c", "request02")
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L34**

```python
    assert b["items"] and k.calls == 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L35**

```python
    await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L36**

```python
        Principal("other", "u"), "general", "knowledge_search", args, "c", "request03"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
    assert k.calls == 2
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
    k.revision = "v2"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
    await tools.call(p, "general", "knowledge_search", args, "c", "request04")
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L41**

```python
    assert k.calls == 3
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L45 · test_bad_args_do_not_trip_breaker_and_denied_tools

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L45**

```python
async def test_bad_args_do_not_trip_breaker_and_denied_tools(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L46**

```python
    tools = Tools(Store(tmp_path / "tools.sqlite"), FakeKnowledge())
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L47**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L48**

```python
    for _ in range(4):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L49**

```python
        with pytest.raises(ValidationError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L50**

```python
            await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L51**

```python
                p, "general", "knowledge_search", {"query": 42}, "c", "request01"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
    assert not tools.breakers
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
    with pytest.raises(PermissionError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L55**

```python
        await tools.call(p, "technical", "refund_request", {}, "c", "request02")
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L56**

```python
    with pytest.raises(PermissionError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L57**

```python
        await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L58**

```python
            p,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
            "refund_request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
            {"order_id": "ORD1", "amount_cents": 100, "reason": "x"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
            "c",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
            "request03",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L68 · test_breaker_outage_and_trace

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L68**

```python
async def test_breaker_outage_and_trace(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L69**

```python
    k = FakeKnowledge()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L70**

```python
    k.fail = True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L71**

```python
    tools = Tools(Store(tmp_path / "tools.sqlite"), k)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
    trace = Trace("trace1")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L74**

```python
    ctx = active_trace.set(trace)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
    try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
        for _ in range(3):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L77**

```python
            with pytest.raises(RuntimeError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L78**

```python
                await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L79**

```python
                    p, "general", "knowledge_search", {"query": "q"}, "c", "request1"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
        with pytest.raises(RuntimeError, match="circuit_open"):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L82**

```python
            await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L83**

```python
                p, "general", "knowledge_search", {"query": "q"}, "c", "request1"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L85**

```python
        assert (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
            k.calls == 3
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L87**

```python
            and len(trace.tools) == 4
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L88**

```python
            and not any(t["success"] for t in trace.tools)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L90**

```python
    finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L91**

```python
        active_trace.reset(ctx)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L95 · test_same_mcp_idempotency_key_cannot_change_refund_payload

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L95**

```python
async def test_same_mcp_idempotency_key_cannot_change_refund_payload(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L96**

```python
    store = Store(tmp_path / "tools.sqlite")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L97**

```python
    k = FakeKnowledge()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L98**

```python
    tools = Tools(store, k)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L99**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L100**

```python
    a = Principal("t", "a", frozenset({"admin"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L101**

```python
    store.seed_order(a, "ORD1", 5000, "u")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
    args = {"order_id": "ORD1", "amount_cents": 100, "reason": "x"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L103**

```python
    first = await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L104**

```python
        p, "billing", "refund_request", args, "c", "request123", consent=True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L105**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
    again = await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L107**

```python
        p, "billing", "refund_request", args, "c", "request123", consent=True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L108**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
    assert first["id"] == again["id"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L110**

```python
    with pytest.raises(ValueError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L111**

```python
        await tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L112**

```python
            p,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
            "refund_request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
            {**args, "amount_cents": 101},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
            "c",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
            "request123",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
            consent=True,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L119**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

增加真实供应商、并发进程、故障恢复和独立业务标签验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
