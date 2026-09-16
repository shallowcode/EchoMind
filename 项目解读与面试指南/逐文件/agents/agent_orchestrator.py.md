# agents/agent_orchestrator.py 解读

## 输入、输出与流向

**定位：** 用规则做领域路由，再调用角色不同的 LLM Agent。

**输入：** Request：message、user_id、conv_id、context、history、entities、intent、urgency、intent_confidence；可选 SkillManager。

**输出 / 副作用：** OrchestratorResult：回答、实际/计划 Agent、路由理由、升级标记和编排延迟；副作用：请求补齐意图、实例累计统计。

**流向：** run → 必要时识别 → 低置信度澄清 → _route_decision → 单 Agent _execute 或 run_parallel → _best_agent → BaseAgent.handle → 拼 Skills 与背景 → LLM → 统计/降级/返回。

[返回阅读入口](../../README.md) · [对照原文件](../../../agents/agent_orchestrator.py)

当前工作区快照：641 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`7f2ccf43c9133a9c3616dd1ec4ca7f18f4e9f6af514903eaafa007e1ea10e269`。

## 类与函数导航

[AgentType](#symbol-37) → [AgentStats](#symbol-44) → [AgentStats.success_rate](#symbol-52) → [AgentStats.avg_ms](#symbol-56) → [AgentStats.routing_score](#symbol-60) → [AgentResponse](#symbol-67) → [Request](#symbol-77) → [OrchestratorResult](#symbol-92) → [RoutingDecision](#symbol-107) → [RoutingDecision.agent_types](#symbol-115) → [RoutingDecision.multi_agent](#symbol-119) → [BaseAgent](#symbol-126) → [BaseAgent.__init__](#symbol-132) → [BaseAgent.handle](#symbol-138) → [BaseAgent._call_llm](#symbol-165) → [_clean](#symbol-166) → [BaseAgent._build_system_prompt](#symbol-187) → [BaseAgent._needs_escalation](#symbol-196) → [GeneralAgent](#symbol-202) → [TechnicalAgent](#symbol-210) → [BillingAgent](#symbol-218) → [AgentOrchestrator](#symbol-228) → [AgentOrchestrator.__init__](#symbol-254) → [AgentOrchestrator.set_skill_manager](#symbol-276) → [AgentOrchestrator.recognize_intent](#symbol-283) → [AgentOrchestrator.run](#symbol-293) → [AgentOrchestrator.run_parallel](#symbol-354) → [AgentOrchestrator._route](#symbol-393) → [AgentOrchestrator._route_decision](#symbol-411) → [AgentOrchestrator._domain_scores](#symbol-461) → [AgentOrchestrator._routing_reason](#symbol-521) → [AgentOrchestrator._collaboration_targets](#symbol-539) → [AgentOrchestrator._needs_clarification](#symbol-572) → [AgentOrchestrator._best_agent](#symbol-582) → [AgentOrchestrator._execute](#symbol-592) → [AgentOrchestrator.get_stats](#symbol-617) → [AgentOrchestrator.update_routing_penalties](#symbol-631)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>亮点：多 Agent 路由与编排</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>核心问题：多 Agent 情况下如何做 Routing？</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | （空行） | 空行，分隔逻辑。 |
| L6 | <code>路由策略（三层决策）：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;1. 意图路由 —— 根据 IntentCategory 直接映射到专属 Agent</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L8 | <code>&nbsp;&nbsp;2. 性能路由 —— 同类 Agent 有多个时，选成功率最高、延迟最低的</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L9 | <code>&nbsp;&nbsp;3. 降级路由 —— 专属 Agent 不可用时，自动降级到 GeneralAgent</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L10 | （空行） | 空行，分隔逻辑。 |
| L11 | <code>并行协作：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L12 | <code>&nbsp;&nbsp;- 复杂问题（如&quot;技术问题 + 账单问题&quot;）可同时派发给多个 Agent</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L13 | <code>&nbsp;&nbsp;- 结果由 Orchestrator 合并后返回</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L14 | （空行） | 空行，分隔逻辑。 |
| L15 | <code>升级机制：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L16 | <code>&nbsp;&nbsp;- Agent 置信度低于阈值 → 自动升级到更高级 Agent 或转人工</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L17 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L18 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L19 | <code>import json</code> | 导入 <code>import json</code>；只建立名称依赖，真正业务调用见后文。 |
| L20 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L21 | <code>import time</code> | 导入 <code>import time</code>；只建立名称依赖，真正业务调用见后文。 |
| L22 | <code>import uuid</code> | 导入 <code>import uuid</code>；只建立名称依赖，真正业务调用见后文。 |
| L23 | <code>from dataclasses import dataclass, field</code> | 导入 <code>from dataclasses import dataclass, field</code>；只建立名称依赖，真正业务调用见后文。 |
| L24 | <code>from enum import Enum</code> | 导入 <code>from enum import Enum</code>；只建立名称依赖，真正业务调用见后文。 |
| L25 | <code>from typing import Any, Dict, List, Optional</code> | 导入 <code>from typing import Any, Dict, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L26 | （空行） | 空行，分隔逻辑。 |
| L27 | <code>from anthropic import AsyncAnthropic</code> | 导入 <code>from anthropic import AsyncAnthropic</code>；只建立名称依赖，真正业务调用见后文。 |
| L28 | （空行） | 空行，分隔逻辑。 |
| L29 | <code>from core.intent_recognizer import IntentCategory, IntentRecognizer, UrgencyLevel</code> | 导入 <code>from core.intent_recognizer import IntentCategory, IntentRecognizer, UrgencyLevel</code>；只建立名称依赖，真正业务调用见后文。 |
| L30 | <code>from core.llm_utils import extract_text_content</code> | 导入 <code>from core.llm_utils import extract_text_content</code>；只建立名称依赖，真正业务调用见后文。 |
| L31 | （空行） | 空行，分隔逻辑。 |
| L32 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L33 | （空行） | 空行，分隔逻辑。 |
| L34 | （空行） | 空行，分隔逻辑。 |
| L35 | <code># ── 数据结构 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 数据结构 ────────────────────────────────────────────────────────────────── |
| L36 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-37"></a>

### L37–L41 · AgentType

四种目标标签，只有 general/technical/billing 有实例；escalation 表达路由意图。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L37 | <code>class AgentType(Enum):</code> | 定义 <code>AgentType</code> 的数据契约/行为；继承与字段见本段。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;GENERAL   = &quot;general&quot;    # 通用客服</code> | 将结果保存到 <code>GENERAL</code>：使用固定文本/配置值。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;TECHNICAL = &quot;technical&quot;  # 技术支持</code> | 将结果保存到 <code>TECHNICAL</code>：使用固定文本/配置值。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;BILLING   = &quot;billing&quot;    # 账单/退款</code> | 将结果保存到 <code>BILLING</code>：使用固定文本/配置值。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ESCALATION = &quot;escalation&quot; # 人工升级（占位）</code> | 将结果保存到 <code>ESCALATION</code>：使用固定文本/配置值。 |
| L42 | （空行） | 空行，分隔逻辑。 |
| L43 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-44"></a>

### L44–L64 · AgentStats

total 在请求开始就加，success 在 LLM 返回后加；进行中的请求可能暂时拉低成功率。total_ms 累积成功与失败耗时。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L44 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L45 | <code>class AgentStats:</code> | 定义 <code>AgentStats</code> 的数据契约/行为；继承与字段见本段。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;Agent 运行时统计，供 Monitor 和路由决策使用。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;total:     int   = 0</code> | 将结果保存到 <code>total</code>：使用这里写明的固定值。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;success:   int   = 0</code> | 将结果保存到 <code>success</code>：使用这里写明的固定值。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;total_ms:  float = 0.0</code> | 将结果保存到 <code>total_ms</code>：使用这里写明的固定值。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;monitor_penalty: float = 0.0</code> | 将结果保存到 <code>monitor_penalty</code>：使用这里写明的固定值。 |
| L51 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-52"></a>

### L52–L54 · AgentStats.success_rate

没有样本默认 1.0，是冷启动乐观估计；不能解释为验证过 100% 成功。

**签名输入：** <code>self</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def success_rate(self) -&gt; float:</code> | 定义函数 <code>success_rate</code>；输入参数见签名，下方导读解释调用目的。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.success / self.total if self.total else 1.0</code> | 结束当前函数并返回；条件 <code>self.total</code> 成立选前值，否则选 else 后值。 |
| L55 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-56"></a>

### L56–L58 · AgentStats.avg_ms

累计平均值，不是最近窗口或 P95。

**签名输入：** <code>self</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def avg_ms(self) -&gt; float:</code> | 定义函数 <code>avg_ms</code>；输入参数见签名，下方导读解释调用目的。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.total_ms / self.total if self.total else 0.0</code> | 结束当前函数并返回；条件 <code>self.total</code> 成立选前值，否则选 else 后值。 |
| L59 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-60"></a>

### L60–L64 · AgentStats.routing_score

实例分数=(0.7×成功率+0.3×1/(1+平均毫秒/1000))×(1-惩罚)。例如 sr=.9、avg=1000ms、penalty=.2，得到 (.63+.15)×.8=.624。

**签名输入：** <code>self</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def routing_score(self) -&gt; float:</code> | 定义函数 <code>routing_score</code>；输入参数见签名，下方导读解释调用目的。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;路由评分：成功率高、延迟低的 Agent 得分高。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_score = 1.0 / (1.0 + self.avg_ms / 1000)</code> | 将结果保存到 <code>latency_score</code>：按此表达式计算 <code>1.0 / (1.0 + self.avg_ms / 1000)</code>。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_score = self.success_rate * 0.7 + latency_score * 0.3</code> | 将结果保存到 <code>base_score</code>：按此表达式计算 <code>self.success_rate * 0.7 + latency_score * 0.3</code>。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return base_score * max(0.0, 1.0 - self.monitor_penalty)</code> | 结束当前函数并返回；按此表达式计算 <code>base_score * max(0.0, 1.0 - self.monitor_penalty)</code>。 |
| L65 | （空行） | 空行，分隔逻辑。 |
| L66 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-67"></a>

### L67–L74 · AgentResponse

单次 Agent 执行结果；success 只标识调用是否异常，escalate 来自回复中的词。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L67 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L68 | <code>class AgentResponse:</code> | 定义 <code>AgentResponse</code> 的数据契约/行为；继承与字段见本段。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_type:  AgentType</code> | 声明字段 <code>agent_type</code> 的类型，赋值由构造方完成。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;content:     str</code> | 声明字段 <code>content</code> 的类型，赋值由构造方完成。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;success:     bool</code> | 声明字段 <code>success</code> 的类型，赋值由构造方完成。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;confidence:  float = 1.0</code> | 将结果保存到 <code>confidence</code>：使用这里写明的固定值。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;latency_ms:  float = 0.0</code> | 将结果保存到 <code>latency_ms</code>：使用这里写明的固定值。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;escalate:    bool  = False   # 是否需要升级</code> | 将结果保存到 <code>escalate</code>：使用这里写明的固定值。 |
| L75 | （空行） | 空行，分隔逻辑。 |
| L76 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-77"></a>

### L77–L89 · Request

内部请求对象把意图/记忆/实体汇合。default_factory 为每个请求独立创建字典、列表/ID，防止共享可变默认值。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L77 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L78 | <code>class Request:</code> | 定义 <code>Request</code> 的数据契约/行为；继承与字段见本段。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;message:     str</code> | 声明字段 <code>message</code> 的类型，赋值由构造方完成。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;user_id:     str</code> | 声明字段 <code>user_id</code> 的类型，赋值由构造方完成。 |
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;conv_id:     str</code> | 声明字段 <code>conv_id</code> 的类型，赋值由构造方完成。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;context:     str = &quot;&quot;        # 来自 MemoryManager 的格式化上下文</code> | 将结果保存到 <code>context</code>：使用固定文本/配置值。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;history:     Optional[List[Dict[str, str]]] = None  # 对话历史，传给意图识别</code> | 将结果保存到 <code>history</code>：使用这里写明的固定值。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;entities:    Dict[str, List[str]] = field(default_factory=dict)</code> | 将结果保存到 <code>entities</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent:      Optional[IntentCategory] = None</code> | 将结果保存到 <code>intent</code>：使用这里写明的固定值。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_group: Optional[str] = None</code> | 将结果保存到 <code>intent_group</code>：使用这里写明的固定值。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;urgency:     Optional[UrgencyLevel]   = None</code> | 将结果保存到 <code>urgency</code>：使用这里写明的固定值。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_confidence: float = 1.0</code> | 将结果保存到 <code>intent_confidence</code>：使用这里写明的固定值。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;request_id:  str = field(default_factory=lambda: str(uuid.uuid4())[:8])</code> | 将结果保存到 <code>request_id</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L90 | （空行） | 空行，分隔逻辑。 |
| L91 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-92"></a>

### L92–L104 · OrchestratorResult

返回统一结构，primary_agent 是计划主 Agent，agent_type 单路时反映实际执行者；并行时被填为计划主 Agent，口径不同。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L92 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L93 | <code>class OrchestratorResult:</code> | 定义 <code>OrchestratorResult</code> 的数据契约/行为；继承与字段见本段。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;request_id:  str</code> | 声明字段 <code>request_id</code> 的类型，赋值由构造方完成。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;response:    str</code> | 声明字段 <code>response</code> 的类型，赋值由构造方完成。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_type:  AgentType</code> | 声明字段 <code>agent_type</code> 的类型，赋值由构造方完成。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent:      Optional[IntentCategory]</code> | 声明字段 <code>intent</code> 的类型，赋值由构造方完成。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;escalated:   bool  = False</code> | 将结果保存到 <code>escalated</code>：使用这里写明的固定值。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;latency_ms:  float = 0.0</code> | 将结果保存到 <code>latency_ms</code>：使用这里写明的固定值。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_types: List[AgentType] = field(default_factory=list)</code> | 将结果保存到 <code>agent_types</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;primary_agent: Optional[AgentType] = None</code> | 将结果保存到 <code>primary_agent</code>：使用这里写明的固定值。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents: List[AgentType] = field(default_factory=list)</code> | 将结果保存到 <code>supporting_agents</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;routing_reason: str = &quot;&quot;</code> | 将结果保存到 <code>routing_reason</code>：使用固定文本/配置值。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;routing_confidence: float = 0.0</code> | 将结果保存到 <code>routing_confidence</code>：使用这里写明的固定值。 |
| L105 | （空行） | 空行，分隔逻辑。 |
| L106 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-107"></a>

### L107–L121 · RoutingDecision

执行前计划：主 Agent、辅助 Agent、原因、分数。计划与实际结果分离，才有可能解释故障降级。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L107 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L108 | <code>class RoutingDecision:</code> | 定义 <code>RoutingDecision</code> 的数据契约/行为；继承与字段见本段。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;一次请求的结构化路由决策。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;primary_agent: AgentType</code> | 声明字段 <code>primary_agent</code> 的类型，赋值由构造方完成。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents: List[AgentType] = field(default_factory=list)</code> | 将结果保存到 <code>supporting_agents</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;reason: str = &quot;&quot;</code> | 将结果保存到 <code>reason</code>：使用固定文本/配置值。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;confidence: float = 0.0</code> | 将结果保存到 <code>confidence</code>：使用这里写明的固定值。 |
| L114 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-115"></a>

### L115–L117 · RoutingDecision.agent_types

主 Agent 放首位再拼辅助列表；gather 保持任务列表的结果顺序。

**签名输入：** <code>self</code>；**返回契约：** <code>List[AgentType]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def agent_types(self) -&gt; List[AgentType]:</code> | 定义函数 <code>agent_types</code>；输入参数见签名，下方导读解释调用目的。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [self.primary_agent] + self.supporting_agents</code> | 结束当前函数并返回；按此表达式计算 <code>[self.primary_agent] + self.supporting_agents</code>。 |
| L118 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-119"></a>

### L119–L121 · RoutingDecision.multi_agent

只要存在至少一个辅助 Agent 就并行。

**签名输入：** <code>self</code>；**返回契约：** <code>bool</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def multi_agent(self) -&gt; bool:</code> | 定义函数 <code>multi_agent</code>；输入参数见签名，下方导读解释调用目的。 |
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return bool(self.supporting_agents)</code> | 结束当前函数并返回；求真值。 |
| L122 | （空行） | 空行，分隔逻辑。 |
| L123 | （空行） | 空行，分隔逻辑。 |
| L124 | <code># ── 基础 Agent ────────────────────────────────────────────────────────────────</code> | 源码注释：── 基础 Agent ──────────────────────────────────────────────────────────────── |
| L125 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-126"></a>

### L126–L199 · BaseAgent

用规则做领域路由，再调用角色不同的 LLM Agent。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L126 | <code>class BaseAgent:</code> | 定义 <code>BaseAgent</code> 的数据契约/行为；继承与字段见本段。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;所有 Agent 的基类，封装 LLM 调用和统计。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L128 | （空行） | 空行，分隔逻辑。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_type: AgentType</code> | 声明字段 <code>agent_type</code> 的类型，赋值由构造方完成。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;system_prompt: str</code> | 声明字段 <code>system_prompt</code> 的类型，赋值由构造方完成。 |
| L131 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-132"></a>

### L132–L136 · BaseAgent.__init__

共享客户端与模型，仅各实例 stats 独立；动态规则通过可选管理器注入。

**签名输入：** <code>self, client: AsyncAnthropic, model: str, skill_manager: Optional[Any]=None</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, client: AsyncAnthropic, model: str, skill_manager: Optional[Any] = None):</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._client = client</code> | 将结果保存到 <code>self._client</code>：读取 <code>client</code>。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._model  = model</code> | 将结果保存到 <code>self._model</code>：读取 <code>model</code>。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._skill_manager = skill_manager</code> | 将结果保存到 <code>self._skill_manager</code>：读取 <code>skill_manager</code>。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stats   = AgentStats()</code> | 将结果保存到 <code>self.stats</code>：进入 <code>AgentStats</code>：total 在请求开始就加，success 在 LLM 返回后加；进行中的请求可能暂时拉低成功率。 |
| L137 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-138"></a>

