# monitor/performance_monitor.py 解读

## 输入、输出与流向

**定位：** 周期读取累计统计，做异常提示、规则告警并反馈实例降权。

**输入：** Orchestrator.get_stats、ToolManager.get_stats；采集周期、可选 webhook/Prometheus 端口。

**输出 / 副作用：** summary JSON、日志、可选 webhook、Prometheus 注册表；副作用：Agent monitor_penalty、内存告警/建议。

**流向：** start→后台 _loop→_collect→Z-score/阈值→指标与建议→update_routing_penalties；API /monitor 与 /metrics 读取。

[返回阅读入口](../../README.md) · [对照原文件](../../../monitor/performance_monitor.py)

当前工作区快照：317 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`40f0068eed4386efa591717915a7c8f68bf5d53c7d166c88d95d066290aa3d62`。

## 类与函数导航

[Severity](#symbol-32) → [Alert](#symbol-39) → [Suggestion](#symbol-50) → [AnomalyDetector](#symbol-61) → [AnomalyDetector.__init__](#symbol-69) → [AnomalyDetector.record](#symbol-74) → [PerformanceMonitor](#symbol-101) → [PerformanceMonitor.__init__](#symbol-121) → [PerformanceMonitor._setup_prometheus](#symbol-145) → [PerformanceMonitor.start](#symbol-157) → [PerformanceMonitor.stop](#symbol-164) → [PerformanceMonitor._loop](#symbol-175) → [PerformanceMonitor._collect](#symbol-183) → [PerformanceMonitor._routing_penalty](#symbol-243) → [PerformanceMonitor._check_threshold](#symbol-253) → [PerformanceMonitor._generate_routing_suggestions](#symbol-273) → [PerformanceMonitor._add_suggestion](#symbol-292) → [PerformanceMonitor._send_webhook](#symbol-298) → [PerformanceMonitor.summary](#symbol-307)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>亮点：利用 Monitor 监控 Agent 在线表现</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>核心问题：如何利用 Monitor 监控 Agent 的在线表现？</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | （空行） | 空行，分隔逻辑。 |
| L6 | <code>本模块的答案：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;1. 实时采集 —— 每隔 N 秒从 Orchestrator 和 ToolManager 拉取最新统计</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L8 | <code>&nbsp;&nbsp;2. 异常检测 —— Z-score 统计方法，自动发现指标突变</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L9 | <code>&nbsp;&nbsp;3. 路由反馈 —— 将 Agent 成功率/延迟写回 Orchestrator，</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Orchestrator 的 _best_agent() 会据此动态调整路由权重</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L11 | <code>&nbsp;&nbsp;4. 优化建议 —— 基于规则生成可操作的优化建议（不是空话）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L12 | <code>&nbsp;&nbsp;5. 告警 —— 超阈值时打日志 + 可选 Webhook</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L13 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L14 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L15 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L16 | <code>import statistics</code> | 导入 <code>import statistics</code>；只建立名称依赖，真正业务调用见后文。 |
| L17 | <code>import time</code> | 导入 <code>import time</code>；只建立名称依赖，真正业务调用见后文。 |
| L18 | <code>from collections import defaultdict, deque</code> | 导入 <code>from collections import defaultdict, deque</code>；只建立名称依赖，真正业务调用见后文。 |
| L19 | <code>from dataclasses import asdict, dataclass, field</code> | 导入 <code>from dataclasses import asdict, dataclass, field</code>；只建立名称依赖，真正业务调用见后文。 |
| L20 | <code>from datetime import datetime</code> | 导入 <code>from datetime import datetime</code>；只建立名称依赖，真正业务调用见后文。 |
| L21 | <code>from enum import Enum</code> | 导入 <code>from enum import Enum</code>；只建立名称依赖，真正业务调用见后文。 |
| L22 | <code>from typing import Any, Deque, Dict, List, Optional</code> | 导入 <code>from typing import Any, Deque, Dict, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L23 | （空行） | 空行，分隔逻辑。 |
| L24 | <code>import httpx</code> | 导入 <code>import httpx</code>；只建立名称依赖，真正业务调用见后文。 |
| L25 | <code>from prometheus_client import Counter, Gauge, Histogram, start_http_server</code> | 导入 <code>from prometheus_client import Counter, Gauge, Histogram, start_http_server</code>；只建立名称依赖，真正业务调用见后文。 |
| L26 | （空行） | 空行，分隔逻辑。 |
| L27 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L28 | （空行） | 空行，分隔逻辑。 |
| L29 | （空行） | 空行，分隔逻辑。 |
| L30 | <code># ── 数据结构 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 数据结构 ────────────────────────────────────────────────────────────────── |
| L31 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-32"></a>

### L32–L36 · Severity

普通 Enum 表示等级；FastAPI 返回可能由其编码器处理，但 httpx json 参数用普通 JSON 编码，两条路径不同。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L32 | <code>class Severity(Enum):</code> | 定义 <code>Severity</code> 的数据契约/行为；继承与字段见本段。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;INFO     = &quot;info&quot;</code> | 将结果保存到 <code>INFO</code>：使用固定文本/配置值。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;WARNING  = &quot;warning&quot;</code> | 将结果保存到 <code>WARNING</code>：使用固定文本/配置值。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ERROR    = &quot;error&quot;</code> | 将结果保存到 <code>ERROR</code>：使用固定文本/配置值。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;CRITICAL = &quot;critical&quot;</code> | 将结果保存到 <code>CRITICAL</code>：使用固定文本/配置值。 |
| L37 | （空行） | 空行，分隔逻辑。 |
| L38 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-39"></a>

### L39–L47 · Alert

告警含等级、指标、数值、阈值、时间、resolved；当前没有函数将 resolved 更新为 True。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L39 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L40 | <code>class Alert:</code> | 定义 <code>Alert</code> 的数据契约/行为；继承与字段见本段。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;severity:    Severity</code> | 声明字段 <code>severity</code> 的类型，赋值由构造方完成。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;metric:      str</code> | 声明字段 <code>metric</code> 的类型，赋值由构造方完成。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;message:     str</code> | 声明字段 <code>message</code> 的类型，赋值由构造方完成。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;value:       float</code> | 声明字段 <code>value</code> 的类型，赋值由构造方完成。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;threshold:   float</code> | 声明字段 <code>threshold</code> 的类型，赋值由构造方完成。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ts:          str = field(default_factory=lambda: datetime.now().isoformat())</code> | 将结果保存到 <code>ts</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;resolved:    bool = False</code> | 将结果保存到 <code>resolved</code>：使用这里写明的固定值。 |
| L48 | （空行） | 空行，分隔逻辑。 |
| L49 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-50"></a>

### L50–L56 · Suggestion

规则生成的优化文字与优先级，不是可执行修复任务。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L50 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L51 | <code>class Suggestion:</code> | 定义 <code>Suggestion</code> 的数据契约/行为；继承与字段见本段。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;可操作的优化建议。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;title:       str</code> | 声明字段 <code>title</code> 的类型，赋值由构造方完成。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;detail:      str</code> | 声明字段 <code>detail</code> 的类型，赋值由构造方完成。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;action:      str    # 具体操作步骤</code> | 声明字段 <code>action</code> 的类型，赋值由构造方完成。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;priority:    int    # 1-10</code> | 声明字段 <code>priority</code> 的类型，赋值由构造方完成。 |
| L57 | （空行） | 空行，分隔逻辑。 |
| L58 | （空行） | 空行，分隔逻辑。 |
| L59 | <code># ── 异常检测 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 异常检测 ────────────────────────────────────────────────────────────────── |
| L60 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-61"></a>

### L61–L96 · AnomalyDetector

周期读取累计统计，做异常提示、规则告警并反馈实例降权。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L61 | <code>class AnomalyDetector:</code> | 定义 <code>AnomalyDetector</code> 的数据契约/行为；继承与字段见本段。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;基于滑动窗口 Z-score 的异常检测。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L64 | （空行） | 空行，分隔逻辑。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Z-score = &#124;当前值 - 均值&#124; / 标准差</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;超过 sensitivity 倍标准差则判定为异常。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L68 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-69"></a>

### L69–L72 · AnomalyDetector.__init__

每个指标维护最多 60 个采样点，灵敏度默认 2.5，deque 自动丢最旧样本。

**签名输入：** <code>self, window: int=60, sensitivity: float=2.5</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, window: int = 60, sensitivity: float = 2.5):</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._window      = window</code> | 将结果保存到 <code>self._window</code>：读取 <code>window</code>。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._sensitivity = sensitivity</code> | 将结果保存到 <code>self._sensitivity</code>：读取 <code>sensitivity</code>。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=window))</code> | 将结果保存到 <code>self._history</code>：调用 <code>defaultdict</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L73 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-74"></a>

