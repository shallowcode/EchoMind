# mcp/tool_manager.py 解读

## 输入、输出与流向

**定位：** 本地工具注册与检索可靠性封装；类名虽含 MCP，本文件没有协议会话和传输实现。

**输入：** Tool(name, handler, schema, ttl, timeout, fallback)；调用 name/params/context；检索 query/top_k。

**输出 / 副作用：** ToolResult(success, data, error, cached, latency_ms, reranked)；修改进程内 TTL 缓存、工具统计、熔断状态。

**流向：** call：查注册→缓存→熔断→参数校验→超时包装 handler→可选重排→缓存；search_with_rewrite：LLM 改写→多次 call 并发→去重→LLM 重排。

[返回阅读入口](../../README.md) · [对照原文件](../../../mcp/tool_manager.py)

当前工作区快照：465 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`f76b914a3565ddc44011ad9910cd99bcd054813d4845b724f5a8221bb8b3d09c`。

## 类与函数导航

[CircuitState](#symbol-34) → [ToolResult](#symbol-40) → [ToolStats](#symbol-51) → [ToolStats.success_rate](#symbol-60) → [ToolStats.avg_latency_ms](#symbol-64) → [CircuitBreaker](#symbol-71) → [CircuitBreaker.__init__](#symbol-80) → [CircuitBreaker.allow](#symbol-87) → [CircuitBreaker.record_success](#symbol-97) → [CircuitBreaker.record_failure](#symbol-101) → [Tool](#symbol-111) → [MCPToolManager](#symbol-129) → [MCPToolManager.__init__](#symbol-137) → [MCPToolManager.register](#symbol-148) → [MCPToolManager.unregister](#symbol-152) → [MCPToolManager.call](#symbol-157) → [MCPToolManager._fallback_result](#symbol-237) → [MCPToolManager._run_handler](#symbol-261) → [MCPToolManager.rewrite_query](#symbol-282) → [MCPToolManager.search_with_rewrite](#symbol-312) → [MCPToolManager._rerank](#symbol-355) → [MCPToolManager._cache_key](#symbol-393) → [MCPToolManager._get_cache](#symbol-397) → [MCPToolManager._set_cache](#symbol-406) → [MCPToolManager._validate_params](#symbol-425) → [MCPToolManager._clean_text](#symbol-444) → [MCPToolManager.get_stats](#symbol-455)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>亮点：MCP 工具调用框架</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>核心问题：工具调用出错（检索不全、召回不好）怎么优化？</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | （空行） | 空行，分隔逻辑。 |
| L6 | <code>本模块的答案：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;1. 查询改写（Query Rewriting）—— 用 LLM 把用户原始问题扩写成多个角度的子查询，</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;再合并去重，解决&quot;召回不全&quot;问题。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L9 | <code>&nbsp;&nbsp;2. 结果重排（Reranking）—— 对召回结果用 LLM 打分，按相关性重新排序，</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;解决&quot;召回不好/排序差&quot;问题。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L11 | <code>&nbsp;&nbsp;3. 熔断器（Circuit Breaker）—— 连续失败超阈值时自动断开，防止雪崩。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L12 | <code>&nbsp;&nbsp;4. 结果缓存（TTL Cache）—— 相同参数直接返回缓存，减少重复调用。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L13 | <code>&nbsp;&nbsp;5. 降级策略（Fallback）—— 工具不可用时返回有意义的降级结果。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L14 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L15 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L16 | <code>import hashlib</code> | 导入 <code>import hashlib</code>；只建立名称依赖，真正业务调用见后文。 |
| L17 | <code>import inspect</code> | 导入 <code>import inspect</code>；只建立名称依赖，真正业务调用见后文。 |
| L18 | <code>import json</code> | 导入 <code>import json</code>；只建立名称依赖，真正业务调用见后文。 |
| L19 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L20 | <code>import time</code> | 导入 <code>import time</code>；只建立名称依赖，真正业务调用见后文。 |
| L21 | <code>from dataclasses import dataclass, field</code> | 导入 <code>from dataclasses import dataclass, field</code>；只建立名称依赖，真正业务调用见后文。 |
| L22 | <code>from enum import Enum</code> | 导入 <code>from enum import Enum</code>；只建立名称依赖，真正业务调用见后文。 |
| L23 | <code>from typing import Any, Callable, Dict, List, Optional, Tuple</code> | 导入 <code>from typing import Any, Callable, Dict, List, Optional, Tuple</code>；只建立名称依赖，真正业务调用见后文。 |
| L24 | （空行） | 空行，分隔逻辑。 |
| L25 | <code>from anthropic import AsyncAnthropic</code> | 导入 <code>from anthropic import AsyncAnthropic</code>；只建立名称依赖，真正业务调用见后文。 |
| L26 | （空行） | 空行，分隔逻辑。 |
| L27 | <code>from core.llm_utils import extract_text_content</code> | 导入 <code>from core.llm_utils import extract_text_content</code>；只建立名称依赖，真正业务调用见后文。 |
| L28 | （空行） | 空行，分隔逻辑。 |
| L29 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L30 | （空行） | 空行，分隔逻辑。 |
| L31 | （空行） | 空行，分隔逻辑。 |
| L32 | <code># ── 数据结构 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 数据结构 ────────────────────────────────────────────────────────────────── |
| L33 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-34"></a>

### L34–L37 · CircuitState

CLOSED 正常、OPEN 快速拒绝、HALF_OPEN 尝试恢复。与连接的开关含义容易相反：OPEN 是熔断。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L34 | <code>class CircuitState(Enum):</code> | 定义 <code>CircuitState</code> 的数据契约/行为；继承与字段见本段。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;CLOSED    = &quot;closed&quot;     # 正常</code> | 将结果保存到 <code>CLOSED</code>：使用固定文本/配置值。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;OPEN      = &quot;open&quot;       # 熔断，拒绝请求</code> | 将结果保存到 <code>OPEN</code>：使用固定文本/配置值。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;HALF_OPEN = &quot;half_open&quot;  # 探测恢复</code> | 将结果保存到 <code>HALF_OPEN</code>：使用固定文本/配置值。 |
| L38 | （空行） | 空行，分隔逻辑。 |
| L39 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-40"></a>

### L40–L48 · ToolResult

返回业务数据及执行状态。success 目前混用了真实执行成功与降级返回成功，应拆分 execution_status/degraded。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L40 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L41 | <code>class ToolResult:</code> | 定义 <code>ToolResult</code> 的数据契约/行为；继承与字段见本段。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;success:        bool</code> | 声明字段 <code>success</code> 的类型，赋值由构造方完成。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;data:           Any</code> | 声明字段 <code>data</code> 的类型，赋值由构造方完成。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;tool_name:      str</code> | 声明字段 <code>tool_name</code> 的类型，赋值由构造方完成。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;error:          Optional[str] = None</code> | 将结果保存到 <code>error</code>：使用这里写明的固定值。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cached:         bool = False</code> | 将结果保存到 <code>cached</code>：使用这里写明的固定值。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;latency_ms:     float = 0.0</code> | 将结果保存到 <code>latency_ms</code>：使用这里写明的固定值。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;reranked:       bool = False   # 是否经过重排</code> | 将结果保存到 <code>reranked</code>：使用这里写明的固定值。 |
| L49 | （空行） | 空行，分隔逻辑。 |
| L50 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-51"></a>

### L51–L66 · ToolStats

total/success/failed/consecutive_fails 记录 handler 相关过程；缓存命中也增加 total/success。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L51 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L52 | <code>class ToolStats:</code> | 定义 <code>ToolStats</code> 的数据契约/行为；继承与字段见本段。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;工具运行时统计，供 Monitor 读取。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;total:              int = 0</code> | 将结果保存到 <code>total</code>：使用这里写明的固定值。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;success:            int = 0</code> | 将结果保存到 <code>success</code>：使用这里写明的固定值。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;failed:             int = 0</code> | 将结果保存到 <code>failed</code>：使用这里写明的固定值。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;total_latency_ms:   float = 0.0</code> | 将结果保存到 <code>total_latency_ms</code>：使用这里写明的固定值。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;consecutive_fails:  int = 0</code> | 将结果保存到 <code>consecutive_fails</code>：使用这里写明的固定值。 |
| L59 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-60"></a>

### L60–L62 · ToolStats.success_rate

success/total，无样本按 1.0。OPEN 拒绝不计 total，会掩盖用户侧失败比例。

**签名输入：** <code>self</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def success_rate(self) -&gt; float:</code> | 定义函数 <code>success_rate</code>；输入参数见签名，下方导读解释调用目的。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.success / self.total if self.total else 1.0</code> | 结束当前函数并返回；条件 <code>self.total</code> 成立选前值，否则选 else 后值。 |
| L63 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-64"></a>

### L64–L66 · ToolStats.avg_latency_ms

total_latency_ms/total；分母含缓存和失败而分子不含它们完整耗时，不能直接解释为端到端工具平均延迟。

**签名输入：** <code>self</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def avg_latency_ms(self) -&gt; float:</code> | 定义函数 <code>avg_latency_ms</code>；输入参数见签名，下方导读解释调用目的。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.total_latency_ms / self.total if self.total else 0.0</code> | 结束当前函数并返回；条件 <code>self.total</code> 成立选前值，否则选 else 后值。 |
| L67 | （空行） | 空行，分隔逻辑。 |
| L68 | （空行） | 空行，分隔逻辑。 |
| L69 | <code># ── 熔断器 ────────────────────────────────────────────────────────────────────</code> | 源码注释：── 熔断器 ──────────────────────────────────────────────────────────────────── |
| L70 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-71"></a>

### L71–L106 · CircuitBreaker

本地工具注册与检索可靠性封装；类名虽含 MCP，本文件没有协议会话和传输实现。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L71 | <code>class CircuitBreaker:</code> | 定义 <code>CircuitBreaker</code> 的数据契约/行为；继承与字段见本段。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;三态熔断器：CLOSED → OPEN → HALF_OPEN → CLOSED</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L74 | （空行） | 空行，分隔逻辑。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;连续失败 failure_threshold 次后打开；</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;打开 recovery_s 秒后进入 HALF_OPEN 探测；</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;探测成功则关闭，失败则重新打开。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L79 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-80"></a>

### L80–L85 · CircuitBreaker.__init__

默认连续失败 5 次打开，60 秒后允许恢复；状态只在进程内，不与其他 worker 共享。

**签名输入：** <code>self, failure_threshold: int=5, recovery_s: float=60.0</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, failure_threshold: int = 5, recovery_s: float = 60.0):</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.threshold   = failure_threshold</code> | 将结果保存到 <code>self.threshold</code>：读取 <code>failure_threshold</code>。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.recovery_s  = recovery_s</code> | 将结果保存到 <code>self.recovery_s</code>：读取 <code>recovery_s</code>。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.state       = CircuitState.CLOSED</code> | 将结果保存到 <code>self.state</code>：读取 <code>CircuitState.CLOSED</code>。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.fail_count  = 0</code> | 将结果保存到 <code>self.fail_count</code>：使用这里写明的固定值。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.opened_at:  Optional[float] = None</code> | 将结果保存到 <code>self.opened_at</code>：使用这里写明的固定值。 |
| L86 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-87"></a>

