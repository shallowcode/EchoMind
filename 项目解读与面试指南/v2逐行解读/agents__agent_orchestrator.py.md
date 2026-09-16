# agents\agent_orchestrator.py

## 输入输出流

用户消息、历史、实体与模型/Skills 依赖进入原核心组件；输出意图、Agent 路由、技能上下文或模型结果。

## 先理解设计

这部分是新版复用的原始核心。v2 在 ChatService 与 ToolAgent 中接入事务、权限与完整工具循环。

源码 SHA256：`4f9d199eef99dc6822312d860474f4582cdac5b84e6f983f47b040a8a1eed783`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L2**

```python
亮点：多 Agent 路由与编排
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
核心问题：多 Agent 情况下如何做 Routing？
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L6**

```python
路由策略（三层决策）：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```python
  1. 意图路由 —— 根据 IntentCategory 直接映射到专属 Agent
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L8**

```python
  2. 性能路由 —— 同类 Agent 有多个时，选成功率最高、延迟最低的
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L9**

```python
  3. 降级路由 —— 专属 Agent 不可用时，自动降级到 GeneralAgent
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```python
并行协作：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L12**

```python
  - 复杂问题（如"技术问题 + 账单问题"）可同时派发给多个 Agent
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```python
  - 结果由 Orchestrator 合并后返回
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L15**

```python
升级机制：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```python
  - Agent 置信度低于阈值 → 自动升级到更高级 Agent 或转人工
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
import asyncio
```

导入本段使用的标准库、依赖或项目组件。

**L19**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L20**

```python
import logging
```

导入本段使用的标准库、依赖或项目组件。

**L21**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L22**

```python
import uuid
```

导入本段使用的标准库、依赖或项目组件。

**L23**

```python
from dataclasses import dataclass, field
```

导入本段使用的标准库、依赖或项目组件。

**L24**

```python
from enum import Enum
```

导入本段使用的标准库、依赖或项目组件。

**L25**

```python
from typing import Any, Dict, List, Optional
```

导入本段使用的标准库、依赖或项目组件。

**L27**

```python
from anthropic import AsyncAnthropic
```

导入本段使用的标准库、依赖或项目组件。

**L29**

```python
from core.intent_recognizer import IntentCategory, IntentRecognizer, UrgencyLevel
```

导入本段使用的标准库、依赖或项目组件。

**L30**

```python
from core.llm_utils import extract_text_content
```

导入本段使用的标准库、依赖或项目组件。

**L32**

```python
logger = logging.getLogger(__name__)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L35**

```python
# ── 数据结构 ──────────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L37**

```python
class AgentType(Enum):
```

定义一组状态和行为，或定义可校验的数据契约。

**L38**

```python
    GENERAL   = "general"    # 通用客服
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
    TECHNICAL = "technical"  # 技术支持
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
    BILLING   = "billing"    # 账单/退款
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
    ESCALATION = "escalation" # 人工升级（占位）
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L45**

```python
class AgentStats:
```

定义一组状态和行为，或定义可校验的数据契约。

**L46**

```python
    """Agent 运行时统计，供 Monitor 和路由决策使用。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
    total:     int   = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L48**

```python
    success:   int   = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L49**

```python
    total_ms:  float = 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
    monitor_penalty: float = 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L52**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L53 · success_rate

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L53**

```python
    def success_rate(self) -> float:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L54**

```python
        return self.success / self.total if self.total else 1.0
```

结束当前函数并把本行构造的结果交给调用方。

**L56**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L57 · avg_ms

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L57**

```python
    def avg_ms(self) -> float:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L58**

```python
        return self.total_ms / self.total if self.total else 0.0
```

结束当前函数并把本行构造的结果交给调用方。

### L60 · routing_score

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L60**

```python
    def routing_score(self) -> float:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L61**

```python
        """路由评分：成功率高、延迟低的 Agent 得分高。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
        latency_score = 1.0 / (1.0 + self.avg_ms / 1000)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L63**

```python
        base_score = self.success_rate * 0.7 + latency_score * 0.3
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L64**

```python
        return base_score * max(0.0, 1.0 - self.monitor_penalty)
```

结束当前函数并把本行构造的结果交给调用方。

**L67**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L68**

```python
class AgentResponse:
```

定义一组状态和行为，或定义可校验的数据契约。

**L69**

```python
    agent_type:  AgentType
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```python
    content:     str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L71**

```python
    success:     bool
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
    confidence:  float = 1.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
    latency_ms:  float = 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L74**

```python
    escalate:    bool  = False   # 是否需要升级
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L77**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L78**

```python
class Request:
```

定义一组状态和行为，或定义可校验的数据契约。

**L79**

