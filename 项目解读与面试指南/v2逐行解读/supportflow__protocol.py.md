# supportflow\protocol.py

## 输入输出流

MCP Streamable HTTP 消息与 Bearer token 进入官方 SDK；输出标准协议响应并复用相同业务工具。

## 先理解设计

协议层不复制业务规则，身份从 token 重查；MCP 名称不是本地函数管理器的别名。

源码 SHA256：`7140206bfbfa8f4b4a8b7ae70408a387703056c5735f3e5036a6dde39c5f79b6`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Official MCP SDK Streamable HTTP resource server sharing HTTP's identity and tools."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
from mcp.server.fastmcp import FastMCP
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
from mcp.server.auth.provider import AccessToken
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from mcp.server.auth.settings import AuthSettings
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
from mcp.server.auth.middleware.auth_context import get_access_token
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
from mcp.server.transport_security import TransportSecuritySettings
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from urllib.parse import urlsplit
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
class TokenVerifier:
```

定义一组状态和行为，或定义可校验的数据契约。

### L13 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L13**

```python
    def __init__(self, store):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L14**

```python
        self.store = store
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L16 · verify_token

将本项目 token 校验适配为官方 MCP SDK 的 AccessToken。

**L16**

```python
    async def verify_token(self, token):
```

将本项目 token 校验适配为官方 MCP SDK 的 AccessToken。

**L17**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
            p = self.store.authenticate(token)
```

把 token 摘要转换成可信 Principal，同时检查撤销和过期。

**L19**

```python
        except PermissionError:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L20**

```python
            return None
```

结束当前函数并把本行构造的结果交给调用方。

**L21**

```python
        return AccessToken(
```

结束当前函数并把本行构造的结果交给调用方。

**L22**

```python
            token=token,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L23**

```python
            client_id=p.user,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
            scopes=["supportflow"],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
            subject=p.user,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L26**

```python
            claims={"tenant": p.tenant},
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
            expires_at=int(time.time()) + 60,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L28**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L31 · build_mcp

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L31**

```python
def build_mcp(service):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L32**

```python
    public = service.settings.public_url.rstrip("/")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
    host = urlsplit(public).hostname
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L34**

```python
    if not host:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L35**

```python
        raise ValueError("Valid public_url required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L36**

```python
    server = FastMCP(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
        "SupportFlow",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
        stateless_http=True,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
        json_response=True,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
        streamable_http_path="/",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
        transport_security=TransportSecuritySettings(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L42**

```python
            allowed_hosts=[host, host + ":*", "127.0.0.1:*", "localhost:*"],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L43**

```python
            allowed_origins=[public, "http://127.0.0.1:*", "http://localhost:*"],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
        ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
        token_verifier=TokenVerifier(service.store),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L46**

```python
        auth=AuthSettings(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L47**

```python
            issuer_url=public,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L48**

```python
            resource_server_url=public + "/mcp",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L49**

```python
            required_scopes=["supportflow"],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
            validate_token_resource=False,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L51**

```python
        ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L54 · principal

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L54**

```python
    def principal():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L55**

```python
        token = get_access_token()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
        if not token:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L57**

```python
            raise PermissionError("Authentication required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L58**

```python
        return service.store.authenticate(token.token)
```

把 token 摘要转换成可信 Principal，同时检查撤销和过期。

**L60**

```python
    @server.tool()
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L61 · knowledge_search

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L61**

```python
    async def knowledge_search(query: str):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L62**

```python
        """Search only the authenticated tenant's policy documents."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
        return await service.tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L64**

```python
            principal(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
            "knowledge_search",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
            {"query": query},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
            "mcp-search",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
    @server.tool()
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L73 · order_lookup

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L73**

```python
    async def order_lookup(order_id: str):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L74**

```python
        """Read an order after ownership/role checks."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
        return await service.tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L76**

```python
            principal(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L78**

```python
            "order_lookup",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
            {"order_id": order_id},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
            "mcp-order",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
    @server.tool()
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L85 · refund_request

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L85**

```python
    async def refund_request(
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L86**

```python
        order_id: str, amount_cents: int, reason: str, idempotency_key: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
        """Explicitly request a pending refund. Cannot approve or transfer money."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
        return await service.tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L90**

```python
            principal(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
            "refund_request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
            {"order_id": order_id, "amount_cents": amount_cents, "reason": reason},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
            idempotency_key,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
            consent=True,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L97**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
    @server.tool()
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L100 · ticket_create

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L100**

```python
    async def ticket_create(conv_id: str, summary: str, idempotency_key: str):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L101**

```python
        """Create a human support ticket linked to an owned conversation."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
        p = principal()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L103**

```python
        service.store.history(p, conv_id)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L104**

```python
        return await service.tools.call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L105**

```python
            p,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L107**

```python
            "ticket_create",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L108**

```python
            {"summary": summary},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
            conv_id,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L110**

```python
            idempotency_key,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L111**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
    @server.tool()
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L114 · ticket_status

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L114**

```python
    async def ticket_status(ticket_id: str):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L115**

```python
        """Read an accessible support ticket."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
        return service.store.ticket(principal(), ticket_id)
```

结束当前函数并把本行构造的结果交给调用方。

**L118**

```python
    return server
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

公开 HTTPS 资源地址、企业 OAuth/OIDC 元数据和权限范围需要目标环境配置。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
