# supportflow\contracts.py

## 输入输出流

HTTP/环境变量与服务器生成的身份进入 schema；输出经过类型、长度和枚举限制的请求、配置及 trace。

## 先理解设计

严格数据契约不等于授权；Principal.require 与 Store 的属主检查共同完成权限判断。

源码 SHA256：`531296a4141913e9080433eb39f2c58e5d72171403bcb8c66f604e91353e001b`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
from dataclasses import dataclass, field
```

导入本段使用的标准库、依赖或项目组件。

**L2**

```python
from typing import Literal
```

导入本段使用的标准库、依赖或项目组件。

**L3**

```python
from pydantic import BaseModel, ConfigDict, Field
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
class BusinessRejection(ValueError):
```

定义一组状态和行为，或定义可校验的数据契约。

**L7**

```python
    """Confirmed business decision, distinct from backend failure."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L9 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L9**

```python
    def __init__(self, code, message):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L10**

```python
        super().__init__(message)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```python
        self.code = code
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L14**

```python
@dataclass(frozen=True)
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L15**

```python
class Principal:
```

定义一组状态和行为，或定义可校验的数据契约。

**L16**

```python
    tenant: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```python
    user: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
    roles: frozenset[str] = frozenset({"customer"})
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L20 · require

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L20**

```python
    def require(self, role: str):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L21**

```python
        if role not in self.roles and "admin" not in self.roles:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L22**

```python
            raise PermissionError(f"Required role: {role}")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L25**

```python
class ChatInput(BaseModel):
```

定义一组状态和行为，或定义可校验的数据契约。

**L26**

```python
    model_config = ConfigDict(extra="forbid")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
    message: str = Field(min_length=1, max_length=6000)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L28**

```python
    conv_id: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9_-]{1,80}$")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
    request_id: str = Field(min_length=8, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L32**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L33**

```python
class Trace:
```

定义一组状态和行为，或定义可校验的数据契约。

**L34**

```python
    request_id: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
    spans: list = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
    tools: list = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
    input_tokens: int = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
    output_tokens: int = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
    model_calls: int = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
    failures: list = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
    usage: list = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
class ToolCall(BaseModel):
```

定义一组状态和行为，或定义可校验的数据契约。

**L45**

```python
    model_config = ConfigDict(extra="forbid")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L46**

```python
    name: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
    arguments: dict = Field(default_factory=dict)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
class AgentTurn(BaseModel):
```

定义一组状态和行为，或定义可校验的数据契约。

**L51**

```python
    model_config = ConfigDict(extra="forbid")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L52**

```python
    answer: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L53**

```python
    tool_calls: list[ToolCall] = Field(default_factory=list, max_length=3)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
class JudgeScores(BaseModel):
```

定义一组状态和行为，或定义可校验的数据契约。

**L57**

```python
    relevance: float = Field(ge=0, le=1)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L58**

```python
    accuracy: float = Field(ge=0, le=1)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L59**

```python
    completeness: float = Field(ge=0, le=1)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L60**

```python
    helpfulness: float = Field(ge=0, le=1)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L63**

```python
class Settings(BaseModel):
```

定义一组状态和行为，或定义可校验的数据契约。

**L64**

```python
    db_path: str = "data/supportflow.sqlite3"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L65**

```python
    model_backend: Literal["compatible", "anthropic", "fixture"] = "compatible"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L66**

```python
    model_url: str = "http://127.0.0.1:8081/v1"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L67**

```python
    model_name: str = "qwen3-local"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L68**

```python
    model_key: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L69**

```python
    local_chat_template: bool = True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L70**

```python
    supports_json_schema: bool = True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L71**

```python
    model_thinking: Literal["enabled", "disabled"] | None = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
    public_url: str = "http://localhost:8000"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
    model_timeout: float = 90
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L74**

```python
    request_timeout: float = 180
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
    max_inflight: int = 4
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L76**

```python
    max_tool_rounds: int = 3
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L77**

```python
    storage: Literal["sqlite", "chroma"] = "sqlite"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L78**

```python
    chroma_path: str = "data/supportflow-chroma"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L79**

```python
    redis_url: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L80**

```python
    skills_dir: str = "skills"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L81**

```python
    token_ttl: int = 3600
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L82**

```python
    model_input_price: float | None = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L83**

```python
    model_output_price: float | None = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
    pricing_profile: Literal["glm-air-20260908"] | None = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L85**

```python
    currency: str = "CNY"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L86**

```python
    machine_hourly_cost: float | None = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L87**

```python
    business_mode: Literal["sandbox", "external"] = "sandbox"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L88**

```python
    business_currency: Literal["CNY"] = "CNY"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L89**

```python
    payment_url: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L90**

```python
    payment_key: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L91**

```python
    payment_webhook_secret: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L93**

```python
    @classmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L94 · from_env

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L94**

```python
    def from_env(cls):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L95**

```python
        import os
```

导入本段使用的标准库、依赖或项目组件。

**L96**

```python
        from dotenv import load_dotenv
```

导入本段使用的标准库、依赖或项目组件。

**L98**

```python
        load_dotenv(os.environ.get("SF_ENV_FILE", ".env"))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
        return cls(
```

结束当前函数并把本行构造的结果交给调用方。

**L100**

```python
            **{
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
                key: os.environ["SF_" + key.upper()]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
                for key in cls.model_fields
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L103**

```python
                if "SF_" + key.upper() in os.environ
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L104**

```python
            }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L105**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

企业 IdP、集中策略、配置启动检查仍应按目标部署继续增强。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