### L87–L95 · CircuitBreaker.allow

OPEN 未到恢复时间拒绝，到了转 HALF_OPEN。这里没有“已有一个探测在运行”检查，多调用会同时放行。

**签名输入：** <code>self</code>；**返回契约：** <code>bool</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def allow(self) -&gt; bool:</code> | 定义函数 <code>allow</code>；输入参数见签名，下方导读解释调用目的。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.state == CircuitState.CLOSED:</code> | 判断 <code>self.state == CircuitState.CLOSED</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return True</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.state == CircuitState.OPEN:</code> | 判断 <code>self.state == CircuitState.OPEN</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if time.monotonic() - self.opened_at &gt;= self.recovery_s:  # type: ignore</code> | 判断 <code>time.monotonic() - self.opened_at &gt;= self.recovery_s</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.state = CircuitState.HALF_OPEN</code> | 将结果保存到 <code>self.state</code>：读取 <code>CircuitState.HALF_OPEN</code>。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return True</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return True  # HALF_OPEN：放行一次探测</code> | **关键：**所有 HALF_OPEN 请求都 True；没有控制单个探测。 |
| L96 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-97"></a>

### L97–L99 · CircuitBreaker.record_success

任一成功重置失败计数并关熔断器。并发失败和成功回报次序可能影响最终状态。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def record_success(self) -&gt; None:</code> | 定义函数 <code>record_success</code>；输入参数见签名，下方导读解释调用目的。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.fail_count = 0</code> | 将结果保存到 <code>self.fail_count</code>：使用这里写明的固定值。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.state = CircuitState.CLOSED</code> | 将结果保存到 <code>self.state</code>：读取 <code>CircuitState.CLOSED</code>。 |
| L100 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-101"></a>

### L101–L106 · CircuitBreaker.record_failure

