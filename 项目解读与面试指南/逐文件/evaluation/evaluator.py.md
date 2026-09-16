# evaluation/evaluator.py 解读

## 输入、输出与流向

**定位：** 自动生成回答、分类对标和 LLM 质量评分的评测框架。

**输入：** IntentTestCase 标注消息；单轮 question 或多轮 turns；编排器/识别器/裁判模型；可选历史 baseline.json。

**输出 / 副作用：** EvalReport：通过率、四维均分、意图 accuracy、回归提示、逐例结果；副作用：调用模型、改变在线 Agent 统计、覆盖 baseline 文件。

**流向：** IntentEvaluator 逐例分类→accuracy/macro-F1；对话逐轮 Orchestrator.run→LLMJudge→记录历史；聚合→比上轮基线→建议→保存。

[返回阅读入口](../../README.md) · [对照原文件](../../../evaluation/evaluator.py)

当前工作区快照：501 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`0c320755e171987f49d42925c89326036201a49d5a93f073e1df4abb5bcfdc60`。

## 类与函数导航

[IntentTestCase](#symbol-37) → [QualityScores](#symbol-44) → [QualityScores.overall](#symbol-54) → [EvalResult](#symbol-59) → [EvalReport](#symbol-68) → [LLMJudge](#symbol-83) → [LLMJudge.__init__](#symbol-109) → [LLMJudge.judge](#symbol-113) → [LLMJudge._clean_text](#symbol-148) → [IntentEvaluator](#symbol-160) → [IntentEvaluator.__init__](#symbol-163) → [IntentEvaluator.evaluate](#symbol-166) → [EndToEndEvaluator](#symbol-213) → [EndToEndEvaluator.__init__](#symbol-227) → [EndToEndEvaluator.run](#symbol-248) → [EndToEndEvaluator._evaluate_dialog_case](#symbol-323) → [EndToEndEvaluator._dialog_turns](#symbol-380) → [EndToEndEvaluator._history_context](#symbol-388) → [EndToEndEvaluator._detect_regressions](#symbol-395) → [EndToEndEvaluator._recommendations](#symbol-411) → [EndToEndEvaluator.history](#symbol-429) → [EndToEndEvaluator._load_baseline](#symbol-433) → [EndToEndEvaluator._save_baseline](#symbol-443) → [EndToEndEvaluator._report_from_dict](#symbol-456)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>亮点：端到端 Agent 评测框架</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>核心问题：如何评测端到端 Agent？</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | （空行） | 空行，分隔逻辑。 |
| L6 | <code>评测维度：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;1. 意图识别准确率 —— 预测意图 vs 标注意图，计算 Accuracy / F1</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L8 | <code>&nbsp;&nbsp;2. 响应质量评分 —— 用 LLM 作为评判者（LLM-as-Judge），</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;从相关性、准确性、完整性、有用性四个维度打分</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L10 | <code>&nbsp;&nbsp;3. 端到端对话评测 —— 模拟完整多轮对话，评估整体体验</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L11 | <code>&nbsp;&nbsp;4. 回归测试 —— 与历史基线对比，防止性能退化</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L12 | （空行） | 空行，分隔逻辑。 |
| L13 | <code>LLM-as-Judge 是评测 Agent 质量的关键技术：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L14 | <code>&nbsp;&nbsp;人工标注成本高、主观性强；用 LLM 评判可以规模化、可重复。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L15 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L16 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L17 | <code>import json</code> | 导入 <code>import json</code>；只建立名称依赖，真正业务调用见后文。 |
| L18 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L19 | <code>import pathlib</code> | 导入 <code>import pathlib</code>；只建立名称依赖，真正业务调用见后文。 |
| L20 | <code>import statistics</code> | 导入 <code>import statistics</code>；只建立名称依赖，真正业务调用见后文。 |
| L21 | <code>import time</code> | 导入 <code>import time</code>；只建立名称依赖，真正业务调用见后文。 |
| L22 | <code>from dataclasses import asdict, dataclass, field</code> | 导入 <code>from dataclasses import asdict, dataclass, field</code>；只建立名称依赖，真正业务调用见后文。 |
| L23 | <code>from datetime import datetime</code> | 导入 <code>from datetime import datetime</code>；只建立名称依赖，真正业务调用见后文。 |
| L24 | <code>from typing import Any, Dict, List, Optional</code> | 导入 <code>from typing import Any, Dict, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L25 | （空行） | 空行，分隔逻辑。 |
| L26 | <code>from anthropic import AsyncAnthropic</code> | 导入 <code>from anthropic import AsyncAnthropic</code>；只建立名称依赖，真正业务调用见后文。 |
| L27 | （空行） | 空行，分隔逻辑。 |
| L28 | <code>from core.llm_utils import extract_text_content</code> | 导入 <code>from core.llm_utils import extract_text_content</code>；只建立名称依赖，真正业务调用见后文。 |
| L29 | （空行） | 空行，分隔逻辑。 |
| L30 | <code>from core.intent_recognizer import IntentCategory, IntentRecognizer</code> | 导入 <code>from core.intent_recognizer import IntentCategory, IntentRecognizer</code>；只建立名称依赖，真正业务调用见后文。 |
| L31 | （空行） | 空行，分隔逻辑。 |
| L32 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L33 | （空行） | 空行，分隔逻辑。 |
| L34 | （空行） | 空行，分隔逻辑。 |
| L35 | <code># ── 数据结构 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 数据结构 ────────────────────────────────────────────────────────────────── |
| L36 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-37"></a>

### L37–L41 · IntentTestCase

分类任务的 gold label 输入；context 是未被消费的字段。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L37 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L38 | <code>class IntentTestCase:</code> | 定义 <code>IntentTestCase</code> 的数据契约/行为；继承与字段见本段。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;message:          str</code> | 声明字段 <code>message</code> 的类型，赋值由构造方完成。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;expected_intent:  str</code> | 声明字段 <code>expected_intent</code> 的类型，赋值由构造方完成。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;context:          Optional[Dict[str, Any]] = None</code> | 将结果保存到 <code>context</code>：使用这里写明的固定值。 |
| L42 | （空行） | 空行，分隔逻辑。 |
| L43 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-44"></a>

### L44–L56 · QualityScores

四个维度各 .0–1.0 是 prompt 约定，Python dataclass 不强制范围；judge_failed/error 单独记录故障。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L44 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L45 | <code>class QualityScores:</code> | 定义 <code>QualityScores</code> 的数据契约/行为；继承与字段见本段。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;LLM-as-Judge 评分结果。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;relevance:    float   # 相关性：回答是否针对问题</code> | 声明字段 <code>relevance</code> 的类型，赋值由构造方完成。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;accuracy:     float   # 准确性：信息是否正确</code> | 声明字段 <code>accuracy</code> 的类型，赋值由构造方完成。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;completeness: float   # 完整性：是否完整解决问题</code> | 声明字段 <code>completeness</code> 的类型，赋值由构造方完成。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;helpfulness:  float   # 有用性：用户是否能据此行动</code> | 声明字段 <code>helpfulness</code> 的类型，赋值由构造方完成。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;judge_failed: bool = False</code> | 将结果保存到 <code>judge_failed</code>：使用这里写明的固定值。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;error: Optional[str] = None</code> | 将结果保存到 <code>error</code>：使用这里写明的固定值。 |
| L53 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-54"></a>

### L54–L56 · QualityScores.overall

四维等权算术平均，未按业务风险加权。

**签名输入：** <code>self</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def overall(self) -&gt; float:</code> | 定义函数 <code>overall</code>；输入参数见签名，下方导读解释调用目的。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return statistics.mean([self.relevance, self.accuracy, self.completeness, self.helpfulness])</code> | 结束当前函数并返回；计算算术平均。 |
| L57 | （空行） | 空行，分隔逻辑。 |
| L58 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-59"></a>

### L59–L65 · EvalResult

一个报告项，可能是一整组意图评测，也可能是一轮回答，计数口径不同。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L59 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L60 | <code>class EvalResult:</code> | 定义 <code>EvalResult</code> 的数据契约/行为；继承与字段见本段。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;test_id:    str</code> | 声明字段 <code>test_id</code> 的类型，赋值由构造方完成。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;passed:     bool</code> | 声明字段 <code>passed</code> 的类型，赋值由构造方完成。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;scores:     Dict[str, float]</code> | 声明字段 <code>scores</code> 的类型，赋值由构造方完成。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;detail:     str = &quot;&quot;</code> | 将结果保存到 <code>detail</code>：使用固定文本/配置值。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;metadata:   Dict[str, Any] = field(default_factory=dict)</code> | 将结果保存到 <code>metadata</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L66 | （空行） | 空行，分隔逻辑。 |
| L67 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-68"></a>

### L68–L78 · EvalReport

汇总快照加详细结果；持久化完整 report 作为下一次比较材料。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L68 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L69 | <code>class EvalReport:</code> | 定义 <code>EvalReport</code> 的数据契约/行为；继承与字段见本段。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;评测报告。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;timestamp:        str</code> | 声明字段 <code>timestamp</code> 的类型，赋值由构造方完成。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;total:            int</code> | 声明字段 <code>total</code> 的类型，赋值由构造方完成。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;passed:           int</code> | 声明字段 <code>passed</code> 的类型，赋值由构造方完成。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;pass_rate:        float</code> | 声明字段 <code>pass_rate</code> 的类型，赋值由构造方完成。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;avg_scores:       Dict[str, float]</code> | 声明字段 <code>avg_scores</code> 的类型，赋值由构造方完成。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;regressions:      List[str]          # 相比基线退化的指标</code> | 声明字段 <code>regressions</code> 的类型，赋值由构造方完成。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;recommendations:  List[str]</code> | 声明字段 <code>recommendations</code> 的类型，赋值由构造方完成。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;results:          List[EvalResult]</code> | 声明字段 <code>results</code> 的类型，赋值由构造方完成。 |
| L79 | （空行） | 空行，分隔逻辑。 |
| L80 | （空行） | 空行，分隔逻辑。 |
| L81 | <code># ── LLM-as-Judge ─────────────────────────────────────────────────────────────</code> | 源码注释：── LLM-as-Judge ───────────────────────────────────────────────────────────── |
| L82 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-83"></a>

### L83–L155 · LLMJudge

自动生成回答、分类对标和 LLM 质量评分的评测框架。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L83 | <code>class LLMJudge:</code> | 定义 <code>LLMJudge</code> 的数据契约/行为；继承与字段见本段。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;用 LLM 评判 Agent 响应质量。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L86 | （空行） | 空行，分隔逻辑。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;为什么用 LLM 而不是人工？</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;- 可规模化：数千条测试用例自动评测</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;- 可重复：相同输入得到稳定评分</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;- 多维度：同时评估相关性、准确性等多个维度</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L91 | （空行） | 空行，分隔逻辑。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;注意：LLM Judge 本身也有偏差，建议定期用人工标注校准。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L94 | （空行） | 空行，分隔逻辑。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;JUDGE_PROMPT = &quot;&quot;&quot;你是一个客服质量评估专家。请对以下客服响应进行评分。</code> | 将结果保存到 <code>JUDGE_PROMPT</code>：使用固定文本/配置值。 |
| L96 | （空行） | 空行，分隔逻辑。 |
| L97 | <code>用户问题: {question}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L98 | <code>Agent 响应: {response}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L99 | <code>{context_section}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L100 | （空行） | 空行，分隔逻辑。 |
| L101 | <code>请从以下四个维度评分（0.0-1.0），返回 JSON：</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L102 | <code>- relevance: 响应是否直接针对用户问题（0=完全无关，1=完全相关）</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L103 | <code>- accuracy: 信息是否准确无误（0=明显错误，1=完全正确）</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L104 | <code>- completeness: 是否完整解决了用户需求（0=完全没解决，1=完全解决）</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L105 | <code>- helpfulness: 用户能否据此采取行动（0=毫无帮助，1=非常有帮助）</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L106 | （空行） | 空行，分隔逻辑。 |
| L107 | <code>只返回 JSON，例如: {{&quot;relevance&quot;: 0.9, &quot;accuracy&quot;: 0.8, &quot;completeness&quot;: 0.7, &quot;helpfulness&quot;: 0.85}}&quot;&quot;&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L108 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-109"></a>

### L109–L111 · LLMJudge.__init__

独立裁判客户端引用和模型名；初始化使用与被评 Agent 相同配置，未做裁判独立性控制。

**签名输入：** <code>self, client: AsyncAnthropic, model: str</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, client: AsyncAnthropic, model: str):</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._client = client</code> | 将结果保存到 <code>self._client</code>：读取 <code>client</code>。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._model  = model</code> | 将结果保存到 <code>self._model</code>：读取 <code>model</code>。 |
| L112 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-113"></a>