```python
    message:     str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
    user_id:     str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
    conv_id:     str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
    context:     str = ""        # 来自 MemoryManager 的格式化上下文
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L83**

```python
    history:     Optional[List[Dict[str, str]]] = None  # 对话历史，传给意图识别
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
    entities:    Dict[str, List[str]] = field(default_factory=dict)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L85**

```python
    intent:      Optional[IntentCategory] = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L86**

```python
    intent_group: Optional[str] = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L87**

```python
    urgency:     Optional[UrgencyLevel]   = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L88**

```python
    intent_confidence: float = 1.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L89**

```python
    request_id:  str = field(default_factory=lambda: str(uuid.uuid4())[:8])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L92**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L93**

```python
class OrchestratorResult:
```

定义一组状态和行为，或定义可校验的数据契约。

**L94**

```python
    request_id:  str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
    response:    str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
    agent_type:  AgentType
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
    intent:      Optional[IntentCategory]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
    escalated:   bool  = False
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L99**

```python
    latency_ms:  float = 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L100**

```python
    agent_types: List[AgentType] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L101**

```python
    primary_agent: Optional[AgentType] = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L102**

```python
    supporting_agents: List[AgentType] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L103**

```python
    routing_reason: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L104**

```python
    routing_confidence: float = 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L107**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L108**

```python
class RoutingDecision:
```

定义一组状态和行为，或定义可校验的数据契约。

**L109**

```python
    """一次请求的结构化路由决策。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L110**

```python
    primary_agent: AgentType
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L111**

```python
    supporting_agents: List[AgentType] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L112**

```python
    reason: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L113**

```python
    confidence: float = 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L115**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L116 · agent_types

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L116**

```python
    def agent_types(self) -> List[AgentType]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L117**

```python
        return [self.primary_agent] + self.supporting_agents
```

结束当前函数并把本行构造的结果交给调用方。

**L119**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L120 · multi_agent

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L120**

```python
    def multi_agent(self) -> bool:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L121**

```python
        return bool(self.supporting_agents)
```

结束当前函数并把本行构造的结果交给调用方。

**L124**

```python
# ── 基础 Agent ────────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L126**

```python
class BaseAgent:
```

定义一组状态和行为，或定义可校验的数据契约。

**L127**

```python
    """所有 Agent 的基类，封装 LLM 调用和统计。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
    agent_type: AgentType
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L130**

```python
    system_prompt: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L132 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L132**

```python
    def __init__(self, client: AsyncAnthropic, model: str, skill_manager: Optional[Any] = None):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L133**

```python
        self._client = client
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L134**

```python
        self._model  = model
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L135**

```python
        self._skill_manager = skill_manager
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L136**

```python
        self.stats   = AgentStats()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L138 · handle

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L138**

```python
    async def handle(self, req: Request) -> AgentResponse:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L139**

```python
        t0 = time.monotonic()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L140**

```python
        self.stats.total += 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L141**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L142**

```python
            content = await self._call_llm(req)
```

在固定预算内交替生成结构化决策和执行工具；遇到缺少证据时不能凭空声称完成。

**L143**

```python
            ms = (time.monotonic() - t0) * 1000
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L144**

```python
            self.stats.success += 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L145**

```python
            self.stats.total_ms += ms
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L146**

```python
            escalate = self._needs_escalation(content)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L147**

```python
            return AgentResponse(
```

结束当前函数并把本行构造的结果交给调用方。

**L148**

```python
                agent_type=self.agent_type,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L149**

```python
                content=content,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L150**

```python
                success=True,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L151**

```python
                latency_ms=ms,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L152**

```python
                escalate=escalate,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L153**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L154**

```python
        except Exception as ex:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L155**

```python
            ms = (time.monotonic() - t0) * 1000
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L156**

```python
            self.stats.total_ms += ms
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L157**