### L74–L96 · AnomalyDetector.record

至少半窗口=30 个点才检测，用样本标准差计算双侧 Z 分数。成功率升高或延迟下降也可能被判“异常”。

**签名输入：** <code>self, metric: str, value: float</code>；**返回契约：** <code>Optional[Dict[str, Any]]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def record(self, metric: str, value: float) -&gt; Optional[Dict[str, Any]]:</code> | 定义函数 <code>record</code>；输入参数见签名，下方导读解释调用目的。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;记录一个数据点，如果异常则返回异常信息，否则返回 None。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buf = self._history[metric]</code> | 将结果保存到 <code>buf</code>：按索引/切片取 <code>self._history[metric]</code>，注意是否截掉旧历史或长文本。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;buf.append(value)</code> | **关键：**当前值先进入基线窗口，再用同一窗口评估当前点。 |
| L78 | （空行） | 空行，分隔逻辑。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(buf) &lt; self._window // 2:</code> | 判断 <code>len(buf) &lt; self._window // 2</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None  # 数据不足，不检测</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L81 | （空行） | 空行，分隔逻辑。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mean  = statistics.mean(buf)</code> | 将结果保存到 <code>mean</code>：计算算术平均。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stdev = statistics.stdev(buf) if len(buf) &gt; 1 else 0.0</code> | 将结果保存到 <code>stdev</code>：条件 <code>len(buf) &gt; 1</code> 成立选前值，否则选 else 后值。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if stdev == 0:</code> | 判断 <code>stdev == 0</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L86 | （空行） | 空行，分隔逻辑。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;z = abs(value - mean) / stdev</code> | 将结果保存到 <code>z</code>：按此表达式计算 <code>abs(value - mean) / stdev</code>。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if z &gt; self._sensitivity:</code> | 判断 <code>z &gt; self._sensitivity</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metric&quot;:   metric,</code> | 字段 <code>metric</code>（当前映射中的键）：读取 <code>metric</code>。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;value&quot;:    value,</code> | 字段 <code>value</code>（当前映射中的键）：读取 <code>value</code>。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;mean&quot;:     mean,</code> | 字段 <code>mean</code>（当前映射中的键）：读取 <code>mean</code>。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;z_score&quot;:  round(z, 2),</code> | 字段 <code>z_score</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;severity&quot;: &quot;high&quot; if z &gt; self._sensitivity * 1.5 else &quot;medium&quot;,</code> | 字段 <code>severity</code>（当前映射中的键）：条件 <code>z &gt; self._sensitivity * 1.5</code> 成立选前值，否则选 else 后值。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L97 | （空行） | 空行，分隔逻辑。 |
| L98 | （空行） | 空行，分隔逻辑。 |
| L99 | <code># ── 性能监控器 ────────────────────────────────────────────────────────────────</code> | 源码注释：── 性能监控器 ──────────────────────────────────────────────────────────────── |
| L100 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-101"></a>