累计连续失败，达到阈值记录打开时间；下一次 allow 才判断冷却是否到期。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def record_failure(self) -&gt; None:</code> | 定义函数 <code>record_failure</code>；输入参数见签名，下方导读解释调用目的。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.fail_count += 1</code> | 更新 <code>self.fail_count</code>：<code>self.fail_count += 1</code>；此处会改变累计状态。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.fail_count &gt;= self.threshold:</code> | 判断 <code>self.fail_count &gt;= self.threshold</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.state     = CircuitState.OPEN</code> | 将结果保存到 <code>self.state</code>：读取 <code>CircuitState.OPEN</code>。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.opened_at = time.monotonic()</code> | 将结果保存到 <code>self.opened_at</code>：读取单调时钟，用来算耗时/过期，不作为日历时间。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;熔断器打开（连续失败 {self.fail_count} 次）&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L107 | （空行） | 空行，分隔逻辑。 |
| L108 | （空行） | 空行，分隔逻辑。 |
| L109 | <code># ── 工具定义 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 工具定义 ────────────────────────────────────────────────────────────────── |
| L110 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-111"></a>

### L111–L124 · Tool

描述工具能力和执行策略。每个 Tool 用 default_factory 创建独立 stats/breaker，避免跨工具共用状态。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L111 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L112 | <code>class Tool:</code> | 定义 <code>Tool</code> 的数据契约/行为；继承与字段见本段。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;name:        str</code> | 声明字段 <code>name</code> 的类型，赋值由构造方完成。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;description: str</code> | 声明字段 <code>description</code> 的类型，赋值由构造方完成。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;handler:     Callable                    # async (params, context) -&gt; Any</code> | 声明字段 <code>handler</code> 的类型，赋值由构造方完成。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;schema:      Dict[str, Any]              # JSON Schema</code> | 声明字段 <code>schema</code> 的类型，赋值由构造方完成。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cache_ttl:   float = 0.0                 # 0 = 不缓存</code> | 将结果保存到 <code>cache_ttl</code>：使用这里写明的固定值。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;timeout_s:   float = 30.0</code> | 将结果保存到 <code>timeout_s</code>：使用这里写明的固定值。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;supports_rerank: bool = False            # 是否支持结果重排</code> | 将结果保存到 <code>supports_rerank</code>：使用这里写明的固定值。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fallback:    Optional[Callable] = None    # sync/async (params, context, error) -&gt; Any</code> | 将结果保存到 <code>fallback</code>：使用这里写明的固定值。 |
| L121 | （空行） | 空行，分隔逻辑。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 运行时状态（不参与构造）</code> | 源码注释：运行时状态（不参与构造） |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;stats:   ToolStats    = field(default_factory=ToolStats, init=False)</code> | 将结果保存到 <code>stats</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;breaker: CircuitBreaker = field(default_factory=CircuitBreaker, init=False)</code> | 将结果保存到 <code>breaker</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L125 | （空行） | 空行，分隔逻辑。 |
| L126 | （空行） | 空行，分隔逻辑。 |
| L127 | <code># ── MCP 工具管理器 ────────────────────────────────────────────────────────────</code> | 源码注释：── MCP 工具管理器 ──────────────────────────────────────────────────────────── |
| L128 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-129"></a>

### L129–L465 · MCPToolManager

本地工具注册与检索可靠性封装；类名虽含 MCP，本文件没有协议会话和传输实现。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L129 | <code>class MCPToolManager:</code> | 定义 <code>MCPToolManager</code> 的数据契约/行为；继承与字段见本段。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;MCP 工具调用框架。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L132 | （空行） | 空行，分隔逻辑。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;核心优化链路（针对检索类工具）：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;用户查询 → 查询改写（多角度子查询）→ 并行召回 → 结果重排 → 返回 Top-K</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L136 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-137"></a>

### L137–L144 · MCPToolManager.__init__

客户端用于改写/重排；注册表和缓存为当前进程字典，没有远程发现工具。

**签名输入：** <code>self, api_key: str, base_url: Optional[str]=None, model: str=&#x27;claude-3-5-sonnet-20241022&#x27;</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = &quot;claude-3-5-sonnet-20241022&quot;):</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs: Dict[str, Any] = {&quot;api_key&quot;: api_key}</code> | 将结果保存到 <code>kwargs</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if base_url:</code> | 判断 <code>base_url</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs[&quot;base_url&quot;] = base_url</code> | 将结果保存到 <code>kwargs[&#x27;base_url&#x27;]</code>：读取 <code>base_url</code>。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._client = AsyncAnthropic(**kwargs)</code> | 将结果保存到 <code>self._client</code>：调用 <code>AsyncAnthropic</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._model  = model</code> | 将结果保存到 <code>self._model</code>：读取 <code>model</code>。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._tools: Dict[str, Tool] = {}</code> | 将结果保存到 <code>self._tools</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._cache: Dict[str, tuple] = {}   # key → (result, expire_at, reranked)</code> | 将结果保存到 <code>self._cache</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L145 | （空行） | 空行，分隔逻辑。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 注册 / 注销 ───────────────────────────────────────────────────────────</code> | 源码注释：── 注册 / 注销 ─────────────────────────────────────────────────────────── |
| L147 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-148"></a>

### L148–L150 · MCPToolManager.register

同名覆盖已有 Tool；旧缓存不会自动清理。

**签名输入：** <code>self, tool: Tool</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def register(self, tool: Tool) -&gt; None:</code> | 定义函数 <code>register</code>；输入参数见签名，下方导读解释调用目的。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._tools[tool.name] = tool</code> | 将结果保存到 <code>self._tools[tool.name]</code>：读取 <code>tool</code>。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;注册工具: {tool.name}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L151 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-152"></a>

### L152–L153 · MCPToolManager.unregister

删除注册项，未删除相同名字缓存。重新注册同名工具可能读到旧结果。

**签名输入：** <code>self, name: str</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def unregister(self, name: str) -&gt; None:</code> | 定义函数 <code>unregister</code>；输入参数见签名，下方导读解释调用目的。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._tools.pop(name, None)</code> | 移除并取出键/元素。 |
| L154 | （空行） | 空行，分隔逻辑。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 核心调用 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 核心调用 ────────────────────────────────────────────────────────────── |
| L156 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-157"></a>

### L157–L235 · MCPToolManager.call

工具治理单入口。缓存置于熔断之前，依赖故障期间仍能用旧有效结果；参数在熔断之后校验，错误参数会计作服务故障。