### L138–L163 · BaseAgent.handle

统一包装计时、统计、LLM 异常处理和升级关键词检测。异常被转为 AgentResponse(success=False)，让编排器决定是否降级。

**签名输入：** <code>self, req: Request</code>；**返回契约：** <code>AgentResponse</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def handle(self, req: Request) -&gt; AgentResponse:</code> | 定义异步函数 <code>handle</code>；输入参数见签名，下方导读解释调用目的。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;t0 = time.monotonic()</code> | 将结果保存到 <code>t0</code>：读取单调时钟，用来算耗时/过期，不作为日历时间。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stats.total += 1</code> | 更新 <code>self.stats.total</code>：<code>self.stats.total += 1</code>；此处会改变累计状态。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content = await self._call_llm(req)</code> | 将结果保存到 <code>content</code>：等待完成后继续；进入 <code>self._call_llm</code>：把记忆和实体放在 user 消息，并插入人工构造的 assistant 确认句，最后是实际问题。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ms = (time.monotonic() - t0) * 1000</code> | 将结果保存到 <code>ms</code>：按此表达式计算 <code>(time.monotonic() - t0) * 1000</code>。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stats.success += 1</code> | 更新 <code>self.stats.success</code>：<code>self.stats.success += 1</code>；此处会改变累计状态。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stats.total_ms += ms</code> | 更新 <code>self.stats.total_ms</code>：<code>self.stats.total_ms += ms</code>；此处会改变累计状态。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalate = self._needs_escalation(content)</code> | 将结果保存到 <code>escalate</code>：进入 <code>self._needs_escalation</code>：大小写敏感子串匹配；“不需要转人工”也命中，specialist 等词也可能误报。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return AgentResponse(</code> | 结束当前函数并返回；进入 <code>AgentResponse</code>：单次 Agent 执行结果；success 只标识调用是否异常，escalate 来自回复中的词。 |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type=self.agent_type,</code> | 参数 <code>agent_type</code>（Agent 类别）：读取 <code>self.agent_type</code>。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content=content,</code> | 参数 <code>content</code>（文本正文）：读取 <code>content</code>。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;success=True,</code> | 参数 <code>success</code>（执行成功标记）：使用这里写明的固定值。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=ms,</code> | 参数 <code>latency_ms</code>（当前计时范围的毫秒耗时）：读取 <code>ms</code>。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalate=escalate,</code> | 参数 <code>escalate</code>（escalate）：读取 <code>escalate</code>。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ms = (time.monotonic() - t0) * 1000</code> | 将结果保存到 <code>ms</code>：按此表达式计算 <code>(time.monotonic() - t0) * 1000</code>。 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.stats.total_ms += ms</code> | 更新 <code>self.stats.total_ms</code>：<code>self.stats.total_ms += ms</code>；此处会改变累计状态。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.error(f&quot;{self.agent_type.value} 处理失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return AgentResponse(</code> | 结束当前函数并返回；进入 <code>AgentResponse</code>：单次 Agent 执行结果；success 只标识调用是否异常，escalate 来自回复中的词。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type=self.agent_type,</code> | 参数 <code>agent_type</code>（Agent 类别）：读取 <code>self.agent_type</code>。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content=&quot;抱歉，处理您的请求时出现问题，请稍后重试。&quot;,</code> | 参数 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;success=False,</code> | 参数 <code>success</code>（执行成功标记）：使用这里写明的固定值。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=ms,</code> | 参数 <code>latency_ms</code>（当前计时范围的毫秒耗时）：读取 <code>ms</code>。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L164 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-165"></a>

### L165–L185 · BaseAgent._call_llm

把记忆和实体放在 user 消息，并插入人工构造的 assistant 确认句，最后是实际问题。一次 messages.create 只取文本，不传 tools，不解析 tool_use。

**签名输入：** <code>self, req: Request</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _call_llm(self, req: Request) -&gt; str:</code> | 定义异步函数 <code>_call_llm</code>；输入参数见签名，下方导读解释调用目的。 |

<a id="symbol-166"></a>

### L166–L167 · _clean

清除非法 Unicode 代理字符，解决编码错误；不是提示注入防护。

**签名输入：** <code>s: str</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;def _clean(s: str) -&gt; str:</code> | 定义函数 <code>_clean</code>；输入参数见签名，下方导读解释调用目的。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return s.encode(&quot;utf-8&quot;, errors=&quot;ignore&quot;).decode(&quot;utf-8&quot;)</code> | 结束当前函数并返回；调用 <code>s.encode(&#x27;utf-8&#x27;, errors=&#x27;ignore&#x27;).decode</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L168 | （空行） | 空行，分隔逻辑。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages = []</code> | 将结果保存到 <code>messages</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.context:</code> | 判断 <code>req.context</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages.append({&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: f&quot;[背景信息]\n{_clean(req.context)}&quot;})</code> | 追加一个元素到当前列表。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages.append({&quot;role&quot;: &quot;assistant&quot;, &quot;content&quot;: &quot;好的，我已了解背景信息。&quot;})</code> | 追加一个元素到当前列表。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.entities:</code> | 判断 <code>req.entities</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entities_text = json.dumps(req.entities, ensure_ascii=False)</code> | 将结果保存到 <code>entities_text</code>：把对象序列化为 JSON 文本供存储、提示词或缓存 key 使用。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages.append({&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: f&quot;[结构化实体]\n{_clean(entities_text)}&quot;})</code> | 追加一个元素到当前列表。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages.append({&quot;role&quot;: &quot;assistant&quot;, &quot;content&quot;: &quot;好的，我会结合这些结构化实体处理。&quot;})</code> | 追加一个元素到当前列表。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages.append({&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: _clean(req.message)})</code> | 追加一个元素到当前列表。 |
| L178 | （空行） | 空行，分隔逻辑。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await self._client.messages.create(</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=self._model,</code> | 参数 <code>model</code>（模型名称）：读取 <code>self._model</code>。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_tokens=1024,</code> | 参数 <code>max_tokens</code>（模型最多输出 token 数）：使用这里写明的固定值。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;system=self._build_system_prompt(req),</code> | 参数 <code>system</code>（模型系统指令）：进入 <code>self._build_system_prompt</code>：原有角色指令 + 当前请求匹配的 Skill 文本。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages=messages,</code> | 参数 <code>messages</code>（模型消息序列/当前函数的消息列表）：读取 <code>messages</code>。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return extract_text_content(resp.content)</code> | 结束当前函数并返回；进入共享响应适配器，只保留模型文本块。 |
| L186 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-187"></a>

### L187–L194 · BaseAgent._build_system_prompt

原有角色指令 + 当前请求匹配的 Skill 文本。业务规则外置便于运营改动，但本质仍是模型输入，不能代替后端权限控制。

**签名输入：** <code>self, req: Request</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _build_system_prompt(self, req: Request) -&gt; str:</code> | 定义函数 <code>_build_system_prompt</code>；输入参数见签名，下方导读解释调用目的。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;把动态加载的 Skills 拼入 system prompt，让业务规则随请求生效。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._skill_manager is None:</code> | 判断 <code>self._skill_manager is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.system_prompt</code> | 结束当前函数并返回；读取 <code>self.system_prompt</code>。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;skill_prompt = self._skill_manager.prompt_for(req.message, self.agent_type.value)</code> | 将结果保存到 <code>skill_prompt</code>：进入 <code>self._skill_manager.prompt_for</code>：按已加载顺序检查匹配，构造块并消耗 remaining，耗尽停止。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not skill_prompt:</code> | 判断 <code>not skill_prompt</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.system_prompt</code> | 结束当前函数并返回；读取 <code>self.system_prompt</code>。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return f&quot;{self.system_prompt}\n\n[动态 Skills]\n{skill_prompt}&quot;</code> | 结束当前函数并返回；将变量插入模板，构造提示词、标识或可读说明。 |
| L195 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-196"></a>

### L196–L199 · BaseAgent._needs_escalation

大小写敏感子串匹配；“不需要转人工”也命中，specialist 等词也可能误报。

**签名输入：** <code>self, content: str</code>；**返回契约：** <code>bool</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _needs_escalation(self, content: str) -&gt; bool:</code> | 定义函数 <code>_needs_escalation</code>；输入参数见签名，下方导读解释调用目的。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;检测 Agent 是否建议升级（简单关键词检测）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keywords = [&quot;转人工&quot;, &quot;人工客服&quot;, &quot;escalate&quot;, &quot;specialist&quot;, &quot;无法处理&quot;]</code> | 将结果保存到 <code>keywords</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return any(kw in content for kw in keywords)</code> | 结束当前函数并返回；至少一项为真就返回True，并可提前结束迭代。 |
| L200 | （空行） | 空行，分隔逻辑。 |
| L201 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-202"></a>

### L202–L207 · GeneralAgent

只覆盖类别和 system_prompt，复用父类调用代码；负责基础客服说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L202 | <code>class GeneralAgent(BaseAgent):</code> | 定义 <code>GeneralAgent</code> 的数据契约/行为；继承与字段见本段。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_type    = AgentType.GENERAL</code> | 将结果保存到 <code>agent_type</code>：读取 <code>AgentType.GENERAL</code>。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;system_prompt = (</code> | 将结果保存到 <code>system_prompt</code>：使用固定文本/配置值。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;你是 EchoMind 智能客服。友好、简洁地回答用户问题。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;如果问题超出你的能力范围，明确说明并建议转接专业客服。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L208 | （空行） | 空行，分隔逻辑。 |
| L209 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-210"></a>

### L210–L215 · TechnicalAgent

角色偏向诊断和步骤，没有实际后台日志/维修工具。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L210 | <code>class TechnicalAgent(BaseAgent):</code> | 定义 <code>TechnicalAgent</code> 的数据契约/行为；继承与字段见本段。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_type    = AgentType.TECHNICAL</code> | 将结果保存到 <code>agent_type</code>：读取 <code>AgentType.TECHNICAL</code>。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;system_prompt = (</code> | 将结果保存到 <code>system_prompt</code>：使用固定文本/配置值。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;你是技术支持专家。专注于：故障排查、错误诊断、系统配置。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;提供清晰的步骤化解决方案。遇到需要后台操作的问题，说明需要升级处理。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L216 | （空行） | 空行，分隔逻辑。 |
| L217 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-218"></a>

### L218–L223 · BillingAgent

提供账务说明并要求人工审核，没有退款支付执行器。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L218 | <code>class BillingAgent(BaseAgent):</code> | 定义 <code>BillingAgent</code> 的数据契约/行为；继承与字段见本段。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_type    = AgentType.BILLING</code> | 将结果保存到 <code>agent_type</code>：读取 <code>AgentType.BILLING</code>。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;system_prompt = (</code> | 将结果保存到 <code>system_prompt</code>：使用固定文本/配置值。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;你是账单服务专家。专注于：账单查询、退款申请、发票问题、订阅管理。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;对财务问题保持准确和专业。涉及实际退款操作时，说明需要人工审核。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L224 | （空行） | 空行，分隔逻辑。 |
| L225 | （空行） | 空行，分隔逻辑。 |
| L226 | <code># ── 编排器 ────────────────────────────────────────────────────────────────────</code> | 源码注释：── 编排器 ──────────────────────────────────────────────────────────────────── |
| L227 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-228"></a>

### L228–L641 · AgentOrchestrator

用规则做领域路由，再调用角色不同的 LLM Agent。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L228 | <code>class AgentOrchestrator:</code> | 定义 <code>AgentOrchestrator</code> 的数据契约/行为；继承与字段见本段。 |
| L229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;多 Agent 编排器。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L231 | （空行） | 空行，分隔逻辑。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;路由逻辑（三层）：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. 意图 → Agent 类型映射</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. 同类多实例时按 routing_score() 选最优</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. 专属 Agent 失败时降级到 GeneralAgent</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L237 | （空行） | 空行，分隔逻辑。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 意图 → Agent 类型的静态映射（路由表）</code> | 源码注释：意图 → Agent 类型的静态映射（路由表） |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_INTENT_ROUTING: Dict[IntentCategory, AgentType] = {</code> | 将结果保存到 <code>_INTENT_ROUTING</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL:  AgentType.TECHNICAL,</code> | 字段 <code>IntentCategory.TECHNICAL</code>（当前映射中的键）：读取 <code>AgentType.TECHNICAL</code>。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_LOGIN: AgentType.TECHNICAL,</code> | 字段 <code>IntentCategory.TECHNICAL_LOGIN</code>（当前映射中的键）：读取 <code>AgentType.TECHNICAL</code>。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_CRASH: AgentType.TECHNICAL,</code> | 字段 <code>IntentCategory.TECHNICAL_CRASH</code>（当前映射中的键）：读取 <code>AgentType.TECHNICAL</code>。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.BILLING:    AgentType.BILLING,</code> | 字段 <code>IntentCategory.BILLING</code>（当前映射中的键）：读取 <code>AgentType.BILLING</code>。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REFUND:     AgentType.BILLING,</code> | 字段 <code>IntentCategory.REFUND</code>（当前映射中的键）：读取 <code>AgentType.BILLING</code>。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.INVOICE:    AgentType.BILLING,</code> | 字段 <code>IntentCategory.INVOICE</code>（当前映射中的键）：读取 <code>AgentType.BILLING</code>。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.PAYMENT_ISSUE: AgentType.BILLING,</code> | 字段 <code>IntentCategory.PAYMENT_ISSUE</code>（当前映射中的键）：读取 <code>AgentType.BILLING</code>。 |
| L247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT:    AgentType.BILLING,</code> | 字段 <code>IntentCategory.ACCOUNT</code>（当前映射中的键）：读取 <code>AgentType.BILLING</code>。 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT_SECURITY: AgentType.BILLING,</code> | 字段 <code>IntentCategory.ACCOUNT_SECURITY</code>（当前映射中的键）：读取 <code>AgentType.BILLING</code>。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ESCALATION: AgentType.ESCALATION,</code> | 字段 <code>IntentCategory.ESCALATION</code>（当前映射中的键）：读取 <code>AgentType.ESCALATION</code>。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.HUMAN_HANDOFF: AgentType.ESCALATION,</code> | 字段 <code>IntentCategory.HUMAN_HANDOFF</code>（当前映射中的键）：读取 <code>AgentType.ESCALATION</code>。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 其余意图 → GENERAL（默认）</code> | 源码注释：其余意图 → GENERAL（默认） |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L253 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-254"></a>

### L254–L274 · AgentOrchestrator.__init__

建立意图识别器及三类实例池；每类列表为未来扩容留接口，当前都是单实例。

**签名输入：** <code>self, api_key: str, base_url: Optional[str]=None, model: str=&#x27;claude-3-5-sonnet-20241022&#x27;, skill_manager: Optional[Any]=None</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key:  str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url: Optional[str] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model:    str = &quot;claude-3-5-sonnet-20241022&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;skill_manager: Optional[Any] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs: Dict[str, Any] = {&quot;api_key&quot;: api_key}</code> | 将结果保存到 <code>kwargs</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if base_url:</code> | 判断 <code>base_url</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs[&quot;base_url&quot;] = base_url</code> | 将结果保存到 <code>kwargs[&#x27;base_url&#x27;]</code>：读取 <code>base_url</code>。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;client = AsyncAnthropic(**kwargs)</code> | 将结果保存到 <code>client</code>：调用 <code>AsyncAnthropic</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L265 | （空行） | 空行，分隔逻辑。 |
| L266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._intent_recognizer = IntentRecognizer(api_key=api_key, base_url=base_url, model=model)</code> | 将结果保存到 <code>self._intent_recognizer</code>：调用 <code>IntentRecognizer</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._skill_manager = skill_manager</code> | 将结果保存到 <code>self._skill_manager</code>：读取 <code>skill_manager</code>。 |
| L268 | （空行） | 空行，分隔逻辑。 |
| L269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Agent 池：每种类型可有多个实例（水平扩展）</code> | 源码注释：Agent 池：每种类型可有多个实例（水平扩展） |
| L270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._pool: Dict[AgentType, List[BaseAgent]] = {</code> | 将结果保存到 <code>self._pool</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AgentType.GENERAL:   [GeneralAgent(client, model, skill_manager)],</code> | 字段 <code>AgentType.GENERAL</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AgentType.TECHNICAL: [TechnicalAgent(client, model, skill_manager)],</code> | 字段 <code>AgentType.TECHNICAL</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AgentType.BILLING:   [BillingAgent(client, model, skill_manager)],</code> | 字段 <code>AgentType.BILLING</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L275 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-276"></a>

### L276–L281 · AgentOrchestrator.set_skill_manager

替换编排器与池内各实例的管理器引用。

**签名输入：** <code>self, skill_manager: Optional[Any]</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def set_skill_manager(self, skill_manager: Optional[Any]) -&gt; None:</code> | 定义函数 <code>set_skill_manager</code>；输入参数见签名，下方导读解释调用目的。 |
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;更新 SkillManager 引用，供运行时重载或测试替换使用。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._skill_manager = skill_manager</code> | 将结果保存到 <code>self._skill_manager</code>：读取 <code>skill_manager</code>。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agents in self._pool.values():</code> | 遍历 <code>self._pool.values()</code>，本轮元素绑定 <code>agents</code>。 |
| L280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent in agents:</code> | 遍历 <code>agents</code>，本轮元素绑定 <code>agent</code>。 |
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent._skill_manager = skill_manager</code> | 将结果保存到 <code>agent._skill_manager</code>：读取 <code>skill_manager</code>。 |
| L282 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-283"></a>

### L283–L289 · AgentOrchestrator.recognize_intent

给 API 的前置意图识别入口，便于 API 先做 RAG 决策。

**签名输入：** <code>self, message: str, history: Optional[List[Dict[str, str]]]=None</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def recognize_intent(</code> | 定义异步函数 <code>recognize_intent</code>；输入参数见签名，下方导读解释调用目的。 |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history: Optional[List[Dict[str, str]]] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;对外暴露意图识别，供 API 层先判断是否需要 RAG 等前置能力。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await self._intent_recognizer.recognize(message, history=history)</code> | 结束当前函数并返回；等待完成后继续；进入 <code>self._intent_recognizer.recognize</code>：先按当前消息和最近历史查缓存。 |
| L290 | （空行） | 空行，分隔逻辑。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 主入口 ────────────────────────────────────────────────────────────────</code> | 源码注释：── 主入口 ──────────────────────────────────────────────────────────────── |
| L292 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-293"></a>

### L293–L352 · AgentOrchestrator.run

若 intent 缺失才识别。先澄清，再生成领域决策；并行分支直接返回，单路执行后检查升级。应读清 return 位置，不能假设并行也经过单路收尾。

**签名输入：** <code>self, req: Request</code>；**返回契约：** <code>OrchestratorResult</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def run(self, req: Request) -&gt; OrchestratorResult:</code> | 定义异步函数 <code>run</code>；输入参数见签名，下方导读解释调用目的。 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;处理一次请求的完整流程：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;意图识别 → 路由选 Agent → 执行 → 检查升级 → 返回结果</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;t0 = time.monotonic()</code> | 将结果保存到 <code>t0</code>：读取单调时钟，用来算耗时/过期，不作为日历时间。 |
| L299 | （空行） | 空行，分隔逻辑。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 1. 意图识别（如果调用方已识别则跳过）</code> | 源码注释：1. 意图识别（如果调用方已识别则跳过） |
| L301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent is None:</code> | 判断 <code>req.intent is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_result = await self._intent_recognizer.recognize(req.message, history=req.history)</code> | 将结果保存到 <code>intent_result</code>：等待完成后继续；进入 <code>self._intent_recognizer.recognize</code>：先按当前消息和最近历史查缓存。 |
| L303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;req.intent  = intent_result.intent</code> | 将结果保存到 <code>req.intent</code>：读取 <code>intent_result.intent</code>。 |
| L304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;req.intent_group = intent_result.intent_group</code> | 将结果保存到 <code>req.intent_group</code>：读取 <code>intent_result.intent_group</code>。 |
| L305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;req.urgency = intent_result.urgency</code> | 将结果保存到 <code>req.urgency</code>：读取 <code>intent_result.urgency</code>。 |
| L306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;req.intent_confidence = intent_result.confidence</code> | **关键：**此后没有 req.entities=intent_result.entities，内部识别路径与 API 预填路径不一致。 |
| L307 | （空行） | 空行，分隔逻辑。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._needs_clarification(req):</code> | 判断 <code>self._needs_clarification(req)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return OrchestratorResult(</code> | 结束当前函数并返回；进入 <code>OrchestratorResult</code>：返回统一结构，primary_agent 是计划主 Agent，agent_type 单路时反映实际执行者；并行时被填为计划主 Agent，口径不同。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;request_id=req.request_id,</code> | 参数 <code>request_id</code>（request_id）：读取 <code>req.request_id</code>。 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response=&quot;我还不能确定您要处理的是哪类问题。请补充一下是订单物流、退款账单、账户资料，还是技术故障？&quot;,</code> | 参数 <code>response</code>（response）：使用固定文本/配置值。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type=AgentType.GENERAL,</code> | 参数 <code>agent_type</code>（Agent 类别）：读取 <code>AgentType.GENERAL</code>。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent=req.intent,</code> | 参数 <code>intent</code>（意图标签）：读取 <code>req.intent</code>。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalated=False,</code> | 参数 <code>escalated</code>（escalated）：使用这里写明的固定值。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=(time.monotonic() - t0) * 1000,</code> | 参数 <code>latency_ms</code>（当前计时范围的毫秒耗时）：按此表达式计算 <code>(time.monotonic() - t0) * 1000</code>。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_types=[AgentType.GENERAL],</code> | 参数 <code>agent_types</code>（agent_types）：组装有序值或集合，元素在后续逻辑中消费。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=AgentType.GENERAL,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：读取 <code>AgentType.GENERAL</code>。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_reason=&quot;低置信度 OTHER 意图，先澄清用户需求&quot;,</code> | 参数 <code>routing_reason</code>（可解释路由文字）：使用固定文本/配置值。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_confidence=req.intent_confidence,</code> | 参数 <code>routing_confidence</code>（裁剪后的领域分数）：读取 <code>req.intent_confidence</code>。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L321 | （空行） | 空行，分隔逻辑。 |
| L322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 复杂问题自动并行协作，例如同一句同时涉及登录故障和扣款/退款。</code> | 源码注释：复杂问题自动并行协作，例如同一句同时涉及登录故障和扣款/退款。 |
| L323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;decision = self._route_decision(req)</code> | 将结果保存到 <code>decision</code>：进入 <code>self._route_decision</code>：先处理 CRITICAL/转人工，再按领域分数排序。 |
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if decision.multi_agent:</code> | 判断 <code>decision.multi_agent</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await self.run_parallel(req, decision)</code> | **关键：**直接返回并行结果，后面的单路升级代码不会再运行。 |
| L326 | （空行） | 空行，分隔逻辑。 |
| L327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 2. 执行主 Agent（含降级）</code> | 源码注释：2. 执行主 Agent（含降级） |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response = await self._execute(req, decision.primary_agent)</code> | 将结果保存到 <code>response</code>：等待完成后继续；进入 <code>self._execute</code>：先取目标实例，不存在取通用；执行失败且原目标非通用时再尝试通用。 |
| L329 | （空行） | 空行，分隔逻辑。 |
| L330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 4. 升级检查</code> | 源码注释：4. 升级检查 |
| L331 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalated = False</code> | 将结果保存到 <code>escalated</code>：使用这里写明的固定值。 |
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if response.escalate or req.urgency == UrgencyLevel.CRITICAL or req.intent in (</code> | 判断 <code>response.escalate or req.urgency == UrgencyLevel.CRITICAL or req.intent in (IntentCategory.ESCALATION, IntentCategory.HUMAN_HANDOFF)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ESCALATION,</code> | 续接 L332 的表达式：按前述语句组装参数、条件或集合。 |
| L334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.HUMAN_HANDOFF,</code> | 续接 L332 的表达式：按前述语句组装参数、条件或集合。 |
| L335 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalated = True</code> | 将结果保存到 <code>escalated</code>：使用这里写明的固定值。 |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;请求 {req.request_id} 触发升级: urgency={req.urgency}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 生产环境：此处创建工单、通知人工客服</code> | **关键：**只有未来工单接入的注释，当前没有任何工单副作用。 |
| L339 | （空行） | 空行，分隔逻辑。 |
| L340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return OrchestratorResult(</code> | 结束当前函数并返回；进入 <code>OrchestratorResult</code>：返回统一结构，primary_agent 是计划主 Agent，agent_type 单路时反映实际执行者；并行时被填为计划主 Agent，口径不同。 |
| L341 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;request_id=req.request_id,</code> | 参数 <code>request_id</code>（request_id）：读取 <code>req.request_id</code>。 |
| L342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response=response.content,</code> | 参数 <code>response</code>（response）：读取 <code>response.content</code>。 |
| L343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type=response.agent_type,</code> | 参数 <code>agent_type</code>（Agent 类别）：读取 <code>response.agent_type</code>。 |
| L344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent=req.intent,</code> | 参数 <code>intent</code>（意图标签）：读取 <code>req.intent</code>。 |
| L345 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalated=escalated,</code> | 参数 <code>escalated</code>（escalated）：读取 <code>escalated</code>。 |
| L346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=(time.monotonic() - t0) * 1000,</code> | 参数 <code>latency_ms</code>（当前计时范围的毫秒耗时）：按此表达式计算 <code>(time.monotonic() - t0) * 1000</code>。 |
| L347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_types=[response.agent_type],</code> | 参数 <code>agent_types</code>（agent_types）：组装有序值或集合，元素在后续逻辑中消费。 |
| L348 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=decision.primary_agent,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：读取 <code>decision.primary_agent</code>。 |
| L349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents=[],</code> | 参数 <code>supporting_agents</code>（计划辅助 Agent 列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_reason=decision.reason,</code> | 参数 <code>routing_reason</code>（可解释路由文字）：读取 <code>decision.reason</code>。 |
| L351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_confidence=decision.confidence,</code> | 参数 <code>routing_confidence</code>（裁剪后的领域分数）：读取 <code>decision.confidence</code>。 |
| L352 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L353 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-354"></a>

### L354–L389 · AgentOrchestrator.run_parallel

对目标列表逐个创建协程再 gather；异常作为返回值隔离。只拼 success=True 的 AgentResponse，没有综合模型。统计延迟从本函数开始，排除前面意图识别和决策时间。

**签名输入：** <code>self, req: Request, decision: RoutingDecision</code>；**返回契约：** <code>OrchestratorResult</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L354 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def run_parallel(self, req: Request, decision: RoutingDecision) -&gt; OrchestratorResult:</code> | 定义异步函数 <code>run_parallel</code>；输入参数见签名，下方导读解释调用目的。 |
| L355 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;并行派发给多个 Agent，合并结果。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;适用于复杂问题（如同时涉及技术和账单）。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L358 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L359 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;t0 = time.monotonic()</code> | 将结果保存到 <code>t0</code>：读取单调时钟，用来算耗时/过期，不作为日历时间。 |
| L360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_types = decision.agent_types</code> | 将结果保存到 <code>agent_types</code>：读取 <code>decision.agent_types</code>。 |
| L361 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tasks = [self._execute(req, at) for at in agent_types]</code> | 将结果保存到 <code>tasks</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;responses = await asyncio.gather(*tasks, return_exceptions=True)</code> | 将结果保存到 <code>responses</code>：等待完成后继续；并发等待这批任务，结果顺序与输入任务顺序一致。 |
| L363 | （空行） | 空行，分隔逻辑。 |
| L364 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 合并：主 Agent 在前，辅助 Agent 在后。</code> | 源码注释：合并：主 Agent 在前，辅助 Agent 在后。 |
| L365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts = []</code> | 将结果保存到 <code>parts</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L366 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for r in responses:</code> | 遍历 <code>responses</code>，本轮元素绑定 <code>r</code>。 |
| L367 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(r, AgentResponse) and r.success:</code> | 判断 <code>isinstance(r, AgentResponse) and r.success</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L368 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;role = &quot;主处理&quot; if r.agent_type == decision.primary_agent else &quot;辅助处理&quot;</code> | 将结果保存到 <code>role</code>：条件 <code>r.agent_type == decision.primary_agent</code> 成立选前值，否则选 else 后值。 |
| L369 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(f&quot;[{r.agent_type.value} - {role}]\n{r.content}&quot;)</code> | 追加一个元素到当前列表。 |
| L370 | （空行） | 空行，分隔逻辑。 |
| L371 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;combined = &quot;\n\n&quot;.join(parts) if parts else &quot;抱歉，所有 Agent 均处理失败。&quot;</code> | 将结果保存到 <code>combined</code>：条件 <code>parts</code> 成立选前值，否则选 else 后值。 |
| L372 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalated = any(isinstance(r, AgentResponse) and r.escalate for r in responses)</code> | 将结果保存到 <code>escalated</code>：至少一项为真就返回True，并可提前结束迭代。 |
| L373 | （空行） | 空行，分隔逻辑。 |
| L374 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return OrchestratorResult(</code> | 结束当前函数并返回；进入 <code>OrchestratorResult</code>：返回统一结构，primary_agent 是计划主 Agent，agent_type 单路时反映实际执行者；并行时被填为计划主 Agent，口径不同。 |
| L375 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;request_id=req.request_id,</code> | 参数 <code>request_id</code>（request_id）：读取 <code>req.request_id</code>。 |
| L376 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response=combined,</code> | 参数 <code>response</code>（response）：读取 <code>combined</code>。 |
| L377 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type=decision.primary_agent,</code> | 参数 <code>agent_type</code>（Agent 类别）：读取 <code>decision.primary_agent</code>。 |
| L378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent=req.intent,</code> | 参数 <code>intent</code>（意图标签）：读取 <code>req.intent</code>。 |
| L379 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalated=escalated,</code> | 参数 <code>escalated</code>（escalated）：读取 <code>escalated</code>。 |
| L380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=(time.monotonic() - t0) * 1000,</code> | 参数 <code>latency_ms</code>（当前计时范围的毫秒耗时）：按此表达式计算 <code>(time.monotonic() - t0) * 1000</code>。 |
| L381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_types=[</code> | 参数 <code>agent_types</code>（agent_types）：读取 <code>[r.agent_type for r in responses if isinstance(r, AgentResponse) and r.success] or agent_types</code>。 |
| L382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;r.agent_type for r in responses</code> | 续接 L374 的表达式：按前述语句组装参数、条件或集合。 |
| L383 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(r, AgentResponse) and r.success</code> | 续接 L374 的表达式：按前述语句组装参数、条件或集合。 |
| L384 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;] or agent_types,</code> | 续接 L374 的表达式：按前述语句组装参数、条件或集合。 |
| L385 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=decision.primary_agent,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：读取 <code>decision.primary_agent</code>。 |
| L386 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents=decision.supporting_agents,</code> | 参数 <code>supporting_agents</code>（计划辅助 Agent 列表）：读取 <code>decision.supporting_agents</code>。 |
| L387 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_reason=decision.reason,</code> | 参数 <code>routing_reason</code>（可解释路由文字）：读取 <code>decision.reason</code>。 |
| L388 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_confidence=decision.confidence,</code> | 参数 <code>routing_confidence</code>（裁剪后的领域分数）：读取 <code>decision.confidence</code>。 |
| L389 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L390 | （空行） | 空行，分隔逻辑。 |
| L391 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 路由逻辑 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 路由逻辑 ────────────────────────────────────────────────────────────── |
| L392 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-393"></a>

### L393–L409 · AgentOrchestrator._route

旧静态路由辅助方法；主入口已不使用。紧急度覆盖和目标可用性检查在此只能解释历史实现。

**签名输入：** <code>self, intent: Optional[IntentCategory], urgency: Optional[UrgencyLevel]</code>；**返回契约：** <code>AgentType</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L393 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _route(self, intent: Optional[IntentCategory], urgency: Optional[UrgencyLevel]) -&gt; AgentType:</code> | 定义函数 <code>_route</code>；输入参数见签名，下方导读解释调用目的。 |
| L394 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L395 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;三层路由决策：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L396 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. 意图映射</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L397 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. 紧急度覆盖（CRITICAL 直接升级）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L398 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. 默认 GENERAL</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L399 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L400 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if urgency == UrgencyLevel.CRITICAL:</code> | 判断 <code>urgency == UrgencyLevel.CRITICAL</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L401 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return AgentType.ESCALATION</code> | 结束当前函数并返回；读取 <code>AgentType.ESCALATION</code>。 |
| L402 | （空行） | 空行，分隔逻辑。 |
| L403 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if intent and intent in self._INTENT_ROUTING:</code> | 判断 <code>intent and intent in self._INTENT_ROUTING</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L404 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;target = self._INTENT_ROUTING[intent]</code> | 将结果保存到 <code>target</code>：按索引/切片取 <code>self._INTENT_ROUTING[intent]</code>，注意是否截掉旧历史或长文本。 |
| L405 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 如果目标类型有可用实例则使用，否则降级</code> | 源码注释：如果目标类型有可用实例则使用，否则降级 |
| L406 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if target in self._pool and self._pool[target]:</code> | 判断 <code>target in self._pool and self._pool[target]</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L407 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return target</code> | 结束当前函数并返回；读取 <code>target</code>。 |
| L408 | （空行） | 空行，分隔逻辑。 |
| L409 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return AgentType.GENERAL</code> | 结束当前函数并返回；读取 <code>AgentType.GENERAL</code>。 |
| L410 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-411"></a>

### L411–L459 · AgentOrchestrator._route_decision

先处理 CRITICAL/转人工，再按领域分数排序。辅助 Agent 必须同时满足 ≥.45 且 ≥主分数×.55，General 永不成为辅助。这个相对门槛使强主意图压制次要问题。

**签名输入：** <code>self, req: Request</code>；**返回契约：** <code>RoutingDecision</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L411 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _route_decision(self, req: Request) -&gt; RoutingDecision:</code> | 定义函数 <code>_route_decision</code>；输入参数见签名，下方导读解释调用目的。 |
| L412 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L413 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;结构化路由决策。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L414 | （空行） | 空行，分隔逻辑。 |
| L415 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;先处理紧急/转人工，再用领域分数决定主 Agent 和辅助 Agent。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L416 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;这样可以表达“主处理 + 辅助诊断”，避免关键词命中后无主次地拼接。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L417 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L418 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.urgency == UrgencyLevel.CRITICAL:</code> | 判断 <code>req.urgency == UrgencyLevel.CRITICAL</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L419 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RoutingDecision(</code> | 结束当前函数并返回；进入 <code>RoutingDecision</code>：执行前计划：主 Agent、辅助 Agent、原因、分数。 |
| L420 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=AgentType.ESCALATION,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：读取 <code>AgentType.ESCALATION</code>。 |
| L421 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reason=&quot;紧急度为 CRITICAL，触发升级路由&quot;,</code> | 参数 <code>reason</code>（reason）：使用固定文本/配置值。 |
| L422 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;confidence=1.0,</code> | 参数 <code>confidence</code>（置信度分数）：使用这里写明的固定值。 |
| L423 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L424 | （空行） | 空行，分隔逻辑。 |
| L425 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent in (IntentCategory.ESCALATION, IntentCategory.HUMAN_HANDOFF):</code> | 判断 <code>req.intent in (IntentCategory.ESCALATION, IntentCategory.HUMAN_HANDOFF)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L426 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RoutingDecision(</code> | 结束当前函数并返回；进入 <code>RoutingDecision</code>：执行前计划：主 Agent、辅助 Agent、原因、分数。 |
| L427 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=AgentType.ESCALATION,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：读取 <code>AgentType.ESCALATION</code>。 |
| L428 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reason=f&quot;意图为 {req.intent.value if req.intent else &#x27;unknown&#x27;}，触发升级路由&quot;,</code> | 参数 <code>reason</code>（reason）：将变量插入模板，构造提示词、标识或可读说明。 |
| L429 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;confidence=max(req.intent_confidence, 0.8),</code> | 参数 <code>confidence</code>（置信度分数）：取当前候选中的最大值。 |
| L430 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L431 | （空行） | 空行，分隔逻辑。 |
| L432 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores = self._domain_scores(req)</code> | 将结果保存到 <code>scores</code>：进入 <code>self._domain_scores</code>：累加三类证据：意图主类别（.55/.75）、关键词封顶加分、实体加分。 |
| L433 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;available_scores = {</code> | 将结果保存到 <code>available_scores</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L434 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type: score</code> | 续接 L433 的表达式：按前述语句组装参数、条件或集合。 |
| L435 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent_type, score in scores.items()</code> | 续接 L433 的表达式：按前述语句组装参数、条件或集合。 |
| L436 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if agent_type == AgentType.GENERAL or self._pool.get(agent_type)</code> | 续接 L433 的表达式：按前述语句组装参数、条件或集合。 |
| L437 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L438 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not available_scores:</code> | 判断 <code>not available_scores</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L439 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RoutingDecision(</code> | 结束当前函数并返回；进入 <code>RoutingDecision</code>：执行前计划：主 Agent、辅助 Agent、原因、分数。 |
| L440 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=AgentType.GENERAL,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：读取 <code>AgentType.GENERAL</code>。 |
| L441 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reason=&quot;无可用专属 Agent，降级到 GeneralAgent&quot;,</code> | 参数 <code>reason</code>（reason）：使用固定文本/配置值。 |
| L442 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;confidence=0.1,</code> | 参数 <code>confidence</code>（置信度分数）：使用这里写明的固定值。 |
| L443 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L444 | （空行） | 空行，分隔逻辑。 |
| L445 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ordered = sorted(available_scores.items(), key=lambda item: item[1], reverse=True)</code> | 将结果保存到 <code>ordered</code>：按指定规则排序，不直接改变原列表。 |
| L446 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent, primary_score = ordered[0]</code> | 将结果保存到 <code>(primary_agent, primary_score)</code>：按索引/切片取 <code>ordered[0]</code>，注意是否截掉旧历史或长文本。 |
| L447 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents = [</code> | 将结果保存到 <code>supporting_agents</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L448 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type</code> | 续接 L447 的表达式：按前述语句组装参数、条件或集合。 |
| L449 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent_type, score in ordered[1:]</code> | 续接 L447 的表达式：按前述语句组装参数、条件或集合。 |
| L450 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if agent_type != AgentType.GENERAL and score &gt;= 0.45 and score &gt;= primary_score * 0.55</code> | **关键：**两个门槛取更严格者。例如主分数 1.31 时辅助至少 .7205，.33 的账单分不够。 |
| L451 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L452 | （空行） | 空行，分隔逻辑。 |
| L453 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reason = self._routing_reason(req, available_scores, primary_agent, supporting_agents)</code> | 将结果保存到 <code>reason</code>：进入 <code>self._routing_reason</code>：把意图、分组、领域分数、主辅标签串成诊断文本。 |
| L454 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RoutingDecision(</code> | 结束当前函数并返回；进入 <code>RoutingDecision</code>：执行前计划：主 Agent、辅助 Agent、原因、分数。 |
| L455 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=primary_agent,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：读取 <code>primary_agent</code>。 |
| L456 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents=supporting_agents,</code> | 参数 <code>supporting_agents</code>（计划辅助 Agent 列表）：读取 <code>supporting_agents</code>。 |
| L457 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reason=reason,</code> | 参数 <code>reason</code>（reason）：读取 <code>reason</code>。 |
| L458 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;confidence=round(min(primary_score, 1.0), 3),</code> | 参数 <code>confidence</code>（置信度分数）：四舍五入用于返回/展示。 |
| L459 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L460 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-461"></a>

### L461–L519 · AgentOrchestrator._domain_scores

累加三类证据：意图主类别（.55/.75）、关键词封顶加分、实体加分。输出可大于 1，只有返回 routing_confidence 时裁剪到 1；不是概率模型。

**签名输入：** <code>self, req: Request</code>；**返回契约：** <code>Dict[AgentType, float]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L461 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _domain_scores(self, req: Request) -&gt; Dict[AgentType, float]:</code> | 定义函数 <code>_domain_scores</code>；输入参数见签名，下方导读解释调用目的。 |
| L462 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;按意图、关键词和实体为各领域 Agent 打分。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L463 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg = req.message.lower()</code> | 将结果保存到 <code>msg</code>：转小写进行大小写无关比较。 |
| L464 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores = {</code> | 将结果保存到 <code>scores</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L465 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AgentType.GENERAL: 0.1,</code> | 字段 <code>AgentType.GENERAL</code>（当前映射中的键）：使用这里写明的固定值。 |
| L466 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AgentType.TECHNICAL: 0.0,</code> | 字段 <code>AgentType.TECHNICAL</code>（当前映射中的键）：使用这里写明的固定值。 |
| L467 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AgentType.BILLING: 0.0,</code> | 字段 <code>AgentType.BILLING</code>（当前映射中的键）：使用这里写明的固定值。 |
| L468 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L469 | （空行） | 空行，分隔逻辑。 |
| L470 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent in (</code> | 判断 <code>req.intent in (IntentCategory.QUERY, IntentCategory.ORDER_STATUS, IntentCategory.LOGISTICS, IntentCategory.REQUEST, IntentCategory.COMP…</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L471 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.QUERY,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L472 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ORDER_STATUS,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L473 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.LOGISTICS,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L474 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REQUEST,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L475 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.COMPLAINT,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L476 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.GREETING,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L477 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.FEEDBACK,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L478 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.OTHER,</code> | 续接 L470 的表达式：按前述语句组装参数、条件或集合。 |
| L479 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L480 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.GENERAL] += 0.55</code> | 更新 <code>scores[AgentType.GENERAL]</code>：<code>scores[AgentType.GENERAL] += 0.55</code>；此处会改变累计状态。 |
| L481 | （空行） | 空行，分隔逻辑。 |
| L482 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent in (</code> | 判断 <code>req.intent in (IntentCategory.TECHNICAL, IntentCategory.TECHNICAL_LOGIN, IntentCategory.TECHNICAL_CRASH)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L483 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL,</code> | 续接 L482 的表达式：按前述语句组装参数、条件或集合。 |
| L484 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_LOGIN,</code> | 续接 L482 的表达式：按前述语句组装参数、条件或集合。 |
| L485 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_CRASH,</code> | 续接 L482 的表达式：按前述语句组装参数、条件或集合。 |
| L486 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L487 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.TECHNICAL] += 0.75</code> | 更新 <code>scores[AgentType.TECHNICAL]</code>：<code>scores[AgentType.TECHNICAL] += 0.75</code>；此处会改变累计状态。 |
| L488 | （空行） | 空行，分隔逻辑。 |
| L489 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent in (</code> | 判断 <code>req.intent in (IntentCategory.BILLING, IntentCategory.ACCOUNT, IntentCategory.ACCOUNT_SECURITY, IntentCategory.REFUND, IntentCategory.I…</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L490 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.BILLING,</code> | 续接 L489 的表达式：按前述语句组装参数、条件或集合。 |
| L491 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT,</code> | 续接 L489 的表达式：按前述语句组装参数、条件或集合。 |
| L492 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT_SECURITY,</code> | 续接 L489 的表达式：按前述语句组装参数、条件或集合。 |
| L493 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REFUND,</code> | 续接 L489 的表达式：按前述语句组装参数、条件或集合。 |
| L494 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.INVOICE,</code> | 续接 L489 的表达式：按前述语句组装参数、条件或集合。 |
| L495 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.PAYMENT_ISSUE,</code> | 续接 L489 的表达式：按前述语句组装参数、条件或集合。 |
| L496 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L497 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.BILLING] += 0.75</code> | 更新 <code>scores[AgentType.BILLING]</code>：<code>scores[AgentType.BILLING] += 0.75</code>；此处会改变累计状态。 |
| L498 | （空行） | 空行，分隔逻辑。 |
| L499 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;technical_kws = [&quot;崩溃&quot;, &quot;报错&quot;, &quot;error&quot;, &quot;crash&quot;, &quot;无法登录&quot;, &quot;登录失败&quot;, &quot;500&quot;, &quot;401&quot;, &quot;验证码&quot;]</code> | 将结果保存到 <code>technical_kws</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L500 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;billing_kws = [&quot;退款&quot;, &quot;退货&quot;, &quot;扣款&quot;, &quot;发票&quot;, &quot;账单&quot;, &quot;支付&quot;, &quot;订阅&quot;, &quot;refund&quot;, &quot;invoice&quot;, &quot;多扣&quot;]</code> | 将结果保存到 <code>billing_kws</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L501 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;general_kws = [&quot;订单&quot;, &quot;物流&quot;, &quot;快递&quot;, &quot;配送&quot;, &quot;会员&quot;, &quot;积分&quot;, &quot;咨询&quot;, &quot;帮助&quot;]</code> | 将结果保存到 <code>general_kws</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L502 | （空行） | 空行，分隔逻辑。 |
| L503 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;technical_hits = sum(1 for kw in technical_kws if kw in msg)</code> | 将结果保存到 <code>technical_hits</code>：累加各项数值/布尔命中值。 |
| L504 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;billing_hits = sum(1 for kw in billing_kws if kw in msg)</code> | 将结果保存到 <code>billing_hits</code>：累加各项数值/布尔命中值。 |
| L505 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;general_hits = sum(1 for kw in general_kws if kw in msg)</code> | 将结果保存到 <code>general_hits</code>：累加各项数值/布尔命中值。 |
| L506 | （空行） | 空行，分隔逻辑。 |
| L507 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.TECHNICAL] += min(0.45, technical_hits * 0.18)</code> | 更新 <code>scores[AgentType.TECHNICAL]</code>：<code>scores[AgentType.TECHNICAL] += min(0.45, technical_hits * 0.18)</code>；此处会改变累计状态。 |
| L508 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.BILLING] += min(0.45, billing_hits * 0.18)</code> | 更新 <code>scores[AgentType.BILLING]</code>：<code>scores[AgentType.BILLING] += min(0.45, billing_hits * 0.18)</code>；此处会改变累计状态。 |
| L509 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.GENERAL] += min(0.35, general_hits * 0.12)</code> | 更新 <code>scores[AgentType.GENERAL]</code>：<code>scores[AgentType.GENERAL] += min(0.35, general_hits * 0.12)</code>；此处会改变累计状态。 |
| L510 | （空行） | 空行，分隔逻辑。 |
| L511 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entities = req.entities or {}</code> | 将结果保存到 <code>entities</code>：读取 <code>req.entities or {}</code>。 |
| L512 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if entities.get(&quot;error_code&quot;):</code> | 判断 <code>entities.get(&#x27;error_code&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L513 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.TECHNICAL] += 0.2</code> | 更新 <code>scores[AgentType.TECHNICAL]</code>：<code>scores[AgentType.TECHNICAL] += 0.2</code>；此处会改变累计状态。 |
| L514 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if entities.get(&quot;amount&quot;):</code> | 判断 <code>entities.get(&#x27;amount&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L515 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.BILLING] += 0.15</code> | 更新 <code>scores[AgentType.BILLING]</code>：<code>scores[AgentType.BILLING] += 0.15</code>；此处会改变累计状态。 |
| L516 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if entities.get(&quot;order_id&quot;):</code> | 判断 <code>entities.get(&#x27;order_id&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L517 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[AgentType.GENERAL] += 0.1</code> | 更新 <code>scores[AgentType.GENERAL]</code>：<code>scores[AgentType.GENERAL] += 0.1</code>；此处会改变累计状态。 |
| L518 | （空行） | 空行，分隔逻辑。 |
| L519 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {agent_type: round(score, 3) for agent_type, score in scores.items()}</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L520 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-521"></a>

### L521–L537 · AgentOrchestrator._routing_reason

把意图、分组、领域分数、主辅标签串成诊断文本。解释的是规则证据，不是 LLM 内部推理。

**签名输入：** <code>req: Request, scores: Dict[AgentType, float], primary_agent: AgentType, supporting_agents: List[AgentType]</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L521 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L522 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _routing_reason(</code> | 定义函数 <code>_routing_reason</code>；输入参数见签名，下方导读解释调用目的。 |
| L523 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;req: Request,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L524 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores: Dict[AgentType, float],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L525 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent: AgentType,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L526 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents: List[AgentType],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L527 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; str:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L528 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;score_text = &quot;, &quot;.join(</code> | 将结果保存到 <code>score_text</code>：把字符串片段按分隔符合并。 |
| L529 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;{agent_type.value}={score:.2f}&quot;</code> | 续接 L528 的表达式：按前述语句组装参数、条件或集合。 |
| L530 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent_type, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)</code> | 参数 <code>reverse</code>（reverse）：使用这里写明的固定值。 |
| L531 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L532 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;support_text = &quot;, &quot;.join(agent.value for agent in supporting_agents) or &quot;none&quot;</code> | 将结果保存到 <code>support_text</code>：读取 <code>&#x27;, &#x27;.join((agent.value for agent in supporting_agents)) or &#x27;none&#x27;</code>。 |
| L533 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent = req.intent.value if req.intent else &quot;unknown&quot;</code> | 将结果保存到 <code>intent</code>：条件 <code>req.intent</code> 成立选前值，否则选 else 后值。 |
| L534 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return (</code> | 结束当前函数并返回；将变量插入模板，构造提示词、标识或可读说明。 |
| L535 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;intent={intent}, group={req.intent_group or &#x27;unknown&#x27;}, &quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L536 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;primary={primary_agent.value}, supporting={support_text}, scores=[{score_text}]&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L537 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L538 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-539"></a>

### L539–L570 · AgentOrchestrator._collaboration_targets

旧关键词协作检测函数；阈值更宽松，但 run 未调用，不能据此推断示例必然并行。

**签名输入：** <code>self, req: Request</code>；**返回契约：** <code>List[AgentType]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L539 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _collaboration_targets(self, req: Request) -&gt; List[AgentType]:</code> | 定义函数 <code>_collaboration_targets</code>；输入参数见签名，下方导读解释调用目的。 |
| L540 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L541 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;判断是否需要多个 Agent 并行协作。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L542 | （空行） | 空行，分隔逻辑。 |
| L543 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;意图识别通常只返回一个主意图；这里用领域关键词补充检测复合问题，</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L544 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;例如&quot;登录报错且被重复扣款&quot;需要技术和账单 Agent 同时处理。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L545 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L546 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg = req.message.lower()</code> | 将结果保存到 <code>msg</code>：转小写进行大小写无关比较。 |
| L547 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;targets: List[AgentType] = []</code> | 将结果保存到 <code>targets</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L548 | （空行） | 空行，分隔逻辑。 |
| L549 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;technical_kws = [&quot;崩溃&quot;, &quot;报错&quot;, &quot;error&quot;, &quot;crash&quot;, &quot;无法登录&quot;, &quot;登录失败&quot;, &quot;500&quot;, &quot;401&quot;]</code> | 将结果保存到 <code>technical_kws</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L550 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;billing_kws = [&quot;退款&quot;, &quot;扣款&quot;, &quot;发票&quot;, &quot;账单&quot;, &quot;支付&quot;, &quot;订阅&quot;, &quot;refund&quot;, &quot;invoice&quot;]</code> | 将结果保存到 <code>billing_kws</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L551 | （空行） | 空行，分隔逻辑。 |
| L552 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent in (</code> | 判断 <code>req.intent in (IntentCategory.TECHNICAL, IntentCategory.TECHNICAL_LOGIN, IntentCategory.TECHNICAL_CRASH) or any((kw in msg for kw in te…</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L553 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL,</code> | 续接 L552 的表达式：按前述语句组装参数、条件或集合。 |
| L554 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_LOGIN,</code> | 续接 L552 的表达式：按前述语句组装参数、条件或集合。 |
| L555 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_CRASH,</code> | 续接 L552 的表达式：按前述语句组装参数、条件或集合。 |
| L556 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;) or any(kw in msg for kw in technical_kws):</code> | 续接 L552 的表达式：按前述语句组装参数、条件或集合。 |
| L557 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;targets.append(AgentType.TECHNICAL)</code> | 追加一个元素到当前列表。 |
| L558 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent in (</code> | 判断 <code>req.intent in (IntentCategory.BILLING, IntentCategory.ACCOUNT, IntentCategory.ACCOUNT_SECURITY, IntentCategory.REFUND, IntentCategory.I…</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L559 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.BILLING,</code> | 续接 L558 的表达式：按前述语句组装参数、条件或集合。 |
| L560 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT,</code> | 续接 L558 的表达式：按前述语句组装参数、条件或集合。 |
| L561 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT_SECURITY,</code> | 续接 L558 的表达式：按前述语句组装参数、条件或集合。 |
| L562 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REFUND,</code> | 续接 L558 的表达式：按前述语句组装参数、条件或集合。 |
| L563 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.INVOICE,</code> | 续接 L558 的表达式：按前述语句组装参数、条件或集合。 |
| L564 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.PAYMENT_ISSUE,</code> | 续接 L558 的表达式：按前述语句组装参数、条件或集合。 |
| L565 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;) or any(kw in msg for kw in billing_kws):</code> | 续接 L558 的表达式：按前述语句组装参数、条件或集合。 |
| L566 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;targets.append(AgentType.BILLING)</code> | 追加一个元素到当前列表。 |
| L567 | （空行） | 空行，分隔逻辑。 |
| L568 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 保持顺序去重，并只返回当前有实例的 Agent 类型。</code> | 源码注释：保持顺序去重，并只返回当前有实例的 Agent 类型。 |
| L569 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;deduped = list(dict.fromkeys(targets))</code> | 将结果保存到 <code>deduped</code>：将迭代内容物化成列表。 |
| L570 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [agent_type for agent_type in deduped if self._pool.get(agent_type)]</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L571 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-572"></a>

### L572–L580 · AgentOrchestrator._needs_clarification

OTHER、长度>2、confidence<.5 三条件同时成立才追问；一两个字未知请求反而不澄清。

**签名输入：** <code>req: Request</code>；**返回契约：** <code>bool</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L572 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L573 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _needs_clarification(req: Request) -&gt; bool:</code> | 定义函数 <code>_needs_clarification</code>；输入参数见签名，下方导读解释调用目的。 |
| L574 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;低置信度且无明确意图时，先追问，避免误路由。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L575 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if req.intent != IntentCategory.OTHER:</code> | 判断 <code>req.intent != IntentCategory.OTHER</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L576 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L577 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text = (req.message or &quot;&quot;).strip()</code> | 将结果保存到 <code>text</code>：去除两端指定字符或空白。 |
| L578 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(text) &lt;= 2:</code> | 判断 <code>len(text) &lt;= 2</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L579 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L580 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return req.intent_confidence &lt; 0.5</code> | 结束当前函数并返回；读取 <code>req.intent_confidence &lt; 0.5</code>。 |
| L581 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-582"></a>

### L582–L590 · AgentOrchestrator._best_agent

类型确定后才按运行得分挑实例。领域分数解决找哪个专业，实例分数解决该专业找谁，两者不可混讲。

**签名输入：** <code>self, agent_type: AgentType</code>；**返回契约：** <code>Optional[BaseAgent]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L582 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _best_agent(self, agent_type: AgentType) -&gt; Optional[BaseAgent]:</code> | 定义函数 <code>_best_agent</code>；输入参数见签名，下方导读解释调用目的。 |
| L583 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L584 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;性能路由：从同类 Agent 中选 routing_score() 最高的。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L585 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;这是&quot;基于在线表现动态调整路由&quot;的核心。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L586 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L587 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agents = self._pool.get(agent_type, [])</code> | 将结果保存到 <code>agents</code>：按键取值，缺失用给定默认值。 |
| L588 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not agents:</code> | 判断 <code>not agents</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L589 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L590 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return max(agents, key=lambda a: a.stats.routing_score())</code> | **关键：**max 永远挑当前最高分；没有流量探索，也没有按当前并发数分配。 |
| L591 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-592"></a>

### L592–L613 · AgentOrchestrator._execute

先取目标实例，不存在取通用；执行失败且原目标非通用时再尝试通用。目标缺失且通用也失败可能重复调用通用。

**签名输入：** <code>self, req: Request, agent_type: AgentType</code>；**返回契约：** <code>AgentResponse</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L592 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _execute(self, req: Request, agent_type: AgentType) -&gt; AgentResponse:</code> | 定义异步函数 <code>_execute</code>；输入参数见签名，下方导读解释调用目的。 |
| L593 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;执行 Agent，失败时降级到 GeneralAgent。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L594 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent = self._best_agent(agent_type)</code> | 将结果保存到 <code>agent</code>：进入 <code>self._best_agent</code>：类型确定后才按运行得分挑实例。 |
| L595 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if agent is None:</code> | 判断 <code>agent is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L596 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent = self._best_agent(AgentType.GENERAL)</code> | 将结果保存到 <code>agent</code>：进入 <code>self._best_agent</code>：类型确定后才按运行得分挑实例。 |
| L597 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if agent is None:</code> | 判断 <code>agent is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L598 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return AgentResponse(</code> | 结束当前函数并返回；进入 <code>AgentResponse</code>：单次 Agent 执行结果；success 只标识调用是否异常，escalate 来自回复中的词。 |
| L599 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type=AgentType.GENERAL,</code> | 参数 <code>agent_type</code>（Agent 类别）：读取 <code>AgentType.GENERAL</code>。 |
| L600 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content=&quot;服务暂时不可用，请稍后重试。&quot;,</code> | 参数 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L601 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;success=False,</code> | 参数 <code>success</code>（执行成功标记）：使用这里写明的固定值。 |
| L602 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L603 | （空行） | 空行，分隔逻辑。 |
| L604 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response = await agent.handle(req)</code> | 将结果保存到 <code>response</code>：等待完成后继续；进入 <code>agent.handle</code>：统一包装计时、统计、LLM 异常处理和升级关键词检测。 |
| L605 | （空行） | 空行，分隔逻辑。 |
| L606 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 专属 Agent 失败时降级到 GeneralAgent</code> | 源码注释：专属 Agent 失败时降级到 GeneralAgent |
| L607 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not response.success and agent_type != AgentType.GENERAL:</code> | 判断 <code>not response.success and agent_type != AgentType.GENERAL</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L608 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;{agent_type.value} 失败，降级到 GeneralAgent&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L609 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fallback = self._best_agent(AgentType.GENERAL)</code> | 将结果保存到 <code>fallback</code>：进入 <code>self._best_agent</code>：类型确定后才按运行得分挑实例。 |
| L610 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if fallback:</code> | 判断 <code>fallback</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L611 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response = await fallback.handle(req)</code> | 将结果保存到 <code>response</code>：等待完成后继续；进入 <code>fallback.handle</code>：统一包装计时、统计、LLM 异常处理和升级关键词检测。 |
| L612 | （空行） | 空行，分隔逻辑。 |
| L613 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return response</code> | 结束当前函数并返回；读取 <code>response</code>。 |
| L614 | （空行） | 空行，分隔逻辑。 |
| L615 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 统计（供 Monitor 读取）────────────────────────────────────────────────</code> | 源码注释：── 统计（供 Monitor 读取）──────────────────────────────────────────────── |
| L616 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-617"></a>

### L617–L629 · AgentOrchestrator.get_stats

用 general_0 等进程内键导出累计统计，供 Monitor 采集。

**签名输入：** <code>self</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L617 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def get_stats(self) -&gt; Dict[str, Any]:</code> | 定义函数 <code>get_stats</code>；输入参数见签名，下方导读解释调用目的。 |
| L618 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result = {}</code> | 将结果保存到 <code>result</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L619 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent_type, agents in self._pool.items():</code> | 遍历 <code>self._pool.items()</code>，本轮元素绑定 <code>(agent_type, agents)</code>。 |
| L620 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i, agent in enumerate(agents):</code> | 遍历 <code>enumerate(agents)</code>，本轮元素绑定 <code>(i, agent)</code>。 |
| L621 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key = f&quot;{agent_type.value}_{i}&quot;</code> | 将结果保存到 <code>key</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L622 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result[key] = {</code> | 将结果保存到 <code>result[key]</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L623 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;total&quot;:        agent.stats.total,</code> | 字段 <code>total</code>（当前映射中的键）：读取 <code>agent.stats.total</code>。 |
| L624 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;success_rate&quot;: round(agent.stats.success_rate, 3),</code> | 字段 <code>success_rate</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L625 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;avg_ms&quot;:       round(agent.stats.avg_ms, 1),</code> | 字段 <code>avg_ms</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L626 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;monitor_penalty&quot;: round(agent.stats.monitor_penalty, 3),</code> | 字段 <code>monitor_penalty</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L627 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;routing_score&quot;: round(agent.stats.routing_score(), 3),</code> | 字段 <code>routing_score</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L628 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L629 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return result</code> | 结束当前函数并返回；读取 <code>result</code>。 |
| L630 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-631"></a>

### L631–L641 · AgentOrchestrator.update_routing_penalties

按实例键写入 Monitor 反馈，限制在 0–.9；没有做实例下线或强制熔断。

**签名输入：** <code>self, penalties: Dict[str, float]</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L631 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def update_routing_penalties(self, penalties: Dict[str, float]) -&gt; None:</code> | 定义函数 <code>update_routing_penalties</code>；输入参数见签名，下方导读解释调用目的。 |
| L632 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L633 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;接收 Monitor 的在线表现反馈，动态调整路由惩罚项。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L634 | （空行） | 空行，分隔逻辑。 |
| L635 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;penalties 的 key 使用 get_stats() 中的 agent key，例如 technical_0。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L636 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L637 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent_type, agents in self._pool.items():</code> | 遍历 <code>self._pool.items()</code>，本轮元素绑定 <code>(agent_type, agents)</code>。 |
| L638 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i, agent in enumerate(agents):</code> | 遍历 <code>enumerate(agents)</code>，本轮元素绑定 <code>(i, agent)</code>。 |
| L639 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key = f&quot;{agent_type.value}_{i}&quot;</code> | 将结果保存到 <code>key</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L640 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;penalty = penalties.get(key, 0.0)</code> | 将结果保存到 <code>penalty</code>：按键取值，缺失用给定默认值。 |
| L641 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent.stats.monitor_penalty = min(max(penalty, 0.0), 0.9)</code> | 将结果保存到 <code>agent.stats.monitor_penalty</code>：取上界/限制后的较小值。 |

## 结合全项目：设计缺口与增强方向

- L393 _route 与 L539 _collaboration_targets 留在文件中，但当前 run 调用的是 _route_decision；不能拿旧函数讲主链路。
- ESCALATION 枚举存在但池中无 EscalationAgent；_execute 实际回退 GeneralAgent。L338 是注释，没有工单、人工通知或状态追踪。
- run 自行识别时 L303–306 未写 req.entities；HTTP 先识别后预填可用，CLI/评测路径丢失实体，导致路由和 prompt 与 HTTP 不同。
- 每类只注册一个实例；监控 penalty 会变但通常不能切换同类实例。_best_agent 只做同类 max，不跨领域切换，也没有探索机制。
- AgentResponse.confidence 默认 1.0，没有质量置信度计算；升级依赖响应关键词、紧急度和意图，不是实现了“低回答置信度升级”。
- 并行 Agent 收到同一个完整请求，没有独立子任务、互相交接、仲裁或二次综合；结果只是带标题拼接，可能重复或矛盾。
- 澄清在紧急路由前执行：OTHER 且低置信度、长度大于 2 时，即使 CRITICAL 也会先澄清。应把安全升级放在澄清前。
- 没有应用级 Agent 截止时间/并发信号量；多个请求共享统计，累计成功率只是调用不抛异常，不是业务解决率。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
