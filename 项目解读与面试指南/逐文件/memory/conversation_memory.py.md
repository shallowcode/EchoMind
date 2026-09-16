# memory/conversation_memory.py 解读

## 输入、输出与流向

**定位：** 把当前会话、相关旧摘要和用户偏好组合成生成模型的记忆背景。

**输入：** user_id、conv_id、query；消息 role/content/metadata；Redis 与 Chroma 配置。

**输出 / 副作用：** MemoryContext(recent_messages,relevant_history,user_profile,summary) 及 prompt 文本；副作用：Redis 列表/摘要、Chroma episodic/user_profile。

**流向：** add_message LPUSH→刷新 24h TTL→达到 15 条压缩；get_context 顺序读工作记忆→相关摘要→画像→Redis 摘要；压缩保留 5 条，其余 LLM 摘要并归档。

[返回阅读入口](../../README.md) · [对照原文件](../../../memory/conversation_memory.py)

当前工作区快照：382 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`91721d26bac423d9bd127f2d15dd1fcd1d3f21524dc7e426edae53d5df20cf9c`。

## 类与函数导航

[MsgRole](#symbol-33) → [Message](#symbol-39) → [MemoryContext](#symbol-47) → [MemoryContext._clean](#symbol-55) → [MemoryContext.to_prompt_text](#symbol-60) → [MemoryManager](#symbol-76) → [MemoryManager.__init__](#symbol-87) → [MemoryManager.add_message](#symbol-129) → [MemoryManager.update_profile](#symbol-160) → [MemoryManager.get_context](#symbol-210) → [MemoryManager._compress](#symbol-241) → [MemoryManager._get_working_memory](#symbol-290) → [MemoryManager._search_episodic](#symbol-304) → [MemoryManager._store_episodic](#symbol-323) → [MemoryManager._get_profile](#symbol-342) → [MemoryManager.close](#symbol-352) → [MemoryManager._wm_key](#symbol-356) → [MemoryManager._summary_key](#symbol-360) → [MemoryManager._safe_text](#symbol-364) → [MemoryManager._safe_metadata_value](#symbol-373)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>亮点：多轮对话记忆管理</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>三级记忆架构，模拟人类记忆机制：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | <code>&nbsp;&nbsp;1. 工作记忆（Redis）—— 当前会话的最近 N 条消息，毫秒级读写</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L6 | <code>&nbsp;&nbsp;2. 情景记忆（ChromaDB）—— 跨会话的历史对话，按语义相似度检索</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;3. 用户画像（ChromaDB）—— 从对话中提炼的长期偏好和实体</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L8 | （空行） | 空行，分隔逻辑。 |
| L9 | <code>关键设计：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L10 | <code>&nbsp;&nbsp;- 上下文构建时三级记忆融合，按重要性 + 时效性排序</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L11 | <code>&nbsp;&nbsp;- 工作记忆超过阈值时自动压缩（LLM 摘要），防止 context 爆炸</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L12 | <code>&nbsp;&nbsp;- 所有 Embedding 通过 Anthropic API 生成，无本地模型</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L13 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L14 | <code>import hashlib</code> | 导入 <code>import hashlib</code>；只建立名称依赖，真正业务调用见后文。 |
| L15 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L16 | <code>import json</code> | 导入 <code>import json</code>；只建立名称依赖，真正业务调用见后文。 |
| L17 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L18 | <code>import time</code> | 导入 <code>import time</code>；只建立名称依赖，真正业务调用见后文。 |
| L19 | <code>from dataclasses import dataclass, field</code> | 导入 <code>from dataclasses import dataclass, field</code>；只建立名称依赖，真正业务调用见后文。 |
| L20 | <code>from datetime import datetime, timedelta</code> | 导入 <code>from datetime import datetime, timedelta</code>；只建立名称依赖，真正业务调用见后文。 |
| L21 | <code>from enum import Enum</code> | 导入 <code>from enum import Enum</code>；只建立名称依赖，真正业务调用见后文。 |
| L22 | <code>from typing import Any, Dict, List, Optional</code> | 导入 <code>from typing import Any, Dict, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L23 | （空行） | 空行，分隔逻辑。 |
| L24 | <code>import chromadb</code> | 导入 <code>import chromadb</code>；只建立名称依赖，真正业务调用见后文。 |
| L25 | <code>import redis.asyncio as redis</code> | 导入 <code>import redis.asyncio as redis</code>；只建立名称依赖，真正业务调用见后文。 |
| L26 | <code>from anthropic import AsyncAnthropic</code> | 导入 <code>from anthropic import AsyncAnthropic</code>；只建立名称依赖，真正业务调用见后文。 |
| L27 | （空行） | 空行，分隔逻辑。 |
| L28 | <code>from core.llm_utils import extract_text_content</code> | 导入 <code>from core.llm_utils import extract_text_content</code>；只建立名称依赖，真正业务调用见后文。 |
| L29 | （空行） | 空行，分隔逻辑。 |
| L30 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L31 | （空行） | 空行，分隔逻辑。 |
| L32 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-33"></a>

### L33–L36 · MsgRole

消息角色落库用字符串，读取再还原枚举。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L33 | <code>class MsgRole(Enum):</code> | 定义 <code>MsgRole</code> 的数据契约/行为；继承与字段见本段。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;USER      = &quot;user&quot;</code> | 将结果保存到 <code>USER</code>：使用固定文本/配置值。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ASSISTANT = &quot;assistant&quot;</code> | 将结果保存到 <code>ASSISTANT</code>：使用固定文本/配置值。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;SYSTEM    = &quot;system&quot;</code> | 将结果保存到 <code>SYSTEM</code>：使用固定文本/配置值。 |
| L37 | （空行） | 空行，分隔逻辑。 |
| L38 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-39"></a>

### L39–L44 · Message

单条消息有 role/content/本地时间戳/元数据；default_factory 保证每条时间和字典独立。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L39 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L40 | <code>class Message:</code> | 定义 <code>Message</code> 的数据契约/行为；继承与字段见本段。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;role:       MsgRole</code> | 声明字段 <code>role</code> 的类型，赋值由构造方完成。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;content:    str</code> | 声明字段 <code>content</code> 的类型，赋值由构造方完成。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;timestamp:  datetime = field(default_factory=datetime.now)</code> | 将结果保存到 <code>timestamp</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;metadata:   Dict[str, Any] = field(default_factory=dict)</code> | 将结果保存到 <code>metadata</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L45 | （空行） | 空行，分隔逻辑。 |
| L46 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-47"></a>

### L47–L73 · MemoryContext

读取结果的集合对象，避免 Agent 直接依赖 Redis/Chroma 存储细节。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L47 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L48 | <code>class MemoryContext:</code> | 定义 <code>MemoryContext</code> 的数据契约/行为；继承与字段见本段。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;传给 Agent 的完整上下文。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;recent_messages:  List[Message]   # 工作记忆：最近对话</code> | 声明字段 <code>recent_messages</code> 的类型，赋值由构造方完成。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;relevant_history: List[str]       # 情景记忆：语义相关的历史片段</code> | 声明字段 <code>relevant_history</code> 的类型，赋值由构造方完成。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;user_profile:     Dict[str, Any]  # 用户画像：偏好、常用实体</code> | 声明字段 <code>user_profile</code> 的类型，赋值由构造方完成。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;summary:          str             # 当前会话摘要（压缩后）</code> | 声明字段 <code>summary</code> 的类型，赋值由构造方完成。 |
| L54 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-55"></a>

### L55–L58 · MemoryContext._clean

移除非法代理字符，避免 prompt 编码异常。

**签名输入：** <code>text: str</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _clean(text: str) -&gt; str:</code> | 定义函数 <code>_clean</code>；输入参数见签名，下方导读解释调用目的。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;移除 Unicode 代理字符，防止编码错误。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return text.encode(&quot;utf-8&quot;, errors=&quot;ignore&quot;).decode(&quot;utf-8&quot;)</code> | 结束当前函数并返回；调用 <code>text.encode(&#x27;utf-8&#x27;, errors=&#x27;ignore&#x27;).decode</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L59 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-60"></a>

### L60–L73 · MemoryContext.to_prompt_text

按摘要、相关历史（最多 3）、画像、最近消息拼接。画像用 ensure_ascii=True 转义中文，其他字段清理编码；没有统一 token 裁剪。

**签名输入：** <code>self</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def to_prompt_text(self) -&gt; str:</code> | 定义函数 <code>to_prompt_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;将记忆上下文格式化为 LLM 可用的文本。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts = []</code> | 将结果保存到 <code>parts</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.summary:</code> | 判断 <code>self.summary</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(f&quot;[会话摘要]\n{self._clean(self.summary)}&quot;)</code> | 追加一个元素到当前列表。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.relevant_history:</code> | 判断 <code>self.relevant_history</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(&quot;[相关历史]\n&quot; + &quot;\n&quot;.join(f&quot;- {self._clean(h)}&quot; for h in self.relevant_history[:3]))</code> | 追加一个元素到当前列表。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.user_profile:</code> | 判断 <code>self.user_profile</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(f&quot;[用户画像]\n{json.dumps(self.user_profile, ensure_ascii=True)}&quot;)</code> | 追加一个元素到当前列表。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.recent_messages:</code> | 判断 <code>self.recent_messages</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(&quot;[最近对话]&quot;)</code> | 追加一个元素到当前列表。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for m in self.recent_messages:</code> | 遍历 <code>self.recent_messages</code>，本轮元素绑定 <code>m</code>。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(f&quot;{m.role.value}: {self._clean(m.content)}&quot;)</code> | 追加一个元素到当前列表。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;\n\n&quot;.join(parts)</code> | 结束当前函数并返回；把字符串片段按分隔符合并。 |
| L74 | （空行） | 空行，分隔逻辑。 |
| L75 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-76"></a>

### L76–L382 · MemoryManager

把当前会话、相关旧摘要和用户偏好组合成生成模型的记忆背景。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L76 | <code>class MemoryManager:</code> | 定义 <code>MemoryManager</code> 的数据契约/行为；继承与字段见本段。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;三级记忆管理器。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L79 | （空行） | 空行，分隔逻辑。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;工作记忆存 Redis（TTL 24h），情景记忆和用户画像存 ChromaDB（持久化）。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L82 | （空行） | 空行，分隔逻辑。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;WORKING_MAX   = 20    # 工作记忆最大条数，超过则触发压缩</code> | **关键：**只限制读取 20 条，不是 Redis 列表的硬长度上限。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;COMPRESS_AT   = 15    # 达到此条数时压缩，保留摘要 + 最近 5 条</code> | 将结果保存到 <code>COMPRESS_AT</code>：使用这里写明的固定值。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;HISTORY_TOP_K = 5     # 情景记忆检索返回条数</code> | 将结果保存到 <code>HISTORY_TOP_K</code>：使用这里写明的固定值。 |
| L86 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-87"></a>

### L87–L125 · MemoryManager.__init__

创建异步 Redis 客户端（此处不 ping），同步尝试 Chroma HTTP 后本地兜底，建立 episodic 和 user_profile collection。

**签名输入：** <code>self, redis_url: str=&#x27;redis://localhost:6379/0&#x27;, chroma_host: str=&#x27;localhost&#x27;, chroma_port: int=8000, chroma_path: str=&#x27;./data/chroma&#x27;, api_key: str=&#x27;&#x27;, base_url: Optional[str]=None, model: str=&#x27;claude-3-5-sonnet-20241022&#x27;</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;redis_url:    str = &quot;redis://localhost:6379/0&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_host:  str = &quot;localhost&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_port:  int = 8000,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_path:  str = &quot;./data/chroma&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key:      str = &quot;&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url:     Optional[str] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model:        str = &quot;claude-3-5-sonnet-20241022&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs: Dict[str, Any] = {&quot;api_key&quot;: api_key}</code> | 将结果保存到 <code>kwargs</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if base_url:</code> | 判断 <code>base_url</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;kwargs[&quot;base_url&quot;] = base_url</code> | 将结果保存到 <code>kwargs[&#x27;base_url&#x27;]</code>：读取 <code>base_url</code>。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._client = AsyncAnthropic(**kwargs)</code> | 将结果保存到 <code>self._client</code>：调用 <code>AsyncAnthropic</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._model  = model</code> | 将结果保存到 <code>self._model</code>：读取 <code>model</code>。 |
| L102 | （空行） | 空行，分隔逻辑。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._redis = redis.from_url(redis_url, decode_responses=True)</code> | 将结果保存到 <code>self._redis</code>：调用 <code>redis.from_url</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L104 | （空行） | 空行，分隔逻辑。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# ChromaDB：优先连接独立服务（docker compose 模式），连不上则降级为本地嵌入式</code> | 源码注释：ChromaDB：优先连接独立服务（docker compose 模式），连不上则降级为本地嵌入式 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# HttpClient 默认也会初始化 ChromaDB telemetry；显式关闭避免 posthog 兼容性错误日志。</code> | 源码注释：HttpClient 默认也会初始化 ChromaDB telemetry；显式关闭避免 posthog 兼容性错误日志。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma = chromadb.HttpClient(</code> | 将结果保存到 <code>chroma</code>：调用 <code>chromadb.HttpClient</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;host=chroma_host,</code> | 参数 <code>host</code>（host）：读取 <code>chroma_host</code>。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;port=chroma_port,</code> | 参数 <code>port</code>（port）：读取 <code>chroma_port</code>。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;settings=chromadb.Settings(anonymized_telemetry=False),</code> | 参数 <code>anonymized_telemetry</code>（anonymized_telemetry）：使用这里写明的固定值。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma.heartbeat()  # 测试连接</code> | 调用 <code>chroma.heartbeat</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;ChromaDB 已连接: {chroma_host}:{chroma_port}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;ChromaDB 服务不可用，使用本地嵌入式模式: {chroma_path}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma = chromadb.PersistentClient(</code> | 将结果保存到 <code>chroma</code>：调用 <code>chromadb.PersistentClient</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path=chroma_path,</code> | 参数 <code>path</code>（path）：读取 <code>chroma_path</code>。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;settings=chromadb.Settings(anonymized_telemetry=False),</code> | 参数 <code>anonymized_telemetry</code>（anonymized_telemetry）：使用这里写明的固定值。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L121 | （空行） | 空行，分隔逻辑。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 情景记忆：存储历史对话片段</code> | 源码注释：情景记忆：存储历史对话片段 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._episodic = chroma.get_or_create_collection(&quot;episodic&quot;)</code> | 将结果保存到 <code>self._episodic</code>：调用 <code>chroma.get_or_create_collection</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 用户画像：存储提炼出的偏好和实体</code> | 源码注释：用户画像：存储提炼出的偏好和实体 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._profile  = chroma.get_or_create_collection(&quot;user_profile&quot;)</code> | 将结果保存到 <code>self._profile</code>：调用 <code>chroma.get_or_create_collection</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L126 | （空行） | 空行，分隔逻辑。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 写入 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 写入 ────────────────────────────────────────────────────────────────── |
| L128 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-129"></a>

### L129–L158 · MemoryManager.add_message

消息序列化后 LPUSH 放列表头，最新在前；每写一条延长 TTL，到 15 条就同步等待压缩。用户和助手分别调用，所以一次对话不等于一条消息。

**签名输入：** <code>self, user_id: str, conv_id: str, role: MsgRole, content: str, metadata: Optional[Dict[str, Any]]=None</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def add_message(</code> | 定义异步函数 <code>add_message</code>；输入参数见签名，下方导读解释调用目的。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;role:    MsgRole,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content: str,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadata: Optional[Dict[str, Any]] = None,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;) -&gt; None:</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;将一条消息写入工作记忆，超阈值时自动压缩。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id = self._safe_text(user_id)</code> | 将结果保存到 <code>user_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id = self._safe_text(conv_id)</code> | 将结果保存到 <code>conv_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;clean_metadata = {</code> | 将结果保存到 <code>clean_metadata</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._safe_text(k): self._safe_metadata_value(v)</code> | 续接 L140 的表达式：按前述语句组装参数、条件或集合。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for k, v in (metadata or {}).items()</code> | 续接 L140 的表达式：按前述语句组装参数、条件或集合。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg = Message(role=role, content=self._safe_text(content), metadata=clean_metadata)</code> | 将结果保存到 <code>msg</code>：进入 <code>Message</code>：单条消息有 role/content/本地时间戳/元数据；default_factory 保证每条时间和字典独立。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key = self._wm_key(user_id, conv_id)</code> | 将结果保存到 <code>key</code>：进入 <code>self._wm_key</code>：wm:user_id:conv_id，同一用户同一会话才命中同一列表；冒号拼接未转义。 |
| L146 | （空行） | 空行，分隔逻辑。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 追加到 Redis 列表（左推，最新在前）</code> | 源码注释：追加到 Redis 列表（左推，最新在前） |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._redis.lpush(key, json.dumps({</code> | 等待完成后继续；向 Redis 列表头写消息。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;role&quot;:      msg.role.value,</code> | 字段 <code>role</code>（当前映射中的键）：读取 <code>msg.role.value</code>。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;:   msg.content,</code> | 字段 <code>content</code>（文本正文）：读取 <code>msg.content</code>。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;ts&quot;:        msg.timestamp.isoformat(),</code> | 字段 <code>ts</code>（当前映射中的键）：调用 <code>msg.timestamp.isoformat</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;:  msg.metadata,</code> | 字段 <code>metadata</code>（附加元信息）：读取 <code>msg.metadata</code>。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._redis.expire(key, 86400)  # 24h TTL</code> | 等待完成后继续；刷新 Redis 键过期时间。 |
| L155 | （空行） | 空行，分隔逻辑。 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 超过压缩阈值时触发压缩</code> | 源码注释：超过压缩阈值时触发压缩 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if await self._redis.llen(key) &gt;= self.COMPRESS_AT:</code> | **关键：**阈值计“条消息”；15 条约为 7.5 轮双边对话。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._compress(user_id, conv_id)</code> | 等待完成后继续；进入 <code>self._compress</code>：读最多 20 条，少于 15 不做。 |
| L159 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-160"></a>

### L160–L206 · MemoryManager.update_profile

取最近 10 条让 LLM 抽偏好和实体，按 user+conv 创建画像文档，先删后加。同用户不同会话有多条画像，不是一个聚合用户主档。

**签名输入：** <code>self, user_id: str, conv_id: str</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def update_profile(self, user_id: str, conv_id: str) -&gt; None:</code> | 定义异步函数 <code>update_profile</code>；输入参数见签名，下方导读解释调用目的。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;从当前工作记忆中提炼用户偏好，更新用户画像。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;用 LLM 提炼偏好，然后存入 ChromaDB（ChromaDB 内置 embedding，不依赖外部 API）。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id = self._safe_text(user_id)</code> | 将结果保存到 <code>user_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id = self._safe_text(conv_id)</code> | 将结果保存到 <code>conv_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages = await self._get_working_memory(user_id, conv_id)</code> | 将结果保存到 <code>messages</code>：等待完成后继续；进入 <code>self._get_working_memory</code>：LRANGE 0..19 得到最新在前的原始值，然后 reversed 恢复旧到新，再 JSON→Message。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not messages:</code> | 判断 <code>not messages</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | 结束当前函数并返回；无返回值。 |
| L170 | （空行） | 空行，分隔逻辑。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text = self._safe_text(&quot;\n&quot;.join(f&quot;{m.role.value}: {m.content}&quot; for m in messages[-10:]))</code> | **关键：**历史含 assistant 输出，画像抽取可能混入模型生成事实。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = f&quot;&quot;&quot;从以下对话中提炼用户偏好和关键实体，返回 JSON。</code> | 将结果保存到 <code>prompt</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L173 | <code>对话:</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L174 | <code>{text}</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L175 | （空行） | 空行，分隔逻辑。 |
| L176 | <code>返回格式: {{&quot;preferences&quot;: [&quot;...&quot;], &quot;entities&quot;: {{&quot;产品&quot;: [], &quot;问题类型&quot;: []}}}}&quot;&quot;&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = self._safe_text(prompt)</code> | 将结果保存到 <code>prompt</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L178 | （空行） | 空行，分隔逻辑。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await self._client.messages.create(</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=self._model, max_tokens=512, temperature=0.0,</code> | 参数 <code>temperature</code>（生成采样温度）：使用这里写明的固定值。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: prompt}],</code> | 参数 <code>messages</code>（模型消息序列/当前函数的消息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = extract_text_content(resp.content)</code> | 将结果保存到 <code>raw</code>：进入共享响应适配器，只保留模型文本块。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;s, e = raw.find(&quot;{&quot;), raw.rfind(&quot;}&quot;) + 1</code> | 将结果保存到 <code>(s, e)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;profile_data = json.loads(raw[s:e])</code> | 将结果保存到 <code>profile_data</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L187 | （空行） | 空行，分隔逻辑。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;doc_id = f&quot;{user_id}_profile_{conv_id}&quot;</code> | 将结果保存到 <code>doc_id</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;doc_text = self._safe_text(json.dumps(profile_data, ensure_ascii=False))</code> | 将结果保存到 <code>doc_text</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L190 | （空行） | 空行，分隔逻辑。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await asyncio.to_thread(self._profile.delete, ids=[doc_id])</code> | 等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pass</code> | 有意不处理；异常分支可能因此丢失错误信号。 |
| L195 | （空行） | 空行，分隔逻辑。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 直接传 documents，让 ChromaDB 内置模型生成 embedding（不依赖 Voyage API）</code> | 源码注释：直接传 documents，让 ChromaDB 内置模型生成 embedding（不依赖 Voyage API） |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await asyncio.to_thread(</code> | 等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._profile.add,</code> | 续接 L197 的表达式：按前述语句组装参数、条件或集合。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ids=[doc_id],</code> | 参数 <code>ids</code>（文档标识列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;documents=[doc_text],</code> | 参数 <code>documents</code>（送入存储的文本列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadatas=[{&quot;user_id&quot;: user_id, &quot;conv_id&quot;: conv_id,</code> | 参数 <code>metadatas</code>（每个文档的元信息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;ts&quot;: datetime.now().isoformat()}],</code> | 字段 <code>ts</code>（当前映射中的键）：调用 <code>datetime.now().isoformat</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;用户画像已更新: {user_id}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;更新用户画像失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L207 | （空行） | 空行，分隔逻辑。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 读取 ──────────────────────────────────────────────────────────────────</code> | 源码注释：── 读取 ────────────────────────────────────────────────────────────────── |
| L209 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-210"></a>

### L210–L237 · MemoryManager.get_context

四步串行读数据。query 非空用当前问题召回历史，否则用最近一条消息；不是自动并行读取所有层。

**签名输入：** <code>self, user_id: str, conv_id: str, query: str=&#x27;&#x27;</code>；**返回契约：** <code>MemoryContext</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def get_context(self, user_id: str, conv_id: str, query: str = &quot;&quot;) -&gt; MemoryContext:</code> | 定义异步函数 <code>get_context</code>；输入参数见签名，下方导读解释调用目的。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;构建完整的记忆上下文。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L213 | （空行） | 空行，分隔逻辑。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query 用于从情景记忆中检索语义相关的历史片段。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 1. 工作记忆（当前会话最近消息）</code> | 源码注释：1. 工作记忆（当前会话最近消息） |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id = self._safe_text(user_id)</code> | 将结果保存到 <code>user_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id = self._safe_text(conv_id)</code> | 将结果保存到 <code>conv_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query = self._safe_text(query)</code> | 将结果保存到 <code>query</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L220 | （空行） | 空行，分隔逻辑。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recent = await self._get_working_memory(user_id, conv_id)</code> | 将结果保存到 <code>recent</code>：等待完成后继续；进入 <code>self._get_working_memory</code>：LRANGE 0..19 得到最新在前的原始值，然后 reversed 恢复旧到新，再 JSON→Message。 |
| L222 | （空行） | 空行，分隔逻辑。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 2. 情景记忆（跨会话语义检索）</code> | 源码注释：2. 情景记忆（跨会话语义检索） |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history = await self._search_episodic(user_id, query or (recent[-1].content if recent else &quot;&quot;))</code> | 将结果保存到 <code>history</code>：等待完成后继续；进入 <code>self._search_episodic</code>：query_texts 检索并用 where.user_id 限定用户，返回最多 5 个文档，prompt 实际只用前三个。 |
| L225 | （空行） | 空行，分隔逻辑。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 3. 用户画像</code> | 源码注释：3. 用户画像 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;profile = await self._get_profile(user_id)</code> | 将结果保存到 <code>profile</code>：等待完成后继续；进入 <code>self._get_profile</code>：where user_id + limit=1 取一条，JSON 解析；没有 order_by 时间，不能保证最新。 |
| L228 | （空行） | 空行，分隔逻辑。 |
| L229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 4. 会话摘要（如果已压缩过）</code> | 源码注释：4. 会话摘要（如果已压缩过） |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;summary = await self._redis.get(self._summary_key(user_id, conv_id)) or &quot;&quot;</code> | 将结果保存到 <code>summary</code>：读取 <code>await self._redis.get(self._summary_key(user_id, conv_id)) or &#x27;&#x27;</code>。 |
| L231 | （空行） | 空行，分隔逻辑。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return MemoryContext(</code> | 结束当前函数并返回；进入 <code>MemoryContext</code>：读取结果的集合对象，避免 Agent 直接依赖 Redis/Chroma 存储细节。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recent_messages=recent,</code> | 参数 <code>recent_messages</code>（recent_messages）：读取 <code>recent</code>。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;relevant_history=history,</code> | 参数 <code>relevant_history</code>（relevant_history）：读取 <code>history</code>。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_profile=profile,</code> | 参数 <code>user_profile</code>（user_profile）：读取 <code>profile</code>。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;summary=summary,</code> | 参数 <code>summary</code>（summary）：读取 <code>summary</code>。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L238 | （空行） | 空行，分隔逻辑。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 压缩（防止 context 爆炸）─────────────────────────────────────────────</code> | 源码注释：── 压缩（防止 context 爆炸）───────────────────────────────────────────── |
| L240 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-241"></a>

### L241–L286 · MemoryManager._compress

读最多 20 条，少于 15 不做。旧消息生成 2–3 句摘要，失败用占位摘要；拼接已有摘要，存 episodic，再重建最近 5 条。应特别跟踪 Redis 的逆序约定。

**签名输入：** <code>self, user_id: str, conv_id: str</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _compress(self, user_id: str, conv_id: str) -&gt; None:</code> | 定义异步函数 <code>_compress</code>；输入参数见签名，下方导读解释调用目的。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;工作记忆压缩：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. 用 LLM 对旧消息生成摘要</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. 摘要存 Redis（覆盖旧摘要）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. 旧消息存入情景记忆（ChromaDB）供跨会话检索</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4. 工作记忆只保留最近 5 条</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages = await self._get_working_memory(user_id, conv_id)</code> | 将结果保存到 <code>messages</code>：等待完成后继续；进入 <code>self._get_working_memory</code>：LRANGE 0..19 得到最新在前的原始值，然后 reversed 恢复旧到新，再 JSON→Message。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(messages) &lt; self.COMPRESS_AT:</code> | 判断 <code>len(messages) &lt; self.COMPRESS_AT</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return</code> | 结束当前函数并返回；无返回值。 |
| L252 | （空行） | 空行，分隔逻辑。 |
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;to_compress = messages[:-5]   # 保留最近 5 条</code> | 将结果保存到 <code>to_compress</code>：按索引/切片取 <code>messages[:-5]</code>，注意是否截掉旧历史或长文本。 |
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keep        = messages[-5:]</code> | 将结果保存到 <code>keep</code>：按索引/切片取 <code>messages[-5:]</code>，注意是否截掉旧历史或长文本。 |
| L255 | （空行） | 空行，分隔逻辑。 |
| L256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# LLM 摘要</code> | 源码注释：LLM 摘要 |
| L257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text = self._safe_text(&quot;\n&quot;.join(f&quot;{m.role.value}: {m.content}&quot; for m in to_compress))</code> | 将结果保存到 <code>text</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prompt = self._safe_text(f&quot;用 2-3 句话总结以下对话的关键信息：\n{text}&quot;)</code> | 将结果保存到 <code>prompt</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resp = await self._client.messages.create(</code> | 将结果保存到 <code>resp</code>：等待完成后继续；调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算。 |
| L261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=self._model, max_tokens=256, temperature=0.0,</code> | 参数 <code>temperature</code>（生成采样温度）：使用这里写明的固定值。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: prompt}],</code> | 参数 <code>messages</code>（模型消息序列/当前函数的消息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;summary = self._safe_text(extract_text_content(resp.content)).strip()</code> | 将结果保存到 <code>summary</code>：去除两端指定字符或空白。 |
| L265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;summary = f&quot;对话包含 {len(to_compress)} 条消息（摘要生成失败）&quot;</code> | 将结果保存到 <code>summary</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L267 | （空行） | 空行，分隔逻辑。 |
| L268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 存摘要到 Redis</code> | 源码注释：存摘要到 Redis |
| L269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;skey = self._summary_key(user_id, conv_id)</code> | 将结果保存到 <code>skey</code>：进入 <code>self._summary_key</code>：summary:user_id:conv_id，与消息列表独立 TTL。 |
| L270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;old_summary = await self._redis.get(skey) or &quot;&quot;</code> | 将结果保存到 <code>old_summary</code>：读取 <code>await self._redis.get(skey) or &#x27;&#x27;</code>。 |
| L271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;new_summary = self._safe_text(f&quot;{old_summary}\n{summary}&quot;).strip()</code> | **关键：**旧摘要不断追加，注释“覆盖旧摘要”不等于控制总长度。 |
| L272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._redis.setex(skey, 86400, new_summary)</code> | 等待完成后继续；写 Redis 字符串并设置 TTL。 |
| L273 | （空行） | 空行，分隔逻辑。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 旧消息存入情景记忆</code> | 源码注释：旧消息存入情景记忆 |
| L275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._store_episodic(user_id, conv_id, text, summary)</code> | **关键：**存档失败被内部捕获，本函数仍可能继续删除原工作记忆。 |
| L276 | （空行） | 空行，分隔逻辑。 |
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 重置工作记忆为最近 5 条</code> | 源码注释：重置工作记忆为最近 5 条 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key = self._wm_key(user_id, conv_id)</code> | 将结果保存到 <code>key</code>：进入 <code>self._wm_key</code>：wm:user_id:conv_id，同一用户同一会话才命中同一列表；冒号拼接未转义。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._redis.delete(key)</code> | **关键：**读/删/重建无锁；LLM 等待期间新增的消息可能被删除。 |
| L280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for m in reversed(keep):</code> | **关键：**keep 已旧→新，反转后再 LPUSH 会让 Redis 内顺序错误。 |
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._redis.lpush(key, json.dumps({</code> | 等待完成后继续；向 Redis 列表头写消息。 |
| L282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;role&quot;: m.role.value, &quot;content&quot;: m.content,</code> | 字段 <code>content</code>（文本正文）：读取 <code>m.content</code>。 |
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;ts&quot;: m.timestamp.isoformat(), &quot;metadata&quot;: m.metadata,</code> | 字段 <code>metadata</code>（附加元信息）：读取 <code>m.metadata</code>。 |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._redis.expire(key, 86400)</code> | 等待完成后继续；刷新 Redis 键过期时间。 |
| L286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;工作记忆压缩完成: {user_id}/{conv_id}，摘要 {len(summary)} 字&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L287 | （空行） | 空行，分隔逻辑。 |
| L288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 内部辅助 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 内部辅助 ────────────────────────────────────────────────────────────── |
| L289 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-290"></a>

### L290–L302 · MemoryManager._get_working_memory

LRANGE 0..19 得到最新在前的原始值，然后 reversed 恢复旧到新，再 JSON→Message。这个契约是压缩顺序 bug 的判断依据。

**签名输入：** <code>self, user_id: str, conv_id: str</code>；**返回契约：** <code>List[Message]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _get_working_memory(self, user_id: str, conv_id: str) -&gt; List[Message]:</code> | 定义异步函数 <code>_get_working_memory</code>；输入参数见签名，下方导读解释调用目的。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key  = self._wm_key(user_id, conv_id)</code> | 将结果保存到 <code>key</code>：进入 <code>self._wm_key</code>：wm:user_id:conv_id，同一用户同一会话才命中同一列表；冒号拼接未转义。 |
| L292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raws = await self._redis.lrange(key, 0, self.WORKING_MAX - 1)</code> | 将结果保存到 <code>raws</code>：等待完成后继续；读取 Redis 指定索引范围。 |
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msgs = []</code> | 将结果保存到 <code>msgs</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for raw in reversed(raws):  # Redis lpush 最新在前，reversed 还原时序</code> | 遍历 <code>reversed(raws)</code>，本轮元素绑定 <code>raw</code>。 |
| L295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d = json.loads(raw)</code> | 将结果保存到 <code>d</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msgs.append(Message(</code> | 追加一个元素到当前列表。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;role=MsgRole(d[&quot;role&quot;]),</code> | 参数 <code>role</code>（role）：进入 <code>MsgRole</code>：消息角色落库用字符串，读取再还原枚举。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content=d[&quot;content&quot;],</code> | 参数 <code>content</code>（文本正文）：按索引/切片取 <code>d[&#x27;content&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timestamp=datetime.fromisoformat(d[&quot;ts&quot;]),</code> | 参数 <code>timestamp</code>（timestamp）：调用 <code>datetime.fromisoformat</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadata=d.get(&quot;metadata&quot;, {}),</code> | 参数 <code>metadata</code>（附加元信息）：按键取值，缺失用给定默认值。 |
| L301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return msgs</code> | 结束当前函数并返回；读取 <code>msgs</code>。 |
| L303 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-304"></a>

### L304–L321 · MemoryManager._search_episodic

query_texts 检索并用 where.user_id 限定用户，返回最多 5 个文档，prompt 实际只用前三个。没有排除当前会话或加时效权重。

**签名输入：** <code>self, user_id: str, query: str</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _search_episodic(self, user_id: str, query: str) -&gt; List[str]:</code> | 定义异步函数 <code>_search_episodic</code>；输入参数见签名，下方导读解释调用目的。 |
| L305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;语义检索情景记忆。ChromaDB 内置 embedding，不依赖外部 API。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query_text = self._safe_text(query).strip()</code> | 将结果保存到 <code>query_text</code>：去除两端指定字符或空白。 |
| L307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not query_text:</code> | 判断 <code>not query_text</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return []</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 直接传 query_texts，ChromaDB 内置模型自动生成向量做匹配</code> | 源码注释：直接传 query_texts，ChromaDB 内置模型自动生成向量做匹配 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results = await asyncio.to_thread(</code> | 将结果保存到 <code>results</code>：等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._episodic.query,</code> | 续接 L311 的表达式：按前述语句组装参数、条件或集合。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query_texts=[query_text],</code> | 参数 <code>query_texts</code>（要向量化检索的文本列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;n_results=self.HISTORY_TOP_K,</code> | 参数 <code>n_results</code>（请求召回数量）：读取 <code>self.HISTORY_TOP_K</code>。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;where={&quot;user_id&quot;: self._safe_text(user_id)},</code> | 参数 <code>where</code>（存储查询过滤条件）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docs = results[&quot;documents&quot;][0] if results[&quot;documents&quot;] else []</code> | 将结果保存到 <code>docs</code>：条件 <code>results[&#x27;documents&#x27;]</code> 成立选前值，否则选 else 后值。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [self._safe_text(doc) for doc in docs if isinstance(doc, str) and doc.strip()]</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;情景记忆检索失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return []</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L322 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-323"></a>

### L323–L340 · MemoryManager._store_episodic

summary 放 document 参与向量检索；前 500 字原文放 metadata，ID 用 user/conv/time 哈希。异常只记日志。

**签名输入：** <code>self, user_id: str, conv_id: str, text: str, summary: str</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _store_episodic(self, user_id: str, conv_id: str, text: str, summary: str) -&gt; None:</code> | 定义异步函数 <code>_store_episodic</code>；输入参数见签名，下方导读解释调用目的。 |
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;将压缩后的对话片段存入情景记忆。ChromaDB 内置 embedding，不依赖外部 API。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id = self._safe_text(user_id)</code> | 将结果保存到 <code>user_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id = self._safe_text(conv_id)</code> | 将结果保存到 <code>conv_id</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text = self._safe_text(text)</code> | 将结果保存到 <code>text</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;summary = self._safe_text(summary)</code> | 将结果保存到 <code>summary</code>：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;doc_id = hashlib.md5(f&quot;{user_id}{conv_id}{time.time()}&quot;.encode()).hexdigest()</code> | 将结果保存到 <code>doc_id</code>：调用 <code>hashlib.md5(f&#x27;{user_id}{conv_id}{time.time()}&#x27;.encode()).hexdigest</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L331 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 直接传 documents，ChromaDB 内置模型自动生成 embedding</code> | 源码注释：直接传 documents，ChromaDB 内置模型自动生成 embedding |
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await asyncio.to_thread(</code> | 等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._episodic.add,</code> | 续接 L332 的表达式：按前述语句组装参数、条件或集合。 |
| L334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ids=[doc_id],</code> | 参数 <code>ids</code>（文档标识列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L335 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;documents=[summary],</code> | **关键：**向量化的是摘要，不是整段原始对话。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadatas=[{&quot;user_id&quot;: user_id, &quot;conv_id&quot;: conv_id,</code> | 参数 <code>metadatas</code>（每个文档的元信息列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;ts&quot;: datetime.now().isoformat(), &quot;full_text&quot;: self._safe_text(text[:500])}],</code> | 字段 <code>full_text</code>（当前映射中的键）：进入 <code>self._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;存储情景记忆失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L341 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-342"></a>

### L342–L350 · MemoryManager._get_profile

where user_id + limit=1 取一条，JSON 解析；没有 order_by 时间，不能保证最新。

**签名输入：** <code>self, user_id: str</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def _get_profile(self, user_id: str) -&gt; Dict[str, Any]:</code> | 定义异步函数 <code>_get_profile</code>；输入参数见签名，下方导读解释调用目的。 |
| L343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;获取用户画像（取最新一条）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L345 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results = await asyncio.to_thread(self._profile.get, where={&quot;user_id&quot;: user_id}, limit=1)</code> | **关键：**limit=1 只控制数量，没有按 ts 排序。 |
| L346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if results[&quot;documents&quot;]:</code> | 判断 <code>results[&#x27;documents&#x27;]</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return json.loads(results[&quot;documents&quot;][0])</code> | 结束当前函数并返回；将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L348 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pass</code> | 有意不处理；异常分支可能因此丢失错误信号。 |
| L350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L351 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-352"></a>

### L352–L354 · MemoryManager.close

只关闭 Redis；LLM 客户端未在这里关闭。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L352 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def close(self) -&gt; None:</code> | 定义异步函数 <code>close</code>；输入参数见签名，下方导读解释调用目的。 |
| L353 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;关闭异步 Redis 连接。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L354 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await self._redis.aclose()</code> | 等待完成后继续；释放 Redis 异步连接。 |
| L355 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-356"></a>

### L356–L358 · MemoryManager._wm_key

wm:user_id:conv_id，同一用户同一会话才命中同一列表；冒号拼接未转义。

**签名输入：** <code>user_id: str, conv_id: str</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _wm_key(user_id: str, conv_id: str) -&gt; str:</code> | 定义函数 <code>_wm_key</code>；输入参数见签名，下方导读解释调用目的。 |
| L358 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return f&quot;wm:{user_id}:{conv_id}&quot;</code> | 结束当前函数并返回；将变量插入模板，构造提示词、标识或可读说明。 |
| L359 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-360"></a>

### L360–L362 · MemoryManager._summary_key

summary:user_id:conv_id，与消息列表独立 TTL。

**签名输入：** <code>user_id: str, conv_id: str</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L361 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _summary_key(user_id: str, conv_id: str) -&gt; str:</code> | 定义函数 <code>_summary_key</code>；输入参数见签名，下方导读解释调用目的。 |
| L362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return f&quot;summary:{user_id}:{conv_id}&quot;</code> | 结束当前函数并返回；将变量插入模板，构造提示词、标识或可读说明。 |
| L363 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-364"></a>

### L364–L371 · MemoryManager._safe_text

非字符串转字符串并删除代理字符；不会匿名化用户内容。

**签名输入：** <code>value: Any</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L364 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _safe_text(value: Any) -&gt; str:</code> | 定义函数 <code>_safe_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L366 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;转成 ChromaDB 可接受的普通 UTF-8 字符串。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L367 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if value is None:</code> | 判断 <code>value is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L368 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;</code> | 结束当前函数并返回；使用固定文本/配置值。 |
| L369 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(value, str):</code> | 判断 <code>not isinstance(value, str)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L370 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value = str(value)</code> | 将结果保存到 <code>value</code>：转换为字符串表示。 |
| L371 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return value.encode(&quot;utf-8&quot;, errors=&quot;ignore&quot;).decode(&quot;utf-8&quot;)</code> | 结束当前函数并返回；调用 <code>value.encode(&#x27;utf-8&#x27;, errors=&#x27;ignore&#x27;).decode</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L372 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-373"></a>

### L373–L382 · MemoryManager._safe_metadata_value

递归清理字符串/字典/列表，其他对象原样保留，仍可能不支持 JSON 序列化。

**签名输入：** <code>cls, value: Any</code>；**返回契约：** <code>Any</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L373 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@classmethod</code> | 装饰器 <code>@classmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L374 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _safe_metadata_value(cls, value: Any) -&gt; Any:</code> | 定义函数 <code>_safe_metadata_value</code>；输入参数见签名，下方导读解释调用目的。 |
| L375 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;递归清洗 metadata，避免 Redis/ChromaDB 后续读写遇到非法 UTF-8。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L376 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(value, str):</code> | 判断 <code>isinstance(value, str)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L377 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return cls._safe_text(value)</code> | 结束当前函数并返回；进入 <code>cls._safe_text</code>：非字符串转字符串并删除代理字符；不会匿名化用户内容。 |
| L378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(value, dict):</code> | 判断 <code>isinstance(value, dict)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L379 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {cls._safe_text(k): cls._safe_metadata_value(v) for k, v in value.items()}</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(value, list):</code> | 判断 <code>isinstance(value, list)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [cls._safe_metadata_value(v) for v in value]</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return value</code> | 结束当前函数并返回；读取 <code>value</code>。 |

## 结合全项目：设计缺口与增强方向

- L280 reversed(keep)+LPUSH 与 L294 reversed(raws) 组合使压缩后保留消息倒序，已在离线复现中核实。
- 压缩读快照、调用 LLM、delete 后重建不是原子操作；并发追加可能在 delete 时丢失。画像 delete+add 也有并发竞争。
- 摘要实现是 old_summary+新摘要不断拼接，不是注释说的覆盖；无 token 预算，长会话摘要仍会无限长。
- 情景存储只在压缩时发生；短会话 Redis 过期后不会自动完整归档。Chroma 存的是 summary，full_text 元数据只保留前 500 字符。
- _get_profile 的 limit=1 未按 ts 排序，也没有合并多会话偏好；注释“最新一条”没有实现保证。
- 画像/摘要从含模型回复的文本提取，可能把助手猜测当用户事实；缺少事实来源、纠错、过期、删除策略。
- Redis 调用大多无降级，情景存储失败却被捕获后继续删旧消息；没有持久化确认与重试队列。
- 文件头“全部 Embedding 通过 Anthropic”和“按重要性+时效性排序”与实现不符；实际通过 Chroma 文本接口、情景按检索返回顺序，没有时间重排。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