**签名输入：** <code>self, name: str, params: Dict[str, Any], context: Optional[Dict[str, Any]]=None, *, use_cache: bool=True, rerank_top_k: int=0</code>；**返回契约：** <code>ToolResult</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def call(</code> | 定义异步函数 <code>call</code>；输入参数见签名，下方导读解释调用目的。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;params: Dict[str, Any],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context: Optional[Dict[str, Any]] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;use_cache: bool = True,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rerank_top_k: int = 0,          # &gt;0 时对结果重排，取 Top-K</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; ToolResult:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;调用工具，完整执行链：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;缓存检查 → 熔断检查 → 参数校验 → 执行（含超时）→ 可选重排 → 缓存写入</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool = self._tools.get(name)</code> | 将结果保存到 <code>tool</code>：按键取值，缺失用给定默认值。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not tool:</code> | 判断 <code>not tool</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(success=False, data=None, tool_name=name, error=f&quot;工具不存在: {name}&quot;)</code> | 结束当前函数并返回；进入 <code>ToolResult</code>：返回业务数据及执行状态。 |
| L173 | （空行） | 空行，分隔逻辑。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cache_rerank_top_k = rerank_top_k if rerank_top_k &gt; 0 and tool.supports_rerank else 0</code> | 将结果保存到 <code>cache_rerank_top_k</code>：条件 <code>rerank_top_k &gt; 0 and tool.supports_rerank</code> 成立选前值，否则选 else 后值。 |
| L175 | （空行） | 空行，分隔逻辑。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 缓存命中</code> | 源码注释：缓存命中 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if use_cache and tool.cache_ttl &gt; 0:</code> | 判断 <code>use_cache and tool.cache_ttl &gt; 0</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cached = self._get_cache(name, params, cache_rerank_top_k)</code> | 将结果保存到 <code>cached</code>：进入 <code>self._get_cache</code>：未过期返回数据和 reranked 标记；过期只在访问此键时删除，是惰性过期。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if cached is not None:</code> | 判断 <code>cached is not None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cached_data, cached_reranked = cached</code> | 将结果保存到 <code>(cached_data, cached_reranked)</code>：读取 <code>cached</code>。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.total += 1</code> | 更新 <code>tool.stats.total</code>：<code>tool.stats.total += 1</code>；此处会改变累计状态。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.success += 1</code> | 更新 <code>tool.stats.success</code>：<code>tool.stats.success += 1</code>；此处会改变累计状态。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(</code> | 结束当前函数并返回；进入 <code>ToolResult</code>：返回业务数据及执行状态。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;success=True,</code> | 参数 <code>success</code>（执行成功标记）：使用这里写明的固定值。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data=cached_data,</code> | 参数 <code>data</code>（data）：读取 <code>cached_data</code>。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool_name=name,</code> | 参数 <code>tool_name</code>（tool_name）：读取 <code>name</code>。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cached=True,</code> | 参数 <code>cached</code>（缓存命中标记）：使用这里写明的固定值。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reranked=cached_reranked,</code> | 参数 <code>reranked</code>（重排标记）：读取 <code>cached_reranked</code>。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L190 | （空行） | 空行，分隔逻辑。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 熔断检查</code> | 源码注释：熔断检查 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not tool.breaker.allow():</code> | 判断 <code>not tool.breaker.allow()</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;error = f&quot;工具熔断中: {name}，请稍后重试&quot;</code> | 将结果保存到 <code>error</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await self._fallback_result(tool, params, context, error)</code> | 结束当前函数并返回；等待完成后继续；进入 <code>self._fallback_result</code>：兼容同步/协程 fallback；保留 error 却设 success=True，调用方要理解这是可返回，不等于真实工具成功。 |
| L195 | （空行） | 空行，分隔逻辑。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;t0 = time.monotonic()</code> | 将结果保存到 <code>t0</code>：读取单调时钟，用来算耗时/过期，不作为日历时间。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.total += 1</code> | 更新 <code>tool.stats.total</code>：<code>tool.stats.total += 1</code>；此处会改变累计状态。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 参数校验（根据 JSON Schema 的 required 和 properties.type）</code> | 源码注释：参数校验（根据 JSON Schema 的 required 和 properties.type） |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._validate_params(tool, params)</code> | 进入 <code>self._validate_params</code>：逐个 required 检查存在，逐个 properties 检查 Python 类型。 |
| L201 | （空行） | 空行，分隔逻辑。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data = await asyncio.wait_for(self._run_handler(tool, params, context), timeout=tool.timeout_s)</code> | **关键：**30 秒默认超时仅限制 _run_handler 的等待范围。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency = (time.monotonic() - t0) * 1000</code> | 将结果保存到 <code>latency</code>：按此表达式计算 <code>(time.monotonic() - t0) * 1000</code>。 |
| L204 | （空行） | 空行，分隔逻辑。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.success += 1</code> | **关键：**成功计数在重排之前增加，延迟也只到 handler 返回。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.consecutive_fails = 0</code> | 将结果保存到 <code>tool.stats.consecutive_fails</code>：使用这里写明的固定值。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.total_latency_ms += latency</code> | 更新 <code>tool.stats.total_latency_ms</code>：<code>tool.stats.total_latency_ms += latency</code>；此处会改变累计状态。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.breaker.record_success()</code> | 进入 <code>tool.breaker.record_success</code>：任一成功重置失败计数并关熔断器。 |
| L209 | （空行） | 空行，分隔逻辑。 |
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 重排（针对返回列表的检索工具）</code> | 源码注释：重排（针对返回列表的检索工具） |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reranked = False</code> | 将结果保存到 <code>reranked</code>：使用这里写明的固定值。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if rerank_top_k &gt; 0 and tool.supports_rerank and isinstance(data, list):</code> | 判断 <code>rerank_top_k &gt; 0 and tool.supports_rerank and isinstance(data, list)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query = params.get(&quot;query&quot;, &quot;&quot;)</code> | 将结果保存到 <code>query</code>：按键取值，缺失用给定默认值。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data, reranked = await self._rerank(query, data, rerank_top_k), True</code> | 将结果保存到 <code>(data, reranked)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L215 | （空行） | 空行，分隔逻辑。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 写缓存：缓存最终返回结果，避免下次命中未重排的原始结果。</code> | 源码注释：写缓存：缓存最终返回结果，避免下次命中未重排的原始结果。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if tool.cache_ttl &gt; 0:</code> | **关键：**即使 use_cache=False，满足 ttl>0 仍写入缓存。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._set_cache(name, params, data, tool.cache_ttl, cache_rerank_top_k, reranked)</code> | 进入 <code>self._set_cache</code>：达到 5000 条删除最早插入的 1250 条，再用 monotonic 记录过期时间。 |
| L219 | （空行） | 空行，分隔逻辑。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(success=True, data=data, tool_name=name,</code> | 结束当前函数并返回；进入 <code>ToolResult</code>：返回业务数据及执行状态。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=latency, reranked=reranked)</code> | 参数 <code>reranked</code>（重排标记）：读取 <code>reranked</code>。 |
| L222 | （空行） | 空行，分隔逻辑。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except asyncio.TimeoutError:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.failed += 1</code> | 更新 <code>tool.stats.failed</code>：<code>tool.stats.failed += 1</code>；此处会改变累计状态。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.consecutive_fails += 1</code> | 更新 <code>tool.stats.consecutive_fails</code>：<code>tool.stats.consecutive_fails += 1</code>；此处会改变累计状态。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.breaker.record_failure()</code> | 进入 <code>tool.breaker.record_failure</code>：累计连续失败，达到阈值记录打开时间；下一次 allow 才判断冷却是否到期。 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.error(f&quot;工具超时: {name} ({tool.timeout_s}s)&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await self._fallback_result(tool, params, context, &quot;执行超时&quot;)</code> | 结束当前函数并返回；等待完成后继续；进入 <code>self._fallback_result</code>：兼容同步/协程 fallback；保留 error 却设 success=True，调用方要理解这是可返回，不等于真实工具成功。 |
| L229 | （空行） | 空行，分隔逻辑。 |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.failed += 1</code> | 更新 <code>tool.stats.failed</code>：<code>tool.stats.failed += 1</code>；此处会改变累计状态。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.stats.consecutive_fails += 1</code> | 更新 <code>tool.stats.consecutive_fails</code>：<code>tool.stats.consecutive_fails += 1</code>；此处会改变累计状态。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool.breaker.record_failure()</code> | 进入 <code>tool.breaker.record_failure</code>：累计连续失败，达到阈值记录打开时间；下一次 allow 才判断冷却是否到期。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.error(f&quot;工具异常: {name} — {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await self._fallback_result(tool, params, context, str(ex))</code> | 结束当前函数并返回；等待完成后继续；进入 <code>self._fallback_result</code>：兼容同步/协程 fallback；保留 error 却设 success=True，调用方要理解这是可返回，不等于真实工具成功。 |
| L236 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-237"></a>

### L237–L259 · MCPToolManager._fallback_result

兼容同步/协程 fallback；保留 error 却设 success=True，调用方要理解这是可返回，不等于真实工具成功。

**签名输入：** <code>self, tool: Tool, params: Dict[str, Any], context: Optional[Dict[str, Any]], error: str</code>；**返回契约：** <code>ToolResult</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _fallback_result(</code> | 定义异步函数 <code>_fallback_result</code>；输入参数见签名，下方导读解释调用目的。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool: Tool,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;params: Dict[str, Any],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context: Optional[Dict[str, Any]],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;error: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; ToolResult:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;工具不可用时返回降级结果，而不是把空错误直接暴露给调用方。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if tool.fallback is None:</code> | 判断 <code>tool.fallback is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(success=False, data=None, tool_name=tool.name, error=error)</code> | 结束当前函数并返回；进入 <code>ToolResult</code>：返回业务数据及执行状态。 |
| L247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data = tool.fallback(params, context, error)</code> | 将结果保存到 <code>data</code>：调用 <code>tool.fallback</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if asyncio.iscoroutine(data):</code> | 判断 <code>asyncio.iscoroutine(data)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data = await data</code> | 将结果保存到 <code>data</code>：等待完成后继续；读取 <code>data</code>。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(</code> | 结束当前函数并返回；进入 <code>ToolResult</code>：返回业务数据及执行状态。 |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;success=True,</code> | **关键：**降级可返回也标成功，调用层必须另看 error/fallback。 |
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data=data,</code> | 参数 <code>data</code>（data）：读取 <code>data</code>。 |
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool_name=tool.name,</code> | 参数 <code>tool_name</code>（tool_name）：读取 <code>tool.name</code>。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;error=error,</code> | 参数 <code>error</code>（error）：读取 <code>error</code>。 |
| L256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.error(f&quot;工具降级失败: {tool.name} — {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(success=False, data=None, tool_name=tool.name, error=f&quot;{error}; fallback失败: {ex}&quot;)</code> | 结束当前函数并返回；进入 <code>ToolResult</code>：返回业务数据及执行状态。 |
| L260 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-261"></a>

### L261–L278 · MCPToolManager._run_handler

async handler 直接 await；普通函数放线程，再检查返回值是否 awaitable。这样避免同步 I/O 卡住事件循环。

**签名输入：** <code>self, tool: Tool, params: Dict[str, Any], context: Optional[Dict[str, Any]]</code>；**返回契约：** <code>Any</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _run_handler(</code> | 定义异步函数 <code>_run_handler</code>；输入参数见签名，下方导读解释调用目的。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool: Tool,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;params: Dict[str, Any],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context: Optional[Dict[str, Any]],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; Any:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;执行工具 handler。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L269 | （空行） | 空行，分隔逻辑。 |
| L270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;优先支持 async handler；如果历史工具仍是同步函数，则放入线程池执行，</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;避免阻塞事件循环。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if inspect.iscoroutinefunction(tool.handler):</code> | 判断 <code>inspect.iscoroutinefunction(tool.handler)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await tool.handler(params, context)</code> | 结束当前函数并返回；等待完成后继续；调用 <code>tool.handler</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result = await asyncio.to_thread(tool.handler, params, context)</code> | 将结果保存到 <code>result</code>：等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if inspect.isawaitable(result):</code> | 判断 <code>inspect.isawaitable(result)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await result</code> | 结束当前函数并返回；等待完成后继续；读取 <code>result</code>。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return result</code> | 结束当前函数并返回；读取 <code>result</code>。 |
| L279 | （空行） | 空行，分隔逻辑。 |
| L280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 查询改写（解决召回不全）────────────────────────────────────────────────</code> | 源码注释：── 查询改写（解决召回不全）──────────────────────────────────────────────── |
| L281 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-282"></a>

### L282–L310 · MCPToolManager.rewrite_query

让 LLM 生成 3 个角度的子查询，再保留原查询并保序去重。数量仅是 prompt 要求，未严格截断；JSON 异常则只用原查询。

**签名输入：** <code>self, query: str, n: int=3</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def rewrite_query(self, query: str, n: int = 3) -&gt; List[str]:</code> | 定义异步函数 <code>rewrite_query</code>；输入参数见签名，下方导读解释调用目的。 |
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;用 LLM 将原始查询改写为 n 个不同角度的子查询。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L285 | （空行） | 空行，分隔逻辑。 |
| L286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;目的：单一查询往往只能召回某一角度的文档，</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;多角度子查询并行检索后合并，显著提升召回率。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L288 | （空行） | 空行，分隔逻辑。 |
| L289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;示例：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;原始: &quot;退款流程&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;改写: [&quot;如何申请退款&quot;, &quot;退款需要多少天&quot;, &quot;退款政策是什么&quot;]</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = f&quot;&quot;&quot;将以下用户查询改写为 {n} 个不同角度的搜索子查询，用于检索知识库。</code> | 将结果保存到 <code>prompt</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L294 | <code>要求：每个子查询角度不同，覆盖原始问题的不同方面。</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L295 | <code>原始查询: &quot;{query}&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L296 | <code>返回 JSON 数组，例如: [&quot;子查询1&quot;, &quot;子查询2&quot;, &quot;子查询3&quot;]&quot;&quot;&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = self._clean_text(prompt)</code> | 将结果保存到 <code>prompt</code>：调用 <code>self._clean_text</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await self._client.messages.create(</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=self._model, max_tokens=256, temperature=0.3,</code> | 参数 <code>temperature</code>（生成采样温度）：使用这里写明的固定值。 |
| L301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: prompt}],</code> | 参数 <code>messages</code>（模型消息序列/当前函数的消息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = extract_text_content(resp.content)</code> | 将结果保存到 <code>raw</code>：进入共享响应适配器，只保留模型文本块。 |
| L304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;s, e = raw.find(&quot;[&quot;), raw.rfind(&quot;]&quot;) + 1</code> | 将结果保存到 <code>(s, e)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;queries = json.loads(raw[s:e])</code> | 将结果保存到 <code>queries</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 原始查询也保留，去重</code> | 源码注释：原始查询也保留，去重 |
| L307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return list(dict.fromkeys([query] + queries))</code> | 结束当前函数并返回；将迭代内容物化成列表。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;查询改写失败，使用原始查询: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [query]</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L311 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-312"></a>

### L312–L351 · MCPToolManager.search_with_rewrite

先改写再并行召回，各分支至少取 5 条；个别异常被 gather 收集，不阻止其他结果。最终候选交给重排。扩大召回是设计意图，提升幅度需标注集验证。

**签名输入：** <code>self, tool_name: str, query: str, top_k: int=5, context: Optional[Dict[str, Any]]=None</code>；**返回契约：** <code>ToolResult</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def search_with_rewrite(</code> | 定义异步函数 <code>search_with_rewrite</code>；输入参数见签名，下方导读解释调用目的。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool_name: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;top_k: int = 5,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context: Optional[Dict[str, Any]] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; ToolResult:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;完整的检索优化链路：查询改写 → 并行召回 → 去重 → 重排 → Top-K</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L321 | （空行） | 空行，分隔逻辑。 |
| L322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;这是解决&quot;检索不全、召回不好&quot;的完整方案。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 1. 查询改写：生成多角度子查询</code> | 源码注释：1. 查询改写：生成多角度子查询 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sub_queries = await self.rewrite_query(query, n=3)</code> | 将结果保存到 <code>sub_queries</code>：等待完成后继续；进入 <code>self.rewrite_query</code>：让 LLM 生成 3 个角度的子查询，再保留原查询并保序去重。 |
| L326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;查询改写: {query!r} → {sub_queries}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L327 | （空行） | 空行，分隔逻辑。 |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 2. 并行召回：所有子查询同时检索</code> | 源码注释：2. 并行召回：所有子查询同时检索 |
| L329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recall_k = max(top_k, 5)</code> | 将结果保存到 <code>recall_k</code>：取当前候选中的最大值。 |
| L330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tasks = [</code> | 将结果保存到 <code>tasks</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L331 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.call(tool_name, {&quot;query&quot;: q, &quot;top_k&quot;: recall_k}, context, use_cache=True)</code> | 参数 <code>use_cache</code>（use_cache）：使用这里写明的固定值。 |
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for q in sub_queries</code> | 续接 L330 的表达式：按前述语句组装参数、条件或集合。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results = await asyncio.gather(*tasks, return_exceptions=True)</code> | 将结果保存到 <code>results</code>：等待完成后继续；并发等待这批任务，结果顺序与输入任务顺序一致。 |
| L335 | （空行） | 空行，分隔逻辑。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 3. 合并去重（按内容哈希去重）</code> | 源码注释：3. 合并去重（按内容哈希去重） |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;seen, merged = set(), []</code> | 将结果保存到 <code>(seen, merged)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for r in results:</code> | 遍历 <code>results</code>，本轮元素绑定 <code>r</code>。 |
| L339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(r, ToolResult) and r.success and isinstance(r.data, list):</code> | 判断 <code>isinstance(r, ToolResult) and r.success and isinstance(r.data, list)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for item in r.data:</code> | 遍历 <code>r.data</code>，本轮元素绑定 <code>item</code>。 |
| L341 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key = hashlib.md5(str(item).encode()).hexdigest()</code> | **关键：**整个字典字符串含 score，不能保证按片段内容去重。 |
| L342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if key not in seen:</code> | 判断 <code>key not in seen</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;seen.add(key)</code> | 向集合/存储添加数据，具体目标见左侧接收者。 |
| L344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;merged.append(item)</code> | 追加一个元素到当前列表。 |
| L345 | （空行） | 空行，分隔逻辑。 |
| L346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not merged:</code> | 判断 <code>not merged</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(success=False, data=[], tool_name=tool_name, error=&quot;所有子查询均无结果&quot;)</code> | 结束当前函数并返回；进入 <code>ToolResult</code>：返回业务数据及执行状态。 |
| L348 | （空行） | 空行，分隔逻辑。 |
| L349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 4. 重排：用 LLM 对合并结果按相关性打分，取 Top-K</code> | 源码注释：4. 重排：用 LLM 对合并结果按相关性打分，取 Top-K |
| L350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reranked = await self._rerank(query, merged, top_k)</code> | 将结果保存到 <code>reranked</code>：等待完成后继续；进入 <code>self._rerank</code>：候选不超过 top_k 直接返回，否则每项截 200 字符给 LLM，解析返回索引排序。 |
| L351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return ToolResult(success=True, data=reranked, tool_name=tool_name, reranked=True)</code> | **关键：**固定标记 True，即使候选少而跳过重排或模型异常回原顺序。 |
| L352 | （空行） | 空行，分隔逻辑。 |
| L353 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 结果重排（解决召回不好）──────────────────────────────────────────────</code> | 源码注释：── 结果重排（解决召回不好）────────────────────────────────────────────── |
| L354 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-355"></a>

### L355–L389 · MCPToolManager._rerank

候选不超过 top_k 直接返回，否则每项截 200 字符给 LLM，解析返回索引排序。没有去重索引、补齐遗漏；模型返回 [] 会让已有结果全部消失。

**签名输入：** <code>self, query: str, items: List[Any], top_k: int</code>；**返回契约：** <code>List[Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L355 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _rerank(self, query: str, items: List[Any], top_k: int) -&gt; List[Any]:</code> | 定义异步函数 <code>_rerank</code>；输入参数见签名，下方导读解释调用目的。 |
| L356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;用 LLM 对召回结果重新打分排序。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L358 | （空行） | 空行，分隔逻辑。 |
| L359 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;解决问题：向量检索的相似度分数不等于&quot;对用户有用&quot;，</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;LLM 能理解语义相关性，重排后 Top-K 质量显著提升。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L361 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(items) &lt;= top_k:</code> | 判断 <code>len(items) &lt;= top_k</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L363 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return items</code> | 结束当前函数并返回；读取 <code>items</code>。 |
| L364 | （空行） | 空行，分隔逻辑。 |
| L365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 将结果序列化为文本供 LLM 评分</code> | 源码注释：将结果序列化为文本供 LLM 评分 |
| L366 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;items_text = &quot;\n&quot;.join(f&quot;{i}. {json.dumps(item, ensure_ascii=False)[:200]}&quot;</code> | 将结果保存到 <code>items_text</code>：把字符串片段按分隔符合并。 |
| L367 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i, item in enumerate(items))</code> | 续接 L366 的表达式：按前述语句组装参数、条件或集合。 |
| L368 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = f&quot;&quot;&quot;根据用户查询，对以下检索结果按相关性打分（0-10），返回 JSON 数组。</code> | 将结果保存到 <code>prompt</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L369 | <code>用户查询: &quot;{query}&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L370 | <code>检索结果:</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L371 | <code>{items_text}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L372 | （空行） | 空行，分隔逻辑。 |
| L373 | <code>返回格式（按相关性降序排列的索引列表）: [最相关的索引, ..., 最不相关的索引]</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L374 | <code>只返回 JSON 数组，不要其他文字。&quot;&quot;&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L375 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = self._clean_text(prompt)</code> | 将结果保存到 <code>prompt</code>：调用 <code>self._clean_text</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L376 | （空行） | 空行，分隔逻辑。 |
| L377 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await self._client.messages.create(</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算。 |
| L379 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=self._model, max_tokens=256, temperature=0.0,</code> | 参数 <code>temperature</code>（生成采样温度）：使用这里写明的固定值。 |
| L380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: prompt}],</code> | 参数 <code>messages</code>（模型消息序列/当前函数的消息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = extract_text_content(resp.content)</code> | 将结果保存到 <code>raw</code>：进入共享响应适配器，只保留模型文本块。 |
| L383 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;s, e = raw.find(&quot;[&quot;), raw.rfind(&quot;]&quot;) + 1</code> | 将结果保存到 <code>(s, e)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L384 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;order: List[int] = json.loads(raw[s:e])</code> | 将结果保存到 <code>order</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L385 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reranked = [items[i] for i in order if 0 &lt;= i &lt; len(items)]</code> | **关键：**只过滤越界索引；重复索引和遗漏没有修复。 |
| L386 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return reranked[:top_k]</code> | 结束当前函数并返回；按索引/切片取 <code>reranked[:top_k]</code>，注意是否截掉旧历史或长文本。 |
| L387 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L388 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;重排失败，返回原始顺序: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L389 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return items[:top_k]</code> | 结束当前函数并返回；按索引/切片取 <code>items[:top_k]</code>，注意是否截掉旧历史或长文本。 |
| L390 | （空行） | 空行，分隔逻辑。 |
| L391 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 缓存 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 缓存 ────────────────────────────────────────────────────────────────── |
| L392 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-393"></a>

### L393–L395 · MCPToolManager._cache_key

名称 + 参数和重排 top_k 的规范 JSON 哈希，使重排结果与原始结果分开缓存；忽略 context。

**签名输入：** <code>self, name: str, params: Dict, rerank_top_k: int=0</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L393 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _cache_key(self, name: str, params: Dict, rerank_top_k: int = 0) -&gt; str:</code> | 定义函数 <code>_cache_key</code>；输入参数见签名，下方导读解释调用目的。 |
| L394 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;payload = {&quot;params&quot;: params, &quot;rerank_top_k&quot;: rerank_top_k}</code> | 将结果保存到 <code>payload</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L395 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return f&quot;{name}:{hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()}&quot;</code> | 结束当前函数并返回；将变量插入模板，构造提示词、标识或可读说明。 |
| L396 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-397"></a>

### L397–L404 · MCPToolManager._get_cache

未过期返回数据和 reranked 标记；过期只在访问此键时删除，是惰性过期。

**签名输入：** <code>self, name: str, params: Dict, rerank_top_k: int=0</code>；**返回契约：** <code>Optional[Tuple[Any, bool]]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L397 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _get_cache(self, name: str, params: Dict, rerank_top_k: int = 0) -&gt; Optional[Tuple[Any, bool]]:</code> | 定义函数 <code>_get_cache</code>；输入参数见签名，下方导读解释调用目的。 |
| L398 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key = self._cache_key(name, params, rerank_top_k)</code> | 将结果保存到 <code>key</code>：调用 <code>self._cache_key</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L399 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if key in self._cache:</code> | 判断 <code>key in self._cache</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L400 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data, expire_at, reranked = self._cache[key]</code> | 将结果保存到 <code>(data, expire_at, reranked)</code>：按索引/切片取 <code>self._cache[key]</code>，注意是否截掉旧历史或长文本。 |
| L401 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if time.monotonic() &lt; expire_at:</code> | 判断 <code>time.monotonic() &lt; expire_at</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L402 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return data, reranked</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L403 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;del self._cache[key]</code> | 删除 <code>del self._cache[key]</code> 对应状态；淘汰/重建逻辑需看外层范围。 |
| L404 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L405 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-406"></a>

### L406–L419 · MCPToolManager._set_cache

达到 5000 条删除最早插入的 1250 条，再用 monotonic 记录过期时间。不是分布式缓存和严格 LRU。

**签名输入：** <code>self, name: str, params: Dict, data: Any, ttl: float, rerank_top_k: int=0, reranked: bool=False</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L406 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _set_cache(</code> | 定义函数 <code>_set_cache</code>；输入参数见签名，下方导读解释调用目的。 |
| L407 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L408 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L409 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;params: Dict,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L410 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data: Any,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L411 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ttl: float,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L412 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rerank_top_k: int = 0,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L413 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reranked: bool = False,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L414 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; None:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L415 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(self._cache) &gt;= 5000:</code> | 判断 <code>len(self._cache) &gt;= 5000</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L416 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 清掉最旧的 1/4</code> | 源码注释：清掉最旧的 1/4 |
| L417 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for k in list(self._cache)[:1250]:</code> | 遍历 <code>list(self._cache)[:1250]</code>，本轮元素绑定 <code>k</code>。 |
| L418 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;del self._cache[k]</code> | 删除 <code>del self._cache[k]</code> 对应状态；淘汰/重建逻辑需看外层范围。 |
| L419 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._cache[self._cache_key(name, params, rerank_top_k)] = (data, time.monotonic() + ttl, reranked)</code> | 将结果保存到 <code>self._cache[self._cache_key(name, params, rerank_top_k)]</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L420 | （空行） | 空行，分隔逻辑。 |
| L421 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 参数校验 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 参数校验 ────────────────────────────────────────────────────────────── |
| L422 | （空行） | 空行，分隔逻辑。 |
| L423 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_TYPE_MAP = {&quot;string&quot;: str, &quot;number&quot;: (int, float), &quot;integer&quot;: int, &quot;boolean&quot;: bool, &quot;array&quot;: list, &quot;object&quot;: dict}</code> | 将结果保存到 <code>_TYPE_MAP</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L424 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-425"></a>

### L425–L442 · MCPToolManager._validate_params

逐个 required 检查存在，逐个 properties 检查 Python 类型。只是一小部分 JSON Schema，不能称完整 schema 验证。

**签名输入：** <code>self, tool: Tool, params: Dict[str, Any]</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L425 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _validate_params(self, tool: Tool, params: Dict[str, Any]) -&gt; None:</code> | 定义函数 <code>_validate_params</code>；输入参数见签名，下方导读解释调用目的。 |
| L426 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;根据工具的 JSON Schema 校验参数，不合法时抛出 ValueError。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L427 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;schema = tool.schema</code> | 将结果保存到 <code>schema</code>：读取 <code>tool.schema</code>。 |
| L428 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;required = schema.get(&quot;required&quot;, [])</code> | 将结果保存到 <code>required</code>：按键取值，缺失用给定默认值。 |
| L429 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;properties = schema.get(&quot;properties&quot;, {})</code> | 将结果保存到 <code>properties</code>：按键取值，缺失用给定默认值。 |
| L430 | （空行） | 空行，分隔逻辑。 |
| L431 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for field in required:</code> | 遍历 <code>required</code>，本轮元素绑定 <code>field</code>。 |
| L432 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if field not in params:</code> | 判断 <code>field not in params</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L433 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise ValueError(f&quot;工具 {tool.name} 缺少必需参数: {field}&quot;)</code> | 抛出 <code>ValueError(f&#x27;工具 {tool.name} 缺少必需参数: {field}&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L434 | （空行） | 空行，分隔逻辑。 |
| L435 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for key, value in params.items():</code> | 遍历 <code>params.items()</code>，本轮元素绑定 <code>(key, value)</code>。 |
| L436 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if key in properties:</code> | 判断 <code>key in properties</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L437 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;expected_type = properties[key].get(&quot;type&quot;)</code> | 将结果保存到 <code>expected_type</code>：按键取值，缺失用给定默认值。 |
| L438 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if expected_type and expected_type in self._TYPE_MAP:</code> | 判断 <code>expected_type and expected_type in self._TYPE_MAP</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L439 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(value, self._TYPE_MAP[expected_type]):</code> | 判断 <code>not isinstance(value, self._TYPE_MAP[expected_type])</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L440 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise ValueError(</code> | 抛出 <code>ValueError(f&#x27;工具 {tool.name} 参数 {key} 类型错误: 期望 {expected_type}，实际 {type(value).__name__}&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L441 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;工具 {tool.name} 参数 {key} 类型错误: 期望 {expected_type}，实际 {type(value).__name__}&quot;</code> | 续接 L440 的表达式：按前述语句组装参数、条件或集合。 |
| L442 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L443 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-444"></a>

### L444–L451 · MCPToolManager._clean_text

修复编码边界，未清洗提示注入。

**签名输入：** <code>value: Any</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L444 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L445 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _clean_text(value: Any) -&gt; str:</code> | 定义函数 <code>_clean_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L446 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;移除 Unicode 代理字符，避免 LLM 请求编码失败。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L447 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if value is None:</code> | 判断 <code>value is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L448 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;</code> | 结束当前函数并返回；使用固定文本/配置值。 |
| L449 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(value, str):</code> | 判断 <code>not isinstance(value, str)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L450 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value = str(value)</code> | 将结果保存到 <code>value</code>：转换为字符串表示。 |
| L451 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return value.encode(&quot;utf-8&quot;, errors=&quot;ignore&quot;).decode(&quot;utf-8&quot;)</code> | 结束当前函数并返回；调用 <code>value.encode(&#x27;utf-8&#x27;, errors=&#x27;ignore&#x27;).decode</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L452 | （空行） | 空行，分隔逻辑。 |
| L453 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 统计 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 统计 ────────────────────────────────────────────────────────────────── |
| L454 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-455"></a>

### L455–L465 · MCPToolManager.get_stats

供 Monitor 读取工具级统计与熔断状态；不包含检索质量、召回率或重排模型费用。

**签名输入：** <code>self</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L455 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def get_stats(self) -&gt; Dict[str, Any]:</code> | 定义函数 <code>get_stats</code>；输入参数见签名，下方导读解释调用目的。 |
| L456 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L457 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name: {</code> | 续接 L456 的表达式：按前述语句组装参数、条件或集合。 |
| L458 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;total&quot;: t.stats.total,</code> | 字段 <code>total</code>（当前映射中的键）：读取 <code>t.stats.total</code>。 |
| L459 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;success_rate&quot;: round(t.stats.success_rate, 3),</code> | 字段 <code>success_rate</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L460 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;avg_latency_ms&quot;: round(t.stats.avg_latency_ms, 1),</code> | 字段 <code>avg_latency_ms</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L461 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;consecutive_fails&quot;: t.stats.consecutive_fails,</code> | 字段 <code>consecutive_fails</code>（当前映射中的键）：读取 <code>t.stats.consecutive_fails</code>。 |
| L462 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;circuit_state&quot;: t.breaker.state.value,</code> | 字段 <code>circuit_state</code>（当前映射中的键）：读取 <code>t.breaker.state.value</code>。 |
| L463 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L464 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for name, t in self._tools.items()</code> | 续接 L456 的表达式：按前述语句组装参数、条件或集合。 |
| L465 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |

## 结合全项目：设计缺口与增强方向

- 仓库未实现 MCP 协议的会话、握手、传输或 tools/list、tools/call 端点；当前是 MCP 风格的进程内工具治理，Agent 也没有 tool_use 循环。
- HALF_OPEN 注释说一次探测，但 allow 在此状态始终 True；并发请求全部可通过，应增加探测令牌/锁。
- 超时只包 handler，不包查询改写、重排或 fallback；to_thread 超时取消等待不保证底层线程停止。
- 去重 MD5(str(item)) 包括 query 相关的 score；同一片段不同分数保留多份，应按稳定 chunk_id 去重。
- fallback 返回 success=True；search_with_rewrite 合并后不传播降级原因，API 可能把故障提示标为 knowledge_used=True。reranked=True 也不证明模型重排成功。
- 缓存 key 没有 context/租户/权限/知识版本，当前共享公共知识库可工作，扩展私有工具会串缓存；导入文档后旧检索可能保留 300 秒。use_cache=False 只禁止读，仍会写。
- 校验只支持顶层 required/type；bool 是 int 子类可通过 integer 校验，没有 minimum/items/additionalProperties。参数错误也累计工具失败并触发熔断。
- 工具延迟统计仅累积成功 handler 耗时，失败耗时不记；缓存增加总数但不加延迟；查询改写/重排不计入此统计。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
