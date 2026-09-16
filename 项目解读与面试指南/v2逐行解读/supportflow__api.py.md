# supportflow\api.py

## 输入输出流

HTTP 路径、严格请求体和 token 进入 FastAPI；输出身份范围内的数据或明确 401/403/409/422/504。

## 先理解设计

所有业务入口走可信 Principal。客户、客服、财务与运维操作分开，监控观测实际完成 HTTP 请求。

源码 SHA256：`a151306b5f8aaf459a263fa73998777ec187af6f94fceec080a3018c93aa73c3`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Authenticated primary HTTP API; business writes have strict schemas and persistent state."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
from contextlib import asynccontextmanager
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
from fastapi import FastAPI, Depends, Request, HTTPException
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from fastapi.responses import JSONResponse, Response
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
from pydantic import BaseModel, ConfigDict, Field
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from prometheus_client import (
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
    CollectorRegistry,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```python
    Counter,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L12**

```python
    Histogram,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```python
    generate_latest,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L14**

```python
    CONTENT_TYPE_LATEST,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L15**

```python
)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```python
from supportflow.contracts import Settings, ChatInput, Principal
```

导入本段使用的标准库、依赖或项目组件。

**L17**

```python
from supportflow.store import Store
```

导入本段使用的标准库、依赖或项目组件。

**L18**

```python
from supportflow.model import Model
```

导入本段使用的标准库、依赖或项目组件。

**L19**

```python
from supportflow.knowledge import Knowledge
```

导入本段使用的标准库、依赖或项目组件。

**L20**

```python
from supportflow.tools import Tools
```

导入本段使用的标准库、依赖或项目组件。

**L21**

```python
from supportflow.service import ChatService
```

导入本段使用的标准库、依赖或项目组件。

**L22**

```python
from supportflow.protocol import build_mcp
```

导入本段使用的标准库、依赖或项目组件。

**L23**

```python
from supportflow.payments import Payments
```

导入本段使用的标准库、依赖或项目组件。

**L26**

```python
class Strict(BaseModel):
```

定义一组状态和行为，或定义可校验的数据契约。

**L27**

```python
    model_config = ConfigDict(extra="forbid")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
class RefundInput(Strict):
```

定义一组状态和行为，或定义可校验的数据契约。

**L31**

```python
    order_id: str = Field(min_length=1, max_length=100)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L32**

```python
    amount_cents: int = Field(strict=True, gt=0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
    reason: str = Field(min_length=1, max_length=500)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L34**

```python
    idempotency_key: str = Field(min_length=8, max_length=100)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
class Approval(Strict):
```

定义一组状态和行为，或定义可校验的数据契约。

**L38**

```python
    approve: bool = True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
class TicketInput(Strict):
```

定义一组状态和行为，或定义可校验的数据契约。

**L42**

```python
    conv_id: str = Field(min_length=1, max_length=80)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L43**

```python
    summary: str = Field(min_length=1, max_length=1500)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
    idempotency_key: str = Field(min_length=8, max_length=100)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L47**

```python
class TicketUpdate(Strict):
```

定义一组状态和行为，或定义可校验的数据契约。

**L48**

```python
    status: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
    assignee: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
    resolution: str = Field(default="", max_length=4000)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L51**

```python
    version: int = Field(ge=0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L54**

```python
class Document(Strict):
```

定义一组状态和行为，或定义可校验的数据契约。

**L55**

```python
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
    title: str = Field(min_length=1, max_length=200)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L57**

```python
    content: str = Field(min_length=1, max_length=100000)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L60**

```python
class Revoke(Strict):
```

定义一组状态和行为，或定义可校验的数据契约。

**L61**

```python
    token: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
class TokenInput(Strict):
```

定义一组状态和行为，或定义可校验的数据契约。

**L65**

```python
    user: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L66**

```python
    roles: list[str] = Field(min_length=1, max_length=5)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L67**

```python
    ttl: int = Field(default=3600, ge=60, le=86400)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L70 · create_app

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L70**

```python
def create_app(settings=None, model=None, variant="multi"):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L71**

```python
    settings = settings or Settings.from_env()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
    store = Store(settings.db_path)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
    model = model or Model(settings)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L74**

```python
    kb = Knowledge(store, settings, model)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
    service = ChatService(store, settings, model, kb, Tools(store, kb))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L76**

```python
    mcp = build_mcp(service)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L78**

```python
    @asynccontextmanager
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L79 · lifespan

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L79**

```python
    async def lifespan(app):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L80**

```python
        async with mcp.session_manager.run():
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L81**

```python
            yield
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
        await service.close()
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L84**

```python
    app = FastAPI(title="SupportFlow", version="2.0.0", lifespan=lifespan)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L85**

```python
    app.state.service = service
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L86**

```python
    app.state.store = store
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L87**

```python
    payments = Payments(store, settings)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L88**

```python
    reg = CollectorRegistry()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L89**

```python
    count = Counter(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L90**

```python
        "sf_http_requests", "HTTP requests", ["route", "status"], registry=reg
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L91**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
    latency = Histogram(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L93**

```python
        "sf_http_duration_seconds",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
        "Actual completed HTTP duration",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
        ["route"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
        registry=reg,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L97**

```python
        buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 180, 300),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L98**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
    app.state.registry = reg
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L101**

```python
    @app.middleware("http")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L102 · metrics

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L102**

```python
    async def metrics(request, call_next):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L103**

```python
        start = time.perf_counter()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L104**

```python
        status = 500
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L105**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
            response = await call_next(request)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L107**

```python
            status = response.status_code
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L108**

```python
            return response
```

结束当前函数并把本行构造的结果交给调用方。

**L109**

```python
        finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L110**

```python
            route = getattr(request.scope.get("route"), "path", "unmatched")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L111**

```python
            count.labels(route, str(status)).inc()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
            latency.labels(route).observe(time.perf_counter() - start)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
    bearer = HTTPBearer(auto_error=False)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L116 · identity

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L116**

```python
    async def identity(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L117**

```python
        if not credentials:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L118**

```python
            raise HTTPException(401, "Bearer token required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L119**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
            return store.authenticate(credentials.credentials)
```

把 token 摘要转换成可信 Principal，同时检查撤销和过期。

**L121**

```python
        except PermissionError:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L122**

```python
            raise HTTPException(401, "Invalid or expired token")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L124**

```python
    @app.exception_handler(PermissionError)
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L125 · denied

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L125**

```python
    async def denied(req, exc):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L126**

```python
        return JSONResponse({"detail": str(exc)}, status_code=403)
```

结束当前函数并把本行构造的结果交给调用方。

**L128**

```python
    @app.exception_handler(ValueError)
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L129 · conflict

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L129**

```python
    async def conflict(req, exc):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L130**

```python
        return JSONResponse({"detail": str(exc)}, status_code=409)
```

结束当前函数并把本行构造的结果交给调用方。

**L132**

```python
    @app.exception_handler(TimeoutError)
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L133 · timeout

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L133**

```python
    async def timeout(req, exc):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L134**

```python
        return JSONResponse(
```

结束当前函数并把本行构造的结果交给调用方。

**L135**

```python
            {"detail": "Request deadline exceeded; retry same request_id"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L136**

```python
            status_code=504,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L137**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L139**

```python
    @app.get("/health")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L140 · health

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L140**

```python
    async def health():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L141**

```python
        return {"status": "alive", "business_mode": settings.business_mode}
```

结束当前函数并把本行构造的结果交给调用方。

**L143**

```python
    @app.post("/chat")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L144 · chat

为整个请求建立 trace、预算与会话租约，完成业务后原子提交并更新非权威投影。

**L144**

```python
    async def chat(body: ChatInput, p=Depends(identity)):
```

为整个请求建立 trace、预算与会话租约，完成业务后原子提交并更新非权威投影。

**L145**

```python
        return await service.chat(p, body, variant)
```

为整个请求建立 trace、预算与会话租约，完成业务后原子提交并更新非权威投影。

**L147**

```python
    @app.post("/intents")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L148 · intents

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L148**

```python
    async def intents(body: ChatInput, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L149**

```python
        from dataclasses import asdict
```

导入本段使用的标准库、依赖或项目组件。

**L151**

```python
        result = await service.router.recognize_intent(body.message, [])
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L152**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L153**

```python
            **asdict(result),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L154**

```python
            "intent": result.intent.value,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L155**

```python
            "urgency": result.urgency.value,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L156**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L158**

```python
    @app.get("/conversations/{conv_id}")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L159 · history

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L159**

```python
    async def history(conv_id: str, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L160**

```python
        return {"messages": store.history(p, conv_id)}
```

结束当前函数并把本行构造的结果交给调用方。

**L162**

```python
    @app.get("/orders/{order_id}")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L163 · order

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L163**

```python
    async def order(order_id: str, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L164**

```python
        return store.order(p, order_id)
```

结束当前函数并把本行构造的结果交给调用方。

**L166**

```python
    @app.post("/refunds")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L167 · refund

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L167**

```python
    async def refund(body: RefundInput, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L168**

```python
        return store.refund_request(
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L169**

```python
            p, body.order_id, body.amount_cents, body.reason, body.idempotency_key
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L170**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L172**

```python
    @app.get("/refunds")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L173 · refunds

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L173**

```python
    async def refunds(p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L174**

```python
        with store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L175**

```python
            if p.roles.intersection({"finance", "admin"}):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L176**

```python
                rows = c.execute("SELECT * FROM refunds WHERE tenant=?", (p.tenant,))
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L177**

```python
            else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L178**

```python
                rows = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L179**

```python
                    "SELECT * FROM refunds WHERE tenant=? AND user=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L180**

```python
                    (p.tenant, p.user),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L181**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L182**

```python
            return [dict(r) for r in rows]
```

结束当前函数并把本行构造的结果交给调用方。

**L184**

```python
    @app.post("/refunds/{rid}/approval")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L185 · approve

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L185**

```python
    async def approve(rid: str, body: Approval, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L186**

```python
        return store.approve_refund(p, rid, body.approve)
```

要求财务权限并禁止申请者自批，pending 才能转审核结果。

**L188**

```python
    @app.post("/refunds/{rid}/settle")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L189 · settle

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L189**

```python
    async def settle(rid: str, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L190**

```python
        return (
```

结束当前函数并把本行构造的结果交给调用方。

**L191**

```python
            store.settle_refund(p, rid)
```

沙箱内核验审批、幂等更新退款与订单；不向外部支付商发请求。

**L192**

```python
            if settings.business_mode == "sandbox"
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L193**

```python
            else payments.enqueue(p, rid)
```

把批准退款和待发送消息在同一事务内写入，保证崩溃后仍知道要发送什么。

**L194**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L196**

```python
    @app.post("/ops/payments/dispatch")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L197 · dispatch

领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。

**L197**

```python
    async def dispatch(p=Depends(identity)):
```

领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。

**L198**

```python
        return await payments.dispatch(p)
```

领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。

**L200**

```python
    @app.post("/ops/payments/reconcile")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L201 · reconcile

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L201**

```python
    async def reconcile(p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L202**

```python
        return await payments.reconcile(p)
```

结束当前函数并把本行构造的结果交给调用方。

**L204**

```python
    @app.post("/payments/events")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L205 · payment_event

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L205**

```python
    async def payment_event(request: Request):
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L206**

```python
        raw = await request.body()
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L207**

```python
        if len(raw) > 16384:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L208**

```python
            raise HTTPException(413, "Event too large")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L209**

```python
        return payments.event(
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L210**

```python
            raw,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L211**

```python
            request.headers.get("x-timestamp", ""),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L212**

```python
            request.headers.get("x-signature", ""),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L213**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L215**

```python
    @app.post("/tickets")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L216 · ticket

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L216**

```python
    async def ticket(body: TicketInput, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L217**

```python
        store.history(p, body.conv_id)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L218**

```python
        return store.create_ticket(p, body.conv_id, body.summary, body.idempotency_key)
```

要求会话属主，使用持久幂等键创建 open 工单。

**L220**

```python
    @app.get("/tickets")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L221 · queue

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L221**

```python
    async def queue(p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L222**

```python
        p.require("staff")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L223**

```python
        with store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L224**

```python
            return [
```

结束当前函数并把本行构造的结果交给调用方。

**L225**

```python
                dict(r)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L226**

```python
                for r in c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L227**

```python
                    "SELECT * FROM tickets WHERE tenant=? ORDER BY rowid DESC LIMIT 200",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L228**

```python
                    (p.tenant,),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L229**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L230**

```python
            ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L232**

```python
    @app.get("/tickets/{tid}")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L233 · ticket_get

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L233**

```python
    async def ticket_get(tid: str, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L234**

```python
        return store.ticket(p, tid)
```

结束当前函数并把本行构造的结果交给调用方。

**L236**

```python
    @app.patch("/tickets/{tid}")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L237 · ticket_update

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L237**

```python
    async def ticket_update(tid: str, body: TicketUpdate, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L238**

```python
        return store.update_ticket(p, tid, **body.model_dump())
```

校验状态机、受理人和乐观版本；解决说明写回原会话。

**L240**

```python
    @app.post("/knowledge")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L241 · knowledge

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L241**

```python
    async def knowledge(body: Document, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L242**

```python
        p.require("admin")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L243**

```python
        kb.add(p.tenant, body.id, body.title, body.content)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L244**

```python
        return {"version": kb.version(p.tenant)}
```

结束当前函数并把本行构造的结果交给调用方。

**L246**

```python
    @app.post("/skills/reload")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L247 · reload

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L247**

```python
    async def reload(p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L248**

```python
        p.require("admin")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L249**

```python
        service.skills.reload()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L250**

```python
        return service.skills.summary()
```

结束当前函数并把本行构造的结果交给调用方。

**L252**

```python
    @app.get("/audit")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L253 · audit

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L253**

```python
    async def audit(p=Depends(identity)):
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L254**

```python
        return store.audit_log(p)
```

结束当前函数并把本行构造的结果交给调用方。

**L256**

```python
    @app.post("/auth/revoke")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L257 · revoke

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L257**

```python
    async def revoke(body: Revoke, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L258**

```python
        store.revoke(p, body.token)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L259**

```python
        return {"revoked": True}
```

结束当前函数并把本行构造的结果交给调用方。

**L261**

```python
    @app.post("/auth/tokens")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L262 · issue

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L262**

```python
    async def issue(body: TokenInput, p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L263**

```python
        p.require("admin")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L264**

```python
        if not set(body.roles) <= {"customer", "staff", "finance", "ops", "admin"}:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L265**

```python
            raise ValueError("Unknown role")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L266**

```python
        target = Principal(p.tenant, body.user, frozenset(body.roles))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L267**

```python
        token = store.issue_token(target, body.ttl)
```

签发随机不透明 token，数据库只保存摘要、租户、角色和到期时间。

**L268**

```python
        with store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L269**

```python
            store.audit(
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L270**

```python
                c, p, "auth.issue", body.user, {"roles": body.roles, "ttl": body.ttl}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L271**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L272**

```python
        return {"token": token, "expires_in": body.ttl}
```

结束当前函数并把本行构造的结果交给调用方。

**L274**

```python
    @app.get("/metrics")
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L275 · metrics_get

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L275**

```python
    async def metrics_get(p=Depends(identity)):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L276**

```python
        p.require("ops")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L277**

```python
        return Response(generate_latest(reg), media_type=CONTENT_TYPE_LATEST)
```

结束当前函数并把本行构造的结果交给调用方。

**L279**

```python
    app.mount("/mcp", mcp.streamable_http_app())
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L280**

```python
    return app
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

资源配额、公开部署地址、统一错误分类和生产审计/日志脱敏需要继续完善。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
