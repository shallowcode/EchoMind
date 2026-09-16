# core/intent_recognizer.py 解读

## 输入、输出与流向

**定位：** 把自然语言压缩成可供 RAG 和路由使用的结构化意图。

**输入：** message、最近 history；模型配置；可选 learn 纠正样本。

**输出 / 副作用：** IntentResult：细意图、粗分组、置信度、紧急度、实体、LLM 简短理由、来源分数、识别耗时；修改进程内缓存/模板。

**流向：** 上下文缓存 → LLM 与可选向量分支并发 + 本地关键词 → 加权投票/细化 → 正则实体 → 紧急度 → 写缓存。

[返回阅读入口](../../README.md) · [对照原文件](../../../core/intent_recognizer.py)

当前工作区快照：507 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`242fc4034a21bcf3458a33f37583c3cee0d26338f4d37f76892f488bafb4cda4`。

## 类与函数导航

[IntentCategory](#symbol-29) → [UrgencyLevel](#symbol-51) → [IntentResult](#symbol-58) → [_cosine](#symbol-132) → [IntentRecognizer](#symbol-140) → [IntentRecognizer.__init__](#symbol-148) → [IntentRecognizer.recognize](#symbol-173) → [IntentRecognizer.learn](#symbol-224) → [IntentRecognizer._llm_recognize](#symbol-234) → [IntentRecognizer._embedding_recognize](#symbol-290) → [IntentRecognizer._pattern_recognize](#symbol-307) → [IntentRecognizer._vote](#symbol-341) → [IntentRecognizer._extract_entities](#symbol-378) → [IntentRecognizer._load_template_embeddings](#symbol-391) → [IntentRecognizer._embed_text](#symbol-405) → [IntentRecognizer._local_embedding](#symbol-423) → [IntentRecognizer._urgency](#symbol-442) → [IntentRecognizer._cache_key](#symbol-453) → [IntentRecognizer._unique](#symbol-466) → [IntentRecognizer._best_pattern_match](#symbol-470) → [IntentRecognizer._intent_group](#symbol-486) → [IntentRecognizer._clean_text](#symbol-490) → [IntentRecognizer.cache_stats](#symbol-499)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>亮点：端到端意图识别</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>三路融合策略：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | <code>&nbsp;&nbsp;1. LLM 语义理解（权重 70%）—— 主力，理解复杂语义和上下文</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L6 | <code>&nbsp;&nbsp;2. Embedding 向量相似度（权重 20%）—— 快速匹配常见表达</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;3. 关键词模式匹配（权重 10%）—— 零延迟兜底</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L8 | （空行） | 空行，分隔逻辑。 |
| L9 | <code>三路结果通过加权投票合并，置信度低于阈值时降级为 OTHER。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L10 | <code>LLM 和 Embedding 并行调用，不串行等待。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L11 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L12 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L13 | <code>import hashlib</code> | 导入 <code>import hashlib</code>；只建立名称依赖，真正业务调用见后文。 |
| L14 | <code>import json</code> | 导入 <code>import json</code>；只建立名称依赖，真正业务调用见后文。 |
| L15 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L16 | <code>import re</code> | 导入 <code>import re</code>；只建立名称依赖，真正业务调用见后文。 |
| L17 | <code>import time</code> | 导入 <code>import time</code>；只建立名称依赖，真正业务调用见后文。 |
| L18 | <code>from dataclasses import dataclass, field</code> | 导入 <code>from dataclasses import dataclass, field</code>；只建立名称依赖，真正业务调用见后文。 |
| L19 | <code>from enum import Enum</code> | 导入 <code>from enum import Enum</code>；只建立名称依赖，真正业务调用见后文。 |
| L20 | <code>from typing import Any, Dict, List, Optional</code> | 导入 <code>from typing import Any, Dict, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L21 | （空行） | 空行，分隔逻辑。 |
| L22 | <code>from anthropic import AsyncAnthropic</code> | 导入 <code>from anthropic import AsyncAnthropic</code>；只建立名称依赖，真正业务调用见后文。 |
| L23 | （空行） | 空行，分隔逻辑。 |
| L24 | <code>from core.llm_utils import extract_text_content</code> | 导入 <code>from core.llm_utils import extract_text_content</code>；只建立名称依赖，真正业务调用见后文。 |
| L25 | （空行） | 空行，分隔逻辑。 |
| L26 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L27 | （空行） | 空行，分隔逻辑。 |
| L28 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-29"></a>

### L29–L48 · IntentCategory

19 个标签，粗分类与细分类同时存在。分类模型不是只做十分类；评测标注必须统一粒度。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L29 | <code>class IntentCategory(Enum):</code> | 定义 <code>IntentCategory</code> 的数据契约/行为；继承与字段见本段。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;QUERY      = &quot;query&quot;       # 查询信息</code> | 将结果保存到 <code>QUERY</code>：使用固定文本/配置值。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;COMPLAINT  = &quot;complaint&quot;   # 投诉不满</code> | 将结果保存到 <code>COMPLAINT</code>：使用固定文本/配置值。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;REQUEST    = &quot;request&quot;     # 请求操作</code> | 将结果保存到 <code>REQUEST</code>：使用固定文本/配置值。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;GREETING   = &quot;greeting&quot;    # 问候</code> | 将结果保存到 <code>GREETING</code>：使用固定文本/配置值。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ESCALATION = &quot;escalation&quot;  # 要求升级/转人工</code> | 将结果保存到 <code>ESCALATION</code>：使用固定文本/配置值。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;TECHNICAL  = &quot;technical&quot;   # 技术问题</code> | 将结果保存到 <code>TECHNICAL</code>：使用固定文本/配置值。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;BILLING    = &quot;billing&quot;     # 账单/退款</code> | 将结果保存到 <code>BILLING</code>：使用固定文本/配置值。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ACCOUNT    = &quot;account&quot;     # 账户管理</code> | 将结果保存到 <code>ACCOUNT</code>：使用固定文本/配置值。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;FEEDBACK   = &quot;feedback&quot;    # 正面反馈</code> | 将结果保存到 <code>FEEDBACK</code>：使用固定文本/配置值。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ORDER_STATUS = &quot;order_status&quot;        # 订单状态</code> | 将结果保存到 <code>ORDER_STATUS</code>：使用固定文本/配置值。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;LOGISTICS = &quot;logistics&quot;              # 物流配送</code> | 将结果保存到 <code>LOGISTICS</code>：使用固定文本/配置值。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;REFUND = &quot;refund&quot;                    # 退款/退货</code> | 将结果保存到 <code>REFUND</code>：使用固定文本/配置值。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;INVOICE = &quot;invoice&quot;                  # 发票</code> | 将结果保存到 <code>INVOICE</code>：使用固定文本/配置值。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;PAYMENT_ISSUE = &quot;payment_issue&quot;      # 支付/扣款异常</code> | 将结果保存到 <code>PAYMENT_ISSUE</code>：使用固定文本/配置值。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ACCOUNT_SECURITY = &quot;account_security&quot; # 账户安全</code> | 将结果保存到 <code>ACCOUNT_SECURITY</code>：使用固定文本/配置值。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;TECHNICAL_LOGIN = &quot;technical_login&quot;  # 登录认证故障</code> | 将结果保存到 <code>TECHNICAL_LOGIN</code>：使用固定文本/配置值。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;TECHNICAL_CRASH = &quot;technical_crash&quot;  # 崩溃/错误码</code> | 将结果保存到 <code>TECHNICAL_CRASH</code>：使用固定文本/配置值。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;HUMAN_HANDOFF = &quot;human_handoff&quot;      # 转人工</code> | 将结果保存到 <code>HUMAN_HANDOFF</code>：使用固定文本/配置值。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;OTHER      = &quot;other&quot;</code> | 将结果保存到 <code>OTHER</code>：使用固定文本/配置值。 |
| L49 | （空行） | 空行，分隔逻辑。 |
| L50 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-51"></a>

### L51–L55 · UrgencyLevel

四级枚举按数字表示严重程度，但由规则赋值，不是 LLM 风险评估。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L51 | <code>class UrgencyLevel(Enum):</code> | 定义 <code>UrgencyLevel</code> 的数据契约/行为；继承与字段见本段。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;LOW      = 1</code> | 将结果保存到 <code>LOW</code>：使用这里写明的固定值。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;MEDIUM   = 2</code> | 将结果保存到 <code>MEDIUM</code>：使用这里写明的固定值。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;HIGH     = 3</code> | 将结果保存到 <code>HIGH</code>：使用这里写明的固定值。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;CRITICAL = 4</code> | 将结果保存到 <code>CRITICAL</code>：使用这里写明的固定值。 |
| L56 | （空行） | 空行，分隔逻辑。 |
| L57 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-58"></a>

### L58–L67 · IntentResult

统一三路输出并保留来源分数，便于定位是 LLM、词面还是规则造成错分。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L58 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L59 | <code>class IntentResult:</code> | 定义 <code>IntentResult</code> 的数据契约/行为；继承与字段见本段。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent:     IntentCategory</code> | 声明字段 <code>intent</code> 的类型，赋值由构造方完成。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;confidence: float</code> | 声明字段 <code>confidence</code> 的类型，赋值由构造方完成。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;urgency:    UrgencyLevel</code> | 声明字段 <code>urgency</code> 的类型，赋值由构造方完成。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_group: str</code> | 声明字段 <code>intent_group</code> 的类型，赋值由构造方完成。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;entities:   Dict[str, List[str]]   # 从消息中提取的实体</code> | 声明字段 <code>entities</code> 的类型，赋值由构造方完成。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;reasoning:  str</code> | 声明字段 <code>reasoning</code> 的类型，赋值由构造方完成。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;latency_ms: float</code> | 声明字段 <code>latency_ms</code> 的类型，赋值由构造方完成。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;source_scores: Dict[str, float] = field(default_factory=dict)</code> | 将结果保存到 <code>source_scores</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L68 | （空行） | 空行，分隔逻辑。 |
| L69 | （空行） | 空行，分隔逻辑。 |
| L70 | <code># ── Few-shot 模板（同时用于 LLM 示例和 Embedding 匹配）────────────────────────</code> | 源码注释：── Few-shot 模板（同时用于 LLM 示例和 Embedding 匹配）──────────────────────── |
| L71 | <code>_TEMPLATES: Dict[IntentCategory, List[str]] = {</code> | 将结果保存到 <code>_TEMPLATES</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.QUERY:      [&quot;我的订单状态是什么？&quot;, &quot;如何重置密码？&quot;, &quot;快递什么时候到？&quot;],</code> | 字段 <code>IntentCategory.QUERY</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.COMPLAINT:  [&quot;等了好几个小时！&quot;, &quot;服务太差了！&quot;, &quot;一直没人处理！&quot;],</code> | 字段 <code>IntentCategory.COMPLAINT</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REQUEST:    [&quot;帮我取消订单&quot;, &quot;我需要修改地址&quot;, &quot;请协助退款&quot;],</code> | 字段 <code>IntentCategory.REQUEST</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.GREETING:   [&quot;你好&quot;, &quot;嗨，有人吗&quot;, &quot;早上好&quot;],</code> | 字段 <code>IntentCategory.GREETING</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ESCALATION: [&quot;我要投诉！&quot;, &quot;转人工客服&quot;, &quot;找你们经理&quot;],</code> | 字段 <code>IntentCategory.ESCALATION</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL:  [&quot;应用一直崩溃&quot;, &quot;无法登录&quot;, &quot;出现500错误&quot;],</code> | 字段 <code>IntentCategory.TECHNICAL</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.BILLING:    [&quot;为什么扣了两次款？&quot;, &quot;申请退款&quot;, &quot;发票问题&quot;],</code> | 字段 <code>IntentCategory.BILLING</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT:    [&quot;修改邮箱&quot;, &quot;注销账户&quot;, &quot;更新个人信息&quot;],</code> | 字段 <code>IntentCategory.ACCOUNT</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.FEEDBACK:   [&quot;服务很棒！&quot;, &quot;非常满意&quot;, &quot;给个好评&quot;],</code> | 字段 <code>IntentCategory.FEEDBACK</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ORDER_STATUS: [&quot;我的订单现在是什么状态？&quot;, &quot;订单有没有发货？&quot;, &quot;订单处理到哪一步了？&quot;],</code> | 字段 <code>IntentCategory.ORDER_STATUS</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.LOGISTICS: [&quot;快递什么时候到？&quot;, &quot;物流一直不更新&quot;, &quot;配送要多久？&quot;],</code> | 字段 <code>IntentCategory.LOGISTICS</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REFUND: [&quot;我要申请退款&quot;, &quot;退货退款怎么处理？&quot;, &quot;退款多久到账？&quot;],</code> | 字段 <code>IntentCategory.REFUND</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.INVOICE: [&quot;帮我开发票&quot;, &quot;发票抬头怎么改？&quot;, &quot;电子发票在哪里？&quot;],</code> | 字段 <code>IntentCategory.INVOICE</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.PAYMENT_ISSUE: [&quot;为什么重复扣款？&quot;, &quot;支付失败怎么办？&quot;, &quot;这个月多扣了钱&quot;],</code> | 字段 <code>IntentCategory.PAYMENT_ISSUE</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT_SECURITY: [&quot;账户被盗了&quot;, &quot;发现异常登录&quot;, &quot;我要重置密码&quot;],</code> | 字段 <code>IntentCategory.ACCOUNT_SECURITY</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_LOGIN: [&quot;登录一直报401&quot;, &quot;验证码收不到&quot;, &quot;无法登录账号&quot;],</code> | 字段 <code>IntentCategory.TECHNICAL_LOGIN</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_CRASH: [&quot;应用一直崩溃&quot;, &quot;页面报500错误&quot;, &quot;系统闪退&quot;],</code> | 字段 <code>IntentCategory.TECHNICAL_CRASH</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.HUMAN_HANDOFF: [&quot;转人工客服&quot;, &quot;我要找人工&quot;, &quot;请升级处理&quot;],</code> | 字段 <code>IntentCategory.HUMAN_HANDOFF</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L90 | <code>}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L91 | （空行） | 空行，分隔逻辑。 |
| L92 | <code>_SPECIFIC_INTENTS = {</code> | 将结果保存到 <code>_SPECIFIC_INTENTS</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ORDER_STATUS,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.LOGISTICS,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REFUND,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.INVOICE,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.PAYMENT_ISSUE,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT_SECURITY,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_LOGIN,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_CRASH,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.HUMAN_HANDOFF,</code> | 续接 L92 的表达式：按前述语句组装参数、条件或集合。 |
| L102 | <code>}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L103 | （空行） | 空行，分隔逻辑。 |
| L104 | <code>_GENERIC_INTENTS = {</code> | 将结果保存到 <code>_GENERIC_INTENTS</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.QUERY,</code> | 续接 L104 的表达式：按前述语句组装参数、条件或集合。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.BILLING,</code> | 续接 L104 的表达式：按前述语句组装参数、条件或集合。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL,</code> | 续接 L104 的表达式：按前述语句组装参数、条件或集合。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT,</code> | 续接 L104 的表达式：按前述语句组装参数、条件或集合。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ESCALATION,</code> | 续接 L104 的表达式：按前述语句组装参数、条件或集合。 |
| L110 | <code>}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L111 | （空行） | 空行，分隔逻辑。 |
| L112 | <code>_INTENT_GROUPS: Dict[IntentCategory, IntentCategory] = {</code> | 将结果保存到 <code>_INTENT_GROUPS</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ORDER_STATUS: IntentCategory.QUERY,</code> | 字段 <code>IntentCategory.ORDER_STATUS</code>（当前映射中的键）：读取 <code>IntentCategory.QUERY</code>。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.LOGISTICS: IntentCategory.QUERY,</code> | 字段 <code>IntentCategory.LOGISTICS</code>（当前映射中的键）：读取 <code>IntentCategory.QUERY</code>。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REFUND: IntentCategory.BILLING,</code> | 字段 <code>IntentCategory.REFUND</code>（当前映射中的键）：读取 <code>IntentCategory.BILLING</code>。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.INVOICE: IntentCategory.BILLING,</code> | 字段 <code>IntentCategory.INVOICE</code>（当前映射中的键）：读取 <code>IntentCategory.BILLING</code>。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.PAYMENT_ISSUE: IntentCategory.BILLING,</code> | 字段 <code>IntentCategory.PAYMENT_ISSUE</code>（当前映射中的键）：读取 <code>IntentCategory.BILLING</code>。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT_SECURITY: IntentCategory.ACCOUNT,</code> | 字段 <code>IntentCategory.ACCOUNT_SECURITY</code>（当前映射中的键）：读取 <code>IntentCategory.ACCOUNT</code>。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_LOGIN: IntentCategory.TECHNICAL,</code> | 字段 <code>IntentCategory.TECHNICAL_LOGIN</code>（当前映射中的键）：读取 <code>IntentCategory.TECHNICAL</code>。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_CRASH: IntentCategory.TECHNICAL,</code> | 字段 <code>IntentCategory.TECHNICAL_CRASH</code>（当前映射中的键）：读取 <code>IntentCategory.TECHNICAL</code>。 |
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.HUMAN_HANDOFF: IntentCategory.ESCALATION,</code> | 字段 <code>IntentCategory.HUMAN_HANDOFF</code>（当前映射中的键）：读取 <code>IntentCategory.ESCALATION</code>。 |
| L122 | <code>}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L123 | （空行） | 空行，分隔逻辑。 |
| L124 | <code># 紧急关键词</code> | 源码注释：紧急关键词 |
| L125 | <code>_URGENCY_KEYWORDS = {</code> | 将结果保存到 <code>_URGENCY_KEYWORDS</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;UrgencyLevel.CRITICAL: [&quot;紧急&quot;, &quot;emergency&quot;, &quot;urgent&quot;, &quot;asap&quot;, &quot;立刻&quot;],</code> | 字段 <code>UrgencyLevel.CRITICAL</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;UrgencyLevel.HIGH:     [&quot;今天&quot;, &quot;马上&quot;, &quot;尽快&quot;, &quot;hurry&quot;, &quot;now&quot;],</code> | 字段 <code>UrgencyLevel.HIGH</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;UrgencyLevel.MEDIUM:   [&quot;这周&quot;, &quot;soon&quot;, &quot;快点&quot;],</code> | 字段 <code>UrgencyLevel.MEDIUM</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L129 | <code>}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L130 | （空行） | 空行，分隔逻辑。 |
| L131 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-132"></a>

### L132–L137 · _cosine

点积除以两向量模长；零向量返回 0。zip 遇维度不一致会截断，远端/本地混用时应另加维度校验。

**签名输入：** <code>a: List[float], b: List[float]</code>；**返回契约：** <code>float</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L132 | <code>def _cosine(a: List[float], b: List[float]) -&gt; float:</code> | 定义函数 <code>_cosine</code>；输入参数见签名，下方导读解释调用目的。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;纯 Python 余弦相似度，不依赖 numpy。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;dot = sum(x * y for x, y in zip(a, b))</code> | 将结果保存到 <code>dot</code>：累加各项数值/布尔命中值。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;na  = sum(x * x for x in a) ** 0.5</code> | 将结果保存到 <code>na</code>：按此表达式计算 <code>sum((x * x for x in a)) ** 0.5</code>。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;nb  = sum(x * x for x in b) ** 0.5</code> | 将结果保存到 <code>nb</code>：按此表达式计算 <code>sum((x * x for x in b)) ** 0.5</code>。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return dot / (na * nb) if na and nb else 0.0</code> | 结束当前函数并返回；条件 <code>na and nb</code> 成立选前值，否则选 else 后值。 |
| L138 | （空行） | 空行，分隔逻辑。 |
| L139 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-140"></a>

### L140–L507 · IntentRecognizer

把自然语言压缩成可供 RAG 和路由使用的结构化意图。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L140 | <code>class IntentRecognizer:</code> | 定义 <code>IntentRecognizer</code> 的数据契约/行为；继承与字段见本段。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;端到端意图识别器。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L143 | （空行） | 空行，分隔逻辑。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;初始化时不加载任何本地模型，所有 AI 能力通过 Anthropic API 调用。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;模板 Embedding 在首次请求时懒加载并缓存，后续复用。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L147 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-148"></a>

### L148–L169 · IntentRecognizer.__init__

记录模型与 .5 阈值；base_url 决定是否运行 embedding；模板向量、结果缓存都是当前对象内存。

**签名输入：** <code>self, api_key: str, base_url: Optional[str]=None, model: str=&#x27;claude-3-5-sonnet-20241022&#x27;, confidence_threshold: float=0.5</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url: Optional[str] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model: str = &quot;claude-3-5-sonnet-20241022&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;confidence_threshold: float = 0.5,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs: Dict[str, Any] = {&quot;api_key&quot;: api_key}</code> | 将结果保存到 <code>kwargs</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if base_url:</code> | 判断 <code>base_url</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs[&quot;base_url&quot;] = base_url</code> | 将结果保存到 <code>kwargs[&#x27;base_url&#x27;]</code>：读取 <code>base_url</code>。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.client    = AsyncAnthropic(**kwargs)</code> | 将结果保存到 <code>self.client</code>：调用 <code>AsyncAnthropic</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.model     = model</code> | 将结果保存到 <code>self.model</code>：读取 <code>model</code>。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.threshold = confidence_threshold</code> | 将结果保存到 <code>self.threshold</code>：读取 <code>confidence_threshold</code>。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 第三方兼容 API（如 DeepSeek）通常不支持 Embedding，禁用该策略。</code> | 源码注释：第三方兼容 API（如 DeepSeek）通常不支持 Embedding，禁用该策略。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 官方 Anthropic SDK 当前没有 embeddings 资源，因此下面会使用稳定的</code> | 源码注释：官方 Anthropic SDK 当前没有 embeddings 资源，因此下面会使用稳定的 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 本地字符 n-gram 向量作为轻量兜底，保证三路融合链路真实可跑。</code> | 源码注释：本地字符 n-gram 向量作为轻量兜底，保证三路融合链路真实可跑。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._embedding_enabled = not bool(base_url)</code> | **关键：**base_url 非空直接禁用；不是探测服务能力后关闭。 |
| L165 | （空行） | 空行，分隔逻辑。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._tpl_embeddings: Dict[IntentCategory, List[List[float]]] = {}</code> | 将结果保存到 <code>self._tpl_embeddings</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._cache: Dict[str, IntentResult] = {}</code> | 将结果保存到 <code>self._cache</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cache_hits   = 0</code> | 将结果保存到 <code>self.cache_hits</code>：使用这里写明的固定值。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cache_misses = 0</code> | 将结果保存到 <code>self.cache_misses</code>：使用这里写明的固定值。 |
| L170 | （空行） | 空行，分隔逻辑。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 公开接口 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 公开接口 ────────────────────────────────────────────────────────────── |
| L172 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-173"></a>

### L173–L222 · IntentRecognizer.recognize

先按当前消息和最近历史查缓存。LLM 与向量异步调度，关键词同步运行；融合后实体/紧急度再独立计算。返回分组和细类便于兼容不同粒度消费者。

**签名输入：** <code>self, message: str, history: Optional[List[Dict[str, str]]]=None</code>；**返回契约：** <code>IntentResult</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def recognize(</code> | 定义异步函数 <code>recognize</code>；输入参数见签名，下方导读解释调用目的。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history: Optional[List[Dict[str, str]]] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; IntentResult:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;识别用户意图。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L180 | （空行） | 空行，分隔逻辑。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history 格式：[{&quot;role&quot;: &quot;user&quot;/&quot;assistant&quot;, &quot;content&quot;: &quot;...&quot;}]</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key = self._cache_key(message, history)</code> | 将结果保存到 <code>key</code>：调用 <code>self._cache_key</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if key in self._cache:</code> | 判断 <code>key in self._cache</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cache_hits += 1</code> | 更新 <code>self.cache_hits</code>：<code>self.cache_hits += 1</code>；此处会改变累计状态。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self._cache[key]</code> | 结束当前函数并返回；按索引/切片取 <code>self._cache[key]</code>，注意是否截掉旧历史或长文本。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cache_misses += 1</code> | 更新 <code>self.cache_misses</code>：<code>self.cache_misses += 1</code>；此处会改变累计状态。 |
| L188 | （空行） | 空行，分隔逻辑。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;t0 = time.monotonic()</code> | 将结果保存到 <code>t0</code>：读取单调时钟，用来算耗时/过期，不作为日历时间。 |
| L190 | （空行） | 空行，分隔逻辑。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# LLM 和 Embedding 并行（Embedding 不可用时跳过）</code> | 源码注释：LLM 和 Embedding 并行（Embedding 不可用时跳过） |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;llm_task = asyncio.create_task(self._llm_recognize(message, history))</code> | 将结果保存到 <code>llm_task</code>：将协程安排为后台任务，当前行不等待业务完成。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emb_task = asyncio.create_task(self._embedding_recognize(message)) if self._embedding_enabled else None</code> | 将结果保存到 <code>emb_task</code>：条件 <code>self._embedding_enabled</code> 成立选前值，否则选 else 后值。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pat      = self._pattern_recognize(message)</code> | 将结果保存到 <code>pat</code>：进入 <code>self._pattern_recognize</code>：先扫描细类词表，任一细类命中就不看粗类词表；相同命中分数保留字典中先出现者。 |
| L195 | （空行） | 空行，分隔逻辑。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if emb_task:</code> | 判断 <code>emb_task</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;llm, emb = await asyncio.gather(llm_task, emb_task)</code> | 将结果保存到 <code>(llm, emb)</code>：等待完成后继续；并发等待这批任务，结果顺序与输入任务顺序一致。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;llm = await llm_task</code> | 将结果保存到 <code>llm</code>：等待完成后继续；读取 <code>llm_task</code>。 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;emb = {&quot;intent&quot;: IntentCategory.OTHER, &quot;confidence&quot;: 0.0}</code> | 将结果保存到 <code>emb</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L201 | （空行） | 空行，分隔逻辑。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent, confidence, source_scores = self._vote(llm, emb, pat)</code> | 将结果保存到 <code>(intent, confidence, source_scores)</code>：进入 <code>self._vote</code>：把每路置信度乘固定权重累加到该路选择的类别。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entities = self._extract_entities(message)</code> | 将结果保存到 <code>entities</code>：进入 <code>self._extract_entities</code>：正则抽订单号、日期、金额、错误码，product 保留空槽位。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;urgency  = self._urgency(message, intent)</code> | 将结果保存到 <code>urgency</code>：进入 <code>self._urgency</code>：按 CRITICAL/HIGH/MEDIUM 词表顺序扫描，首次命中返回；没有命中再按转人工/投诉意图给默认等级。 |
| L205 | （空行） | 空行，分隔逻辑。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result = IntentResult(</code> | 将结果保存到 <code>result</code>：进入 <code>IntentResult</code>：统一三路输出并保留来源分数，便于定位是 LLM、词面还是规则造成错分。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent=intent,</code> | 参数 <code>intent</code>（意图标签）：读取 <code>intent</code>。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;confidence=confidence,</code> | 参数 <code>confidence</code>（置信度分数）：读取 <code>confidence</code>。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;urgency=urgency,</code> | 参数 <code>urgency</code>（紧急程度）：读取 <code>urgency</code>。 |
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_group=self._intent_group(intent),</code> | 参数 <code>intent_group</code>（粗意图组）：进入 <code>self._intent_group</code>：将 refund/invoice 等映射到 billing；未映射就返回自身 value。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entities=entities,</code> | 参数 <code>entities</code>（结构化实体）：读取 <code>entities</code>。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reasoning=llm.get(&quot;reasoning&quot;, &quot;&quot;),</code> | 参数 <code>reasoning</code>（reasoning）：按键取值，缺失用给定默认值。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=(time.monotonic() - t0) * 1000,</code> | 参数 <code>latency_ms</code>（当前计时范围的毫秒耗时）：按此表达式计算 <code>(time.monotonic() - t0) * 1000</code>。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;source_scores=source_scores,</code> | 参数 <code>source_scores</code>（source_scores）：读取 <code>source_scores</code>。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L216 | （空行） | 空行，分隔逻辑。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# LRU 缓存</code> | 源码注释：LRU 缓存 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(self._cache) &gt;= 1000:</code> | 判断 <code>len(self._cache) &gt;= 1000</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for k in list(self._cache)[:500]:</code> | **关键：**删除最先插入的 500 个键，没有记录最近访问，故不是 LRU。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;del self._cache[k]</code> | 删除 <code>del self._cache[k]</code> 对应状态；淘汰/重建逻辑需看外层范围。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._cache[key] = result</code> | 将结果保存到 <code>self._cache[key]</code>：读取 <code>result</code>。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return result</code> | 结束当前函数并返回；读取 <code>result</code>。 |
| L223 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-224"></a>

### L224–L230 · IntentRecognizer.learn

将纠正消息加入类模板，删除该类向量缓存使下一次重算；不是参数微调，也不是完整在线学习闭环。

**签名输入：** <code>self, message: str, correct: IntentCategory</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def learn(self, message: str, correct: IntentCategory) -&gt; None:</code> | 定义函数 <code>learn</code>；输入参数见签名，下方导读解释调用目的。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;在线学习：将纠正样本加入模板，清除对应 Embedding 缓存。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tpls = _TEMPLATES.setdefault(correct, [])</code> | 将结果保存到 <code>tpls</code>：调用 <code>_TEMPLATES.setdefault</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if message not in tpls:</code> | 判断 <code>message not in tpls</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tpls.append(message)</code> | 追加一个元素到当前列表。 |
| L229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._tpl_embeddings.pop(correct, None)  # 下次重新计算</code> | 移除并取出键/元素。 |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;学习新样本 → {correct.value}: {message[:40]}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L231 | （空行） | 空行，分隔逻辑。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 三路识别策略 ──────────────────────────────────────────────────────────</code> | 源码注释：── 三路识别策略 ────────────────────────────────────────────────────────── |
| L233 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-234"></a>

### L234–L288 · IntentRecognizer._llm_recognize

每类一条示例 + 最近三条消息 + 可选标签，要求 JSON。最近三条消息不是三轮 user/assistant 对。模型异常转换成 failed=True 供融合层降级。

**签名输入：** <code>self, message: str, history: Optional[List[Dict[str, str]]]</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _llm_recognize(</code> | 定义异步函数 <code>_llm_recognize</code>；输入参数见签名，下方导读解释调用目的。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history: Optional[List[Dict[str, str]]],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; Dict[str, Any]:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;策略 1：LLM 语义理解（Few-shot + 上下文）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message = self._clean_text(message)</code> | 将结果保存到 <code>message</code>：调用 <code>self._clean_text</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 构建 Few-shot 示例</code> | 源码注释：构建 Few-shot 示例 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;examples = &quot;\n&quot;.join(</code> | 将结果保存到 <code>examples</code>：把字符串片段按分隔符合并。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&#x27;  消息: &quot;{t}&quot; → 意图: {cat.value}&#x27;</code> | 续接 L242 的表达式：按前述语句组装参数、条件或集合。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for cat, tpls in _TEMPLATES.items()</code> | 续接 L242 的表达式：按前述语句组装参数、条件或集合。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for t in tpls[:1]  # 每类取 1 条，控制 prompt 长度</code> | **关键：**每类永远只取第一条示例，learn 追加的尾部样本不会直接出现在这里。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 最近 3 轮对话上下文</code> | 源码注释：最近 3 轮对话上下文 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ctx = &quot;&quot;</code> | 将结果保存到 <code>ctx</code>：使用固定文本/配置值。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if history:</code> | 判断 <code>history</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ctx = &quot;\n最近对话:\n&quot; + &quot;\n&quot;.join(</code> | 将结果保存到 <code>ctx</code>：按此表达式计算 <code>&#x27;\n最近对话:\n&#x27; + &#x27;\n&#x27;.join((f&quot;  {self._clean_text(m.get(&#x27;role&#x27;, &#x27;user&#x27;))}: {self._clean_text(m.get(&#x27;content&#x27;, &#x27;&#x27;))}&quot; for m in history[-3:]…</code>。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;  {self._clean_text(m.get(&#x27;role&#x27;, &#x27;user&#x27;))}: {self._clean_text(m.get(&#x27;content&#x27;, &#x27;&#x27;))}&quot;</code> | 续接 L250 的表达式：按前述语句组装参数、条件或集合。 |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for m in history[-3:]</code> | 续接 L250 的表达式：按前述语句组装参数、条件或集合。 |
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L254 | （空行） | 空行，分隔逻辑。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = f&quot;&quot;&quot;你是客服意图分析专家。根据示例判断用户意图，返回 JSON。</code> | 将结果保存到 <code>prompt</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L256 | <code>如果用户问题能匹配细粒度业务意图，请优先返回细粒度意图，而不是宽泛大类。</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L257 | <code>例如退款优先返回 refund，发票优先返回 invoice，登录故障优先返回 technical_login。</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L258 | （空行） | 空行，分隔逻辑。 |
| L259 | <code>示例:</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L260 | <code>{examples}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L261 | （空行） | 空行，分隔逻辑。 |
| L262 | <code>{ctx}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L263 | <code>用户消息: &quot;{message}&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L264 | （空行） | 空行，分隔逻辑。 |
| L265 | <code>返回格式（仅 JSON，不要其他文字）:</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L266 | <code>{{&quot;intent&quot;: &quot;&lt;意图值&gt;&quot;, &quot;confidence&quot;: &lt;0-1&gt;, &quot;reasoning&quot;: &quot;&lt;一句话说明&gt;&quot;}}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L267 | （空行） | 空行，分隔逻辑。 |
| L268 | <code>可选意图: {&quot;, &quot;.join(c.value for c in IntentCategory)}&quot;&quot;&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = self._clean_text(prompt)</code> | 将结果保存到 <code>prompt</code>：调用 <code>self._clean_text</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L270 | （空行） | 空行，分隔逻辑。 |
| L271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await self.client.messages.create(</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算。 |
| L273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=self.model,</code> | 参数 <code>model</code>（模型名称）：读取 <code>self.model</code>。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_tokens=256,</code> | 参数 <code>max_tokens</code>（模型最多输出 token 数）：使用这里写明的固定值。 |
| L275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;temperature=0.1,</code> | 参数 <code>temperature</code>（生成采样温度）：使用这里写明的固定值。 |
| L276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: prompt}],</code> | 参数 <code>messages</code>（模型消息序列/当前函数的消息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = extract_text_content(resp.content)</code> | 将结果保存到 <code>raw</code>：进入共享响应适配器，只保留模型文本块。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;s, e = raw.find(&quot;{&quot;), raw.rfind(&quot;}&quot;) + 1</code> | 将结果保存到 <code>(s, e)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data = json.loads(raw[s:e])</code> | 将结果保存到 <code>data</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data[&quot;intent&quot;] = IntentCategory(data[&quot;intent&quot;])</code> | 将结果保存到 <code>data[&#x27;intent&#x27;]</code>：进入 <code>IntentCategory</code>：19 个标签，粗分类与细分类同时存在。 |
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except ValueError:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data[&quot;intent&quot;] = IntentCategory.OTHER</code> | 将结果保存到 <code>data[&#x27;intent&#x27;]</code>：读取 <code>IntentCategory.OTHER</code>。 |
| L285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return data</code> | 结束当前函数并返回；读取 <code>data</code>。 |
| L286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;LLM 识别失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;intent&quot;: IntentCategory.OTHER, &quot;confidence&quot;: 0.0, &quot;reasoning&quot;: &quot;LLM 失败&quot;, &quot;failed&quot;: True}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L289 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-290"></a>

### L290–L305 · IntentRecognizer._embedding_recognize

消息向量与所有模板逐一余弦比较，每类取最相似模板，然后选最大类别。模板匹配适合熟悉表达，但向量兜底是词面近似。

**签名输入：** <code>self, message: str</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _embedding_recognize(self, message: str) -&gt; Dict[str, Any]:</code> | 定义异步函数 <code>_embedding_recognize</code>；输入参数见签名，下方导读解释调用目的。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;策略 2：Embedding 向量相似度匹配。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._load_template_embeddings()</code> | 等待完成后继续；进入 <code>self._load_template_embeddings</code>：只计算 _tpl_embeddings 尚无的类别，按扁平顺序计算再切回各类别，减少重复计算。 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg_vec = await self._embed_text(message)</code> | 将结果保存到 <code>msg_vec</code>：等待完成后继续；进入 <code>self._embed_text</code>：动态检测客户端是否具备 embeddings 属性；若有尝试远端，异常/不存在则本地哈希。 |
| L295 | （空行） | 空行，分隔逻辑。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best_cat, best_score = IntentCategory.OTHER, 0.0</code> | 将结果保存到 <code>(best_cat, best_score)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for cat, vecs in self._tpl_embeddings.items():</code> | 遍历 <code>self._tpl_embeddings.items()</code>，本轮元素绑定 <code>(cat, vecs)</code>。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;score = max(_cosine(msg_vec, v) for v in vecs)</code> | 将结果保存到 <code>score</code>：取当前候选中的最大值。 |
| L299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if score &gt; best_score:</code> | 判断 <code>score &gt; best_score</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best_score, best_cat = score, cat</code> | 将结果保存到 <code>(best_score, best_cat)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L301 | （空行） | 空行，分隔逻辑。 |
| L302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;intent&quot;: best_cat, &quot;confidence&quot;: best_score}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;Embedding 识别失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;intent&quot;: IntentCategory.OTHER, &quot;confidence&quot;: 0.0}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L306 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-307"></a>

### L307–L337 · IntentRecognizer._pattern_recognize

先扫描细类词表，任一细类命中就不看粗类词表；相同命中分数保留字典中先出现者。词表顺序会影响结果。

**签名输入：** <code>self, message: str</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _pattern_recognize(self, message: str) -&gt; Dict[str, Any]:</code> | 定义函数 <code>_pattern_recognize</code>；输入参数见签名，下方导读解释调用目的。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;策略 3：关键词模式匹配（同步，零延迟兜底）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg = message.lower()</code> | 将结果保存到 <code>msg</code>：转小写进行大小写无关比较。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;specific_patterns = {</code> | 将结果保存到 <code>specific_patterns</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.HUMAN_HANDOFF: [&quot;转人工&quot;, &quot;人工客服&quot;, &quot;找人工&quot;],</code> | 字段 <code>IntentCategory.HUMAN_HANDOFF</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ORDER_STATUS: [&quot;订单状态&quot;, &quot;发货了吗&quot;, &quot;处理到哪&quot;, &quot;order status&quot;],</code> | 字段 <code>IntentCategory.ORDER_STATUS</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.LOGISTICS: [&quot;物流&quot;, &quot;快递&quot;, &quot;配送&quot;, &quot;运单&quot;, &quot;delivery&quot;, &quot;shipping&quot;],</code> | 字段 <code>IntentCategory.LOGISTICS</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REFUND: [&quot;退款&quot;, &quot;退货&quot;, &quot;refund&quot;, &quot;return&quot;],</code> | 字段 <code>IntentCategory.REFUND</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.INVOICE: [&quot;发票&quot;, &quot;抬头&quot;, &quot;税号&quot;, &quot;invoice&quot;],</code> | 字段 <code>IntentCategory.INVOICE</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.PAYMENT_ISSUE: [&quot;重复扣款&quot;, &quot;多扣&quot;, &quot;支付失败&quot;, &quot;扣费&quot;, &quot;payment failed&quot;],</code> | 字段 <code>IntentCategory.PAYMENT_ISSUE</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT_SECURITY: [&quot;被盗&quot;, &quot;异常登录&quot;, &quot;重置密码&quot;, &quot;两步验证&quot;, &quot;安全&quot;],</code> | 字段 <code>IntentCategory.ACCOUNT_SECURITY</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_LOGIN: [&quot;无法登录&quot;, &quot;登录失败&quot;, &quot;401&quot;, &quot;验证码&quot;],</code> | 字段 <code>IntentCategory.TECHNICAL_LOGIN</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL_CRASH: [&quot;崩溃&quot;, &quot;闪退&quot;, &quot;500&quot;, &quot;报错&quot;, &quot;crash&quot;],</code> | 字段 <code>IntentCategory.TECHNICAL_CRASH</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;generic_patterns = {</code> | 将结果保存到 <code>generic_patterns</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ESCALATION: [&quot;投诉&quot;, &quot;经理&quot;, &quot;supervisor&quot;],</code> | 字段 <code>IntentCategory.ESCALATION</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.COMPLAINT:  [&quot;太差&quot;, &quot;糟糕&quot;, &quot;horrible&quot;, &quot;等了很久&quot;],</code> | 字段 <code>IntentCategory.COMPLAINT</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.QUERY:      [&quot;?&quot;, &quot;？&quot;, &quot;怎么&quot;, &quot;什么&quot;, &quot;status&quot;],</code> | 字段 <code>IntentCategory.QUERY</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.REQUEST:    [&quot;帮我&quot;, &quot;需要&quot;, &quot;please&quot;, &quot;help&quot;],</code> | 字段 <code>IntentCategory.REQUEST</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.GREETING:   [&quot;你好&quot;, &quot;嗨&quot;, &quot;hello&quot;, &quot;hi&quot;],</code> | 字段 <code>IntentCategory.GREETING</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.BILLING:    [&quot;退款&quot;, &quot;扣款&quot;, &quot;发票&quot;, &quot;refund&quot;],</code> | 字段 <code>IntentCategory.BILLING</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.TECHNICAL:  [&quot;崩溃&quot;, &quot;报错&quot;, &quot;error&quot;, &quot;crash&quot;],</code> | 字段 <code>IntentCategory.TECHNICAL</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentCategory.ACCOUNT:    [&quot;密码&quot;, &quot;邮箱&quot;, &quot;账户&quot;, &quot;password&quot;],</code> | 字段 <code>IntentCategory.ACCOUNT</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L331 | （空行） | 空行，分隔逻辑。 |
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best_cat, best_score = self._best_pattern_match(msg, specific_patterns)</code> | 将结果保存到 <code>(best_cat, best_score)</code>：进入 <code>self._best_pattern_match</code>：命中 1 个词=.5，2 个=.75，3 个及以上=1。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if best_cat != IntentCategory.OTHER:</code> | 判断 <code>best_cat != IntentCategory.OTHER</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;intent&quot;: best_cat, &quot;confidence&quot;: best_score}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L335 | （空行） | 空行，分隔逻辑。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best_cat, best_score = self._best_pattern_match(msg, generic_patterns)</code> | 将结果保存到 <code>(best_cat, best_score)</code>：进入 <code>self._best_pattern_match</code>：命中 1 个词=.5，2 个=.75，3 个及以上=1。 |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;intent&quot;: best_cat, &quot;confidence&quot;: best_score}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L338 | （空行） | 空行，分隔逻辑。 |
| L339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 投票合并 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 投票合并 ────────────────────────────────────────────────────────────── |
| L340 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-341"></a>

### L341–L374 · IntentRecognizer._vote

把每路置信度乘固定权重累加到该路选择的类别。来源分数是原始分，不是贡献值；失败降级、粗类细化都可以绕过一般阈值逻辑。

**签名输入：** <code>self, llm: Dict, emb: Dict, pat: Dict</code>；**返回契约：** <code>tuple[IntentCategory, float, Dict[str, float]]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L341 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _vote(self, llm: Dict, emb: Dict, pat: Dict) -&gt; tuple[IntentCategory, float, Dict[str, float]]:</code> | 定义函数 <code>_vote</code>；输入参数见签名，下方导读解释调用目的。 |
| L342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;加权投票。返回最终意图、融合置信度和各路来源得分。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;source_scores = {</code> | 将结果保存到 <code>source_scores</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;llm&quot;: float(llm.get(&quot;confidence&quot;, 0.0) or 0.0),</code> | 字段 <code>llm</code>（当前映射中的键）：转换为浮点数；无效输入会抛出异常。 |
| L345 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;embedding&quot;: float(emb.get(&quot;confidence&quot;, 0.0) or 0.0),</code> | 字段 <code>embedding</code>（当前映射中的键）：转换为浮点数；无效输入会抛出异常。 |
| L346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;pattern&quot;: float(pat.get(&quot;confidence&quot;, 0.0) or 0.0),</code> | 字段 <code>pattern</code>（当前映射中的键）：转换为浮点数；无效输入会抛出异常。 |
| L347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L348 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if llm.get(&quot;failed&quot;):</code> | 判断 <code>llm.get(&#x27;failed&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if emb.get(&quot;intent&quot;) != IntentCategory.OTHER and emb.get(&quot;confidence&quot;, 0.0) &gt; 0:</code> | 判断 <code>emb.get(&#x27;intent&#x27;) != IntentCategory.OTHER and emb.get(&#x27;confidence&#x27;, 0.0) &gt; 0</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return emb[&quot;intent&quot;], source_scores[&quot;embedding&quot;], source_scores</code> | **关键：**即使向量置信度很低，只要大于零就接受；没有应用 threshold。 |
| L351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if pat.get(&quot;intent&quot;) != IntentCategory.OTHER and pat.get(&quot;confidence&quot;, 0.0) &gt; 0:</code> | 判断 <code>pat.get(&#x27;intent&#x27;) != IntentCategory.OTHER and pat.get(&#x27;confidence&#x27;, 0.0) &gt; 0</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L352 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return pat[&quot;intent&quot;], source_scores[&quot;pattern&quot;], source_scores</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L353 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return IntentCategory.OTHER, 0.0, source_scores</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L354 | （空行） | 空行，分隔逻辑。 |
| L355 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._embedding_enabled:</code> | 判断 <code>self._embedding_enabled</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;weights = [(llm, 0.7), (emb, 0.2), (pat, 0.1)]</code> | 将结果保存到 <code>weights</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L358 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;weights = [(llm, 0.85), (pat, 0.15)]</code> | 将结果保存到 <code>weights</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L359 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores: Dict[IntentCategory, float] = {}</code> | 将结果保存到 <code>scores</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for result, w in weights:</code> | 遍历 <code>weights</code>，本轮元素绑定 <code>(result, w)</code>。 |
| L361 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cat  = result.get(&quot;intent&quot;, IntentCategory.OTHER)</code> | 将结果保存到 <code>cat</code>：按键取值，缺失用给定默认值。 |
| L362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conf = result.get(&quot;confidence&quot;, 0.0)</code> | 将结果保存到 <code>conf</code>：按键取值，缺失用给定默认值。 |
| L363 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;scores[cat] = scores.get(cat, 0.0) + w * conf</code> | 将结果保存到 <code>scores[cat]</code>：按此表达式计算 <code>scores.get(cat, 0.0) + w * conf</code>。 |
| L364 | （空行） | 空行，分隔逻辑。 |
| L365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best = max(scores, key=scores.get)  # type: ignore</code> | 将结果保存到 <code>best</code>：取当前候选中的最大值。 |
| L366 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best_score = scores[best]</code> | 将结果保存到 <code>best_score</code>：按索引/切片取 <code>scores[best]</code>，注意是否截掉旧历史或长文本。 |
| L367 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pat_intent = pat.get(&quot;intent&quot;, IntentCategory.OTHER)</code> | 将结果保存到 <code>pat_intent</code>：按键取值，缺失用给定默认值。 |
| L368 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pat_conf = float(pat.get(&quot;confidence&quot;, 0.0) or 0.0)</code> | 将结果保存到 <code>pat_conf</code>：转换为浮点数；无效输入会抛出异常。 |
| L369 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if best in _GENERIC_INTENTS and pat_intent in _SPECIFIC_INTENTS and pat_conf &gt;= 0.5 and best_score &lt; 0.8:</code> | **关键：**没有验证 _intent_group(best)==_intent_group(pat_intent)，存在跨领域细化。 |
| L370 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;source_scores[&quot;refined_by_pattern&quot;] = pat_conf</code> | 将结果保存到 <code>source_scores[&#x27;refined_by_pattern&#x27;]</code>：读取 <code>pat_conf</code>。 |
| L371 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return pat_intent, max(best_score, pat_conf), source_scores</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L372 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if best_score &lt; self.threshold:</code> | 判断 <code>best_score &lt; self.threshold</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L373 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return IntentCategory.OTHER, best_score, source_scores</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L374 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return best, best_score, source_scores</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L375 | （空行） | 空行，分隔逻辑。 |
| L376 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 实体提取 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 实体提取 ────────────────────────────────────────────────────────────── |
| L377 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-378"></a>

### L378–L387 · IntentRecognizer._extract_entities

正则抽订单号、日期、金额、错误码，product 保留空槽位。金额保留单位，日期仍是原文本，没有转换成统一时间。

**签名输入：** <code>self, message: str</code>；**返回契约：** <code>Dict[str, List[str]]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _extract_entities(self, message: str) -&gt; Dict[str, List[str]]:</code> | 定义函数 <code>_extract_entities</code>；输入参数见签名，下方导读解释调用目的。 |
| L379 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;用规则提取高价值实体，避免每次识别都额外调用 LLM。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message = self._clean_text(message)</code> | 将结果保存到 <code>message</code>：调用 <code>self._clean_text</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;order_id&quot;: self._unique(re.findall(r&quot;(?:订单号?&#124;order(?:_id)?&#124;#)\s*[:：#]?\s*([A-Za-z0-9_-]{4,32})&quot;, message, re.I)),</code> | 字段 <code>order_id</code>（当前映射中的键）：进入 <code>self._unique</code>：dict.fromkeys 保序去重，先过滤空白字符串。 |
| L383 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;product&quot;: [],</code> | **关键：**产品实体设计了输出键，但未实现提取。 |
| L384 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;date&quot;: self._unique(re.findall(r&quot;(今天&#124;明天&#124;昨天&#124;本周&#124;这周&#124;下周&#124;\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2}日?)&quot;, message)),</code> | 字段 <code>date</code>（当前映射中的键）：进入 <code>self._unique</code>：dict.fromkeys 保序去重，先过滤空白字符串。 |
| L385 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;amount&quot;: self._unique(re.findall(r&quot;((?:¥&#124;￥)\s*\d+(?:\.\d{1,2})?&#124;\d+(?:\.\d{1,2})?\s*(?:元&#124;块&#124;rmb&#124;cny&#124;usd&#124;美元))&quot;, message, re.I)),</code> | 字段 <code>amount</code>（当前映射中的键）：进入 <code>self._unique</code>：dict.fromkeys 保序去重，先过滤空白字符串。 |
| L386 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;error_code&quot;: self._unique(re.findall(r&quot;\b([45]\d{2}&#124;[A-Z][A-Z0-9_-]{2,16})\b&quot;, message)),</code> | **关键：**大写标识也可能匹配；例如订单 AB12345 会同时出现在 error_code。 |
| L387 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L388 | （空行） | 空行，分隔逻辑。 |
| L389 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 辅助 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 辅助 ────────────────────────────────────────────────────────────────── |
| L390 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-391"></a>

### L391–L403 · IntentRecognizer._load_template_embeddings

只计算 _tpl_embeddings 尚无的类别，按扁平顺序计算再切回各类别，减少重复计算。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L391 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _load_template_embeddings(self) -&gt; None:</code> | 定义异步函数 <code>_load_template_embeddings</code>；输入参数见签名，下方导读解释调用目的。 |
| L392 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;懒加载所有模板的 Embedding（只在首次调用时执行）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L393 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;missing = [cat for cat in _TEMPLATES if cat not in self._tpl_embeddings]</code> | 将结果保存到 <code>missing</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L394 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not missing:</code> | 判断 <code>not missing</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L395 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | 结束当前函数并返回；无返回值。 |
| L396 | （空行） | 空行，分隔逻辑。 |
| L397 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;all_texts = [t for cat in missing for t in _TEMPLATES[cat]]</code> | 将结果保存到 <code>all_texts</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L398 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vecs = [await self._embed_text(text) for text in all_texts]</code> | 将结果保存到 <code>vecs</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L399 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;idx = 0</code> | 将结果保存到 <code>idx</code>：使用这里写明的固定值。 |
| L400 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for cat in missing:</code> | 遍历 <code>missing</code>，本轮元素绑定 <code>cat</code>。 |
| L401 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;n = len(_TEMPLATES[cat])</code> | 将结果保存到 <code>n</code>：计算当前容器或字符串长度。 |
| L402 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._tpl_embeddings[cat] = vecs[idx: idx + n]</code> | 将结果保存到 <code>self._tpl_embeddings[cat]</code>：按索引/切片取 <code>vecs[idx:idx + n]</code>，注意是否截掉旧历史或长文本。 |
| L403 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;idx += n</code> | 更新 <code>idx</code>：<code>idx += n</code>；此处会改变累计状态。 |
| L404 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-405"></a>

### L405–L421 · IntentRecognizer._embed_text

动态检测客户端是否具备 embeddings 属性；若有尝试远端，异常/不存在则本地哈希。这里只解释代码分支，不保证所配外部服务具有该资源。

**签名输入：** <code>self, text: str</code>；**返回契约：** <code>List[float]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L405 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _embed_text(self, text: str) -&gt; List[float]:</code> | 定义异步函数 <code>_embed_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L406 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L407 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;生成文本向量。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L408 | （空行） | 空行，分隔逻辑。 |
| L409 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;如果未来接入的官方/兼容客户端提供 embeddings.create，会优先使用远端向量；</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L410 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;当前 Anthropic SDK 没有该资源时，退化为字符 n-gram 哈希向量。这样不会因为</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L411 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Embedding 服务缺失导致三路融合中断。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L412 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L413 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;embeddings = getattr(self.client, &quot;embeddings&quot;, None)</code> | 将结果保存到 <code>embeddings</code>：读取对象指定属性，不存在时返回这里给出的默认值。 |
| L414 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if embeddings is not None:</code> | 判断 <code>embeddings is not None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L415 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L416 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await embeddings.create(model=&quot;voyage-3-lite&quot;, input=[text])</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用 <code>embeddings.create</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L417 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return list(resp.data[0].embedding)</code> | 结束当前函数并返回；将迭代内容物化成列表。 |
| L418 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L419 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;远端 Embedding 失败，使用本地向量兜底: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L420 | （空行） | 空行，分隔逻辑。 |
| L421 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self._local_embedding(text)</code> | 结束当前函数并返回；进入 <code>self._local_embedding</code>：小写→收集不重复的 1/2/3 字符片段→MD5 映射到 256 个桶→按哈希确定正负累加。 |
| L422 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-423"></a>

### L423–L440 · IntentRecognizer._local_embedding

小写→收集不重复的 1/2/3 字符片段→MD5 映射到 256 个桶→按哈希确定正负累加。相同输入结果稳定，碰撞会损失信息，同义改写不一定相似。

**签名输入：** <code>text: str, dims: int=256</code>；**返回契约：** <code>List[float]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L423 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L424 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _local_embedding(text: str, dims: int = 256) -&gt; List[float]:</code> | 定义函数 <code>_local_embedding</code>；输入参数见签名，下方导读解释调用目的。 |
| L425 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;稳定的字符 n-gram 哈希向量，用于无远端 Embedding 时的语义近似匹配。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L426 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;normalized = text.lower().strip()</code> | 将结果保存到 <code>normalized</code>：去除两端指定字符或空白。 |
| L427 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vec = [0.0] * dims</code> | 将结果保存到 <code>vec</code>：按此表达式计算 <code>[0.0] * dims</code>。 |
| L428 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tokens = set()</code> | 将结果保存到 <code>tokens</code>：构造去重集合。 |
| L429 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for n in (1, 2, 3):</code> | 遍历 <code>(1, 2, 3)</code>，本轮元素绑定 <code>n</code>。 |
| L430 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(normalized) &gt;= n:</code> | 判断 <code>len(normalized) &gt;= n</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L431 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tokens.update(normalized[i:i + n] for i in range(len(normalized) - n + 1))</code> | 调用 <code>tokens.update</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L432 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not tokens:</code> | 判断 <code>not tokens</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L433 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tokens.add(normalized)</code> | 向集合/存储添加数据，具体目标见左侧接收者。 |
| L434 | （空行） | 空行，分隔逻辑。 |
| L435 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for token in tokens:</code> | 遍历 <code>tokens</code>，本轮元素绑定 <code>token</code>。 |
| L436 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;digest = hashlib.md5(token.encode(&quot;utf-8&quot;)).digest()</code> | 将结果保存到 <code>digest</code>：调用 <code>hashlib.md5(token.encode(&#x27;utf-8&#x27;)).digest</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L437 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;idx = int.from_bytes(digest[:4], &quot;big&quot;) % dims</code> | 将结果保存到 <code>idx</code>：按此表达式计算 <code>int.from_bytes(digest[:4], &#x27;big&#x27;) % dims</code>。 |
| L438 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sign = 1.0 if digest[4] % 2 == 0 else -1.0</code> | 将结果保存到 <code>sign</code>：条件 <code>digest[4] % 2 == 0</code> 成立选前值，否则选 else 后值。 |
| L439 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vec[idx] += sign</code> | 更新 <code>vec[idx]</code>：<code>vec[idx] += sign</code>；此处会改变累计状态。 |
| L440 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return vec</code> | 结束当前函数并返回；读取 <code>vec</code>。 |
| L441 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-442"></a>

### L442–L451 · IntentRecognizer._urgency

按 CRITICAL/HIGH/MEDIUM 词表顺序扫描，首次命中返回；没有命中再按转人工/投诉意图给默认等级。

**签名输入：** <code>self, message: str, intent: IntentCategory</code>；**返回契约：** <code>UrgencyLevel</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L442 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _urgency(self, message: str, intent: IntentCategory) -&gt; UrgencyLevel:</code> | 定义函数 <code>_urgency</code>；输入参数见签名，下方导读解释调用目的。 |
| L443 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg = message.lower()</code> | 将结果保存到 <code>msg</code>：转小写进行大小写无关比较。 |
| L444 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for level, kws in _URGENCY_KEYWORDS.items():</code> | 遍历 <code>_URGENCY_KEYWORDS.items()</code>，本轮元素绑定 <code>(level, kws)</code>。 |
| L445 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if any(kw in msg for kw in kws):</code> | 判断 <code>any((kw in msg for kw in kws))</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L446 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return level</code> | 结束当前函数并返回；读取 <code>level</code>。 |
| L447 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if intent in (IntentCategory.ESCALATION, IntentCategory.HUMAN_HANDOFF):</code> | 判断 <code>intent in (IntentCategory.ESCALATION, IntentCategory.HUMAN_HANDOFF)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L448 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return UrgencyLevel.HIGH</code> | 结束当前函数并返回；读取 <code>UrgencyLevel.HIGH</code>。 |
| L449 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if intent == IntentCategory.COMPLAINT:</code> | 判断 <code>intent == IntentCategory.COMPLAINT</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L450 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return UrgencyLevel.MEDIUM</code> | 结束当前函数并返回；读取 <code>UrgencyLevel.MEDIUM</code>。 |
| L451 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return UrgencyLevel.LOW</code> | 结束当前函数并返回；读取 <code>UrgencyLevel.LOW</code>。 |
| L452 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-453"></a>

### L453–L464 · IntentRecognizer._cache_key

将截断后的当前消息和最近三条历史规范序列化，再做 MD5。历史参与避免“这个呢”跨话题直接复用，但截断会引入另一种混淆。

**签名输入：** <code>self, message: str, history: Optional[List[Dict[str, str]]]=None</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L453 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _cache_key(self, message: str, history: Optional[List[Dict[str, str]]] = None) -&gt; str:</code> | 定义函数 <code>_cache_key</code>；输入参数见签名，下方导读解释调用目的。 |
| L454 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;payload = {&quot;message&quot;: self._clean_text(message)[:200]}</code> | 将结果保存到 <code>payload</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L455 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if history:</code> | 判断 <code>history</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L456 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;payload[&quot;history&quot;] = [</code> | 将结果保存到 <code>payload[&#x27;history&#x27;]</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L457 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L458 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;role&quot;: self._clean_text(item.get(&quot;role&quot;, &quot;&quot;))[:20],</code> | 字段 <code>role</code>（当前映射中的键）：按索引/切片取 <code>self._clean_text(item.get(&#x27;role&#x27;, &#x27;&#x27;))[:20]</code>，注意是否截掉旧历史或长文本。 |
| L459 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: self._clean_text(item.get(&quot;content&quot;, &quot;&quot;))[:160],</code> | 字段 <code>content</code>（文本正文）：按索引/切片取 <code>self._clean_text(item.get(&#x27;content&#x27;, &#x27;&#x27;))[:160]</code>，注意是否截掉旧历史或长文本。 |
| L460 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L461 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for item in history[-3:]</code> | 续接 L456 的表达式：按前述语句组装参数、条件或集合。 |
| L462 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L463 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)</code> | 将结果保存到 <code>raw</code>：把对象序列化为 JSON 文本供存储、提示词或缓存 key 使用。 |
| L464 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return hashlib.md5(raw.encode(&quot;utf-8&quot;)).hexdigest()</code> | 结束当前函数并返回；调用 <code>hashlib.md5(raw.encode(&#x27;utf-8&#x27;)).hexdigest</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L465 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-466"></a>

### L466–L468 · IntentRecognizer._unique

dict.fromkeys 保序去重，先过滤空白字符串。

**签名输入：** <code>values: List[str]</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L466 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L467 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _unique(values: List[str]) -&gt; List[str]:</code> | 定义函数 <code>_unique</code>；输入参数见签名，下方导读解释调用目的。 |
| L468 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return list(dict.fromkeys(value.strip() for value in values if value and value.strip()))</code> | 结束当前函数并返回；将迭代内容物化成列表。 |
| L469 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-470"></a>

### L470–L484 · IntentRecognizer._best_pattern_match

命中 1 个词=.5，2 个=.75，3 个及以上=1。是人工启发式分数，不是从标注集校准的概率。

**签名输入：** <code>message: str, patterns: Dict[IntentCategory, List[str]]</code>；**返回契约：** <code>tuple[IntentCategory, float]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L470 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L471 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _best_pattern_match(</code> | 定义函数 <code>_best_pattern_match</code>；输入参数见签名，下方导读解释调用目的。 |
| L472 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L473 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;patterns: Dict[IntentCategory, List[str]],</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L474 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; tuple[IntentCategory, float]:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L475 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best_cat, best_score = IntentCategory.OTHER, 0.0</code> | 将结果保存到 <code>(best_cat, best_score)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L476 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for cat, kws in patterns.items():</code> | 遍历 <code>patterns.items()</code>，本轮元素绑定 <code>(cat, kws)</code>。 |
| L477 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;hits = sum(1 for kw in kws if kw in message)</code> | 将结果保存到 <code>hits</code>：累加各项数值/布尔命中值。 |
| L478 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not hits:</code> | 判断 <code>not hits</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L479 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L480 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 单个明确业务关键词就给可用置信度；多个关键词命中时提高置信度。</code> | 源码注释：单个明确业务关键词就给可用置信度；多个关键词命中时提高置信度。 |
| L481 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;score = min(1.0, 0.5 + 0.25 * (hits - 1))</code> | 将结果保存到 <code>score</code>：取上界/限制后的较小值。 |
| L482 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if score &gt; best_score:</code> | 判断 <code>score &gt; best_score</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L483 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;best_score, best_cat = score, cat</code> | 将结果保存到 <code>(best_score, best_cat)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L484 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return best_cat, best_score</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L485 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-486"></a>

### L486–L488 · IntentRecognizer._intent_group

将 refund/invoice 等映射到 billing；未映射就返回自身 value。

**签名输入：** <code>intent: IntentCategory</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L486 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L487 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _intent_group(intent: IntentCategory) -&gt; str:</code> | 定义函数 <code>_intent_group</code>；输入参数见签名，下方导读解释调用目的。 |
| L488 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return _INTENT_GROUPS.get(intent, intent).value</code> | 结束当前函数并返回；读取 <code>_INTENT_GROUPS.get(intent, intent).value</code>。 |
| L489 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-490"></a>

### L490–L497 · IntentRecognizer._clean_text

将非字符串转字符串，丢弃非法 Unicode 代理字符。

**签名输入：** <code>value: Any</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L490 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L491 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _clean_text(value: Any) -&gt; str:</code> | 定义函数 <code>_clean_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L492 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;移除 Unicode 代理字符，避免 HTTP 客户端编码 prompt 时崩溃。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L493 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if value is None:</code> | 判断 <code>value is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L494 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;</code> | 结束当前函数并返回；使用固定文本/配置值。 |
| L495 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(value, str):</code> | 判断 <code>not isinstance(value, str)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L496 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value = str(value)</code> | 将结果保存到 <code>value</code>：转换为字符串表示。 |
| L497 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return value.encode(&quot;utf-8&quot;, errors=&quot;ignore&quot;).decode(&quot;utf-8&quot;)</code> | 结束当前函数并返回；调用 <code>value.encode(&#x27;utf-8&#x27;, errors=&#x27;ignore&#x27;).decode</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L498 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-499"></a>

### L499–L507 · IntentRecognizer.cache_stats

读取对象内缓存大小、命中/未命中和命中率；不代表 Redis 缓存。

**签名输入：** <code>self</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L499 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L500 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def cache_stats(self) -&gt; Dict[str, Any]:</code> | 定义函数 <code>cache_stats</code>；输入参数见签名，下方导读解释调用目的。 |
| L501 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;total = self.cache_hits + self.cache_misses</code> | 将结果保存到 <code>total</code>：按此表达式计算 <code>self.cache_hits + self.cache_misses</code>。 |
| L502 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L503 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;size&quot;: len(self._cache),</code> | 字段 <code>size</code>（当前映射中的键）：计算当前容器或字符串长度。 |
| L504 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;hits&quot;: self.cache_hits,</code> | 字段 <code>hits</code>（当前映射中的键）：读取 <code>self.cache_hits</code>。 |
| L505 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;misses&quot;: self.cache_misses,</code> | 字段 <code>misses</code>（当前映射中的键）：读取 <code>self.cache_misses</code>。 |
| L506 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;hit_rate&quot;: self.cache_hits / total if total else 0.0,</code> | 字段 <code>hit_rate</code>（当前映射中的键）：条件 <code>total</code> 成立选前值，否则选 else 后值。 |
| L507 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |

## 结合全项目：设计缺口与增强方向

- 设置任何 base_url 都关闭向量分支；开启时若客户端无 embeddings 则用 256 维字符 n-gram 哈希向量。它没有训练所得语义表示，不能等同专门语义 embedding 模型。
- L217 注释说 LRU，但淘汰按字典插入顺序批量删除；命中不移动位置，无 TTL。缓存 key 截断消息/历史可能使不同请求共用结果，返回的 latency_ms 还是首次耗时。
- L369 细化规则不检查粗细类别是否同组；宽泛技术分类也可能被不相关退款关键词改成 refund。LLM 失败分支优先接受任何正向量分数，没有用阈值。
- LLM JSON 只做截取+解析，没有 confidence 范围与数值类型严格验证；_vote 中可能发生类型错误或分数超界。
- learn 修改内存模板、不训练模型、不持久化，也不清结果缓存；LLM few-shot 每类只取第一条，追加样本往往不会进入 LLM prompt。
- product 永远空列表；错误码正则可能把大写订单号当错误码；上下文仅送 LLM，实体只从本轮取。应做槽位跨轮合并和来源标注。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
