# tests\test_supportflow_mcp.py

## 输入输出流

隔离的测试目录、身份、请求或模拟依赖进入测试；输出断言通过/失败与 pytest 结果。

## 先理解设计

测试替身验证工程行为，不能充当真实模型准确率或生产性能证据。

源码 SHA256：`73f4463214ad5cd8cb24d2d9b14284d391069313fba5e6e254dce5b64e1ff6c7`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
import asyncio
```

导入本段使用的标准库、依赖或项目组件。

**L2**

```python
import socket
```

导入本段使用的标准库、依赖或项目组件。

**L3**

```python
import httpx
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import pytest
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import uvicorn
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from mcp import ClientSession
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
from mcp.client.streamable_http import streamable_http_client
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
from supportflow.api import create_app
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from supportflow.contracts import Principal, Settings
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L13 · test_real_mcp_http_handshake_tools_and_auth

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L13**

```python
async def test_real_mcp_http_handshake_tools_and_auth(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L14**

```python
    app = create_app(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```python
        Settings(db_path=str(tmp_path / "mcp.sqlite"), model_backend="fixture")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L16**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```python
    store = app.state.store
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L18**

```python
    p = Principal("t", "alice")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
    admin = Principal("t", "admin", frozenset({"admin"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L20**

```python
    store.seed_order(admin, "ORD1001", 5000, "alice")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
    token = store.issue_token(p)
```

签发随机不透明 token，数据库只保存摘要、租户、角色和到期时间。

**L22**

```python
    sock = socket.socket()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L23**

```python
    sock.bind(("127.0.0.1", 0))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```python
    port = sock.getsockname()[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
    server = uvicorn.Server(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L26**

```python
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```python
    task = asyncio.create_task(server.serve(sockets=[sock]))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
    try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```python
        async with asyncio.timeout(10):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L31**

```python
            while not server.started:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L32**

```python
                await asyncio.sleep(0.02)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L33**

```python
        url = f"http://127.0.0.1:{port}/mcp/"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L34**

```python
        async with httpx.AsyncClient() as unauth:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L35**

```python
            r = await unauth.post(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L36**

```python
                url, json={"jsonrpc": "2.0", "id": 1, "method": "initialize"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
            assert r.status_code == 401
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
        async with httpx.AsyncClient(
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L40**

```python
            headers={"Authorization": "Bearer " + token}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
        ) as client:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L42**

```python
            async with streamable_http_client(url, http_client=client) as (
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L43**

```python
                read,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
                write,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
                _,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
            ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
                async with ClientSession(read, write) as session:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L48**

```python
                    info = await session.initialize()
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L49**

```python
                    assert info.serverInfo.name == "SupportFlow"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
                    listing = await session.list_tools()
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L51**

```python
                    assert {"order_lookup", "refund_request", "ticket_create"} <= {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L52**

```python
                        t.name for t in listing.tools
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
                    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
                    result = await session.call_tool(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L55**

```python
                        "order_lookup", {"order_id": "ORD1001"}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L56**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
                    assert not result.isError and "paid" in str(result)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
                    rejected = await session.call_tool(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L59**

```python
                        "order_lookup", {"order_id": "OTHER"}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
                    assert rejected.isError
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
    finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L63**

```python
        server.should_exit = True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L64**

```python
        await task
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L65**

```python
        sock.close()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

增加真实供应商、并发进程、故障恢复和独立业务标签验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