```python
            logger.error(f"{self.agent_type.value} 处理失败: {ex}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L158**

```python
            return AgentResponse(
```

结束当前函数并把本行构造的结果交给调用方。

**L159**

```python
                agent_type=self.agent_type,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L160**

```python
                content="抱歉，处理您的请求时出现问题，请稍后重试。",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L161**

```python
                success=False,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L162**

```python
                latency_ms=ms,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L163**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L165 · _call_llm

在固定预算内交替生成结构化决策和执行工具；遇到缺少证据时不能凭空声称完成。

**L165**

```python
    async def _call_llm(self, req: Request) -> str:
```

在固定预算内交替生成结构化决策和执行工具；遇到缺少证据时不能凭空声称完成。

### L166 · _clean

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L166**

```python
        def _clean(s: str) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L167**

```python
            return s.encode("utf-8", errors="ignore").decode("utf-8")
```

结束当前函数并把本行构造的结果交给调用方。

**L169**

```python
        messages = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L170**

```python
        if req.context:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L171**

```python
            messages.append({"role": "user", "content": f"[背景信息]\n{_clean(req.context)}"})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L172**

```python
            messages.append({"role": "assistant", "content": "好的，我已了解背景信息。"})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L173**

```python
        if req.entities:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L174**

```python
            entities_text = json.dumps(req.entities, ensure_ascii=False)
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L175**

```python
            messages.append({"role": "user", "content": f"[结构化实体]\n{_clean(entities_text)}"})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L176**

```python
            messages.append({"role": "assistant", "content": "好的，我会结合这些结构化实体处理。"})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L177**

```python
        messages.append({"role": "user", "content": _clean(req.message)})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L179**

```python
        resp = await self._client.messages.create(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L180**

```python
            model=self._model,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L181**

```python
            max_tokens=1024,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L182**

```python
            system=self._build_system_prompt(req),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L183**

```python
            messages=messages,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L184**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L185**

```python
        return extract_text_content(resp.content)
```

结束当前函数并把本行构造的结果交给调用方。

### L187 · _build_system_prompt

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L187**

```python
    def _build_system_prompt(self, req: Request) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L188**

```python
        """把动态加载的 Skills 拼入 system prompt，让业务规则随请求生效。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L189**

```python
        if self._skill_manager is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L190**

```python
            return self.system_prompt
```

结束当前函数并把本行构造的结果交给调用方。

**L191**

```python
        skill_prompt = self._skill_manager.prompt_for(req.message, self.agent_type.value)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L192**

```python
        if not skill_prompt:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L193**

```python
            return self.system_prompt
```

结束当前函数并把本行构造的结果交给调用方。

**L194**

```python
        return f"{self.system_prompt}\n\n[动态 Skills]\n{skill_prompt}"
```

结束当前函数并把本行构造的结果交给调用方。

### L196 · _needs_escalation

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L196**

```python
    def _needs_escalation(self, content: str) -> bool:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L197**

```python
        """检测 Agent 是否建议升级（简单关键词检测）。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L198**

```python
        keywords = ["转人工", "人工客服", "escalate", "specialist", "无法处理"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L199**

```python
        return any(kw in content for kw in keywords)
```

结束当前函数并把本行构造的结果交给调用方。

**L202**

```python
class GeneralAgent(BaseAgent):
```

定义一组状态和行为，或定义可校验的数据契约。

**L203**

```python
    agent_type    = AgentType.GENERAL
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L204**

```python
    system_prompt = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L205**

```python
        "你是 EchoMind 智能客服。友好、简洁地回答用户问题。"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L206**

```python
        "如果问题超出你的能力范围，明确说明并建议转接专业客服。"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L207**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L210**

```python
class TechnicalAgent(BaseAgent):
```

定义一组状态和行为，或定义可校验的数据契约。

**L211**

```python
    agent_type    = AgentType.TECHNICAL
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L212**

```python
    system_prompt = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L213**

```python
        "你是技术支持专家。专注于：故障排查、错误诊断、系统配置。"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L214**

```python
        "提供清晰的步骤化解决方案。遇到需要后台操作的问题，说明需要升级处理。"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L215**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L218**

```python
class BillingAgent(BaseAgent):
```

定义一组状态和行为，或定义可校验的数据契约。

**L219**

```python
    agent_type    = AgentType.BILLING
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L220**

```python
    system_prompt = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L221**

```python
        "你是账单服务专家。专注于：账单查询、退款申请、发票问题、订阅管理。"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L222**

```python
        "对财务问题保持准确和专业。涉及实际退款操作时，说明需要人工审核。"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L223**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L226**

```python
# ── 编排器 ────────────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L228**

```python
class AgentOrchestrator:
```

定义一组状态和行为，或定义可校验的数据契约。

**L229**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L230**

```python
    多 Agent 编排器。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L232**

```python
    路由逻辑（三层）：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L233**

```python
      1. 意图 → Agent 类型映射
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L234**

```python
      2. 同类多实例时按 routing_score() 选最优
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L235**

```python
      3. 专属 Agent 失败时降级到 GeneralAgent
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L236**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L238**

```python
    # 意图 → Agent 类型的静态映射（路由表）
```

作者注释，说明约束或设计意图；本行不执行。

**L239**

```python
    _INTENT_ROUTING: Dict[IntentCategory, AgentType] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L240**

```python
        IntentCategory.TECHNICAL:  AgentType.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L241**

```python
        IntentCategory.TECHNICAL_LOGIN: AgentType.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L242**

```python
        IntentCategory.TECHNICAL_CRASH: AgentType.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L243**

```python
        IntentCategory.BILLING:    AgentType.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L244**

```python
        IntentCategory.REFUND:     AgentType.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L245**

```python
        IntentCategory.INVOICE:    AgentType.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L246**

```python
        IntentCategory.PAYMENT_ISSUE: AgentType.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L247**

```python
        IntentCategory.ACCOUNT:    AgentType.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L248**

```python
        IntentCategory.ACCOUNT_SECURITY: AgentType.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L249**

```python
        IntentCategory.ESCALATION: AgentType.ESCALATION,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L250**

```python
        IntentCategory.HUMAN_HANDOFF: AgentType.ESCALATION,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L251**

```python
        # 其余意图 → GENERAL（默认）
```

作者注释，说明约束或设计意图；本行不执行。

**L252**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L254 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L254**

```python
    def __init__(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L255**

```python
        self,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L256**

```python
        api_key:  str,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L257**

```python
        base_url: Optional[str] = None,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L258**

```python
        model:    str = "claude-3-5-sonnet-20241022",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L259**

```python
        skill_manager: Optional[Any] = None,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L260**

```python
        client: Optional[Any] = None,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L261**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L262**

```python
        kwargs: Dict[str, Any] = {"api_key": api_key}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L263**

```python
        if base_url:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L264**

```python
            kwargs["base_url"] = base_url
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L265**

```python
        client = client or AsyncAnthropic(**kwargs)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L267**

```python
        self._intent_recognizer = IntentRecognizer(api_key=api_key, base_url=base_url, model=model, client=client)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L268**

```python
        self._skill_manager = skill_manager
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L270**

```python
        # Agent 池：每种类型可有多个实例（水平扩展）
```

作者注释，说明约束或设计意图；本行不执行。

**L271**

```python
        self._pool: Dict[AgentType, List[BaseAgent]] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L272**

```python
            AgentType.GENERAL:   [GeneralAgent(client, model, skill_manager)],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L273**

```python
            AgentType.TECHNICAL: [TechnicalAgent(client, model, skill_manager)],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L274**

```python
            AgentType.BILLING:   [BillingAgent(client, model, skill_manager)],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L275**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L277 · set_skill_manager

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L277**

```python
    def set_skill_manager(self, skill_manager: Optional[Any]) -> None:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L278**

```python
        """更新 SkillManager 引用，供运行时重载或测试替换使用。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L279**

```python
        self._skill_manager = skill_manager
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L280**

```python
        for agents in self._pool.values():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L281**

```python
            for agent in agents:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L282**

```python
                agent._skill_manager = skill_manager
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L284 · recognize_intent

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L284**

```python
    async def recognize_intent(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L285**

```python
        self,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L286**

```python
        message: str,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L287**

```python
        history: Optional[List[Dict[str, str]]] = None,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L288**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L289**

```python
        """对外暴露意图识别，供 API 层先判断是否需要 RAG 等前置能力。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L290**

```python
        return await self._intent_recognizer.recognize(message, history=history)
```

结束当前函数并把本行构造的结果交给调用方。

**L292**

```python
    # ── 主入口 ────────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L294 · run

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L294**

```python
    async def run(self, req: Request) -> OrchestratorResult:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L295**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L296**

```python
        处理一次请求的完整流程：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L297**

```python
          意图识别 → 路由选 Agent → 执行 → 检查升级 → 返回结果
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L298**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L299**

```python
        t0 = time.monotonic()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L301**

```python
        # 1. 意图识别（如果调用方已识别则跳过）
```

作者注释，说明约束或设计意图；本行不执行。

**L302**

```python
        if req.intent is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L303**

```python
            intent_result = await self._intent_recognizer.recognize(req.message, history=req.history)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L304**

```python
            req.intent  = intent_result.intent
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L305**

```python
            req.intent_group = intent_result.intent_group
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L306**

```python
            req.urgency = intent_result.urgency
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L307**

```python
            req.intent_confidence = intent_result.confidence
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L308**

```python
            req.entities = intent_result.entities
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L310**

```python
        if self._needs_clarification(req):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L311**

```python
            return OrchestratorResult(
```

结束当前函数并把本行构造的结果交给调用方。

**L312**

```python
                request_id=req.request_id,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L313**

```python
                response="我还不能确定您要处理的是哪类问题。请补充一下是订单物流、退款账单、账户资料，还是技术故障？",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L314**

```python
                agent_type=AgentType.GENERAL,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L315**

```python
                intent=req.intent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L316**

```python
                escalated=False,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L317**

```python
                latency_ms=(time.monotonic() - t0) * 1000,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L318**

```python
                agent_types=[AgentType.GENERAL],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L319**

```python
                primary_agent=AgentType.GENERAL,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L320**

```python
                routing_reason="低置信度 OTHER 意图，先澄清用户需求",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L321**

```python
                routing_confidence=req.intent_confidence,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L322**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L324**

```python
        # 复杂问题自动并行协作，例如同一句同时涉及登录故障和扣款/退款。
```

作者注释，说明约束或设计意图；本行不执行。

**L325**

```python
        decision = self._route_decision(req)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L326**

```python
        if decision.multi_agent:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L327**

```python
            return await self.run_parallel(req, decision)
```

结束当前函数并把本行构造的结果交给调用方。

**L329**

```python
        # 2. 执行主 Agent（含降级）
```

作者注释，说明约束或设计意图；本行不执行。

**L330**

```python
        response = await self._execute(req, decision.primary_agent)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L332**

```python
        # 4. 升级检查
```

作者注释，说明约束或设计意图；本行不执行。

**L333**

```python
        escalated = False
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L334**

```python
        if response.escalate or req.urgency == UrgencyLevel.CRITICAL or req.intent in (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L335**

```python
            IntentCategory.ESCALATION,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L336**

```python
            IntentCategory.HUMAN_HANDOFF,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L337**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L338**

```python
            escalated = True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L339**

```python
            logger.warning(f"请求 {req.request_id} 触发升级: urgency={req.urgency}")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L340**

```python
            # 生产环境：此处创建工单、通知人工客服
```

作者注释，说明约束或设计意图；本行不执行。

**L342**

```python
        return OrchestratorResult(
```

结束当前函数并把本行构造的结果交给调用方。

**L343**

```python
            request_id=req.request_id,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L344**

```python
            response=response.content,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L345**

```python
            agent_type=response.agent_type,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L346**

```python
            intent=req.intent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L347**

```python
            escalated=escalated,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L348**

```python
            latency_ms=(time.monotonic() - t0) * 1000,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L349**

```python
            agent_types=[response.agent_type],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L350**

```python
            primary_agent=decision.primary_agent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L351**

```python
            supporting_agents=[],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L352**

```python
            routing_reason=decision.reason,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L353**

```python
            routing_confidence=decision.confidence,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L354**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L356 · run_parallel

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L356**

```python
    async def run_parallel(self, req: Request, decision: RoutingDecision) -> OrchestratorResult:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L357**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L358**

```python
        并行派发给多个 Agent，合并结果。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L359**

```python
        适用于复杂问题（如同时涉及技术和账单）。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L360**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L361**

```python
        t0 = time.monotonic()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L362**

```python
        agent_types = decision.agent_types
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L363**

```python
        tasks = [self._execute(req, at) for at in agent_types]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L364**

```python
        responses = await asyncio.gather(*tasks, return_exceptions=True)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L366**

```python
        # 合并：主 Agent 在前，辅助 Agent 在后。
```

作者注释，说明约束或设计意图；本行不执行。

**L367**

```python
        parts = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L368**

```python
        for r in responses:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L369**

```python
            if isinstance(r, AgentResponse) and r.success:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L370**

```python
                role = "主处理" if r.agent_type == decision.primary_agent else "辅助处理"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L371**

```python
                parts.append(f"[{r.agent_type.value} - {role}]\n{r.content}")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L373**

```python
        combined = "\n\n".join(parts) if parts else "抱歉，所有 Agent 均处理失败。"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L374**

```python
        escalated = any(isinstance(r, AgentResponse) and r.escalate for r in responses)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L376**

```python
        return OrchestratorResult(
```

结束当前函数并把本行构造的结果交给调用方。

**L377**

```python
            request_id=req.request_id,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L378**

```python
            response=combined,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L379**

```python
            agent_type=decision.primary_agent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L380**

```python
            intent=req.intent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L381**

```python
            escalated=escalated,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L382**

```python
            latency_ms=(time.monotonic() - t0) * 1000,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L383**

```python
            agent_types=[
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L384**

```python
                r.agent_type for r in responses
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L385**

```python
                if isinstance(r, AgentResponse) and r.success
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L386**

```python
            ] or agent_types,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L387**

```python
            primary_agent=decision.primary_agent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L388**

```python
            supporting_agents=decision.supporting_agents,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L389**

```python
            routing_reason=decision.reason,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L390**

```python
            routing_confidence=decision.confidence,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L391**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L393**

```python
    # ── 路由逻辑 ──────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L395 · _route

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L395**

```python
    def _route(self, intent: Optional[IntentCategory], urgency: Optional[UrgencyLevel]) -> AgentType:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L396**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L397**

```python
        三层路由决策：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L398**

```python
          1. 意图映射
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L399**

```python
          2. 紧急度覆盖（CRITICAL 直接升级）
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L400**

```python
          3. 默认 GENERAL
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L401**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L402**

```python
        if urgency == UrgencyLevel.CRITICAL:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L403**

```python
            return AgentType.ESCALATION
```

结束当前函数并把本行构造的结果交给调用方。

**L405**

```python
        if intent and intent in self._INTENT_ROUTING:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L406**

```python
            target = self._INTENT_ROUTING[intent]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L407**

```python
            # 如果目标类型有可用实例则使用，否则降级
```

作者注释，说明约束或设计意图；本行不执行。

**L408**

```python
            if target in self._pool and self._pool[target]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L409**

```python
                return target
```

结束当前函数并把本行构造的结果交给调用方。

**L411**

```python
        return AgentType.GENERAL
```

结束当前函数并把本行构造的结果交给调用方。

### L413 · _route_decision

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L413**

```python
    def _route_decision(self, req: Request) -> RoutingDecision:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L414**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L415**

```python
        结构化路由决策。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L417**

```python
        先处理紧急/转人工，再用领域分数决定主 Agent 和辅助 Agent。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L418**

```python
        这样可以表达“主处理 + 辅助诊断”，避免关键词命中后无主次地拼接。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L419**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L420**

```python
        if req.urgency == UrgencyLevel.CRITICAL:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L421**

```python
            return RoutingDecision(
```

结束当前函数并把本行构造的结果交给调用方。

**L422**

```python
                primary_agent=AgentType.ESCALATION,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L423**

```python
                reason="紧急度为 CRITICAL，触发升级路由",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L424**

```python
                confidence=1.0,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L425**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L427**

```python
        if req.intent in (IntentCategory.ESCALATION, IntentCategory.HUMAN_HANDOFF):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L428**

```python
            return RoutingDecision(
```

结束当前函数并把本行构造的结果交给调用方。

**L429**

```python
                primary_agent=AgentType.ESCALATION,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L430**

```python
                reason=f"意图为 {req.intent.value if req.intent else 'unknown'}，触发升级路由",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L431**

```python
                confidence=max(req.intent_confidence, 0.8),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L432**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L434**

```python
        scores = self._domain_scores(req)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L435**

```python
        available_scores = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L436**

```python
            agent_type: score
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L437**

```python
            for agent_type, score in scores.items()
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L438**

```python
            if agent_type == AgentType.GENERAL or self._pool.get(agent_type)
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L439**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L440**

```python
        if not available_scores:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L441**

```python
            return RoutingDecision(
```

结束当前函数并把本行构造的结果交给调用方。

**L442**

```python
                primary_agent=AgentType.GENERAL,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L443**

```python
                reason="无可用专属 Agent，降级到 GeneralAgent",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L444**

```python
                confidence=0.1,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L445**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L447**

```python
        ordered = sorted(available_scores.items(), key=lambda item: item[1], reverse=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L448**

```python
        primary_agent, primary_score = ordered[0]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L449**

```python
        supporting_agents = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L450**

```python
            agent_type
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L451**

```python
            for agent_type, score in ordered[1:]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L452**

```python
            if agent_type != AgentType.GENERAL and score >= 0.45 and score >= primary_score * 0.55
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L453**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L455**

```python
        reason = self._routing_reason(req, available_scores, primary_agent, supporting_agents)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L456**

```python
        return RoutingDecision(
```

结束当前函数并把本行构造的结果交给调用方。

**L457**

```python
            primary_agent=primary_agent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L458**

```python
            supporting_agents=supporting_agents,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L459**

```python
            reason=reason,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L460**

```python
            confidence=round(min(primary_score, 1.0), 3),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L461**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L463 · _domain_scores

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L463**

```python
    def _domain_scores(self, req: Request) -> Dict[AgentType, float]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L464**

```python
        """按意图、关键词和实体为各领域 Agent 打分。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L465**

```python
        msg = req.message.lower()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L466**

```python
        scores = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L467**

```python
            AgentType.GENERAL: 0.1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L468**

```python
            AgentType.TECHNICAL: 0.0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L469**

```python
            AgentType.BILLING: 0.0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L470**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L472**

```python
        if req.intent in (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L473**

```python
            IntentCategory.QUERY,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L474**

```python
            IntentCategory.ORDER_STATUS,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L475**

```python
            IntentCategory.LOGISTICS,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L476**

```python
            IntentCategory.REQUEST,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L477**

```python
            IntentCategory.COMPLAINT,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L478**

```python
            IntentCategory.GREETING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L479**

```python
            IntentCategory.FEEDBACK,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L480**

```python
            IntentCategory.OTHER,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L481**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L482**

```python
            scores[AgentType.GENERAL] += 0.55
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L484**

```python
        if req.intent in (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L485**

```python
            IntentCategory.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L486**

```python
            IntentCategory.TECHNICAL_LOGIN,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L487**

```python
            IntentCategory.TECHNICAL_CRASH,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L488**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L489**

```python
            scores[AgentType.TECHNICAL] += 0.75
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L491**

```python
        if req.intent in (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L492**

```python
            IntentCategory.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L493**

```python
            IntentCategory.ACCOUNT,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L494**

```python
            IntentCategory.ACCOUNT_SECURITY,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L495**

```python
            IntentCategory.REFUND,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L496**

```python
            IntentCategory.INVOICE,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L497**

```python
            IntentCategory.PAYMENT_ISSUE,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L498**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L499**

```python
            scores[AgentType.BILLING] += 0.75
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L501**

```python
        technical_kws = ["崩溃", "报错", "error", "crash", "无法登录", "登录失败", "500", "401", "验证码"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L502**

```python
        billing_kws = ["退款", "退货", "扣款", "发票", "账单", "支付", "订阅", "refund", "invoice", "多扣"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L503**

```python
        general_kws = ["订单", "物流", "快递", "配送", "会员", "积分", "咨询", "帮助"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L505**

```python
        technical_hits = sum(1 for kw in technical_kws if kw in msg)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L506**

```python
        billing_hits = sum(1 for kw in billing_kws if kw in msg)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L507**

```python
        general_hits = sum(1 for kw in general_kws if kw in msg)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L509**

```python
        scores[AgentType.TECHNICAL] += min(0.45, technical_hits * 0.18)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L510**

```python
        scores[AgentType.BILLING] += min(0.45, billing_hits * 0.18)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L511**

```python
        scores[AgentType.GENERAL] += min(0.35, general_hits * 0.12)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L513**

```python
        entities = req.entities or {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L514**

```python
        if entities.get("error_code"):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L515**

```python
            scores[AgentType.TECHNICAL] += 0.2
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L516**

```python
        if entities.get("amount"):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L517**

```python
            scores[AgentType.BILLING] += 0.15
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L518**

```python
        if entities.get("order_id"):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L519**

```python
            scores[AgentType.GENERAL] += 0.1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L521**

```python
        return {agent_type: round(score, 3) for agent_type, score in scores.items()}
```

结束当前函数并把本行构造的结果交给调用方。

**L523**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L524 · _routing_reason

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L524**

```python
    def _routing_reason(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L525**

```python
        req: Request,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L526**

```python
        scores: Dict[AgentType, float],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L527**

```python
        primary_agent: AgentType,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L528**

```python
        supporting_agents: List[AgentType],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L529**

```python
    ) -> str:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L530**

```python
        score_text = ", ".join(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L531**

```python
            f"{agent_type.value}={score:.2f}"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L532**

```python
            for agent_type, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L533**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L534**

```python
        support_text = ", ".join(agent.value for agent in supporting_agents) or "none"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L535**

```python
        intent = req.intent.value if req.intent else "unknown"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L536**

```python
        return (
```

结束当前函数并把本行构造的结果交给调用方。

**L537**

```python
            f"intent={intent}, group={req.intent_group or 'unknown'}, "
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L538**

```python
            f"primary={primary_agent.value}, supporting={support_text}, scores=[{score_text}]"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L539**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L541 · _collaboration_targets

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L541**

```python
    def _collaboration_targets(self, req: Request) -> List[AgentType]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L542**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L543**

```python
        判断是否需要多个 Agent 并行协作。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L545**

```python
        意图识别通常只返回一个主意图；这里用领域关键词补充检测复合问题，
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L546**

```python
        例如"登录报错且被重复扣款"需要技术和账单 Agent 同时处理。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L547**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L548**

```python
        msg = req.message.lower()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L549**

```python
        targets: List[AgentType] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L551**

```python
        technical_kws = ["崩溃", "报错", "error", "crash", "无法登录", "登录失败", "500", "401"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L552**

```python
        billing_kws = ["退款", "扣款", "发票", "账单", "支付", "订阅", "refund", "invoice"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L554**

```python
        if req.intent in (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L555**

```python
            IntentCategory.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L556**

```python
            IntentCategory.TECHNICAL_LOGIN,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L557**

```python
            IntentCategory.TECHNICAL_CRASH,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L558**

```python
        ) or any(kw in msg for kw in technical_kws):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L559**

```python
            targets.append(AgentType.TECHNICAL)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L560**

```python
        if req.intent in (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L561**

```python
            IntentCategory.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L562**

```python
            IntentCategory.ACCOUNT,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L563**

```python
            IntentCategory.ACCOUNT_SECURITY,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L564**

```python
            IntentCategory.REFUND,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L565**

```python
            IntentCategory.INVOICE,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L566**

```python
            IntentCategory.PAYMENT_ISSUE,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L567**

```python
        ) or any(kw in msg for kw in billing_kws):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L568**

```python
            targets.append(AgentType.BILLING)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L570**

```python
        # 保持顺序去重，并只返回当前有实例的 Agent 类型。
```

作者注释，说明约束或设计意图；本行不执行。

**L571**

```python
        deduped = list(dict.fromkeys(targets))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L572**

```python
        return [agent_type for agent_type in deduped if self._pool.get(agent_type)]
```

结束当前函数并把本行构造的结果交给调用方。

**L574**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L575 · _needs_clarification

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L575**

```python
    def _needs_clarification(req: Request) -> bool:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L576**

```python
        """低置信度且无明确意图时，先追问，避免误路由。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L577**

```python
        if req.intent != IntentCategory.OTHER:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L578**

```python
            return False
```

结束当前函数并把本行构造的结果交给调用方。

**L579**

```python
        text = (req.message or "").strip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L580**

```python
        if len(text) <= 2:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L581**

```python
            return False
```

结束当前函数并把本行构造的结果交给调用方。

**L582**

```python
        return req.intent_confidence < 0.5
```

结束当前函数并把本行构造的结果交给调用方。

### L584 · _best_agent

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L584**

```python
    def _best_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L585**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L586**

```python
        性能路由：从同类 Agent 中选 routing_score() 最高的。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L587**

```python
        这是"基于在线表现动态调整路由"的核心。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L588**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L589**

```python
        agents = self._pool.get(agent_type, [])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L590**

```python
        if not agents:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L591**

```python
            return None
```

结束当前函数并把本行构造的结果交给调用方。

**L592**

```python
        return max(agents, key=lambda a: a.stats.routing_score())
```

结束当前函数并把本行构造的结果交给调用方。

### L594 · _execute

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L594**

```python
    async def _execute(self, req: Request, agent_type: AgentType) -> AgentResponse:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L595**

```python
        """执行 Agent，失败时降级到 GeneralAgent。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L596**

```python
        agent = self._best_agent(agent_type)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L597**

```python
        if agent is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L598**

```python
            agent = self._best_agent(AgentType.GENERAL)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L599**

```python
        if agent is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L600**

```python
            return AgentResponse(
```

结束当前函数并把本行构造的结果交给调用方。

**L601**

```python
                agent_type=AgentType.GENERAL,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L602**

```python
                content="服务暂时不可用，请稍后重试。",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L603**

```python
                success=False,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L604**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L606**

```python
        response = await agent.handle(req)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L608**

```python
        # 专属 Agent 失败时降级到 GeneralAgent
```

作者注释，说明约束或设计意图；本行不执行。

**L609**

```python
        if not response.success and agent_type != AgentType.GENERAL:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L610**

```python
            logger.warning(f"{agent_type.value} 失败，降级到 GeneralAgent")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L611**

```python
            fallback = self._best_agent(AgentType.GENERAL)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L612**

```python
            if fallback:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L613**

```python
                response = await fallback.handle(req)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L615**

```python
        return response
```

结束当前函数并把本行构造的结果交给调用方。

**L617**

```python
    # ── 统计（供 Monitor 读取）────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L619 · get_stats

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L619**

```python
    def get_stats(self) -> Dict[str, Any]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L620**

```python
        result = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L621**

```python
        for agent_type, agents in self._pool.items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L622**

```python
            for i, agent in enumerate(agents):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L623**

```python
                key = f"{agent_type.value}_{i}"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L624**

```python
                result[key] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L625**

```python
                    "total":        agent.stats.total,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L626**

```python
                    "success_rate": round(agent.stats.success_rate, 3),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L627**

```python
                    "avg_ms":       round(agent.stats.avg_ms, 1),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L628**

```python
                    "monitor_penalty": round(agent.stats.monitor_penalty, 3),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L629**

```python
                    "routing_score": round(agent.stats.routing_score(), 3),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L630**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L631**

```python
        return result
```

结束当前函数并把本行构造的结果交给调用方。

### L633 · update_routing_penalties

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L633**

```python
    def update_routing_penalties(self, penalties: Dict[str, float]) -> None:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L634**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L635**

```python
        接收 Monitor 的在线表现反馈，动态调整路由惩罚项。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L637**

```python
        penalties 的 key 使用 get_stats() 中的 agent key，例如 technical_0。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L638**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L639**

```python
        for agent_type, agents in self._pool.items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L640**

```python
            for i, agent in enumerate(agents):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L641**

```python
                key = f"{agent_type.value}_{i}"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L642**

```python
                penalty = penalties.get(key, 0.0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L643**

```python
                agent.stats.monitor_penalty = min(max(penalty, 0.0), 0.9)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

## 结合全项目看：边界与增强

单独运行旧编排方法与新版 HTTP 链路不同；置信度校准、真正多实例调度和路由消融仍需验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