### L113–L146 · LLMJudge.judge

构造四维 rubric，要求 JSON 并按键读分；解析/网络失败记录 judge_failed，分数填 .5。temperature=0 不构成跨服务版本完全确定性的保证。

**签名输入：** <code>self, question: str, response: str, context: Optional[str]=None</code>；**返回契约：** <code>QualityScores</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def judge(</code> | 定义异步函数 <code>judge</code>；输入参数见签名，下方导读解释调用目的。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;question: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context: Optional[str] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; QualityScores:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ctx_section = f&quot;背景信息: {context}&quot; if context else &quot;&quot;</code> | 将结果保存到 <code>ctx_section</code>：条件 <code>context</code> 成立选前值，否则选 else 后值。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = self.JUDGE_PROMPT.format(</code> | 将结果保存到 <code>prompt</code>：调用 <code>self.JUDGE_PROMPT.format</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;question=question,</code> | 参数 <code>question</code>（question）：读取 <code>question</code>。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response=response,</code> | 参数 <code>response</code>（response）：读取 <code>response</code>。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context_section=ctx_section,</code> | 参数 <code>context_section</code>（context_section）：读取 <code>ctx_section</code>。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = self._clean_text(prompt)</code> | 将结果保存到 <code>prompt</code>：调用 <code>self._clean_text</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await self._client.messages.create(</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=self._model, max_tokens=256, temperature=0.0,</code> | 参数 <code>temperature</code>（生成采样温度）：使用这里写明的固定值。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: prompt}],</code> | 参数 <code>messages</code>（模型消息序列/当前函数的消息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = extract_text_content(resp.content)</code> | 将结果保存到 <code>raw</code>：进入共享响应适配器，只保留模型文本块。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;s, e = raw.find(&quot;{&quot;), raw.rfind(&quot;}&quot;) + 1</code> | 将结果保存到 <code>(s, e)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data = json.loads(raw[s:e])</code> | 将结果保存到 <code>data</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return QualityScores(</code> | 结束当前函数并返回；进入 <code>QualityScores</code>：四个维度各 .0–1.0 是 prompt 约定，Python dataclass 不强制范围；judge_failed/error 单独记录故障。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;relevance=float(data.get(&quot;relevance&quot;, 0.5)),</code> | 参数 <code>relevance</code>（relevance）：转换为浮点数；无效输入会抛出异常。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;accuracy=float(data.get(&quot;accuracy&quot;, 0.5)),</code> | 参数 <code>accuracy</code>（accuracy）：转换为浮点数；无效输入会抛出异常。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;completeness=float(data.get(&quot;completeness&quot;, 0.5)),</code> | 参数 <code>completeness</code>（completeness）：转换为浮点数；无效输入会抛出异常。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;helpfulness=float(data.get(&quot;helpfulness&quot;, 0.5)),</code> | 参数 <code>helpfulness</code>（helpfulness）：转换为浮点数；无效输入会抛出异常。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;LLM Judge 失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return QualityScores(</code> | 结束当前函数并返回；进入 <code>QualityScores</code>：四个维度各 .0–1.0 是 prompt 约定，Python dataclass 不强制范围；judge_failed/error 单独记录故障。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0.5, 0.5, 0.5, 0.5,</code> | 续接 L142 的表达式：按前述语句组装参数、条件或集合。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;judge_failed=True,</code> | 参数 <code>judge_failed</code>（judge_failed）：使用这里写明的固定值。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;error=str(ex),</code> | 参数 <code>error</code>（error）：转换为字符串表示。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L147 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-148"></a>

### L148–L155 · LLMJudge._clean_text

统一编码清理，不能防止回答文本影响裁判指令。

**签名输入：** <code>value: Any</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _clean_text(value: Any) -&gt; str:</code> | 定义函数 <code>_clean_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;移除 Unicode 代理字符，避免 LLM 请求编码失败。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if value is None:</code> | 判断 <code>value is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;</code> | 结束当前函数并返回；使用固定文本/配置值。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(value, str):</code> | 判断 <code>not isinstance(value, str)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value = str(value)</code> | 将结果保存到 <code>value</code>：转换为字符串表示。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return value.encode(&quot;utf-8&quot;, errors=&quot;ignore&quot;).decode(&quot;utf-8&quot;)</code> | 结束当前函数并返回；调用 <code>value.encode(&#x27;utf-8&#x27;, errors=&#x27;ignore&#x27;).decode</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L156 | （空行） | 空行，分隔逻辑。 |
| L157 | （空行） | 空行，分隔逻辑。 |
| L158 | <code># ── 意图识别评测 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 意图识别评测 ────────────────────────────────────────────────────────────── |
| L159 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-160"></a>

### L160–L208 · IntentEvaluator

自动生成回答、分类对标和 LLM 质量评分的评测框架。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L160 | <code>class IntentEvaluator:</code> | 定义 <code>IntentEvaluator</code> 的数据契约/行为；继承与字段见本段。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;评测意图识别的准确率和 F1。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L162 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-163"></a>

### L163–L164 · IntentEvaluator.__init__

注入识别器，方便独立分类评测。API 装配的这个识别器与在线编排器内部的是不同实例。

**签名输入：** <code>self, recognizer: IntentRecognizer</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, recognizer: IntentRecognizer):</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._recognizer = recognizer</code> | 将结果保存到 <code>self._recognizer</code>：读取 <code>recognizer</code>。 |
| L165 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-166"></a>

### L166–L208 · IntentEvaluator.evaluate

串行识别，保存预测/标签及理由。对 ground_truth 与 predictions 并集每类算 TP/FP/FN，再平均 F1，纯 Python 实现可现场解释。

**签名输入：** <code>self, cases: List[IntentTestCase]</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def evaluate(self, cases: List[IntentTestCase]) -&gt; Dict[str, Any]:</code> | 定义异步函数 <code>evaluate</code>；输入参数见签名，下方导读解释调用目的。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;predictions, ground_truth = [], []</code> | 将结果保存到 <code>(predictions, ground_truth)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case_details: List[Dict[str, Any]] = []</code> | 将结果保存到 <code>case_details</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L169 | （空行） | 空行，分隔逻辑。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for case in cases:</code> | 遍历 <code>cases</code>，本轮元素绑定 <code>case</code>。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result = await self._recognizer.recognize(case.message)</code> | **关键：**case.context 没被传入，多轮分类上下文评测设计没有落地。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;predicted = result.intent.value</code> | 将结果保存到 <code>predicted</code>：读取 <code>result.intent.value</code>。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;predictions.append(predicted)</code> | 追加一个元素到当前列表。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ground_truth.append(case.expected_intent)</code> | 追加一个元素到当前列表。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case_details.append({</code> | 追加一个元素到当前列表。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: case.message,</code> | 字段 <code>message</code>（本轮用户消息）：读取 <code>case.message</code>。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: case.expected_intent,</code> | 字段 <code>expected</code>（当前映射中的键）：读取 <code>case.expected_intent</code>。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: predicted,</code> | 字段 <code>predicted</code>（当前映射中的键）：读取 <code>predicted</code>。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: result.confidence,</code> | 字段 <code>confidence</code>（置信度分数）：读取 <code>result.confidence</code>。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: result.reasoning,</code> | 字段 <code>reasoning</code>（当前映射中的键）：读取 <code>result.reasoning</code>。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;})</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L182 | （空行） | 空行，分隔逻辑。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 纯 Python 计算指标</code> | 源码注释：纯 Python 计算指标 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;correct = sum(p == g for p, g in zip(predictions, ground_truth))</code> | 将结果保存到 <code>correct</code>：累加各项数值/布尔命中值。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;accuracy = correct / len(predictions) if predictions else 0.0</code> | 将结果保存到 <code>accuracy</code>：条件 <code>predictions</code> 成立选前值，否则选 else 后值。 |
| L186 | （空行） | 空行，分隔逻辑。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 每类 F1</code> | 源码注释：每类 F1 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;labels = sorted(set(ground_truth + predictions))</code> | 将结果保存到 <code>labels</code>：按指定规则排序，不直接改变原列表。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;per_class: Dict[str, Dict[str, float]] = {}</code> | 将结果保存到 <code>per_class</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for label in labels:</code> | 遍历 <code>labels</code>，本轮元素绑定 <code>label</code>。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tp = sum(p == label and g == label for p, g in zip(predictions, ground_truth))</code> | 将结果保存到 <code>tp</code>：累加各项数值/布尔命中值。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fp = sum(p == label and g != label for p, g in zip(predictions, ground_truth))</code> | 将结果保存到 <code>fp</code>：累加各项数值/布尔命中值。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fn = sum(p != label and g == label for p, g in zip(predictions, ground_truth))</code> | 将结果保存到 <code>fn</code>：累加各项数值/布尔命中值。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prec = tp / (tp + fp) if (tp + fp) else 0.0</code> | 将结果保存到 <code>prec</code>：条件 <code>tp + fp</code> 成立选前值，否则选 else 后值。 |
| L195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rec  = tp / (tp + fn) if (tp + fn) else 0.0</code> | 将结果保存到 <code>rec</code>：条件 <code>tp + fn</code> 成立选前值，否则选 else 后值。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0</code> | 将结果保存到 <code>f1</code>：条件 <code>prec + rec</code> 成立选前值，否则选 else 后值。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;per_class[label] = {&quot;precision&quot;: prec, &quot;recall&quot;: rec, &quot;f1&quot;: f1}</code> | 将结果保存到 <code>per_class[label]</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L198 | （空行） | 空行，分隔逻辑。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;macro_f1 = statistics.mean(v[&quot;f1&quot;] for v in per_class.values()) if per_class else 0.0</code> | 将结果保存到 <code>macro_f1</code>：条件 <code>per_class</code> 成立选前值，否则选 else 后值。 |
| L200 | （空行） | 空行，分隔逻辑。 |
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;:   round(accuracy, 4),</code> | 字段 <code>accuracy</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;macro_f1&quot;:   round(macro_f1, 4),</code> | 字段 <code>macro_f1</code>（当前映射中的键）：四舍五入用于返回/展示。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;per_class&quot;:  per_class,</code> | 字段 <code>per_class</code>（当前映射中的键）：读取 <code>per_class</code>。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;total&quot;:      len(cases),</code> | 字段 <code>total</code>（当前映射中的键）：计算当前容器或字符串长度。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;correct&quot;:    correct,</code> | 字段 <code>correct</code>（当前映射中的键）：读取 <code>correct</code>。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;cases&quot;:      case_details,</code> | 字段 <code>cases</code>（当前映射中的键）：读取 <code>case_details</code>。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L209 | （空行） | 空行，分隔逻辑。 |
| L210 | （空行） | 空行，分隔逻辑。 |
| L211 | <code># ── 端到端评测器 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 端到端评测器 ────────────────────────────────────────────────────────────── |
| L212 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-213"></a>

### L213–L476 · EndToEndEvaluator

自动生成回答、分类对标和 LLM 质量评分的评测框架。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L213 | <code>class EndToEndEvaluator:</code> | 定义 <code>EndToEndEvaluator</code> 的数据契约/行为；继承与字段见本段。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;端到端 Agent 评测。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L216 | （空行） | 空行，分隔逻辑。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;评测流程：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. 运行意图识别评测（准确率/F1）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. 运行对话质量评测（LLM-as-Judge）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. 与历史基线对比（回归检测）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4. 生成可操作的优化建议</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L223 | （空行） | 空行，分隔逻辑。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 质量及格线</code> | 源码注释：质量及格线 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;PASS_THRESHOLD = 0.75</code> | 将结果保存到 <code>PASS_THRESHOLD</code>：使用这里写明的固定值。 |
| L226 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-227"></a>

### L227–L246 · EndToEndEvaluator.__init__

组装裁判与意图评测器，初始化内存报告历史，并尝试加载磁盘基线。

**签名输入：** <code>self, orchestrator, recognizer: IntentRecognizer, api_key: str, base_url: Optional[str]=None, model: str=&#x27;claude-3-5-sonnet-20241022&#x27;, baseline_path: Optional[str]=None</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;orchestrator,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recognizer: IntentRecognizer,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key:  str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url: Optional[str] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model:    str = &quot;claude-3-5-sonnet-20241022&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;baseline_path: Optional[str] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs: Dict[str, Any] = {&quot;api_key&quot;: api_key}</code> | 将结果保存到 <code>kwargs</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if base_url:</code> | 判断 <code>base_url</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs[&quot;base_url&quot;] = base_url</code> | 将结果保存到 <code>kwargs[&#x27;base_url&#x27;]</code>：读取 <code>base_url</code>。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;client = AsyncAnthropic(**kwargs)</code> | 将结果保存到 <code>client</code>：调用 <code>AsyncAnthropic</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L240 | （空行） | 空行，分隔逻辑。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._orchestrator     = orchestrator</code> | 将结果保存到 <code>self._orchestrator</code>：读取 <code>orchestrator</code>。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._judge            = LLMJudge(client, model)</code> | 将结果保存到 <code>self._judge</code>：调用 <code>LLMJudge</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._intent_evaluator = IntentEvaluator(recognizer)</code> | 将结果保存到 <code>self._intent_evaluator</code>：调用 <code>IntentEvaluator</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._history:         List[EvalReport] = []</code> | 将结果保存到 <code>self._history</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._baseline_path = pathlib.Path(baseline_path) if baseline_path else None</code> | 将结果保存到 <code>self._baseline_path</code>：条件 <code>baseline_path</code> 成立选前值，否则选 else 后值。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._baseline: Optional[EvalReport] = self._load_baseline()</code> | 将结果保存到 <code>self._baseline</code>：进入 <code>self._load_baseline</code>：文件存在才解析，错误只记日志，没有强制保证比较可用。 |
| L247 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-248"></a>

### L248–L321 · EndToEndEvaluator.run

意图 accuracy≥.75 使整组通过，对话 overall≥.75 使单轮通过；聚合每类均分，检测回归后保存这次报告。报告通过不阻止 regression。

**签名输入：** <code>self, intent_cases: Optional[List[IntentTestCase]]=None, dialog_cases: Optional[List[Dict[str, Any]]]=None</code>；**返回契约：** <code>EvalReport</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def run(</code> | 定义异步函数 <code>run</code>；输入参数见签名，下方导读解释调用目的。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_cases:    Optional[List[IntentTestCase]] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog_cases:    Optional[List[Dict[str, Any]]] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; EvalReport:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;运行完整评测。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L255 | （空行） | 空行，分隔逻辑。 |
| L256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_cases: 意图识别测试用例</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog_cases:</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- 单轮: [{&quot;question&quot;: &quot;...&quot;}]</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- 多轮: [{&quot;turns&quot;: [&quot;第一轮&quot;, &quot;第二轮&quot;, ...]}]</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results: List[EvalResult] = []</code> | 将结果保存到 <code>results</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;all_scores: Dict[str, List[float]] = {</code> | 将结果保存到 <code>all_scores</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: [], &quot;accuracy&quot;: [], &quot;completeness&quot;: [], &quot;helpfulness&quot;: []</code> | 字段 <code>helpfulness</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L265 | （空行） | 空行，分隔逻辑。 |
| L266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 1. 意图识别评测</code> | 源码注释：1. 意图识别评测 |
| L267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_metrics: Dict[str, Any] = {}</code> | 将结果保存到 <code>intent_metrics</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if intent_cases:</code> | 判断 <code>intent_cases</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_metrics = await self._intent_evaluator.evaluate(intent_cases)</code> | 将结果保存到 <code>intent_metrics</code>：等待完成后继续；进入 <code>self._intent_evaluator.evaluate</code>：串行识别，保存预测/标签及理由。 |
| L270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed = intent_metrics[&quot;accuracy&quot;] &gt;= self.PASS_THRESHOLD</code> | **关键：**整组 11 条样本仅生成一个 passed 结果项。 |
| L271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results.append(EvalResult(</code> | 追加一个元素到当前列表。 |
| L272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test_id=&quot;intent_recognition&quot;,</code> | 参数 <code>test_id</code>（test_id）：使用固定文本/配置值。 |
| L273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed=passed,</code> | 参数 <code>passed</code>（passed）：读取 <code>passed</code>。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores={&quot;accuracy&quot;: intent_metrics[&quot;accuracy&quot;], &quot;macro_f1&quot;: intent_metrics[&quot;macro_f1&quot;]},</code> | 参数 <code>scores</code>（scores）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detail=f&quot;准确率 {intent_metrics[&#x27;accuracy&#x27;]:.1%}，Macro-F1 {intent_metrics[&#x27;macro_f1&#x27;]:.3f}&quot;,</code> | 参数 <code>detail</code>（detail）：将变量插入模板，构造提示词、标识或可读说明。 |
| L276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadata={</code> | 参数 <code>metadata</code>（附加元信息）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;total&quot;: intent_metrics.get(&quot;total&quot;, 0),</code> | 字段 <code>total</code>（当前映射中的键）：按键取值，缺失用给定默认值。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;correct&quot;: intent_metrics.get(&quot;correct&quot;, 0),</code> | 字段 <code>correct</code>（当前映射中的键）：按键取值，缺失用给定默认值。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;cases&quot;: intent_metrics.get(&quot;cases&quot;, []),</code> | 字段 <code>cases</code>（当前映射中的键）：按键取值，缺失用给定默认值。 |
| L280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L282 | （空行） | 空行，分隔逻辑。 |
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 2. 对话质量评测（调用 orchestrator 产出回复，再用 LLM Judge 评分）</code> | 源码注释：2. 对话质量评测（调用 orchestrator 产出回复，再用 LLM Judge 评分） |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if dialog_cases:</code> | 判断 <code>dialog_cases</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i, case in enumerate(dialog_cases):</code> | 遍历 <code>enumerate(dialog_cases)</code>，本轮元素绑定 <code>(i, case)</code>。 |
| L286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case_results = await self._evaluate_dialog_case(case, i)</code> | 将结果保存到 <code>case_results</code>：等待完成后继续；进入 <code>self._evaluate_dialog_case</code>：同一 case 用列表保存模拟历史，逐轮生成答案再评分。 |
| L287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results.extend(case_results)</code> | 追加一批元素到列表。 |
| L288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for r in case_results:</code> | 遍历 <code>case_results</code>，本轮元素绑定 <code>r</code>。 |
| L289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for k in all_scores:</code> | 遍历 <code>all_scores</code>，本轮元素绑定 <code>k</code>。 |
| L290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if k in r.scores:</code> | 判断 <code>k in r.scores</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;all_scores[k].append(r.scores[k])</code> | 追加一个元素到当前列表。 |
| L292 | （空行） | 空行，分隔逻辑。 |
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 3. 汇总</code> | 源码注释：3. 汇总 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;avg_scores = {</code> | 将结果保存到 <code>avg_scores</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;k: round(statistics.mean(v), 4) for k, v in all_scores.items() if v</code> | 续接 L294 的表达式：按前述语句组装参数、条件或集合。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if intent_metrics:</code> | 判断 <code>intent_metrics</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;avg_scores[&quot;intent_accuracy&quot;] = intent_metrics[&quot;accuracy&quot;]</code> | 将结果保存到 <code>avg_scores[&#x27;intent_accuracy&#x27;]</code>：按索引/切片取 <code>intent_metrics[&#x27;accuracy&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L299 | （空行） | 空行，分隔逻辑。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed_count = sum(1 for r in results if r.passed)</code> | 将结果保存到 <code>passed_count</code>：累加各项数值/布尔命中值。 |
| L301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pass_rate    = passed_count / len(results) if results else 0.0</code> | 将结果保存到 <code>pass_rate</code>：条件 <code>results</code> 成立选前值，否则选 else 后值。 |
| L302 | （空行） | 空行，分隔逻辑。 |
| L303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 4. 回归检测</code> | 源码注释：4. 回归检测 |
| L304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regressions = self._detect_regressions(avg_scores)</code> | 将结果保存到 <code>regressions</code>：进入 <code>self._detect_regressions</code>：优先上一份内存报告，否则磁盘基线；相对下降超过 5% 才报退化，例如 .8→.75 为下降6.25%，不是5个百分点阈值。 |
| L305 | （空行） | 空行，分隔逻辑。 |
| L306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 5. 优化建议</code> | 源码注释：5. 优化建议 |
| L307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recommendations = self._recommendations(avg_scores, intent_metrics)</code> | 将结果保存到 <code>recommendations</code>：进入 <code>self._recommendations</code>：按 intent_accuracy、relevance、completeness、helpfulness 的固定门槛给文字建议；intent_metrics 参数未使用，不做自动纠正学习。 |
| L308 | （空行） | 空行，分隔逻辑。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;report = EvalReport(</code> | 将结果保存到 <code>report</code>：进入 <code>EvalReport</code>：汇总快照加详细结果；持久化完整 report 作为下一次比较材料。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timestamp=datetime.now().isoformat(),</code> | 参数 <code>timestamp</code>（timestamp）：调用 <code>datetime.now().isoformat</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;total=len(results),</code> | 参数 <code>total</code>（total）：计算当前容器或字符串长度。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed=passed_count,</code> | 参数 <code>passed</code>（passed）：读取 <code>passed_count</code>。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pass_rate=round(pass_rate, 4),</code> | 参数 <code>pass_rate</code>（pass_rate）：四舍五入用于返回/展示。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;avg_scores=avg_scores,</code> | 参数 <code>avg_scores</code>（avg_scores）：读取 <code>avg_scores</code>。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regressions=regressions,</code> | 参数 <code>regressions</code>（regressions）：读取 <code>regressions</code>。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recommendations=recommendations,</code> | 参数 <code>recommendations</code>（recommendations）：读取 <code>recommendations</code>。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results=results,</code> | 参数 <code>results</code>（results）：读取 <code>results</code>。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._history.append(report)</code> | 追加一个元素到当前列表。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._save_baseline(report)</code> | **关键：**本轮即使退化也保存为下一轮基线。 |
| L321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return report</code> | 结束当前函数并返回；读取 <code>report</code>。 |
| L322 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-323"></a>

### L323–L378 · EndToEndEvaluator._evaluate_dialog_case

同一 case 用列表保存模拟历史，逐轮生成答案再评分。上下文为最近 8 条文字，给识别器的是最近 6 条，再由识别器截三条。

**签名输入：** <code>self, case: Dict[str, Any], case_idx: int</code>；**返回契约：** <code>List[EvalResult]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _evaluate_dialog_case(self, case: Dict[str, Any], case_idx: int) -&gt; List[EvalResult]:</code> | 定义异步函数 <code>_evaluate_dialog_case</code>；输入参数见签名，下方导读解释调用目的。 |
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;评测单轮或多轮对话用例。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from agents.agent_orchestrator import Request as OrcReq</code> | 导入 <code>from agents.agent_orchestrator import Request as OrcReq</code>；只建立名称依赖，真正业务调用见后文。 |
| L326 | （空行） | 空行，分隔逻辑。 |
| L327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;questions = self._dialog_turns(case)</code> | 将结果保存到 <code>questions</code>：进入 <code>self._dialog_turns</code>：turns 为列表优先，否则 question；空白过滤，列表中非字符串会 str 化。 |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not questions:</code> | 判断 <code>not questions</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return []</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L330 | （空行） | 空行，分隔逻辑。 |
| L331 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id = str(case.get(&quot;conv_id&quot;) or f&quot;eval_{case_idx}&quot;)</code> | 将结果保存到 <code>conv_id</code>：转换为字符串表示。 |
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id = str(case.get(&quot;user_id&quot;) or &quot;eval_user&quot;)</code> | 将结果保存到 <code>user_id</code>：转换为字符串表示。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history: List[Dict[str, str]] = []</code> | 将结果保存到 <code>history</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results: List[EvalResult] = []</code> | 将结果保存到 <code>results</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L335 | （空行） | 空行，分隔逻辑。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for turn_idx, question in enumerate(questions):</code> | 遍历 <code>enumerate(questions)</code>，本轮元素绑定 <code>(turn_idx, question)</code>。 |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context = self._history_context(history)</code> | 将结果保存到 <code>context</code>：进入 <code>self._history_context</code>：拼接最多 8 条评测内存历史，不访问 MemoryManager，因此无法评到压缩/画像/跨会话召回。 |
| L338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;orch_req = OrcReq(</code> | 将结果保存到 <code>orch_req</code>：调用 <code>OrcReq</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message=question,</code> | 参数 <code>message</code>（本轮用户消息）：读取 <code>question</code>。 |
| L340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id=user_id,</code> | 参数 <code>user_id</code>（用户标识）：读取 <code>user_id</code>。 |
| L341 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id=conv_id,</code> | 参数 <code>conv_id</code>（会话标识）：读取 <code>conv_id</code>。 |
| L342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context=context,</code> | 参数 <code>context</code>（背景上下文）：读取 <code>context</code>。 |
| L343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history=history[-6:] if history else None,</code> | 参数 <code>history</code>（历史消息）：条件 <code>history</code> 成立选前值，否则选 else 后值。 |
| L344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L345 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;orch_result = await self._orchestrator.run(orch_req)</code> | **关键：**调用编排器，不调用 API.chat；无 RAG 与真实 MemoryManager。 |
| L346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;actual_answer = orch_result.response</code> | 将结果保存到 <code>actual_answer</code>：读取 <code>orch_result.response</code>。 |
| L347 | （空行） | 空行，分隔逻辑。 |
| L348 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores = await self._judge.judge(question, actual_answer, context=context or None)</code> | **关键：**裁判依据只有当前问题、回答和模拟历史，没有检索证据。 |
| L349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed = scores.overall &gt;= self.PASS_THRESHOLD</code> | 将结果保存到 <code>passed</code>：读取 <code>scores.overall &gt;= self.PASS_THRESHOLD</code>。 |
| L350 | （空行） | 空行，分隔逻辑。 |
| L351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history.append({&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: question})</code> | 追加一个元素到当前列表。 |
| L352 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history.append({&quot;role&quot;: &quot;assistant&quot;, &quot;content&quot;: actual_answer})</code> | 追加一个元素到当前列表。 |
| L353 | （空行） | 空行，分隔逻辑。 |
| L354 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test_id = f&quot;dialog_{case_idx}&quot; if len(questions) == 1 else f&quot;dialog_{case_idx}_turn_{turn_idx}&quot;</code> | 将结果保存到 <code>test_id</code>：条件 <code>len(questions) == 1</code> 成立选前值，否则选 else 后值。 |
| L355 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results.append(EvalResult(</code> | 追加一个元素到当前列表。 |
| L356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test_id=test_id,</code> | 参数 <code>test_id</code>（test_id）：读取 <code>test_id</code>。 |
| L357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed=passed,</code> | 参数 <code>passed</code>（passed）：读取 <code>passed</code>。 |
| L358 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores={</code> | 参数 <code>scores</code>（scores）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L359 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: scores.relevance,</code> | 字段 <code>relevance</code>（当前映射中的键）：读取 <code>scores.relevance</code>。 |
| L360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: scores.accuracy,</code> | 字段 <code>accuracy</code>（当前映射中的键）：读取 <code>scores.accuracy</code>。 |
| L361 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: scores.completeness,</code> | 字段 <code>completeness</code>（当前映射中的键）：读取 <code>scores.completeness</code>。 |
| L362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: scores.helpfulness,</code> | 字段 <code>helpfulness</code>（当前映射中的键）：读取 <code>scores.helpfulness</code>。 |
| L363 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: scores.overall,</code> | 字段 <code>overall</code>（当前映射中的键）：读取 <code>scores.overall</code>。 |
| L364 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detail=f&quot;Q: {question[:30]}... → 综合评分 {scores.overall:.3f}&quot;,</code> | 参数 <code>detail</code>（detail）：将变量插入模板，构造提示词、标识或可读说明。 |
| L366 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadata={</code> | 参数 <code>metadata</code>（附加元信息）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L367 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: question,</code> | 字段 <code>question</code>（当前映射中的键）：读取 <code>question</code>。 |
| L368 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: actual_answer,</code> | 字段 <code>response</code>（当前映射中的键）：读取 <code>actual_answer</code>。 |
| L369 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: orch_result.agent_type.value,</code> | 字段 <code>agent_type</code>（Agent 类别）：读取 <code>orch_result.agent_type.value</code>。 |
| L370 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: orch_result.intent.value if orch_result.intent else None,</code> | 字段 <code>intent</code>（意图标签）：条件 <code>orch_result.intent</code> 成立选前值，否则选 else 后值。 |
| L371 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: turn_idx,</code> | 字段 <code>turn</code>（当前映射中的键）：读取 <code>turn_idx</code>。 |
| L372 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: conv_id,</code> | 字段 <code>conv_id</code>（会话标识）：读取 <code>conv_id</code>。 |
| L373 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: scores.judge_failed,</code> | 字段 <code>judge_failed</code>（当前映射中的键）：读取 <code>scores.judge_failed</code>。 |
| L374 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: scores.error,</code> | 字段 <code>judge_error</code>（当前映射中的键）：读取 <code>scores.error</code>。 |
| L375 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L376 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L377 | （空行） | 空行，分隔逻辑。 |
| L378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return results</code> | 结束当前函数并返回；读取 <code>results</code>。 |
| L379 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-380"></a>

### L380–L386 · EndToEndEvaluator._dialog_turns

turns 为列表优先，否则 question；空白过滤，列表中非字符串会 str 化。

**签名输入：** <code>case: Dict[str, Any]</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _dialog_turns(case: Dict[str, Any]) -&gt; List[str]:</code> | 定义函数 <code>_dialog_turns</code>；输入参数见签名，下方导读解释调用目的。 |
| L382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;turns = case.get(&quot;turns&quot;)</code> | 将结果保存到 <code>turns</code>：按键取值，缺失用给定默认值。 |
| L383 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(turns, list):</code> | 判断 <code>isinstance(turns, list)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L384 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [str(t) for t in turns if str(t).strip()]</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L385 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;question = case.get(&quot;question&quot;)</code> | 将结果保存到 <code>question</code>：按键取值，缺失用给定默认值。 |
| L386 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [str(question)] if question else []</code> | 结束当前函数并返回；条件 <code>question</code> 成立选前值，否则选 else 后值。 |
| L387 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-388"></a>

### L388–L393 · EndToEndEvaluator._history_context

拼接最多 8 条评测内存历史，不访问 MemoryManager，因此无法评到压缩/画像/跨会话召回。

**签名输入：** <code>history: List[Dict[str, str]]</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L388 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L389 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _history_context(history: List[Dict[str, str]]) -&gt; str:</code> | 定义函数 <code>_history_context</code>；输入参数见签名，下方导读解释调用目的。 |
| L390 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not history:</code> | 判断 <code>not history</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L391 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;</code> | 结束当前函数并返回；使用固定文本/配置值。 |
| L392 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines = [f&quot;{m[&#x27;role&#x27;]}: {m[&#x27;content&#x27;]}&quot; for m in history[-8:]]</code> | 将结果保存到 <code>lines</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L393 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;[评测多轮历史]\n&quot; + &quot;\n&quot;.join(lines)</code> | 结束当前函数并返回；按此表达式计算 <code>&#x27;[评测多轮历史]\n&#x27; + &#x27;\n&#x27;.join(lines)</code>。 |
| L394 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-395"></a>

### L395–L409 · EndToEndEvaluator._detect_regressions

优先上一份内存报告，否则磁盘基线；相对下降超过 5% 才报退化，例如 .8→.75 为下降6.25%，不是5个百分点阈值。

**签名输入：** <code>self, current: Dict[str, float]</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L395 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _detect_regressions(self, current: Dict[str, float]) -&gt; List[str]:</code> | 定义函数 <code>_detect_regressions</code>；输入参数见签名，下方导读解释调用目的。 |
| L396 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;与上一次评测对比，找出退化超过 5% 的指标。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L397 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prev_report = self._history[-1] if self._history else self._baseline</code> | 将结果保存到 <code>prev_report</code>：条件 <code>self._history</code> 成立选前值，否则选 else 后值。 |
| L398 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if prev_report is None:</code> | 判断 <code>prev_report is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L399 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return []</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L400 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prev = prev_report.avg_scores</code> | 将结果保存到 <code>prev</code>：读取 <code>prev_report.avg_scores</code>。 |
| L401 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regressions = []</code> | 将结果保存到 <code>regressions</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L402 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for metric, value in current.items():</code> | 遍历 <code>current.items()</code>，本轮元素绑定 <code>(metric, value)</code>。 |
| L403 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if metric in prev and prev[metric] &gt; 0:</code> | 判断 <code>metric in prev and prev[metric] &gt; 0</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L404 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;delta = (value - prev[metric]) / prev[metric]</code> | 将结果保存到 <code>delta</code>：按此表达式计算 <code>(value - prev[metric]) / prev[metric]</code>。 |
| L405 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if delta &lt; -0.05:</code> | **关键：**相对下降严格超过 5% 才触发。 |
| L406 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regressions.append(</code> | 追加一个元素到当前列表。 |
| L407 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;{metric}: {prev[metric]:.3f} → {value:.3f} (退化 {abs(delta):.1%})&quot;</code> | 续接 L406 的表达式：按前述语句组装参数、条件或集合。 |
| L408 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L409 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return regressions</code> | 结束当前函数并返回；读取 <code>regressions</code>。 |
| L410 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-411"></a>

### L411–L427 · EndToEndEvaluator._recommendations

按 intent_accuracy、relevance、completeness、helpfulness 的固定门槛给文字建议；intent_metrics 参数未使用，不做自动纠正学习。

**签名输入：** <code>self, scores: Dict[str, float], intent_metrics: Dict[str, Any]</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L411 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _recommendations(</code> | 定义函数 <code>_recommendations</code>；输入参数见签名，下方导读解释调用目的。 |
| L412 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L413 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores: Dict[str, float],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L414 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_metrics: Dict[str, Any],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L415 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; List[str]:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L416 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recs = []</code> | 将结果保存到 <code>recs</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L417 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if scores.get(&quot;intent_accuracy&quot;, 1.0) &lt; 0.90:</code> | 判断 <code>scores.get(&#x27;intent_accuracy&#x27;, 1.0) &lt; 0.9</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L418 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recs.append(&quot;意图识别准确率 &lt; 90%：增加 Few-shot 示例，或对低 F1 的意图类别补充训练数据&quot;)</code> | 追加一个元素到当前列表。 |
| L419 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if scores.get(&quot;relevance&quot;, 1.0) &lt; 0.75:</code> | 判断 <code>scores.get(&#x27;relevance&#x27;, 1.0) &lt; 0.75</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L420 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recs.append(&quot;相关性偏低：检查 Agent system_prompt，确保 Agent 聚焦于用户问题&quot;)</code> | 追加一个元素到当前列表。 |
| L421 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if scores.get(&quot;completeness&quot;, 1.0) &lt; 0.75:</code> | 判断 <code>scores.get(&#x27;completeness&#x27;, 1.0) &lt; 0.75</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L422 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recs.append(&quot;完整性偏低：Agent 可能过早结束回答，考虑在 prompt 中要求提供完整解决方案&quot;)</code> | 追加一个元素到当前列表。 |
| L423 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if scores.get(&quot;helpfulness&quot;, 1.0) &lt; 0.75:</code> | 判断 <code>scores.get(&#x27;helpfulness&#x27;, 1.0) &lt; 0.75</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L424 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recs.append(&quot;有用性偏低：回答可能过于抽象，考虑要求 Agent 提供具体操作步骤&quot;)</code> | 追加一个元素到当前列表。 |
| L425 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not recs:</code> | 判断 <code>not recs</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L426 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recs.append(&quot;所有指标均达标，继续保持&quot;)</code> | **关键：**未检查 accuracy 低/裁判失败，可能与实际报告相矛盾。 |
| L427 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return recs</code> | 结束当前函数并返回；读取 <code>recs</code>。 |
| L428 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-429"></a>

### L429–L431 · EndToEndEvaluator.history

直接返回内部可变列表，外部可以修改；可改为只读副本。

**签名输入：** <code>self</code>；**返回契约：** <code>List[EvalReport]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L429 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L430 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def history(self) -&gt; List[EvalReport]:</code> | 定义函数 <code>history</code>；输入参数见签名，下方导读解释调用目的。 |
| L431 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self._history</code> | 结束当前函数并返回；读取 <code>self._history</code>。 |
| L432 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-433"></a>

### L433–L441 · EndToEndEvaluator._load_baseline

文件存在才解析，错误只记日志，没有强制保证比较可用。

**签名输入：** <code>self</code>；**返回契约：** <code>Optional[EvalReport]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L433 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _load_baseline(self) -&gt; Optional[EvalReport]:</code> | 定义函数 <code>_load_baseline</code>；输入参数见签名，下方导读解释调用目的。 |
| L434 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not self._baseline_path or not self._baseline_path.exists():</code> | 判断 <code>not self._baseline_path or not self._baseline_path.exists()</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L435 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L436 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L437 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data = json.loads(self._baseline_path.read_text(encoding=&quot;utf-8&quot;))</code> | 将结果保存到 <code>data</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L438 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self._report_from_dict(data)</code> | 结束当前函数并返回；进入 <code>self._report_from_dict</code>：按默认值重建报告及各 EvalResult，宽松兼容缺少字段的旧报告，但不验证数据集可比性。 |
| L439 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L440 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;读取评测基线失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L441 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L442 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-443"></a>

### L443–L454 · EndToEndEvaluator._save_baseline

创建父目录并将 asdict(report) JSON 写入原路径，是覆盖式保存，没有历史版本或原子替换。

**签名输入：** <code>self, report: EvalReport</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L443 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _save_baseline(self, report: EvalReport) -&gt; None:</code> | 定义函数 <code>_save_baseline</code>；输入参数见签名，下方导读解释调用目的。 |
| L444 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not self._baseline_path:</code> | 判断 <code>not self._baseline_path</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L445 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | 结束当前函数并返回；无返回值。 |
| L446 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L447 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._baseline_path.parent.mkdir(parents=True, exist_ok=True)</code> | 调用 <code>self._baseline_path.parent.mkdir</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L448 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._baseline_path.write_text(</code> | 把文本写入文件，覆盖已有内容。 |
| L449 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;json.dumps(asdict(report), ensure_ascii=False, indent=2),</code> | 参数 <code>indent</code>（indent）：使用这里写明的固定值。 |
| L450 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;encoding=&quot;utf-8&quot;,</code> | 参数 <code>encoding</code>（encoding）：使用固定文本/配置值。 |
| L451 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L452 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._baseline = report</code> | 将结果保存到 <code>self._baseline</code>：读取 <code>report</code>。 |
| L453 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L454 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;保存评测基线失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L455 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-456"></a>

### L456–L476 · EndToEndEvaluator._report_from_dict

按默认值重建报告及各 EvalResult，宽松兼容缺少字段的旧报告，但不验证数据集可比性。

**签名输入：** <code>data: Dict[str, Any]</code>；**返回契约：** <code>EvalReport</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L456 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L457 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _report_from_dict(data: Dict[str, Any]) -&gt; EvalReport:</code> | 定义函数 <code>_report_from_dict</code>；输入参数见签名，下方导读解释调用目的。 |
| L458 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return EvalReport(</code> | 结束当前函数并返回；进入 <code>EvalReport</code>：汇总快照加详细结果；持久化完整 report 作为下一次比较材料。 |
| L459 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timestamp=data.get(&quot;timestamp&quot;, &quot;&quot;),</code> | 参数 <code>timestamp</code>（timestamp）：按键取值，缺失用给定默认值。 |
| L460 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;total=int(data.get(&quot;total&quot;, 0)),</code> | 参数 <code>total</code>（total）：转换为整数。 |
| L461 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed=int(data.get(&quot;passed&quot;, 0)),</code> | 参数 <code>passed</code>（passed）：转换为整数。 |
| L462 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pass_rate=float(data.get(&quot;pass_rate&quot;, 0.0)),</code> | 参数 <code>pass_rate</code>（pass_rate）：转换为浮点数；无效输入会抛出异常。 |
| L463 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;avg_scores=dict(data.get(&quot;avg_scores&quot;, {})),</code> | 参数 <code>avg_scores</code>（avg_scores）：构造字典。 |
| L464 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;regressions=list(data.get(&quot;regressions&quot;, [])),</code> | 参数 <code>regressions</code>（regressions）：将迭代内容物化成列表。 |
| L465 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recommendations=list(data.get(&quot;recommendations&quot;, [])),</code> | 参数 <code>recommendations</code>（recommendations）：将迭代内容物化成列表。 |
| L466 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results=[</code> | 参数 <code>results</code>（results）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L467 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;EvalResult(</code> | 续接 L458 的表达式：按前述语句组装参数、条件或集合。 |
| L468 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test_id=r.get(&quot;test_id&quot;, &quot;&quot;),</code> | 参数 <code>test_id</code>（test_id）：按键取值，缺失用给定默认值。 |
| L469 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;passed=bool(r.get(&quot;passed&quot;, False)),</code> | 参数 <code>passed</code>（passed）：求真值。 |
| L470 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores=dict(r.get(&quot;scores&quot;, {})),</code> | 参数 <code>scores</code>（scores）：构造字典。 |
| L471 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detail=r.get(&quot;detail&quot;, &quot;&quot;),</code> | 参数 <code>detail</code>（detail）：按键取值，缺失用给定默认值。 |
| L472 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadata=dict(r.get(&quot;metadata&quot;, {})),</code> | 参数 <code>metadata</code>（附加元信息）：构造字典。 |
| L473 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L474 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for r in data.get(&quot;results&quot;, [])</code> | 续接 L458 的表达式：按前述语句组装参数、条件或集合。 |
| L475 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;],</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L476 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L477 | （空行） | 空行，分隔逻辑。 |
| L478 | （空行） | 空行，分隔逻辑。 |
| L479 | <code># ── 内置测试用例（开箱即用）──────────────────────────────────────────────────</code> | 源码注释：── 内置测试用例（开箱即用）────────────────────────────────────────────────── |
| L480 | （空行） | 空行，分隔逻辑。 |
| L481 | <code>DEFAULT_INTENT_CASES: List[IntentTestCase] = [</code> | 将结果保存到 <code>DEFAULT_INTENT_CASES</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L482 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;我的订单什么时候到？&quot;,       &quot;logistics&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L483 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;帮我取消订单&quot;,               &quot;request&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L484 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;你们服务太差了！&quot;,            &quot;complaint&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L485 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;应用一直报500错误&quot;,           &quot;technical_crash&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L486 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;为什么扣了两次款？&quot;,          &quot;payment_issue&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L487 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;我要投诉，转人工！&quot;,          &quot;human_handoff&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L488 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;你好&quot;,                        &quot;greeting&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L489 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;修改我的邮箱地址&quot;,            &quot;account&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L490 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;帮我开发票&quot;,                  &quot;invoice&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L491 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;退款多久到账？&quot;,              &quot;refund&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L492 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(&quot;登录一直报401&quot;,               &quot;technical_login&quot;),</code> | 续接 L481 的表达式：按前述语句组装参数、条件或集合。 |
| L493 | <code>]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L494 | （空行） | 空行，分隔逻辑。 |
| L495 | <code>DEFAULT_DIALOG_CASES: List[Dict[str, Any]] = [</code> | 将结果保存到 <code>DEFAULT_DIALOG_CASES</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L496 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{&quot;question&quot;: &quot;我的订单 #12345 还没到，已经超时了&quot;},</code> | 字段 <code>question</code>（当前映射中的键）：使用固定文本/配置值。 |
| L497 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{&quot;question&quot;: &quot;应用登录一直报错 401&quot;},</code> | 字段 <code>question</code>（当前映射中的键）：使用固定文本/配置值。 |
| L498 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{&quot;question&quot;: &quot;为什么这个月多扣了 50 块钱？&quot;},</code> | 字段 <code>question</code>（当前映射中的键）：使用固定文本/配置值。 |
| L499 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{&quot;question&quot;: &quot;帮我把收货地址改成北京市朝阳区&quot;},</code> | 字段 <code>question</code>（当前映射中的键）：使用固定文本/配置值。 |
| L500 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{&quot;turns&quot;: [&quot;你好，我想退款&quot;, &quot;订单号是 #12345&quot;, &quot;退款多久能到账？&quot;]},</code> | 字段 <code>turns</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L501 | <code>]</code> | 结束/连接多行结构；本行没有独立业务动作。 |

## 结合全项目：设计缺口与增强方向

- 对话评测直接调用 Orchestrator，不经过 /chat 的 RAG/真实 Redis/Chroma 记忆读写。当前“端到端”范围是编排器级对话，不是完整服务链路。
- IntentTestCase.context 未传给 recognize；对话 Request 未填实体，编排器内部识别又没写回实体。评测与线上 HTTP 行为存在偏差。
- 裁判只看问题、回答与模拟历史，没有标准答案、知识证据或业务执行结果；accuracy 是主观评分，不能当事实正确率。
- 分数没有 0..1 校验，字段缺失默认 .5；裁判失败也给 .5，混入均分，应将服务失败与质量不及格分开。
- 每次运行都覆盖基线，并优先与上一次运行对比；不能防连续小幅退化。无模型/prompt/数据集版本，旧文件标注粒度与当前默认集不一致。
- pass_rate 将整组意图测试计 1 项、每轮对话计 1 项，不是全部单条样本准确率；默认 11 个意图样本+7 轮对话最后 total=8。
- 没有 CI 门禁或统计显著性判断；_recommendations 忽略低 accuracy 和 judge_failed，可能给出“所有指标均达标”的误导文字。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
