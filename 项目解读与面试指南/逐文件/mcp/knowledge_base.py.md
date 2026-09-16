# mcp/knowledge_base.py 解读

## 输入、输出与流向

**定位：** 知识材料的存储适配层：负责切片、写入和初次向量召回。

**输入：** Chroma 地址/本地路径；documents[{title,content}]；query/top_k；工具 handler 参数。

**输出 / 副作用：** 切片数量、列表[{title,content,score,chunk}]、collection count；副作用：创建 knowledge_base，空库导入默认材料，写 Chroma。

**流向：** 构造时 HTTP heartbeat→失败本地持久化→collection；导入→切片→ID/元数据→add；查询→query_texts→距离→展示分数→ToolManager 重排。

[返回阅读入口](../../README.md) · [对照原文件](../../../mcp/knowledge_base.py)

当前工作区快照：260 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`5869466a02ebfe3115f5107a75a51832a5dee9a56131036a31eef3d656373750`。

## 类与函数导航

[KnowledgeBase](#symbol-24) → [KnowledgeBase.__init__](#symbol-35) → [KnowledgeBase.add_documents](#symbol-73) → [KnowledgeBase.add_documents_async](#symbol-100) → [KnowledgeBase.search](#symbol-104) → [KnowledgeBase.search_async](#symbol-131) → [KnowledgeBase.doc_count](#symbol-135) → [KnowledgeBase.doc_count_async](#symbol-139) → [KnowledgeBase.search_handler](#symbol-145) → [KnowledgeBase._chunk_text](#symbol-161) → [KnowledgeBase._load_default_docs](#symbol-186)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>RAG 知识库 —— 基于 ChromaDB 的真实检索实现。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>功能：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | <code>&nbsp;&nbsp;1. 文档导入：将文本切片后存入 ChromaDB（自动生成 Embedding）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L6 | <code>&nbsp;&nbsp;2. 语义检索：根据 query 从知识库中检索最相关的文档片段</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;3. 与 MCP 工具框架集成：作为 knowledge_search 工具的真实 handler</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L8 | （空行） | 空行，分隔逻辑。 |
| L9 | <code>ChromaDB 在这里的角色：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L10 | <code>&nbsp;&nbsp;- memory/ 中用于存储对话记忆（情景记忆 + 用户画像）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L11 | <code>&nbsp;&nbsp;- 这里用于存储知识库文档（RAG 检索）</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L12 | <code>&nbsp;&nbsp;两者是不同的 collection，互不干扰。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L13 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L14 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L15 | <code>import hashlib</code> | 导入 <code>import hashlib</code>；只建立名称依赖，真正业务调用见后文。 |
| L16 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L17 | <code>from typing import Any, Dict, List, Optional</code> | 导入 <code>from typing import Any, Dict, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L18 | （空行） | 空行，分隔逻辑。 |
| L19 | <code>import chromadb</code> | 导入 <code>import chromadb</code>；只建立名称依赖，真正业务调用见后文。 |
| L20 | （空行） | 空行，分隔逻辑。 |
| L21 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L22 | （空行） | 空行，分隔逻辑。 |
| L23 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-24"></a>

### L24–L260 · KnowledgeBase

知识材料的存储适配层：负责切片、写入和初次向量召回。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L24 | <code>class KnowledgeBase:</code> | 定义 <code>KnowledgeBase</code> 的数据契约/行为；继承与字段见本段。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;基于 ChromaDB 的 RAG 知识库。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L27 | （空行） | 空行，分隔逻辑。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ChromaDB 内置了 Embedding 模型（all-MiniLM-L6-v2），</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;调用 add() 时自动生成向量，query() 时自动做语义匹配。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;不需要额外调用 Anthropic Embeddings API。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L32 | （空行） | 空行，分隔逻辑。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;COLLECTION_NAME = &quot;knowledge_base&quot;</code> | 将结果保存到 <code>COLLECTION_NAME</code>：使用固定文本/配置值。 |
| L34 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-35"></a>

### L35–L69 · KnowledgeBase.__init__

先尝试远程 Chroma 并 heartbeat，任意异常回退 PersistentClient。随后创建 collection、空库导入 6 篇默认知识。构造是同步过程，会影响启动时间。

**签名输入：** <code>self, chroma_host: str=&#x27;localhost&#x27;, chroma_port: int=8000, chroma_path: str=&#x27;./data/chroma&#x27;</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_host: str = &quot;localhost&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_port: int = 8000,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_path: str = &quot;./data/chroma&quot;,</code> | 函数参数/返回类型签名续行；默认值决定调用方可省略什么。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 优先连接独立 ChromaDB 服务（服务端内置 embedding 模型，客户端无需下载）</code> | 源码注释：优先连接独立 ChromaDB 服务（服务端内置 embedding 模型，客户端无需下载） |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._use_server = False</code> | 将结果保存到 <code>self._use_server</code>：使用这里写明的固定值。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# HttpClient 默认也会初始化 ChromaDB telemetry；显式关闭避免 posthog 兼容性错误日志。</code> | 源码注释：HttpClient 默认也会初始化 ChromaDB telemetry；显式关闭避免 posthog 兼容性错误日志。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._client = chromadb.HttpClient(</code> | 将结果保存到 <code>self._client</code>：调用 <code>chromadb.HttpClient</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;host=chroma_host,</code> | 参数 <code>host</code>（host）：读取 <code>chroma_host</code>。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;port=chroma_port,</code> | 参数 <code>port</code>（port）：读取 <code>chroma_port</code>。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;settings=chromadb.Settings(anonymized_telemetry=False),</code> | 参数 <code>anonymized_telemetry</code>（anonymized_telemetry）：使用这里写明的固定值。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._client.heartbeat()</code> | 调用 <code>self._client.heartbeat</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._use_server = True</code> | 将结果保存到 <code>self._use_server</code>：使用这里写明的固定值。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;知识库 ChromaDB 已连接: {chroma_host}:{chroma_port}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;知识库 ChromaDB 服务不可用，使用本地模式: {chroma_path}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._client = chromadb.PersistentClient(</code> | 将结果保存到 <code>self._client</code>：调用 <code>chromadb.PersistentClient</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path=chroma_path,</code> | 参数 <code>path</code>（path）：读取 <code>chroma_path</code>。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;settings=chromadb.Settings(anonymized_telemetry=False),</code> | 参数 <code>anonymized_telemetry</code>（anonymized_telemetry）：使用这里写明的固定值。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L59 | （空行） | 空行，分隔逻辑。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 使用服务端时不传 embedding_function，让服务端处理</code> | 源码注释：使用服务端时不传 embedding_function，让服务端处理 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 本地模式时也不传，使用 ChromaDB 默认的（会触发模型下载）</code> | 源码注释：本地模式时也不传，使用 ChromaDB 默认的（会触发模型下载） |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._collection = self._client.get_or_create_collection(</code> | 将结果保存到 <code>self._collection</code>：调用 <code>self._client.get_or_create_collection</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name=self.COLLECTION_NAME,</code> | 参数 <code>name</code>（name）：读取 <code>self.COLLECTION_NAME</code>。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metadata={&quot;description&quot;: &quot;EchoMind RAG 知识库&quot;},</code> | 参数 <code>metadata</code>（附加元信息）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L66 | （空行） | 空行，分隔逻辑。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 如果知识库为空，导入默认文档</code> | 源码注释：如果知识库为空，导入默认文档 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._collection.count() == 0:</code> | 判断 <code>self._collection.count() == 0</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._load_default_docs()</code> | 进入 <code>self._load_default_docs</code>：内置退款、订单、账户安全、技术、积分、配送六篇 demo 文档；仅空库自动导入。 |
| L70 | （空行） | 空行，分隔逻辑。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 文档管理 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 文档管理 ────────────────────────────────────────────────────────────── |
| L72 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-73"></a>

### L73–L98 · KnowledgeBase.add_documents

按篇切成片段，每片带标题、序号、总片数。使用 MD5 生成可重复 ID，写 documents 让库侧接口所配置的 embedding 过程完成向量化。

**签名输入：** <code>self, documents: List[Dict[str, str]]</code>；**返回契约：** <code>int</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def add_documents(self, documents: List[Dict[str, str]]) -&gt; int:</code> | 定义函数 <code>add_documents</code>；输入参数见签名，下方导读解释调用目的。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;批量导入文档到知识库。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L76 | （空行） | 空行，分隔逻辑。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;documents 格式: [{&quot;title&quot;: &quot;...&quot;, &quot;content&quot;: &quot;...&quot;}, ...]</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;长文档会自动切片（每片 500 字）。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ids, docs, metas = [], [], []</code> | 将结果保存到 <code>(ids, docs, metas)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L81 | （空行） | 空行，分隔逻辑。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for doc in documents:</code> | 遍历 <code>documents</code>，本轮元素绑定 <code>doc</code>。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;title   = doc.get(&quot;title&quot;, &quot;&quot;)</code> | 将结果保存到 <code>title</code>：按键取值，缺失用给定默认值。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content = doc.get(&quot;content&quot;, &quot;&quot;)</code> | 将结果保存到 <code>content</code>：按键取值，缺失用给定默认值。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chunks  = self._chunk_text(content, chunk_size=500)</code> | 将结果保存到 <code>chunks</code>：进入 <code>self._chunk_text</code>：短文保留原文；长文将换行替换为中文句号，再按句子装箱，超预算就另起片。 |
| L86 | （空行） | 空行，分隔逻辑。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i, chunk in enumerate(chunks):</code> | 遍历 <code>enumerate(chunks)</code>，本轮元素绑定 <code>(i, chunk)</code>。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;doc_id = hashlib.md5(f&quot;{title}_{i}_{chunk[:50]}&quot;.encode()).hexdigest()</code> | **关键：**只哈希片段前 50 字符；后半段改动无法改变 ID。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ids.append(doc_id)</code> | 追加一个元素到当前列表。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docs.append(chunk)</code> | 追加一个元素到当前列表。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;metas.append({&quot;title&quot;: title, &quot;chunk_index&quot;: i, &quot;total_chunks&quot;: len(chunks)})</code> | 追加一个元素到当前列表。 |
| L92 | （空行） | 空行，分隔逻辑。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if ids:</code> | 判断 <code>ids</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# ChromaDB 会自动生成 Embedding</code> | 源码注释：ChromaDB 会自动生成 Embedding |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._collection.add(ids=ids, documents=docs, metadatas=metas)</code> | **关键：**add 没有版本替换/删除旧片逻辑。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;知识库导入 {len(ids)} 个文档片段&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L97 | （空行） | 空行，分隔逻辑。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return len(ids)</code> | 结束当前函数并返回；计算当前容器或字符串长度。 |
| L99 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-100"></a>

### L100–L102 · KnowledgeBase.add_documents_async

把同步导入放线程，HTTP await 不阻塞主事件循环，但 CPU/线程资源仍会消耗。

**签名输入：** <code>self, documents: List[Dict[str, str]]</code>；**返回契约：** <code>int</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def add_documents_async(self, documents: List[Dict[str, str]]) -&gt; int:</code> | 定义异步函数 <code>add_documents_async</code>；输入参数见签名，下方导读解释调用目的。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;异步导入文档；ChromaDB 客户端为同步实现，因此放入线程池执行。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await asyncio.to_thread(self.add_documents, documents)</code> | 结束当前函数并返回；等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L103 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-104"></a>

### L104–L129 · KnowledgeBase.search

给一个 query，所以结果嵌套列表取第 0 组，再 zip 文本/元数据/距离。只返回内容和展示字段，没有传回库原始 ID。

**签名输入：** <code>self, query: str, top_k: int=5</code>；**返回契约：** <code>List[Dict[str, Any]]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def search(self, query: str, top_k: int = 5) -&gt; List[Dict[str, Any]]:</code> | 定义函数 <code>search</code>；输入参数见签名，下方导读解释调用目的。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;语义检索：根据 query 返回最相关的文档片段。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L107 | （空行） | 空行，分隔逻辑。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChromaDB 内部自动将 query 转为向量，与存储的文档向量做余弦相似度匹配。</code> | **关键：**注释声称余弦，但 collection 初始化未显式配置；应以实际库配置为准。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results = self._collection.query(</code> | 将结果保存到 <code>results</code>：调用 <code>self._collection.query</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query_texts=[query],</code> | 参数 <code>query_texts</code>（要向量化检索的文本列表）：组装有序值或集合，元素在后续逻辑中消费。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;n_results=top_k,</code> | 参数 <code>n_results</code>（请求召回数量）：读取 <code>top_k</code>。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L114 | （空行） | 空行，分隔逻辑。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;items = []</code> | 将结果保存到 <code>items</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if results[&quot;documents&quot;] and results[&quot;documents&quot;][0]:</code> | 判断 <code>results[&#x27;documents&#x27;] and results[&#x27;documents&#x27;][0]</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for doc, meta, dist in zip(</code> | 遍历 <code>zip(results[&#x27;documents&#x27;][0], results[&#x27;metadatas&#x27;][0], results[&#x27;distances&#x27;][0])</code>，本轮元素绑定 <code>(doc, meta, dist)</code>。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results[&quot;documents&quot;][0],</code> | 续接 L117 的表达式：按前述语句组装参数、条件或集合。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results[&quot;metadatas&quot;][0],</code> | 续接 L117 的表达式：按前述语句组装参数、条件或集合。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results[&quot;distances&quot;][0],</code> | 续接 L117 的表达式：按前述语句组装参数、条件或集合。 |
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;):</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;items.append({</code> | 追加一个元素到当前列表。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;:    meta.get(&quot;title&quot;, &quot;&quot;),</code> | 字段 <code>title</code>（展示标题）：按键取值，缺失用给定默认值。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;:  doc,</code> | 字段 <code>content</code>（文本正文）：读取 <code>doc</code>。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;score&quot;:    round(1.0 - dist, 4),  # ChromaDB 返回距离，转为相似度</code> | **关键：**展示分数=1-距离，不保证范围、不保证等于余弦。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;chunk&quot;:    meta.get(&quot;chunk_index&quot;, 0),</code> | 字段 <code>chunk</code>（当前映射中的键）：按键取值，缺失用给定默认值。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;})</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L128 | （空行） | 空行，分隔逻辑。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return items</code> | 结束当前函数并返回；读取 <code>items</code>。 |
| L130 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-131"></a>

### L131–L133 · KnowledgeBase.search_async

同步 query 放线程池，是 ToolManager 到存储的异步适配。

**签名输入：** <code>self, query: str, top_k: int=5</code>；**返回契约：** <code>List[Dict[str, Any]]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def search_async(self, query: str, top_k: int = 5) -&gt; List[Dict[str, Any]]:</code> | 定义异步函数 <code>search_async</code>；输入参数见签名，下方导读解释调用目的。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;异步检索；ChromaDB 客户端为同步实现，因此放入线程池执行。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await asyncio.to_thread(self.search, query, top_k)</code> | 结束当前函数并返回；等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L134 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-135"></a>

### L135–L137 · KnowledgeBase.doc_count

同步 property 查询 count，访问它就会执行 I/O。

**签名输入：** <code>self</code>；**返回契约：** <code>int</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def doc_count(self) -&gt; int:</code> | 定义函数 <code>doc_count</code>；输入参数见签名，下方导读解释调用目的。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self._collection.count()</code> | 结束当前函数并返回；调用 <code>self._collection.count</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L138 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-139"></a>

### L139–L141 · KnowledgeBase.doc_count_async

线程中执行 collection.count，用于 API 的启动日志/统计。

**签名输入：** <code>self</code>；**返回契约：** <code>int</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def doc_count_async(self) -&gt; int:</code> | 定义异步函数 <code>doc_count_async</code>；输入参数见签名，下方导读解释调用目的。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;异步获取文档片段数量。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await asyncio.to_thread(self._collection.count)</code> | 结束当前函数并返回；等待完成后继续；把同步函数交给线程池，避免同步 I/O 占住事件循环。 |
| L142 | （空行） | 空行，分隔逻辑。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── MCP 工具 handler ─────────────────────────────────────────────────────</code> | 源码注释：── MCP 工具 handler ───────────────────────────────────────────────────── |
| L144 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-145"></a>

### L145–L157 · KnowledgeBase.search_handler

把通用工具 params 翻译成业务 search 参数；context 未使用，当前知识库不按用户区分。

**签名输入：** <code>self, params: Dict[str, Any], context: Any</code>；**返回契约：** <code>List[Dict]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;async def search_handler(self, params: Dict[str, Any], context: Any) -&gt; List[Dict]:</code> | 定义异步函数 <code>search_handler</code>；输入参数见签名，下方导读解释调用目的。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;作为 MCP 工具的 handler 注册。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L148 | （空行） | 空行，分隔逻辑。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;MCPToolManager.register(Tool(</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name=&quot;knowledge_search&quot;,</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;handler=kb.search_handler,</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;))</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query = params.get(&quot;query&quot;, &quot;&quot;)</code> | 将结果保存到 <code>query</code>：按键取值，缺失用给定默认值。 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;top_k = params.get(&quot;top_k&quot;, 5)</code> | 将结果保存到 <code>top_k</code>：按键取值，缺失用给定默认值。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return await self.search_async(query, top_k=top_k)</code> | 结束当前函数并返回；等待完成后继续；进入 <code>self.search_async</code>：同步 query 放线程池，是 ToolManager 到存储的异步适配。 |
| L158 | （空行） | 空行，分隔逻辑。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# ── 内部方法 ──────────────────────────────────────────────────────────────</code> | 源码注释：── 内部方法 ────────────────────────────────────────────────────────────── |
| L160 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-161"></a>

### L161–L184 · KnowledgeBase._chunk_text

短文保留原文；长文将换行替换为中文句号，再按句子装箱，超预算就另起片。长句自己超过 500 时仍完整保留。

**签名输入：** <code>self, text: str, chunk_size: int=500</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _chunk_text(self, text: str, chunk_size: int = 500) -&gt; List[str]:</code> | 定义函数 <code>_chunk_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;将长文本按 chunk_size 切片，保留语义完整性（按句号/换行切分）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(text) &lt;= chunk_size:</code> | 判断 <code>len(text) &lt;= chunk_size</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [text] if text.strip() else []</code> | 结束当前函数并返回；条件 <code>text.strip()</code> 成立选前值，否则选 else 后值。 |
| L165 | （空行） | 空行，分隔逻辑。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chunks = []</code> | 将结果保存到 <code>chunks</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;current = &quot;&quot;</code> | 将结果保存到 <code>current</code>：使用固定文本/配置值。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 按句子切分</code> | 源码注释：按句子切分 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sentences = text.replace(&quot;\n&quot;, &quot;。&quot;).split(&quot;。&quot;)</code> | 将结果保存到 <code>sentences</code>：按分隔符切分字符串。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for sent in sentences:</code> | 遍历 <code>sentences</code>，本轮元素绑定 <code>sent</code>。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sent = sent.strip()</code> | 将结果保存到 <code>sent</code>：去除两端指定字符或空白。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not sent:</code> | 判断 <code>not sent</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(current) + len(sent) + 1 &gt; chunk_size:</code> | 判断 <code>len(current) + len(sent) + 1 &gt; chunk_size</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if current:</code> | 判断 <code>current</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chunks.append(current)</code> | 追加一个元素到当前列表。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;current = sent</code> | **关键：**即使 sent 自己超过 chunk_size 也直接保留，500 非硬限制。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;current = f&quot;{current}。{sent}&quot; if current else sent</code> | 将结果保存到 <code>current</code>：条件 <code>current</code> 成立选前值，否则选 else 后值。 |
| L180 | （空行） | 空行，分隔逻辑。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if current:</code> | 判断 <code>current</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chunks.append(current)</code> | 追加一个元素到当前列表。 |
| L183 | （空行） | 空行，分隔逻辑。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return chunks</code> | 结束当前函数并返回；读取 <code>chunks</code>。 |
| L185 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-186"></a>

### L186–L260 · KnowledgeBase._load_default_docs

内置退款、订单、账户安全、技术、积分、配送六篇 demo 文档；仅空库自动导入。data/demo_docs 下文件不是此函数自动加载源。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _load_default_docs(self) -&gt; None:</code> | 定义函数 <code>_load_default_docs</code>；输入参数见签名，下方导读解释调用目的。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;导入默认知识库文档（客服场景常见问题）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;default_docs = [</code> | 将结果保存到 <code>default_docs</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;: &quot;退款政策&quot;,</code> | 字段 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: (</code> | 字段 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;退款政策说明。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;用户在购买后 7 天内可以申请无理由退款。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;退款申请提交后，系统会在 1-3 个工作日内审核。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;审核通过后，款项将在 5-7 个工作日内退回原支付账户。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;如果商品已发货，需要先完成退货流程才能退款。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;退货运费由用户承担，除非是商品质量问题。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;超过 7 天但未超过 30 天的订单，需要提供商品质量问题的证据才能退款。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;),</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;: &quot;订单查询&quot;,</code> | 字段 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: (</code> | 字段 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;订单查询指南。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;用户可以通过订单号查询订单状态。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;订单状态包括：待支付、已支付、已发货、运输中、已签收、已完成。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;如果订单显示已发货但超过 7 天未收到，可以联系客服申请查件。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;物流信息通常在发货后 24 小时内更新。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;如果订单显示异常，请提供订单号联系客服处理。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;),</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;: &quot;账户安全&quot;,</code> | 字段 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: (</code> | 字段 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;账户安全说明。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;建议用户定期修改密码，密码长度至少 8 位，包含字母和数字。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;如果忘记密码，可以通过绑定的手机号或邮箱重置。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;发现账户异常登录时，系统会自动锁定账户并发送通知。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;用户可以在安全设置中开启两步验证，提高账户安全性。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;不要将密码分享给他人，客服人员不会索要用户密码。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;),</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;: &quot;技术故障排查&quot;,</code> | 字段 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: (</code> | 字段 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;常见技术问题排查。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;应用崩溃：请尝试清除缓存后重启应用，如果问题持续请更新到最新版本。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;登录失败 401 错误：表示认证失败，请检查用户名密码是否正确，或尝试重置密码。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;页面加载慢：检查网络连接，尝试切换 WiFi 或移动数据。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;支付失败：确认银行卡余额充足，检查是否开启了网上支付功能。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;500 服务器错误：这是服务端问题，请稍后重试，如果持续出现请联系技术支持。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;),</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;: &quot;会员与积分&quot;,</code> | 字段 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: (</code> | 字段 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;会员积分规则。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;每消费 1 元累积 1 积分。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;积分可以在下次购物时抵扣，100 积分 = 1 元。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;会员等级分为：普通会员、银卡会员（累计消费 1000 元）、金卡会员（累计消费 5000 元）。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;银卡会员享受 95 折优惠，金卡会员享受 9 折优惠。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;积分有效期为 1 年，过期自动清零。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;生日当月消费可获得双倍积分。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;),</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;: &quot;配送说明&quot;,</code> | 字段 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: (</code> | 字段 <code>content</code>（文本正文）：使用固定文本/配置值。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;配送服务说明。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;标准配送：3-5 个工作日送达，免运费（订单满 99 元）。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;加急配送：1-2 个工作日送达，运费 15 元。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;同城配送：当日达或次日达，运费 10 元。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;偏远地区可能需要额外 2-3 天。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;配送时间为每天 9:00-18:00，节假日可能延迟。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;如果需要修改收货地址，请在发货前联系客服。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;),</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.add_documents(default_docs)</code> | 进入 <code>self.add_documents</code>：按篇切成片段，每片带标题、序号、总片数。 |
| L260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;已导入默认知识库: {len(default_docs)} 篇文档&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |

## 结合全项目：设计缺口与增强方向

- collection 没显式设置距离度量，故注释中的“余弦相似度”不能由本文件保证。1-dist 也不是校准到 [0,1] 的相关概率，可能为负。
- 只传 documents/query_texts、未显式 embedding_function；不能凭 HttpClient 就断言向量一定在服务端算或客户端不下载模型。Dockerfile 反而预下载 ONNX 模型。
- 单个长句没有硬切分，500 是拼句目标而非严格上限；没有 overlap、标题层级/表格处理。
- ID 只含标题、序号、前 50 字符；同前缀但后文改变会同 ID。使用 add 而非版本化 upsert，没有删除旧版本接口。返回数量是准备写入数，不是净新增数。
- 启动远程连不上自动本地降级，运维配置错时可能悄悄产生两个数据源；API health 看不出区别。
- 结果未带稳定 source/chunk ID、时间和访问权限；不能做可靠引用、权限过滤或检索质量归因。默认文档是示例政策，不能当真实企业政策。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