### L101–L317 · PerformanceMonitor

周期读取累计统计，做异常提示、规则告警并反馈实例降权。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L101 | <code>class PerformanceMonitor:</code> | 定义 <code>PerformanceMonitor</code> 的数据契约/行为；继承与字段见本段。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;Agent 在线表现监控。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L104 | （空行） | 空行，分隔逻辑。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;与 Orchestrator 的联动：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Monitor 采集 → 发现某 Agent 成功率下降 →</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Orchestrator.get_stats() 中该 Agent 的 routing_score 自动降低 →</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_best_agent() 路由时自动绕开该 Agent</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L109 | （空行） | 空行，分隔逻辑。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;这就是&quot;利用 Monitor 监控在线表现&quot;的闭环。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L112 | （空行） | 空行，分隔逻辑。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 告警阈值</code> | 源码注释：告警阈值 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;THRESHOLDS = {</code> | 将结果保存到 <code>THRESHOLDS</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_success_rate&quot;:  (0.90, Severity.ERROR,   &quot;less_than&quot;),</code> | 字段 <code>agent_success_rate</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;tool_success_rate&quot;:   (0.95, Severity.WARNING,  &quot;less_than&quot;),</code> | 字段 <code>tool_success_rate</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_avg_ms&quot;:        (3000, Severity.WARNING,  &quot;greater_than&quot;),</code> | 字段 <code>agent_avg_ms</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;tool_avg_ms&quot;:         (5000, Severity.ERROR,    &quot;greater_than&quot;),</code> | 字段 <code>tool_avg_ms</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L120 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-121"></a>

### L121–L143 · PerformanceMonitor.__init__

存组件引用和配置，只有配置 prometheus_port 时才创建指标并开端口。

**签名输入：** <code>self, orchestrator, tool_manager, interval_s: float=10.0, webhook_url: Optional[str]=None, prometheus_port: Optional[int]=None</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;orchestrator,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool_manager,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval_s:       float = 10.0,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;webhook_url:      Optional[str] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prometheus_port:  Optional[int] = None,   # None = 不启动</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._orchestrator = orchestrator</code> | 将结果保存到 <code>self._orchestrator</code>：读取 <code>orchestrator</code>。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._tool_manager = tool_manager</code> | 将结果保存到 <code>self._tool_manager</code>：读取 <code>tool_manager</code>。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._interval     = interval_s</code> | 将结果保存到 <code>self._interval</code>：读取 <code>interval_s</code>。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._webhook      = webhook_url</code> | 将结果保存到 <code>self._webhook</code>：读取 <code>webhook_url</code>。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._detector     = AnomalyDetector()</code> | 将结果保存到 <code>self._detector</code>：调用 <code>AnomalyDetector</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L134 | （空行） | 空行，分隔逻辑。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._alerts:      List[Alert]      = []</code> | 将结果保存到 <code>self._alerts</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._suggestions: List[Suggestion] = []</code> | 将结果保存到 <code>self._suggestions</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._active       = False</code> | 将结果保存到 <code>self._active</code>：使用这里写明的固定值。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._task:        Optional[asyncio.Task] = None</code> | 将结果保存到 <code>self._task</code>：使用这里写明的固定值。 |
| L139 | （空行） | 空行，分隔逻辑。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Prometheus 指标（可选）</code> | 源码注释：Prometheus 指标（可选） |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._prom: Dict[str, Any] = {}</code> | 将结果保存到 <code>self._prom</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if prometheus_port:</code> | 判断 <code>prometheus_port</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._setup_prometheus(prometheus_port)</code> | 进入 <code>self._setup_prometheus</code>：注册带 agent/tool 标签的 Gauge/Histogram 及总计 Counter，再启动独立 HTTP 指标服务；主 FastAPI /metrics 读同一注册表。 |
| L144 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-145"></a>

### L145–L153 · PerformanceMonitor._setup_prometheus

注册带 agent/tool 标签的 Gauge/Histogram 及总计 Counter，再启动独立 HTTP 指标服务；主 FastAPI /metrics 读同一注册表。

**签名输入：** <code>self, port: int</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _setup_prometheus(self, port: int) -&gt; None:</code> | 定义函数 <code>_setup_prometheus</code>；输入参数见签名，下方导读解释调用目的。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._prom = {</code> | 将结果保存到 <code>self._prom</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_success_rate&quot;: Gauge(&quot;agent_success_rate&quot;, &quot;Agent 成功率&quot;, [&quot;agent&quot;]),</code> | 字段 <code>agent_success_rate</code>（当前映射中的键）：调用 <code>Gauge</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_latency_ms&quot;:   Histogram(&quot;agent_latency_ms&quot;, &quot;Agent 延迟&quot;, [&quot;agent&quot;]),</code> | **关键：**未定制毫秒桶，且 observe 传的是累计均值；不要将此 histogram 用作真实 P95。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;tool_success_rate&quot;:  Gauge(&quot;tool_success_rate&quot;, &quot;工具成功率&quot;, [&quot;tool&quot;]),</code> | 字段 <code>tool_success_rate</code>（当前映射中的键）：调用 <code>Gauge</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;requests_total&quot;:     Counter(&quot;requests_total&quot;, &quot;总请求数&quot;),</code> | **关键：**Counter 创建了但本文件没有任何 inc 调用。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;start_http_server(port)</code> | 调用 <code>start_http_server</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;Prometheus 已启动: :{port}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L154 | （空行） | 空行，分隔逻辑。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 生命周期 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 生命周期 ────────────────────────────────────────────────────────────── |
| L156 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-157"></a>

### L157–L162 · PerformanceMonitor.start

幂等开关防止重复建采集 task；create_task 后不等待循环结束。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def start(self) -&gt; None:</code> | 定义异步函数 <code>start</code>；输入参数见签名，下方导读解释调用目的。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._active:</code> | 判断 <code>self._active</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | 结束当前函数并返回；无返回值。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._active = True</code> | 将结果保存到 <code>self._active</code>：使用这里写明的固定值。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._task   = asyncio.create_task(self._loop())</code> | 将结果保存到 <code>self._task</code>：将协程安排为后台任务，当前行不等待业务完成。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;Monitor 已启动，采集间隔 {self._interval}s&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L163 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-164"></a>

### L164–L171 · PerformanceMonitor.stop

取消 task 并 await，吞掉预期 CancelledError 完成退出。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def stop(self) -&gt; None:</code> | 定义异步函数 <code>stop</code>；输入参数见签名，下方导读解释调用目的。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._active = False</code> | 将结果保存到 <code>self._active</code>：使用这里写明的固定值。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._task:</code> | 判断 <code>self._task</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._task.cancel()</code> | 调用 <code>self._task.cancel</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._task</code> | 等待完成后继续；读取 <code>self._task</code>。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except asyncio.CancelledError:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pass</code> | 有意不处理；异常分支可能因此丢失错误信号。 |
| L172 | （空行） | 空行，分隔逻辑。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 采集循环 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 采集循环 ────────────────────────────────────────────────────────────── |
| L174 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-175"></a>

### L175–L181 · PerformanceMonitor._loop

每次 collect 完成后 sleep interval，实际两次起点间隔=采集耗时+配置间隔。异常只记日志继续。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _loop(self) -&gt; None:</code> | 定义异步函数 <code>_loop</code>；输入参数见签名，下方导读解释调用目的。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;while self._active:</code> | 条件 <code>self._active</code> 保持成立时重复循环。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._collect()</code> | 等待完成后继续；进入 <code>self._collect</code>：读取统计快照，Agent 做异常和阈值检测，工具做阈值与连续失败建议；最后将 penalty 写回编排器。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.error(f&quot;Monitor 采集异常: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await asyncio.sleep(self._interval)</code> | 等待完成后继续；调用 <code>asyncio.sleep</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L182 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-183"></a>

### L183–L241 · PerformanceMonitor._collect

读取统计快照，Agent 做异常和阈值检测，工具做阈值与连续失败建议；最后将 penalty 写回编排器。没有读取评测报告质量分。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _collect(self) -&gt; None:</code> | 定义异步函数 <code>_collect</code>；输入参数见签名，下方导读解释调用目的。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;采集 Agent 和工具的实时统计，检测异常，生成建议。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L186 | （空行） | 空行，分隔逻辑。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;关键：这里读取的 stats 就是 Orchestrator/ToolManager 在处理请求时</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;实时更新的数据，Monitor 不需要额外埋点。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_stats = self._orchestrator.get_stats()</code> | 将结果保存到 <code>agent_stats</code>：调用 <code>self._orchestrator.get_stats</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool_stats  = self._tool_manager.get_stats()</code> | 将结果保存到 <code>tool_stats</code>：调用 <code>self._tool_manager.get_stats</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_penalties: Dict[str, float] = {}</code> | 将结果保存到 <code>routing_penalties</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L193 | （空行） | 空行，分隔逻辑。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# ── Agent 指标 ────────────────────────────────────────────────────────</code> | 源码注释：── Agent 指标 ──────────────────────────────────────────────────────── |
| L195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent_key, s in agent_stats.items():</code> | 遍历 <code>agent_stats.items()</code>，本轮元素绑定 <code>(agent_key, s)</code>。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sr  = s[&quot;success_rate&quot;]</code> | 将结果保存到 <code>sr</code>：按索引/切片取 <code>s[&#x27;success_rate&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ms  = s[&quot;avg_ms&quot;]</code> | 将结果保存到 <code>ms</code>：按索引/切片取 <code>s[&#x27;avg_ms&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L198 | （空行） | 空行，分隔逻辑。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 异常检测</code> | 源码注释：异常检测 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for metric, value in [(&quot;agent_success_rate&quot;, sr), (&quot;agent_avg_ms&quot;, ms)]:</code> | 遍历 <code>[(&#x27;agent_success_rate&#x27;, sr), (&#x27;agent_avg_ms&#x27;, ms)]</code>，本轮元素绑定 <code>(metric, value)</code>。 |
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;anomaly = self._detector.record(f&quot;{metric}:{agent_key}&quot;, value)</code> | 将结果保存到 <code>anomaly</code>：进入 <code>self._detector.record</code>：至少半窗口=30 个点才检测，用样本标准差计算双侧 Z 分数。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if anomaly:</code> | 判断 <code>anomaly</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;异常检测 [{agent_key}] {metric}={value:.3f} z={anomaly[&#x27;z_score&#x27;]}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L204 | （空行） | 空行，分隔逻辑。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 阈值告警</code> | 源码注释：阈值告警 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._check_threshold(&quot;agent_success_rate&quot;, sr, agent_key)</code> | 进入 <code>self._check_threshold</code>：根据 less_than/greater_than 判定，每次命中创建新 Alert，并可调度 webhook 后台任务。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._check_threshold(&quot;agent_avg_ms&quot;, ms, agent_key)</code> | 进入 <code>self._check_threshold</code>：根据 less_than/greater_than 判定，每次命中创建新 Alert，并可调度 webhook 后台任务。 |
| L208 | （空行） | 空行，分隔逻辑。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Prometheus</code> | 源码注释：Prometheus |
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if &quot;agent_success_rate&quot; in self._prom:</code> | 判断 <code>&#x27;agent_success_rate&#x27; in self._prom</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._prom[&quot;agent_success_rate&quot;].labels(agent=agent_key).set(sr)</code> | 调用 <code>self._prom[&#x27;agent_success_rate&#x27;].labels(agent=agent_key).set</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._prom[&quot;agent_latency_ms&quot;].labels(agent=agent_key).observe(ms)</code> | **关键：**每轮重复观测累计 avg_ms，不是记录新请求延迟。 |
| L213 | （空行） | 空行，分隔逻辑。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_penalties[agent_key] = self._routing_penalty(sr, ms)</code> | 将结果保存到 <code>routing_penalties[agent_key]</code>：进入 <code>self._routing_penalty</code>：sr<.9 加最多 .5；avg>3000ms 加最多 .4；上限 .9。 |
| L215 | （空行） | 空行，分隔逻辑。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# ── 工具指标 ──────────────────────────────────────────────────────────</code> | 源码注释：── 工具指标 ────────────────────────────────────────────────────────── |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for tool_name, s in tool_stats.items():</code> | 遍历 <code>tool_stats.items()</code>，本轮元素绑定 <code>(tool_name, s)</code>。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sr = s[&quot;success_rate&quot;]</code> | 将结果保存到 <code>sr</code>：按索引/切片取 <code>s[&#x27;success_rate&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ms = s[&quot;avg_latency_ms&quot;]</code> | 将结果保存到 <code>ms</code>：按索引/切片取 <code>s[&#x27;avg_latency_ms&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cf = s[&quot;consecutive_fails&quot;]</code> | 将结果保存到 <code>cf</code>：按索引/切片取 <code>s[&#x27;consecutive_fails&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L221 | （空行） | 空行，分隔逻辑。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._check_threshold(&quot;tool_success_rate&quot;, sr, tool_name)</code> | 进入 <code>self._check_threshold</code>：根据 less_than/greater_than 判定，每次命中创建新 Alert，并可调度 webhook 后台任务。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._check_threshold(&quot;tool_avg_ms&quot;, ms, tool_name)</code> | 进入 <code>self._check_threshold</code>：根据 less_than/greater_than 判定，每次命中创建新 Alert，并可调度 webhook 后台任务。 |
| L224 | （空行） | 空行，分隔逻辑。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if &quot;tool_success_rate&quot; in self._prom:</code> | 判断 <code>&#x27;tool_success_rate&#x27; in self._prom</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._prom[&quot;tool_success_rate&quot;].labels(tool=tool_name).set(sr)</code> | 调用 <code>self._prom[&#x27;tool_success_rate&#x27;].labels(tool=tool_name).set</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L227 | （空行） | 空行，分隔逻辑。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 连续失败 → 生成具体建议</code> | 源码注释：连续失败 → 生成具体建议 |
| L229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if cf &gt;= 3:</code> | 判断 <code>cf &gt;= 3</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._add_suggestion(Suggestion(</code> | 进入 <code>self._add_suggestion</code>：按完全相同 title 去重；含不断变化失败次数的 title 仍会新增。 |
| L231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;title=f&quot;工具 {tool_name} 连续失败 {cf} 次&quot;,</code> | 参数 <code>title</code>（展示标题）：将变量插入模板，构造提示词、标识或可读说明。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detail=f&quot;成功率 {sr:.1%}，平均延迟 {ms:.0f}ms，熔断状态: {s[&#x27;circuit_state&#x27;]}&quot;,</code> | 参数 <code>detail</code>（detail）：将变量插入模板，构造提示词、标识或可读说明。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action=&quot;1. 检查工具依赖服务是否正常\n2. 查看错误日志\n3. 考虑增加超时时间或降级策略&quot;,</code> | 参数 <code>action</code>（action）：使用固定文本/配置值。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;priority=9,</code> | 参数 <code>priority</code>（priority）：使用这里写明的固定值。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L236 | （空行） | 空行，分隔逻辑。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# ── 路由优化建议 ──────────────────────────────────────────────────────</code> | 源码注释：── 路由优化建议 ────────────────────────────────────────────────────── |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;updater = getattr(self._orchestrator, &quot;update_routing_penalties&quot;, None)</code> | 将结果保存到 <code>updater</code>：读取对象指定属性，不存在时返回这里给出的默认值。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if updater:</code> | 判断 <code>updater</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;updater(routing_penalties)</code> | **关键：**真实反馈写入编排器，但只有同类多个实例才有选择空间。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._generate_routing_suggestions(agent_stats)</code> | 进入 <code>self._generate_routing_suggestions</code>：样本总量>10 且成功率<.85 才提出 Agent 优化建议，文字提示检查 prompt/扩容。 |
| L242 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-243"></a>

### L243–L251 · PerformanceMonitor._routing_penalty

sr<.9 加最多 .5；avg>3000ms 加最多 .4；上限 .9。固定启发式，不是学习所得反馈策略。

**签名输入：** <code>success_rate: float, avg_ms: float</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _routing_penalty(success_rate: float, avg_ms: float) -&gt; float:</code> | 定义函数 <code>_routing_penalty</code>；输入参数见签名，下方导读解释调用目的。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;把在线表现转成 0-0.9 的路由降权系数。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;penalty = 0.0</code> | 将结果保存到 <code>penalty</code>：使用这里写明的固定值。 |
| L247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if success_rate &lt; 0.90:</code> | 判断 <code>success_rate &lt; 0.9</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;penalty += min(0.5, (0.90 - success_rate) * 2)</code> | 更新 <code>penalty</code>：<code>penalty += min(0.5, (0.9 - success_rate) * 2)</code>；此处会改变累计状态。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if avg_ms &gt; 3000:</code> | 判断 <code>avg_ms &gt; 3000</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;penalty += min(0.4, (avg_ms - 3000) / 10000)</code> | 更新 <code>penalty</code>：<code>penalty += min(0.4, (avg_ms - 3000) / 10000)</code>；此处会改变累计状态。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return min(penalty, 0.9)</code> | 结束当前函数并返回；取上界/限制后的较小值。 |
| L252 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-253"></a>

### L253–L271 · PerformanceMonitor._check_threshold

根据 less_than/greater_than 判定，每次命中创建新 Alert，并可调度 webhook 后台任务。

**签名输入：** <code>self, metric: str, value: float, label: str</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _check_threshold(self, metric: str, value: float, label: str) -&gt; None:</code> | 定义函数 <code>_check_threshold</code>；输入参数见签名，下方导读解释调用目的。 |
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if metric not in self.THRESHOLDS:</code> | 判断 <code>metric not in self.THRESHOLDS</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | 结束当前函数并返回；无返回值。 |
| L256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;threshold, severity, operator = self.THRESHOLDS[metric]</code> | 将结果保存到 <code>(threshold, severity, operator)</code>：按索引/切片取 <code>self.THRESHOLDS[metric]</code>，注意是否截掉旧历史或长文本。 |
| L257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;triggered = (operator == &quot;less_than&quot; and value &lt; threshold) or \</code> | 将结果保存到 <code>triggered</code>：读取 <code>operator == &#x27;less_than&#x27; and value &lt; threshold or (operator == &#x27;greater_than&#x27; and value &gt; threshold)</code>。 |
| L258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(operator == &quot;greater_than&quot; and value &gt; threshold)</code> | 续接 L257 的表达式：按前述语句组装参数、条件或集合。 |
| L259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if triggered:</code> | 判断 <code>triggered</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;alert = Alert(</code> | 将结果保存到 <code>alert</code>：进入 <code>Alert</code>：告警含等级、指标、数值、阈值、时间、resolved；当前没有函数将 resolved 更新为 True。 |
| L261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;severity=severity,</code> | 参数 <code>severity</code>（severity）：读取 <code>severity</code>。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metric=f&quot;{metric}:{label}&quot;,</code> | 参数 <code>metric</code>（metric）：将变量插入模板，构造提示词、标识或可读说明。 |
| L263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message=f&quot;{label} 的 {metric} = {value:.3f}，阈值 {threshold}&quot;,</code> | 参数 <code>message</code>（本轮用户消息）：将变量插入模板，构造提示词、标识或可读说明。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value=value,</code> | 参数 <code>value</code>（value）：读取 <code>value</code>。 |
| L265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;threshold=threshold,</code> | 参数 <code>threshold</code>（threshold）：读取 <code>threshold</code>。 |
| L266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._alerts.append(alert)</code> | 追加一个元素到当前列表。 |
| L268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;[{severity.value.upper()}] {alert.message}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 异步发送 Webhook（不阻塞采集循环）</code> | 源码注释：异步发送 Webhook（不阻塞采集循环） |
| L270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._webhook:</code> | 判断 <code>self._webhook</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;asyncio.create_task(self._send_webhook(alert))</code> | 将协程安排为后台任务，当前行不等待业务完成。 |
| L272 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-273"></a>

### L273–L290 · PerformanceMonitor._generate_routing_suggestions

样本总量>10 且成功率<.85 才提出 Agent 优化建议，文字提示检查 prompt/扩容。

**签名输入：** <code>self, agent_stats: Dict[str, Any]</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _generate_routing_suggestions(self, agent_stats: Dict[str, Any]) -&gt; None:</code> | 定义函数 <code>_generate_routing_suggestions</code>；输入参数见签名，下方导读解释调用目的。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;基于 Agent 在线表现生成路由优化建议。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;这是 Monitor → Orchestrator 反馈闭环的体现。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for agent_key, s in agent_stats.items():</code> | 遍历 <code>agent_stats.items()</code>，本轮元素绑定 <code>(agent_key, s)</code>。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if s[&quot;success_rate&quot;] &lt; 0.85 and s[&quot;total&quot;] &gt; 10:</code> | 判断 <code>s[&#x27;success_rate&#x27;] &lt; 0.85 and s[&#x27;total&#x27;] &gt; 10</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._add_suggestion(Suggestion(</code> | 进入 <code>self._add_suggestion</code>：按完全相同 title 去重；含不断变化失败次数的 title 仍会新增。 |
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;title=f&quot;Agent {agent_key} 成功率偏低&quot;,</code> | 参数 <code>title</code>（展示标题）：将变量插入模板，构造提示词、标识或可读说明。 |
| L282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detail=f&quot;成功率 {s[&#x27;success_rate&#x27;]:.1%}，路由评分 {s[&#x27;routing_score&#x27;]:.3f}&quot;,</code> | 参数 <code>detail</code>（detail）：将变量插入模板，构造提示词、标识或可读说明。 |
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action=(</code> | 参数 <code>action</code>（action）：使用固定文本/配置值。 |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;Orchestrator 的 _best_agent() 已自动降低该 Agent 的路由权重。\n&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;建议：1. 检查 system_prompt 是否需要优化\n&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;      2. 检查该类型问题的复杂度是否超出 Agent 能力\n&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;      3. 考虑增加同类型 Agent 实例&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;),</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;priority=8,</code> | 参数 <code>priority</code>（priority）：使用这里写明的固定值。 |
| L290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L291 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-292"></a>

### L292–L296 · PerformanceMonitor._add_suggestion

按完全相同 title 去重；含不断变化失败次数的 title 仍会新增。

**签名输入：** <code>self, s: Suggestion</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _add_suggestion(self, s: Suggestion) -&gt; None:</code> | 定义函数 <code>_add_suggestion</code>；输入参数见签名，下方导读解释调用目的。 |
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 去重：相同 title 不重复添加</code> | 源码注释：去重：相同 title 不重复添加 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not any(x.title == s.title for x in self._suggestions):</code> | 判断 <code>not any((x.title == s.title for x in self._suggestions))</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._suggestions.append(s)</code> | 追加一个元素到当前列表。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;优化建议 [P{s.priority}]: {s.title}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L297 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-298"></a>

### L298–L303 · PerformanceMonitor._send_webhook

5 秒 HTTP 超时，每次新建客户端。asdict 不会把 Enum 转 value；也未检查返回 HTTP 状态是否成功。

**签名输入：** <code>self, alert: Alert</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _send_webhook(self, alert: Alert) -&gt; None:</code> | 定义异步函数 <code>_send_webhook</code>；输入参数见签名，下方导读解释调用目的。 |
| L299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;async with httpx.AsyncClient(timeout=5.0) as c:</code> | 在上下文管理器生命周期内使用资源，退出时清理。 |
| L301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await c.post(self._webhook, json=asdict(alert))  # type: ignore</code> | **关键：**asdict(alert) 保留 Severity 对象，标准 JSON 序列化会失败。 |
| L302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.error(f&quot;Webhook 发送失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L304 | （空行） | 空行，分隔逻辑。 |
| L305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 查询接口 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 查询接口 ────────────────────────────────────────────────────────────── |
| L306 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-307"></a>

### L307–L317 · PerformanceMonitor.summary

返回实时统计、最近 10 个未解决告警、优先级前 5 个建议。只是展示截断，未清理底层列表。

**签名输入：** <code>self</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def summary(self) -&gt; Dict[str, Any]:</code> | 定义函数 <code>summary</code>；输入参数见签名，下方导读解释调用目的。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;返回当前监控摘要，供 API 层暴露。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_stats&quot;:   self._orchestrator.get_stats(),</code> | 字段 <code>agent_stats</code>（当前映射中的键）：调用 <code>self._orchestrator.get_stats</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;tool_stats&quot;:    self._tool_manager.get_stats(),</code> | 字段 <code>tool_stats</code>（当前映射中的键）：调用 <code>self._tool_manager.get_stats</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;active_alerts&quot;: [asdict(a) for a in self._alerts if not a.resolved][-10:],</code> | 字段 <code>active_alerts</code>（当前映射中的键）：按索引/切片取 <code>[asdict(a) for a in self._alerts if not a.resolved][-10:]</code>，注意是否截掉旧历史或长文本。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;suggestions&quot;:   [</code> | 字段 <code>suggestions</code>（当前映射中的键）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{&quot;title&quot;: s.title, &quot;action&quot;: s.action, &quot;priority&quot;: s.priority}</code> | 字段 <code>priority</code>（当前映射中的键）：读取 <code>s.priority</code>。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for s in sorted(self._suggestions, key=lambda x: -x.priority)[:5]</code> | 参数 <code>key</code>（key）：读取 <code>lambda x: -x.priority</code>。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;],</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |

## 结合全项目：设计缺口与增强方向

- 采样的是累计均值/成功率，不是逐请求数据。Histogram 每次 observe 累计平均毫秒，不能算真实请求 P95；默认桶也未按毫秒规模设计。requests_total 定义后没有 inc。
- 默认 PROMETHEUS_PORT=0 不注册业务指标，虽然 /metrics 始终可访问；注册业务指标与额外监听端口耦合。
- 告警每轮重复 append，没有解决状态更新、冷却或容量上限；只在返回时截最后 10 条，内存仍增长。
- webhook 用 json=asdict(alert)，其中 severity 是普通 Enum，标准 JSON 编码不能序列化；错误被捕获成日志，通知可能一直发不出去。
- Z-score 先把当前值放入窗口再算均值/标准差，异常点会影响自己的基准；没有采样量门槛、请求量或漂移基线。
- 反馈已真实写回，但每类单实例无法真正绕开差实例；建议不是自动改 prompt、扩容或模型训练。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
