# api/main.py 解读

## 输入、输出与流向

**定位：** 应用装配入口与 HTTP 用例层：把独立模块串成一次客服请求。

**输入：** 启动：进程环境变量和 .env；请求：ChatRequest(message, user_id, conv_id)、上传内容、检索参数、评测用例。

**输出 / 副作用：** HTTP JSON / Prometheus 文本；副作用：Redis 消息、Chroma 文档/摘要/画像、评测基线，以及后台监控任务。

**流向：** lifespan 装配 → chat 读取 MemoryContext → recognize_intent → 按意图调用 RAG → Request → OrchestratorResult → 两次 add_message → 后台画像 → ChatResponse。CLI 是另一条较短链路。

[返回阅读入口](../../README.md) · [对照原文件](../../../api/main.py)

当前工作区快照：651 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`79c86ac7708f4904f8b161dfb4a0ee0e0cf614234efe4b88e0fe1a88727a561e`。

## 类与函数导航

[_anthropic_cfg](#symbol-53) → [lifespan](#symbol-67) → [knowledge_fallback](#symbol-132) → [ChatRequest](#symbol-206) → [ChatResponse](#symbol-212) → [health](#symbol-232) → [skills_summary](#symbol-239) → [reload_skills](#symbol-247) → [chat](#symbol-258) → [_build_knowledge_context](#symbol-331) → [_should_use_knowledge](#symbol-368) → [monitor_summary](#symbol-393) → [prometheus_metrics](#symbol-401) → [search](#symbol-407) → [DocInput](#symbol-419) → [BatchDocInput](#symbol-425) → [EvalIntentInput](#symbol-430) → [EvalDialogInput](#symbol-437) → [EvalRunInput](#symbol-445) → [add_knowledge](#symbol-451) → [upload_knowledge](#symbol-477) → [knowledge_stats](#symbol-522) → [run_eval](#symbol-532) → [_cli](#symbol-584)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>EchoMind 智能客服系统 — FastAPI 入口</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>启动时打印小熊饼干图案。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | <code>所有核心组件在 lifespan 中初始化，通过环境变量配置。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L6 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>import asyncio</code> | 导入 <code>import asyncio</code>；只建立名称依赖，真正业务调用见后文。 |
| L8 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L9 | <code>import os</code> | 导入 <code>import os</code>；只建立名称依赖，真正业务调用见后文。 |
| L10 | <code>import pathlib</code> | 导入 <code>import pathlib</code>；只建立名称依赖，真正业务调用见后文。 |
| L11 | <code>import sys</code> | 导入 <code>import sys</code>；只建立名称依赖，真正业务调用见后文。 |
| L12 | <code>import uuid</code> | 导入 <code>import uuid</code>；只建立名称依赖，真正业务调用见后文。 |
| L13 | <code>from contextlib import asynccontextmanager</code> | 导入 <code>from contextlib import asynccontextmanager</code>；只建立名称依赖，真正业务调用见后文。 |
| L14 | <code>from typing import Any, Dict, List, Optional</code> | 导入 <code>from typing import Any, Dict, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L15 | （空行） | 空行，分隔逻辑。 |
| L16 | （空行） | 空行，分隔逻辑。 |
| L17 | <code>_ROOT = str(pathlib.Path(__file__).parent.parent.resolve())</code> | 将结果保存到 <code>_ROOT</code>：转换为字符串表示。 |
| L18 | <code>if _ROOT not in sys.path:</code> | 判断 <code>_ROOT not in sys.path</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;sys.path.insert(0, _ROOT)</code> | 在模块搜索路径前方插入项目根目录，使内部模块可被找到。 |
| L20 | （空行） | 空行，分隔逻辑。 |
| L21 | <code>import uvicorn</code> | 导入 <code>import uvicorn</code>；只建立名称依赖，真正业务调用见后文。 |
| L22 | <code>from dotenv import load_dotenv</code> | 导入 <code>from dotenv import load_dotenv</code>；只建立名称依赖，真正业务调用见后文。 |
| L23 | <code>from fastapi import FastAPI, HTTPException, Response, UploadFile, File</code> | 导入 <code>from fastapi import FastAPI, HTTPException, Response, UploadFile, File</code>；只建立名称依赖，真正业务调用见后文。 |
| L24 | <code>from fastapi.middleware.cors import CORSMiddleware</code> | 导入 <code>from fastapi.middleware.cors import CORSMiddleware</code>；只建立名称依赖，真正业务调用见后文。 |
| L25 | <code>from prometheus_client import CONTENT_TYPE_LATEST, generate_latest</code> | 导入 <code>from prometheus_client import CONTENT_TYPE_LATEST, generate_latest</code>；只建立名称依赖，真正业务调用见后文。 |
| L26 | <code>from pydantic import BaseModel, Field</code> | 导入 <code>from pydantic import BaseModel, Field</code>；只建立名称依赖，真正业务调用见后文。 |
| L27 | （空行） | 空行，分隔逻辑。 |
| L28 | <code>load_dotenv()</code> | 加载.env配置到进程环境；已有环境变量通常保持优先。 |
| L29 | （空行） | 空行，分隔逻辑。 |
| L30 | <code>logging.basicConfig(</code> | 设置日志等级和显示格式。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;level=getattr(logging, os.getenv(&quot;LOG_LEVEL&quot;, &quot;INFO&quot;)),</code> | 参数 <code>level</code>（level）：读取对象指定属性，不存在时返回这里给出的默认值。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;format=&quot;%(asctime)s [%(levelname)s] %(name)s: %(message)s&quot;,</code> | 参数 <code>format</code>（format）：使用固定文本/配置值。 |
| L33 | <code>)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L34 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L35 | （空行） | 空行，分隔逻辑。 |
| L36 | <code>BANNER = r&quot;&quot;&quot;</code> | 将结果保存到 <code>BANNER</code>：使用固定文本/配置值。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ʕ•ᴥ•ʔ  ʕ•ᴥ•ʔ  ʕ•ᴥ•ʔ</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;╔══════════════════════╗</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;║   EchoMind  v2.0     ║</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;║   智能客服 AI 系统    ║</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;╚══════════════════════╝</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ʕ•ᴥ•ʔ  ʕ•ᴥ•ʔ  ʕ•ᴥ•ʔ</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L43 | <code>&quot;&quot;&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L44 | （空行） | 空行，分隔逻辑。 |
| L45 | <code># ── 全局组件（lifespan 中初始化）─────────────────────────────────────────────</code> | 源码注释：── 全局组件（lifespan 中初始化）───────────────────────────────────────────── |
| L46 | <code>_orchestrator = None</code> | 将结果保存到 <code>_orchestrator</code>：使用这里写明的固定值。 |
| L47 | <code>_memory       = None</code> | 将结果保存到 <code>_memory</code>：使用这里写明的固定值。 |
| L48 | <code>_tool_manager = None</code> | 将结果保存到 <code>_tool_manager</code>：使用这里写明的固定值。 |
| L49 | <code>_monitor      = None</code> | 将结果保存到 <code>_monitor</code>：使用这里写明的固定值。 |
| L50 | <code>_evaluator    = None</code> | 将结果保存到 <code>_evaluator</code>：使用这里写明的固定值。 |
| L51 | <code>_skill_manager = None</code> | 将结果保存到 <code>_skill_manager</code>：使用这里写明的固定值。 |
| L52 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-53"></a>

### L53–L64 · _anthropic_cfg

配置边界：只校验 API Key 非空，再返回模型和可选 base_url；不验证凭据真实可用。模型名来自配置，本仓库不证明外部模型当前可用性。

**签名输入：** <code></code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L53 | <code>def _anthropic_cfg() -&gt; Dict[str, Any]:</code> | 定义函数 <code>_anthropic_cfg</code>；输入参数见签名，下方导读解释调用目的。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;key = os.getenv(&quot;ANTHROPIC_API_KEY&quot;, &quot;&quot;)</code> | 将结果保存到 <code>key</code>：读取进程环境配置，缺失时采用这里写的默认值。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if not key:</code> | 判断 <code>not key</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise RuntimeError(&quot;未设置 ANTHROPIC_API_KEY&quot;)</code> | 抛出 <code>RuntimeError(&#x27;未设置 ANTHROPIC_API_KEY&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cfg: Dict[str, Any] = {</code> | 将结果保存到 <code>cfg</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;api_key&quot;:  key,</code> | 字段 <code>api_key</code>（模型服务凭据）：读取 <code>key</code>。 |
| L59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;model&quot;:    os.getenv(&quot;ANTHROPIC_MODEL&quot;, &quot;claude-3-5-sonnet-20241022&quot;).strip(),</code> | 字段 <code>model</code>（模型名称）：去除两端指定字符或空白。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;base_url = os.getenv(&quot;ANTHROPIC_BASE_URL&quot;, &quot;&quot;).strip()</code> | 将结果保存到 <code>base_url</code>：去除两端指定字符或空白。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if base_url:</code> | 判断 <code>base_url</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cfg[&quot;base_url&quot;] = base_url</code> | 将结果保存到 <code>cfg[&#x27;base_url&#x27;]</code>：读取 <code>base_url</code>。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return cfg</code> | 结束当前函数并返回；读取 <code>cfg</code>。 |
| L65 | （空行） | 空行，分隔逻辑。 |
| L66 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-67"></a>

### L67–L186 · lifespan

进入 yield 之前创建进程级单例。两个 IntentRecognizer 分别供在线编排器和评测使用，因此缓存不共享；KB 构造可能同步连接并导入默认文档。yield 之后释放 Monitor/Redis。生产上应使用 try/finally 和显式依赖容器统一生命周期。

**签名输入：** <code>app: FastAPI</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L67 | <code>@asynccontextmanager</code> | 装饰器 <code>@asynccontextmanager</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L68 | <code>async def lifespan(app: FastAPI):</code> | 定义异步函数 <code>lifespan</code>；输入参数见签名，下方导读解释调用目的。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;global _orchestrator, _memory, _tool_manager, _monitor, _evaluator, _skill_manager</code> | 后续赋值修改模块级组件引用，使 HTTP 路由能共享初始化结果。 |
| L70 | （空行） | 空行，分隔逻辑。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print(BANNER, flush=True)</code> | 向终端输出文本。 |
| L72 | （空行） | 空行，分隔逻辑。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from agents.agent_orchestrator import AgentOrchestrator, Request</code> | 导入 <code>from agents.agent_orchestrator import AgentOrchestrator, Request</code>；只建立名称依赖，真正业务调用见后文。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from core.intent_recognizer import IntentRecognizer</code> | 导入 <code>from core.intent_recognizer import IntentRecognizer</code>；只建立名称依赖，真正业务调用见后文。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from evaluation.evaluator import EndToEndEvaluator</code> | 导入 <code>from evaluation.evaluator import EndToEndEvaluator</code>；只建立名称依赖，真正业务调用见后文。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from mcp.knowledge_base import KnowledgeBase</code> | 导入 <code>from mcp.knowledge_base import KnowledgeBase</code>；只建立名称依赖，真正业务调用见后文。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from mcp.tool_manager import MCPToolManager, Tool</code> | 导入 <code>from mcp.tool_manager import MCPToolManager, Tool</code>；只建立名称依赖，真正业务调用见后文。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from memory.conversation_memory import MemoryManager</code> | 导入 <code>from memory.conversation_memory import MemoryManager</code>；只建立名称依赖，真正业务调用见后文。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from monitor.performance_monitor import PerformanceMonitor</code> | 导入 <code>from monitor.performance_monitor import PerformanceMonitor</code>；只建立名称依赖，真正业务调用见后文。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from core.skill_loader import SkillManager</code> | 导入 <code>from core.skill_loader import SkillManager</code>；只建立名称依赖，真正业务调用见后文。 |
| L81 | （空行） | 空行，分隔逻辑。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cfg = _anthropic_cfg()</code> | 将结果保存到 <code>cfg</code>：进入 <code>_anthropic_cfg</code>：配置边界：只校验 API Key 非空，再返回模型和可选 base_url；不验证凭据真实可用。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;模型: {cfg[&#x27;model&#x27;]}  base_url: {cfg.get(&#x27;base_url&#x27;, &#x27;(官方)&#x27;)}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L84 | （空行） | 空行，分隔逻辑。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 意图识别器（Orchestrator 内部也会创建，这里单独暴露给 Evaluator）</code> | 源码注释：意图识别器（Orchestrator 内部也会创建，这里单独暴露给 Evaluator） |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;recognizer = IntentRecognizer(</code> | 将结果保存到 <code>recognizer</code>：调用 <code>IntentRecognizer</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key=cfg[&quot;api_key&quot;],</code> | 参数 <code>api_key</code>（模型服务凭据）：按索引/切片取 <code>cfg[&#x27;api_key&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url=cfg.get(&quot;base_url&quot;),</code> | 参数 <code>base_url</code>（模型服务地址）：按键取值，缺失用给定默认值。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=cfg[&quot;model&quot;],</code> | 参数 <code>model</code>（模型名称）：按索引/切片取 <code>cfg[&#x27;model&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L91 | （空行） | 空行，分隔逻辑。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# Skills：启动时从目录加载业务能力说明，并在 Agent 调用 LLM 时动态注入。</code> | 源码注释：Skills：启动时从目录加载业务能力说明，并在 Agent 调用 LLM 时动态注入。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;skills_dir = os.getenv(&quot;ECHOMIND_SKILLS_DIR&quot;, str(pathlib.Path(_ROOT) / &quot;skills&quot;))</code> | 将结果保存到 <code>skills_dir</code>：读取进程环境配置，缺失时采用这里写的默认值。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_skill_manager = SkillManager(</code> | 将结果保存到 <code>_skill_manager</code>：调用 <code>SkillManager</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;root_dir=skills_dir,</code> | 参数 <code>root_dir</code>（root_dir）：读取 <code>skills_dir</code>。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_prompt_chars=int(os.getenv(&quot;ECHOMIND_SKILLS_MAX_PROMPT_CHARS&quot;, &quot;5000&quot;)),</code> | 参数 <code>max_prompt_chars</code>（max_prompt_chars）：转换为整数。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_skill_manager.load()</code> | 进入 <code>_skill_manager.load</code>：目录不存在返回空；逐个解析，某个坏文件只记错不影响其他文件，最后整体替换快照并记日志。 |
| L99 | （空行） | 空行，分隔逻辑。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# Agent 编排器</code> | 源码注释：Agent 编排器 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_orchestrator = AgentOrchestrator(</code> | 将结果保存到 <code>_orchestrator</code>：调用 <code>AgentOrchestrator</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key=cfg[&quot;api_key&quot;],</code> | 参数 <code>api_key</code>（模型服务凭据）：按索引/切片取 <code>cfg[&#x27;api_key&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url=cfg.get(&quot;base_url&quot;),</code> | 参数 <code>base_url</code>（模型服务地址）：按键取值，缺失用给定默认值。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=cfg[&quot;model&quot;],</code> | 参数 <code>model</code>（模型名称）：按索引/切片取 <code>cfg[&#x27;model&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;skill_manager=_skill_manager,</code> | 参数 <code>skill_manager</code>（skill_manager）：读取 <code>_skill_manager</code>。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L107 | （空行） | 空行，分隔逻辑。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 记忆管理器（Redis 工作记忆 + ChromaDB 情景记忆/用户画像）</code> | 源码注释：记忆管理器（Redis 工作记忆 + ChromaDB 情景记忆/用户画像） |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_memory = MemoryManager(</code> | 将结果保存到 <code>_memory</code>：调用 <code>MemoryManager</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;redis_url=os.getenv(&quot;REDIS_URL&quot;, &quot;redis://redis:6379/0&quot;),</code> | 参数 <code>redis_url</code>（redis_url）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_host=os.getenv(&quot;CHROMA_HOST&quot;, &quot;chromadb&quot;),</code> | 参数 <code>chroma_host</code>（chroma_host）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_port=int(os.getenv(&quot;CHROMA_PORT&quot;, &quot;8000&quot;)),</code> | 参数 <code>chroma_port</code>（chroma_port）：转换为整数。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_path=os.getenv(&quot;CHROMA_PERSIST_DIRECTORY&quot;, &quot;/app/data/chroma&quot;),</code> | 参数 <code>chroma_path</code>（chroma_path）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key=cfg[&quot;api_key&quot;],</code> | 参数 <code>api_key</code>（模型服务凭据）：按索引/切片取 <code>cfg[&#x27;api_key&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url=cfg.get(&quot;base_url&quot;),</code> | 参数 <code>base_url</code>（模型服务地址）：按键取值，缺失用给定默认值。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=cfg[&quot;model&quot;],</code> | 参数 <code>model</code>（模型名称）：按索引/切片取 <code>cfg[&#x27;model&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L118 | （空行） | 空行，分隔逻辑。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# MCP 工具管理器 + RAG 知识库（基于 ChromaDB 的真实检索）</code> | 源码注释：MCP 工具管理器 + RAG 知识库（基于 ChromaDB 的真实检索） |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_tool_manager = MCPToolManager(</code> | 将结果保存到 <code>_tool_manager</code>：调用 <code>MCPToolManager</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key=cfg[&quot;api_key&quot;],</code> | 参数 <code>api_key</code>（模型服务凭据）：按索引/切片取 <code>cfg[&#x27;api_key&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url=cfg.get(&quot;base_url&quot;),</code> | 参数 <code>base_url</code>（模型服务地址）：按键取值，缺失用给定默认值。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=cfg[&quot;model&quot;],</code> | 参数 <code>model</code>（模型名称）：按索引/切片取 <code>cfg[&#x27;model&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;kb = KnowledgeBase(</code> | 将结果保存到 <code>kb</code>：调用 <code>KnowledgeBase</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_host=os.getenv(&quot;CHROMA_HOST&quot;, &quot;chromadb&quot;),</code> | 参数 <code>chroma_host</code>（chroma_host）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_port=int(os.getenv(&quot;CHROMA_PORT&quot;, &quot;8000&quot;)),</code> | 参数 <code>chroma_port</code>（chroma_port）：转换为整数。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_path=os.getenv(&quot;CHROMA_PERSIST_DIRECTORY&quot;, &quot;/app/data/chroma&quot;),</code> | 参数 <code>chroma_path</code>（chroma_path）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;知识库已加载: {await kb.doc_count_async()} 个文档片段&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L131 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-132"></a>

### L132–L140 · knowledge_fallback

知识检索异常时返回一条标记 fallback=True 的说明，保留错误供排障；不能当作真实检索证据。

**签名输入：** <code>params: Dict[str, Any], context: Optional[Dict[str, Any]], error: str</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def knowledge_fallback(params: Dict[str, Any], context: Optional[Dict[str, Any]], error: str):</code> | 定义函数 <code>knowledge_fallback</code>；输入参数见签名，下方导读解释调用目的。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query = params.get(&quot;query&quot;, &quot;&quot;)</code> | 将结果保存到 <code>query</code>：按键取值，缺失用给定默认值。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [{</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;title&quot;: &quot;知识库降级结果&quot;,</code> | 字段 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content&quot;: f&quot;知识库暂时不可用，未能完成对“{query}”的语义检索。请稍后重试，或转人工客服确认。&quot;,</code> | 字段 <code>content</code>（文本正文）：将变量插入模板，构造提示词、标识或可读说明。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;score&quot;: 0.0,</code> | 字段 <code>score</code>（展示分数）：使用这里写明的固定值。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;fallback&quot;: True,</code> | 字段 <code>fallback</code>（当前映射中的键）：使用这里写明的固定值。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;error&quot;: error,</code> | 字段 <code>error</code>（当前映射中的键）：读取 <code>error</code>。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L141 | （空行） | 空行，分隔逻辑。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_tool_manager.register(Tool(</code> | 进入 <code>_tool_manager.register</code>：同名覆盖已有 Tool；旧缓存不会自动清理。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name=&quot;knowledge_search&quot;,</code> | 参数 <code>name</code>（name）：使用固定文本/配置值。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;description=&quot;搜索知识库（基于 ChromaDB 向量检索）&quot;,</code> | 参数 <code>description</code>（description）：使用固定文本/配置值。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;handler=kb.search_handler,</code> | 参数 <code>handler</code>（handler）：读取 <code>kb.search_handler</code>。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;schema={</code> | 参数 <code>schema</code>（schema）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;type&quot;: &quot;object&quot;,</code> | 字段 <code>type</code>（当前映射中的键）：使用固定文本/配置值。 |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;properties&quot;: {</code> | 字段 <code>properties</code>（当前映射中的键）：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;query&quot;: {&quot;type&quot;: &quot;string&quot;},</code> | 字段 <code>type</code>（当前映射中的键）：使用固定文本/配置值。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;top_k&quot;: {&quot;type&quot;: &quot;integer&quot;},</code> | 字段 <code>type</code>（当前映射中的键）：使用固定文本/配置值。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;required&quot;: [&quot;query&quot;],</code> | 字段 <code>required</code>（当前映射中的键）：组装有序值或集合，元素在后续逻辑中消费。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cache_ttl=300.0,</code> | 参数 <code>cache_ttl</code>（cache_ttl）：使用这里写明的固定值。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;supports_rerank=True,</code> | 参数 <code>supports_rerank</code>（supports_rerank）：使用这里写明的固定值。 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fallback=knowledge_fallback,</code> | 参数 <code>fallback</code>（fallback）：读取 <code>knowledge_fallback</code>。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;))</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L158 | （空行） | 空行，分隔逻辑。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 性能监控（可选启动 Prometheus）</code> | 源码注释：性能监控（可选启动 Prometheus） |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;prom_port = int(os.getenv(&quot;PROMETHEUS_PORT&quot;, &quot;0&quot;)) or None</code> | 将结果保存到 <code>prom_port</code>：读取 <code>int(os.getenv(&#x27;PROMETHEUS_PORT&#x27;, &#x27;0&#x27;)) or None</code>。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_monitor = PerformanceMonitor(</code> | 将结果保存到 <code>_monitor</code>：调用 <code>PerformanceMonitor</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;orchestrator=_orchestrator,</code> | 参数 <code>orchestrator</code>（orchestrator）：读取 <code>_orchestrator</code>。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tool_manager=_tool_manager,</code> | 参数 <code>tool_manager</code>（tool_manager）：读取 <code>_tool_manager</code>。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval_s=float(os.getenv(&quot;MONITOR_INTERVAL&quot;, &quot;10&quot;)),</code> | 参数 <code>interval_s</code>（interval_s）：转换为浮点数；无效输入会抛出异常。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;webhook_url=os.getenv(&quot;ALERT_WEBHOOK_URL&quot;) or None,</code> | 参数 <code>webhook_url</code>（webhook_url）：读取 <code>os.getenv(&#x27;ALERT_WEBHOOK_URL&#x27;) or None</code>。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prometheus_port=prom_port,</code> | 参数 <code>prometheus_port</code>（prometheus_port）：读取 <code>prom_port</code>。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;await _monitor.start()</code> | 等待完成后继续；进入 <code>_monitor.start</code>：幂等开关防止重复建采集 task；create_task 后不等待循环结束。 |
| L169 | （空行） | 空行，分隔逻辑。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 评测器</code> | 源码注释：评测器 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_evaluator = EndToEndEvaluator(</code> | 将结果保存到 <code>_evaluator</code>：调用 <code>EndToEndEvaluator</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;orchestrator=_orchestrator,</code> | 参数 <code>orchestrator</code>（orchestrator）：读取 <code>_orchestrator</code>。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;recognizer=recognizer,</code> | 参数 <code>recognizer</code>（recognizer）：读取 <code>recognizer</code>。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key=cfg[&quot;api_key&quot;],</code> | 参数 <code>api_key</code>（模型服务凭据）：按索引/切片取 <code>cfg[&#x27;api_key&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url=cfg.get(&quot;base_url&quot;),</code> | 参数 <code>base_url</code>（模型服务地址）：按键取值，缺失用给定默认值。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=cfg[&quot;model&quot;],</code> | 参数 <code>model</code>（模型名称）：按索引/切片取 <code>cfg[&#x27;model&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;baseline_path=os.getenv(&quot;EVAL_BASELINE_PATH&quot;, &quot;/app/data/eval/baseline.json&quot;),</code> | 参数 <code>baseline_path</code>（baseline_path）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L179 | （空行） | 空行，分隔逻辑。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;logger.info(&quot;EchoMind 已就绪&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;yield</code> | 读取 <code>(yield)</code>。 |
| L182 | （空行） | 空行，分隔逻辑。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;await _monitor.stop()</code> | 等待完成后继续；进入 <code>_monitor.stop</code>：取消 task 并 await，吞掉预期 CancelledError 完成退出。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _memory is not None:</code> | 判断 <code>_memory is not None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await _memory.close()</code> | 等待完成后继续；进入 <code>_memory.close</code>：只关闭 Redis；LLM 客户端未在这里关闭。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;logger.info(&quot;EchoMind 已关闭&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L187 | （空行） | 空行，分隔逻辑。 |
| L188 | （空行） | 空行，分隔逻辑。 |
| L189 | <code># ── FastAPI ───────────────────────────────────────────────────────────────────</code> | 源码注释：── FastAPI ─────────────────────────────────────────────────────────────────── |
| L190 | <code>app = FastAPI(</code> | 将结果保存到 <code>app</code>：调用 <code>FastAPI</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;title=&quot;EchoMind 智能客服&quot;,</code> | 参数 <code>title</code>（展示标题）：使用固定文本/配置值。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;version=&quot;2.0.0&quot;,</code> | 参数 <code>version</code>（version）：使用固定文本/配置值。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;lifespan=lifespan,</code> | 参数 <code>lifespan</code>（lifespan）：读取 <code>lifespan</code>。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;docs_url=&quot;/docs&quot;,</code> | 参数 <code>docs_url</code>（docs_url）：使用固定文本/配置值。 |
| L195 | <code>)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L196 | （空行） | 空行，分隔逻辑。 |
| L197 | <code>app.add_middleware(</code> | 调用 <code>app.add_middleware</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;CORSMiddleware,</code> | 续接 L197 的表达式：按前述语句组装参数、条件或集合。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;allow_origins=[&quot;*&quot;],</code> | 参数 <code>allow_origins</code>（allow_origins）：组装有序值或集合，元素在后续逻辑中消费。 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;allow_methods=[&quot;*&quot;],</code> | 参数 <code>allow_methods</code>（allow_methods）：组装有序值或集合，元素在后续逻辑中消费。 |
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;allow_headers=[&quot;*&quot;],</code> | 参数 <code>allow_headers</code>（allow_headers）：组装有序值或集合，元素在后续逻辑中消费。 |
| L202 | <code>)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L203 | （空行） | 空行，分隔逻辑。 |
| L204 | （空行） | 空行，分隔逻辑。 |
| L205 | <code># ── 请求/响应模型 ─────────────────────────────────────────────────────────────</code> | 源码注释：── 请求/响应模型 ───────────────────────────────────────────────────────────── |

<a id="symbol-206"></a>

### L206–L209 · ChatRequest

HTTP 输入契约：message 必填；user_id 默认 anonymous；conv_id 缺失才分配新 ID。类型校验不能替代身份验证。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L206 | <code>class ChatRequest(BaseModel):</code> | 定义 <code>ChatRequest</code> 的数据契约/行为；继承与字段见本段。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;message:     str</code> | 声明字段 <code>message</code> 的类型，赋值由构造方完成。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;user_id:     str = &quot;anonymous&quot;</code> | 将结果保存到 <code>user_id</code>：使用固定文本/配置值。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;conv_id:     Optional[str] = None</code> | 将结果保存到 <code>conv_id</code>：使用这里写明的固定值。 |
| L210 | （空行） | 空行，分隔逻辑。 |
| L211 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-212"></a>

### L212–L228 · ChatResponse

把运行信息暴露给调用方，便于解释路由。intent_confidence、routing_confidence 是不同阶段分数；agent_type 和 primary_agent 在降级时可能不同。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L212 | <code>class ChatResponse(BaseModel):</code> | 定义 <code>ChatResponse</code> 的数据契约/行为；继承与字段见本段。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;conv_id:     str</code> | 声明字段 <code>conv_id</code> 的类型，赋值由构造方完成。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;response:    str</code> | 声明字段 <code>response</code> 的类型，赋值由构造方完成。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent:      str</code> | 声明字段 <code>intent</code> 的类型，赋值由构造方完成。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_group: str = &quot;other&quot;</code> | 将结果保存到 <code>intent_group</code>：使用固定文本/配置值。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_type:  str</code> | 声明字段 <code>agent_type</code> 的类型，赋值由构造方完成。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agent_types: List[str] = Field(default_factory=list)</code> | 将结果保存到 <code>agent_types</code>：调用 <code>Field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;primary_agent: str = &quot;&quot;</code> | 将结果保存到 <code>primary_agent</code>：使用固定文本/配置值。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents: List[str] = Field(default_factory=list)</code> | 将结果保存到 <code>supporting_agents</code>：调用 <code>Field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;routing_reason: str = &quot;&quot;</code> | 将结果保存到 <code>routing_reason</code>：使用固定文本/配置值。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;routing_confidence: float = 0.0</code> | 将结果保存到 <code>routing_confidence</code>：使用这里写明的固定值。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;escalated:   bool</code> | 声明字段 <code>escalated</code> 的类型，赋值由构造方完成。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;latency_ms:  float</code> | 声明字段 <code>latency_ms</code> 的类型，赋值由构造方完成。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;knowledge_used: bool = False</code> | 将结果保存到 <code>knowledge_used</code>：使用这里写明的固定值。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;entities: Dict[str, List[str]] = Field(default_factory=dict)</code> | 将结果保存到 <code>entities</code>：调用 <code>Field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_confidence: float = 0.0</code> | 将结果保存到 <code>intent_confidence</code>：使用这里写明的固定值。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_source_scores: Dict[str, float] = Field(default_factory=dict)</code> | 将结果保存到 <code>intent_source_scores</code>：调用 <code>Field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L229 | （空行） | 空行，分隔逻辑。 |
| L230 | （空行） | 空行，分隔逻辑。 |
| L231 | <code># ── 路由 ──────────────────────────────────────────────────────────────────────</code> | 源码注释：── 路由 ────────────────────────────────────────────────────────────────────── |

<a id="symbol-232"></a>

### L232–L236 · health

给 Docker/Nginx 的轻量存活信号。返回实例统计；不是依赖连通性探测。

**签名输入：** <code></code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L232 | <code>@app.get(&quot;/health&quot;)</code> | 装饰器 <code>@app.get(&quot;/health&quot;)</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L233 | <code>async def health():</code> | 定义异步函数 <code>health</code>；输入参数见签名，下方导读解释调用目的。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _orchestrator is None:</code> | 判断 <code>_orchestrator is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;服务未就绪&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;服务未就绪&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;status&quot;: &quot;ok&quot;, &quot;agents&quot;: _orchestrator.get_stats()}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L237 | （空行） | 空行，分隔逻辑。 |
| L238 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-239"></a>

### L239–L244 · skills_summary

把 SkillManager 的解析结果和错误返回给运营排查；会包含文件路径，应作为管理接口控制访问。

**签名输入：** <code></code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L239 | <code>@app.get(&quot;/skills&quot;, tags=[&quot;Skills&quot;])</code> | 装饰器 <code>@app.get(&quot;/skills&quot;, tags=[&quot;Skills&quot;])</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L240 | <code>async def skills_summary():</code> | 定义异步函数 <code>skills_summary</code>；输入参数见签名，下方导读解释调用目的。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;查看当前已加载的 Skills，便于确认热加载结果和排查解析错误。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _skill_manager is None:</code> | 判断 <code>_skill_manager is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;Skills 未初始化&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;Skills 未初始化&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return _skill_manager.summary()</code> | 结束当前函数并返回；调用 <code>_skill_manager.summary</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L245 | （空行） | 空行，分隔逻辑。 |
| L246 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-247"></a>

### L247–L255 · reload_skills

重新扫描目录并更新现有编排器引用。单进程立刻可用，不等于多 worker 同时更新。

**签名输入：** <code></code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L247 | <code>@app.post(&quot;/skills/reload&quot;, tags=[&quot;Skills&quot;])</code> | 装饰器 <code>@app.post(&quot;/skills/reload&quot;, tags=[&quot;Skills&quot;])</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L248 | <code>async def reload_skills():</code> | 定义异步函数 <code>reload_skills</code>；输入参数见签名，下方导读解释调用目的。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;运行时重新扫描 Skill 目录，不需要重启服务。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _skill_manager is None:</code> | 判断 <code>_skill_manager is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;Skills 未初始化&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;Skills 未初始化&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;_skill_manager.reload()</code> | 进入 <code>_skill_manager.reload</code>：load 的别名；没有文件监听器，只有显式调用才重新读磁盘。 |
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _orchestrator is not None:</code> | 判断 <code>_orchestrator is not None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_orchestrator.set_skill_manager(_skill_manager)</code> | 进入 <code>_orchestrator.set_skill_manager</code>：替换编排器与池内各实例的管理器引用。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return _skill_manager.summary()</code> | 结束当前函数并返回；调用 <code>_skill_manager.summary</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L256 | （空行） | 空行，分隔逻辑。 |
| L257 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-258"></a>

### L258–L328 · chat

这是最值得优先读的函数。user_id 用于用户范围，conv_id 用于当前会话；用户应持续带回同一 conv_id。先取历史再识别，避免把本轮消息重复放进历史；API 预填 intent 后编排器跳过二次识别。回答落库之后才返回，画像任务随后运行。

**签名输入：** <code>req: ChatRequest</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L258 | <code>@app.post(&quot;/chat&quot;, response_model=ChatResponse)</code> | 装饰器 <code>@app.post(&quot;/chat&quot;, response_model=ChatResponse)</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L259 | <code>async def chat(req: ChatRequest):</code> | 定义异步函数 <code>chat</code>；输入参数见签名，下方导读解释调用目的。 |
| L260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;主对话接口。完整流程：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;记忆读取 → 意图识别 → Agent 路由 → 执行 → 记忆写入</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L263 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _orchestrator is None or _memory is None:</code> | 判断 <code>_orchestrator is None or _memory is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;服务未就绪&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;服务未就绪&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L266 | （空行） | 空行，分隔逻辑。 |
| L267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from agents.agent_orchestrator import Request as OrcReq</code> | 导入 <code>from agents.agent_orchestrator import Request as OrcReq</code>；只建立名称依赖，真正业务调用见后文。 |
| L268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from memory.conversation_memory import MsgRole</code> | 导入 <code>from memory.conversation_memory import MsgRole</code>；只建立名称依赖，真正业务调用见后文。 |
| L269 | （空行） | 空行，分隔逻辑。 |
| L270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;conv_id = req.conv_id or str(uuid.uuid4())</code> | 将结果保存到 <code>conv_id</code>：读取 <code>req.conv_id or str(uuid.uuid4())</code>。 |
| L271 | （空行） | 空行，分隔逻辑。 |
| L272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 1. 读取记忆上下文</code> | 源码注释：1. 读取记忆上下文 |
| L273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;mem_ctx = await _memory.get_context(req.user_id, conv_id, query=req.message)</code> | 将结果保存到 <code>mem_ctx</code>：等待完成后继续；进入 <code>_memory.get_context</code>：四步串行读数据。 |
| L274 | （空行） | 空行，分隔逻辑。 |
| L275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 2. 构建编排请求（含对话历史，用于意图识别上下文）</code> | 源码注释：2. 构建编排请求（含对话历史，用于意图识别上下文） |
| L276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;history = [</code> | 将结果保存到 <code>history</code>：条件 <code>mem_ctx.recent_messages</code> 成立选前值，否则选 else 后值。 |
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{&quot;role&quot;: m.role.value, &quot;content&quot;: m.content}</code> | 字段 <code>content</code>（文本正文）：读取 <code>m.content</code>。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for m in mem_ctx.recent_messages[-5:]</code> | 续接 L276 的表达式：按前述语句组装参数、条件或集合。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;] if mem_ctx.recent_messages else None</code> | 续接 L276 的表达式：按前述语句组装参数、条件或集合。 |
| L280 | （空行） | 空行，分隔逻辑。 |
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_result = await _orchestrator.recognize_intent(req.message, history=history)</code> | **关键：**先识别意图决定是否值得检索；不是 Agent 自主选择工具。 |
| L282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;knowledge_text, knowledge_used = await _build_knowledge_context(req.message, intent=intent_result.intent)</code> | **关键：**此处等待改写、并发召回、重排完成，再进入编排器。 |
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;context_parts = [mem_ctx.to_prompt_text()]</code> | 将结果保存到 <code>context_parts</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if knowledge_text:</code> | 判断 <code>knowledge_text</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context_parts.append(knowledge_text)</code> | 追加一个元素到当前列表。 |
| L286 | <code>&nbsp;&nbsp;&nbsp;&nbsp;full_context = &quot;\n\n&quot;.join(part for part in context_parts if part)</code> | 将结果保存到 <code>full_context</code>：把字符串片段按分隔符合并。 |
| L287 | （空行） | 空行，分隔逻辑。 |
| L288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;orch_req = OrcReq(</code> | 将结果保存到 <code>orch_req</code>：调用 <code>OrcReq</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message=req.message,</code> | 参数 <code>message</code>（本轮用户消息）：读取 <code>req.message</code>。 |
| L290 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user_id=req.user_id,</code> | 参数 <code>user_id</code>（用户标识）：读取 <code>req.user_id</code>。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id=conv_id,</code> | 参数 <code>conv_id</code>（会话标识）：读取 <code>conv_id</code>。 |
| L292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context=full_context,</code> | 参数 <code>context</code>（背景上下文）：读取 <code>full_context</code>。 |
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history=history,</code> | 参数 <code>history</code>（历史消息）：读取 <code>history</code>。 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entities=intent_result.entities,</code> | **关键：**把实体显式传入 Request；CLI/评测缺少这一传递。 |
| L295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent=intent_result.intent,</code> | 参数 <code>intent</code>（意图标签）：读取 <code>intent_result.intent</code>。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_group=intent_result.intent_group,</code> | 参数 <code>intent_group</code>（粗意图组）：读取 <code>intent_result.intent_group</code>。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;urgency=intent_result.urgency,</code> | 参数 <code>urgency</code>（紧急程度）：读取 <code>intent_result.urgency</code>。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_confidence=intent_result.confidence,</code> | 参数 <code>intent_confidence</code>（intent_confidence）：读取 <code>intent_result.confidence</code>。 |
| L299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L300 | （空行） | 空行，分隔逻辑。 |
| L301 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 3. 执行</code> | 源码注释：3. 执行 |
| L302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;result = await _orchestrator.run(orch_req)</code> | 将结果保存到 <code>result</code>：等待完成后继续；调用 <code>_orchestrator.run</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L303 | （空行） | 空行，分隔逻辑。 |
| L304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 4. 写入记忆</code> | 源码注释：4. 写入记忆 |
| L305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;await _memory.add_message(req.user_id, conv_id, MsgRole.USER, req.message)</code> | 等待完成后继续；进入 <code>_memory.add_message</code>：消息序列化后 LPUSH 放列表头，最新在前；每写一条延长 TTL，到 15 条就同步等待压缩。 |
| L306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;await _memory.add_message(req.user_id, conv_id, MsgRole.ASSISTANT, result.response)</code> | 等待完成后继续；进入 <code>_memory.add_message</code>：消息序列化后 LPUSH 放列表头，最新在前；每写一条延长 TTL，到 15 条就同步等待压缩。 |
| L307 | （空行） | 空行，分隔逻辑。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 5. 异步更新用户画像（不阻塞响应）</code> | 源码注释：5. 异步更新用户画像（不阻塞响应） |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;asyncio.create_task(_memory.update_profile(req.user_id, conv_id))</code> | **关键：**调度后台画像任务；不等待完成，也没有保存任务句柄。 |
| L310 | （空行） | 空行，分隔逻辑。 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return ChatResponse(</code> | 结束当前函数并返回；进入 <code>ChatResponse</code>：把运行信息暴露给调用方，便于解释路由。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;conv_id=conv_id,</code> | 参数 <code>conv_id</code>（会话标识）：读取 <code>conv_id</code>。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response=result.response,</code> | 参数 <code>response</code>（response）：读取 <code>result.response</code>。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent=result.intent.value if result.intent else &quot;other&quot;,</code> | 参数 <code>intent</code>（意图标签）：条件 <code>result.intent</code> 成立选前值，否则选 else 后值。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_group=intent_result.intent_group,</code> | 参数 <code>intent_group</code>（粗意图组）：读取 <code>intent_result.intent_group</code>。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type=result.agent_type.value,</code> | 参数 <code>agent_type</code>（Agent 类别）：读取 <code>result.agent_type.value</code>。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_types=[agent_type.value for agent_type in result.agent_types],</code> | 参数 <code>agent_types</code>（agent_types）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;primary_agent=result.primary_agent.value if result.primary_agent else result.agent_type.value,</code> | 参数 <code>primary_agent</code>（计划主 Agent）：条件 <code>result.primary_agent</code> 成立选前值，否则选 else 后值。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;supporting_agents=[agent_type.value for agent_type in result.supporting_agents],</code> | 参数 <code>supporting_agents</code>（计划辅助 Agent 列表）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_reason=result.routing_reason,</code> | 参数 <code>routing_reason</code>（可解释路由文字）：读取 <code>result.routing_reason</code>。 |
| L321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routing_confidence=result.routing_confidence,</code> | 参数 <code>routing_confidence</code>（裁剪后的领域分数）：读取 <code>result.routing_confidence</code>。 |
| L322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;escalated=result.escalated,</code> | 参数 <code>escalated</code>（escalated）：读取 <code>result.escalated</code>。 |
| L323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;latency_ms=round(result.latency_ms, 1),</code> | 参数 <code>latency_ms</code>（当前计时范围的毫秒耗时）：四舍五入用于返回/展示。 |
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;knowledge_used=knowledge_used,</code> | 参数 <code>knowledge_used</code>（knowledge_used）：读取 <code>knowledge_used</code>。 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;entities=intent_result.entities,</code> | 参数 <code>entities</code>（结构化实体）：读取 <code>intent_result.entities</code>。 |
| L326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_confidence=round(intent_result.confidence, 4),</code> | 参数 <code>intent_confidence</code>（intent_confidence）：四舍五入用于返回/展示。 |
| L327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_source_scores=intent_result.source_scores,</code> | 参数 <code>intent_source_scores</code>（intent_source_scores）：读取 <code>intent_result.source_scores</code>。 |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L329 | （空行） | 空行，分隔逻辑。 |
| L330 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-331"></a>

### L331–L365 · _build_knowledge_context

把工具结果转换成生成模型的背景文本，默认最多 3 条、每条内容最多 600 字符。used 只表示存在非空内容，降级提示也可能被当作知识；无来源 ID、引用约束与最低相关性门槛。

**签名输入：** <code>message: str, intent=None, top_k: int=3</code>；**返回契约：** <code>tuple[str, bool]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L331 | <code>async def _build_knowledge_context(message: str, intent=None, top_k: int = 3) -&gt; tuple[str, bool]:</code> | 定义异步函数 <code>_build_knowledge_context</code>；输入参数见签名，下方导读解释调用目的。 |
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;为 /chat 主链路构建 RAG 知识上下文。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L334 | （空行） | 空行，分隔逻辑。 |
| L335 | <code>&nbsp;&nbsp;&nbsp;&nbsp;这里复用 MCPToolManager 的查询改写、并行召回、重排、fallback 能力。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _tool_manager is None:</code> | 判断 <code>_tool_manager is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;, False</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if not _should_use_knowledge(message, intent=intent):</code> | 判断 <code>not _should_use_knowledge(message, intent=intent)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;, False</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L341 | <code>&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result = await _tool_manager.search_with_rewrite(&quot;knowledge_search&quot;, message, top_k=top_k)</code> | 将结果保存到 <code>result</code>：等待完成后继续；进入 <code>_tool_manager.search_with_rewrite</code>：先改写再并行召回，各分支至少取 5 条；个别异常被 gather 收集，不阻止其他结果。 |
| L343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not result.success or not isinstance(result.data, list) or not result.data:</code> | 判断 <code>not result.success or not isinstance(result.data, list) or (not result.data)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;, False</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L345 | （空行） | 空行，分隔逻辑。 |
| L346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts = [&quot;[知识库检索结果]&quot;]</code> | 将结果保存到 <code>parts</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;used = False</code> | 将结果保存到 <code>used</code>：使用这里写明的固定值。 |
| L348 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i, item in enumerate(result.data[:top_k], start=1):</code> | 遍历 <code>enumerate(result.data[:top_k], start=1)</code>，本轮元素绑定 <code>(i, item)</code>。 |
| L349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(item, dict):</code> | 判断 <code>not isinstance(item, dict)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;title = str(item.get(&quot;title&quot;, &quot;未命名文档&quot;))</code> | 将结果保存到 <code>title</code>：转换为字符串表示。 |
| L352 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content = str(item.get(&quot;content&quot;, &quot;&quot;)).strip()</code> | 将结果保存到 <code>content</code>：去除两端指定字符或空白。 |
| L353 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;score = item.get(&quot;score&quot;, &quot;&quot;)</code> | 将结果保存到 <code>score</code>：按键取值，缺失用给定默认值。 |
| L354 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not content:</code> | 判断 <code>not content</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L355 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L356 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;used = True</code> | **关键：**即使 item 是 fallback 说明也设 True，knowledge_used 会产生语义误报。 |
| L357 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(f&quot;{i}. 标题: {title}\n   相关度: {score}\n   内容: {content[:600]}&quot;)</code> | 追加一个元素到当前列表。 |
| L358 | （空行） | 空行，分隔逻辑。 |
| L359 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not used:</code> | 判断 <code>not used</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L360 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;, False</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L361 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parts.append(&quot;请优先依据以上知识库内容回答；如果知识库内容不足，再结合通用客服能力说明。&quot;)</code> | 追加一个元素到当前列表。 |
| L362 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;\n&quot;.join(parts), True</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L363 | <code>&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L364 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;构建知识库上下文失败: {ex}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L365 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;, False</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L366 | （空行） | 空行，分隔逻辑。 |
| L367 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-368"></a>

### L368–L390 · _should_use_knowledge

意图门控减少无效检索。已知 other/寒暄直接 False，业务类 True，只有未知/缺失 intent 才走长度与关键词兜底。它不会问 LLM 再判断一次。

**签名输入：** <code>message: str, intent=None</code>；**返回契约：** <code>bool</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L368 | <code>def _should_use_knowledge(message: str, intent=None) -&gt; bool:</code> | 定义函数 <code>_should_use_knowledge</code>；输入参数见签名，下方导读解释调用目的。 |
| L369 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;跳过纯寒暄，业务类问题才检索知识库，避免无关 RAG 干扰回复。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L370 | <code>&nbsp;&nbsp;&nbsp;&nbsp;msg = (message or &quot;&quot;).strip().lower()</code> | 将结果保存到 <code>msg</code>：转小写进行大小写无关比较。 |
| L371 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if not msg:</code> | 判断 <code>not msg</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L372 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L373 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_value = getattr(intent, &quot;value&quot;, intent)</code> | 将结果保存到 <code>intent_value</code>：读取对象指定属性，不存在时返回这里给出的默认值。 |
| L374 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if intent_value in {&quot;greeting&quot;, &quot;feedback&quot;, &quot;escalation&quot;, &quot;human_handoff&quot;, &quot;other&quot;}:</code> | 判断 <code>intent_value in {&#x27;greeting&#x27;, &#x27;feedback&#x27;, &#x27;escalation&#x27;, &#x27;human_handoff&#x27;, &#x27;other&#x27;}</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L375 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L376 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if intent_value in {</code> | 判断 <code>intent_value in {&#x27;query&#x27;, &#x27;request&#x27;, &#x27;technical&#x27;, &#x27;billing&#x27;, &#x27;account&#x27;, &#x27;complaint&#x27;, &#x27;order_status&#x27;, &#x27;logistics&#x27;, &#x27;refund&#x27;, &#x27;invoice&#x27;, …</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L377 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;query&quot;, &quot;request&quot;, &quot;technical&quot;, &quot;billing&quot;, &quot;account&quot;, &quot;complaint&quot;,</code> | 续接 L376 的表达式：构造文本/参数值。 |
| L378 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;order_status&quot;, &quot;logistics&quot;, &quot;refund&quot;, &quot;invoice&quot;, &quot;payment_issue&quot;,</code> | 续接 L376 的表达式：构造文本/参数值。 |
| L379 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;account_security&quot;, &quot;technical_login&quot;, &quot;technical_crash&quot;,</code> | 续接 L376 的表达式：构造文本/参数值。 |
| L380 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}:</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L381 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return True</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L382 | <code>&nbsp;&nbsp;&nbsp;&nbsp;greetings = {&quot;你好&quot;, &quot;您好&quot;, &quot;嗨&quot;, &quot;hi&quot;, &quot;hello&quot;, &quot;hey&quot;, &quot;早上好&quot;, &quot;晚上好&quot;}</code> | 将结果保存到 <code>greetings</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L383 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if msg in greetings:</code> | 判断 <code>msg in greetings</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L384 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L385 | <code>&nbsp;&nbsp;&nbsp;&nbsp;business_keywords = [</code> | 将结果保存到 <code>business_keywords</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L386 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;退款&quot;, &quot;订单&quot;, &quot;物流&quot;, &quot;配送&quot;, &quot;发票&quot;, &quot;扣款&quot;, &quot;支付&quot;, &quot;账单&quot;, &quot;订阅&quot;,</code> | 续接 L385 的表达式：构造文本/参数值。 |
| L387 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;登录&quot;, &quot;报错&quot;, &quot;错误&quot;, &quot;崩溃&quot;, &quot;会员&quot;, &quot;积分&quot;, &quot;账户&quot;, &quot;密码&quot;, &quot;地址&quot;,</code> | 续接 L385 的表达式：构造文本/参数值。 |
| L388 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;refund&quot;, &quot;order&quot;, &quot;invoice&quot;, &quot;payment&quot;, &quot;error&quot;, &quot;login&quot;,</code> | 续接 L385 的表达式：构造文本/参数值。 |
| L389 | <code>&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L390 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return len(msg) &gt;= 4 or any(kw in msg for kw in business_keywords)</code> | 结束当前函数并返回；读取 <code>len(msg) &gt;= 4 or any((kw in msg for kw in business_keywords))</code>。 |
| L391 | （空行） | 空行，分隔逻辑。 |
| L392 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-393"></a>

### L393–L398 · monitor_summary

返回进程内统计和最近告警，具体口径来自 monitor/performance_monitor.py。

**签名输入：** <code></code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L393 | <code>@app.get(&quot;/monitor&quot;)</code> | 装饰器 <code>@app.get(&quot;/monitor&quot;)</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L394 | <code>async def monitor_summary():</code> | 定义异步函数 <code>monitor_summary</code>；输入参数见签名，下方导读解释调用目的。 |
| L395 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;实时监控摘要：Agent 成功率、工具统计、告警、优化建议。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L396 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _monitor is None:</code> | 判断 <code>_monitor is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L397 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;服务未就绪&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;服务未就绪&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L398 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return _monitor.summary()</code> | 结束当前函数并返回；调用 <code>_monitor.summary</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L399 | （空行） | 空行，分隔逻辑。 |
| L400 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-401"></a>

### L401–L404 · prometheus_metrics

导出默认 Prometheus 注册表。只有 Monitor 开启自定义指标注册后才会有业务 Gauge/Histogram；此端点存在不等于业务指标存在。

**签名输入：** <code></code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L401 | <code>@app.get(&quot;/metrics&quot;)</code> | 装饰器 <code>@app.get(&quot;/metrics&quot;)</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L402 | <code>async def prometheus_metrics():</code> | 定义异步函数 <code>prometheus_metrics</code>；输入参数见签名，下方导读解释调用目的。 |
| L403 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;Prometheus 指标入口。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L404 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)</code> | 结束当前函数并返回；调用 <code>Response</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L405 | （空行） | 空行，分隔逻辑。 |
| L406 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-407"></a>

### L407–L416 · search

query、top_k 是 URL query 参数，虽然方法是 POST，也不是 JSON Body。直接展示检索结果；丢弃 ToolResult.success/error 等状态使故障诊断不完整。

**签名输入：** <code>query: str, top_k: int=5</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L407 | <code>@app.post(&quot;/search&quot;)</code> | 装饰器 <code>@app.post(&quot;/search&quot;)</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L408 | <code>async def search(query: str, top_k: int = 5):</code> | 定义异步函数 <code>search</code>；输入参数见签名，下方导读解释调用目的。 |
| L409 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L410 | <code>&nbsp;&nbsp;&nbsp;&nbsp;演示检索优化链路：查询改写 → 并行召回 → 重排 → Top-K。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L411 | <code>&nbsp;&nbsp;&nbsp;&nbsp;展示 MCP 工具调用的核心亮点。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L412 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L413 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _tool_manager is None:</code> | 判断 <code>_tool_manager is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L414 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;服务未就绪&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;服务未就绪&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L415 | <code>&nbsp;&nbsp;&nbsp;&nbsp;result = await _tool_manager.search_with_rewrite(&quot;knowledge_search&quot;, query, top_k=top_k)</code> | 将结果保存到 <code>result</code>：等待完成后继续；进入 <code>_tool_manager.search_with_rewrite</code>：先改写再并行召回，各分支至少取 5 条；个别异常被 gather 收集，不阻止其他结果。 |
| L416 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;query&quot;: query, &quot;results&quot;: result.data, &quot;reranked&quot;: result.reranked}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L417 | （空行） | 空行，分隔逻辑。 |
| L418 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-419"></a>

### L419–L422 · DocInput

单篇知识材料：title 是显示来源，content 才参与切片和向量化。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L419 | <code>class DocInput(BaseModel):</code> | 定义 <code>DocInput</code> 的数据契约/行为；继承与字段见本段。 |
| L420 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;单篇文档输入。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L421 | <code>&nbsp;&nbsp;&nbsp;&nbsp;title:   str</code> | 声明字段 <code>title</code> 的类型，赋值由构造方完成。 |
| L422 | <code>&nbsp;&nbsp;&nbsp;&nbsp;content: str</code> | 声明字段 <code>content</code> 的类型，赋值由构造方完成。 |
| L423 | （空行） | 空行，分隔逻辑。 |
| L424 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-425"></a>

### L425–L427 · BatchDocInput

批量封装，多文档共享一次 HTTP 导入请求。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L425 | <code>class BatchDocInput(BaseModel):</code> | 定义 <code>BatchDocInput</code> 的数据契约/行为；继承与字段见本段。 |
| L426 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;批量文档导入请求体。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L427 | <code>&nbsp;&nbsp;&nbsp;&nbsp;documents: List[DocInput]</code> | 声明字段 <code>documents</code> 的类型，赋值由构造方完成。 |
| L428 | （空行） | 空行，分隔逻辑。 |
| L429 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-430"></a>

### L430–L434 · EvalIntentInput

context 字段进入 IntentTestCase，但当前 IntentEvaluator 未使用它。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L430 | <code>class EvalIntentInput(BaseModel):</code> | 定义 <code>EvalIntentInput</code> 的数据契约/行为；继承与字段见本段。 |
| L431 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;意图识别评测用例。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L432 | <code>&nbsp;&nbsp;&nbsp;&nbsp;message: str</code> | 声明字段 <code>message</code> 的类型，赋值由构造方完成。 |
| L433 | <code>&nbsp;&nbsp;&nbsp;&nbsp;expected_intent: str</code> | 声明字段 <code>expected_intent</code> 的类型，赋值由构造方完成。 |
| L434 | <code>&nbsp;&nbsp;&nbsp;&nbsp;context: Optional[Dict[str, Any]] = None</code> | 将结果保存到 <code>context</code>：使用这里写明的固定值。 |
| L435 | （空行） | 空行，分隔逻辑。 |
| L436 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-437"></a>

### L437–L442 · EvalDialogInput

question/turns 两种输入；二者可以同时缺失，评测器会返回空用例结果。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L437 | <code>class EvalDialogInput(BaseModel):</code> | 定义 <code>EvalDialogInput</code> 的数据契约/行为；继承与字段见本段。 |
| L438 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;对话质量评测用例。question 单轮，turns 多轮。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L439 | <code>&nbsp;&nbsp;&nbsp;&nbsp;question: Optional[str] = None</code> | 将结果保存到 <code>question</code>：使用这里写明的固定值。 |
| L440 | <code>&nbsp;&nbsp;&nbsp;&nbsp;turns: Optional[List[str]] = None</code> | 将结果保存到 <code>turns</code>：使用这里写明的固定值。 |
| L441 | <code>&nbsp;&nbsp;&nbsp;&nbsp;user_id: Optional[str] = None</code> | 将结果保存到 <code>user_id</code>：使用这里写明的固定值。 |
| L442 | <code>&nbsp;&nbsp;&nbsp;&nbsp;conv_id: Optional[str] = None</code> | 将结果保存到 <code>conv_id</code>：使用这里写明的固定值。 |
| L443 | （空行） | 空行，分隔逻辑。 |
| L444 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-445"></a>

### L445–L448 · EvalRunInput

None 使用默认用例；显式空数组则跳过该类评测。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L445 | <code>class EvalRunInput(BaseModel):</code> | 定义 <code>EvalRunInput</code> 的数据契约/行为；继承与字段见本段。 |
| L446 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;评测请求。为空时使用内置默认用例。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L447 | <code>&nbsp;&nbsp;&nbsp;&nbsp;intent_cases: Optional[List[EvalIntentInput]] = None</code> | 将结果保存到 <code>intent_cases</code>：使用这里写明的固定值。 |
| L448 | <code>&nbsp;&nbsp;&nbsp;&nbsp;dialog_cases: Optional[List[EvalDialogInput]] = None</code> | 将结果保存到 <code>dialog_cases</code>：使用这里写明的固定值。 |
| L449 | （空行） | 空行，分隔逻辑。 |
| L450 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-451"></a>

### L451–L474 · add_knowledge

Pydantic 先验证 title/content，再把列表交给 KB 在线切片入库。返回 added_chunks 是 KB 构造的片段数量，不能自动视为去重后的净增长。

**签名输入：** <code>body: BatchDocInput</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L451 | <code>@app.post(&quot;/knowledge/add&quot;, tags=[&quot;知识库&quot;])</code> | 装饰器 <code>@app.post(&quot;/knowledge/add&quot;, tags=[&quot;知识库&quot;])</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L452 | <code>async def add_knowledge(body: BatchDocInput):</code> | 定义异步函数 <code>add_knowledge</code>；输入参数见签名，下方导读解释调用目的。 |
| L453 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L454 | <code>&nbsp;&nbsp;&nbsp;&nbsp;批量导入文档到知识库。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L455 | （空行） | 空行，分隔逻辑。 |
| L456 | <code>&nbsp;&nbsp;&nbsp;&nbsp;文档会自动切片（每片 500 字）并存入 ChromaDB，ChromaDB 内置 Embedding 模型自动向量化。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L457 | （空行） | 空行，分隔逻辑。 |
| L458 | <code>&nbsp;&nbsp;&nbsp;&nbsp;示例请求体：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L459 | <code>&nbsp;&nbsp;&nbsp;&nbsp;```json</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L460 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L461 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;documents&quot;: [</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L462 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{&quot;title&quot;: &quot;退款政策&quot;, &quot;content&quot;: &quot;用户在购买后 7 天内可以申请无理由退款...&quot;},</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L463 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{&quot;title&quot;: &quot;配送说明&quot;, &quot;content&quot;: &quot;标准配送 3-5 个工作日...&quot;}</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L464 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L465 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L466 | <code>&nbsp;&nbsp;&nbsp;&nbsp;```</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L467 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L468 | <code>&nbsp;&nbsp;&nbsp;&nbsp;tool = _tool_manager._tools.get(&quot;knowledge_search&quot;) if _tool_manager else None</code> | 将结果保存到 <code>tool</code>：条件 <code>_tool_manager</code> 成立选前值，否则选 else 后值。 |
| L469 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if tool is None:</code> | 判断 <code>tool is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L470 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;知识库未初始化&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;知识库未初始化&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L471 | <code>&nbsp;&nbsp;&nbsp;&nbsp;kb = tool.handler.__self__</code> | **关键：**handler 是 kb.search_handler 的绑定方法；__self__ 恰好是 kb，强依赖注册方式。 |
| L472 | <code>&nbsp;&nbsp;&nbsp;&nbsp;count = await kb.add_documents_async([{&quot;title&quot;: d.title, &quot;content&quot;: d.content} for d in body.documents])</code> | 将结果保存到 <code>count</code>：等待完成后继续；进入 <code>kb.add_documents_async</code>：把同步导入放线程，HTTP await 不阻塞主事件循环，但 CPU/线程资源仍会消耗。 |
| L473 | <code>&nbsp;&nbsp;&nbsp;&nbsp;total = await kb.doc_count_async()</code> | 将结果保存到 <code>total</code>：等待完成后继续；进入 <code>kb.doc_count_async</code>：线程中执行 collection.count，用于 API 的启动日志/统计。 |
| L474 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;message&quot;: f&quot;成功导入 {count} 个文档片段&quot;, &quot;added_chunks&quot;: count, &quot;total_chunks&quot;: total}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L475 | （空行） | 空行，分隔逻辑。 |
| L476 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-477"></a>

### L477–L519 · upload_knowledge

上传路径按 filename 后缀分支：.json 解析数组，其他内容转成单篇文档。解码 errors=ignore 会丢弃非法字节。JSON 仅查是不是列表，没有验证每项字段类型。

**签名输入：** <code>file: UploadFile=File(...)</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L477 | <code>@app.post(&quot;/knowledge/upload&quot;, tags=[&quot;知识库&quot;])</code> | 装饰器 <code>@app.post(&quot;/knowledge/upload&quot;, tags=[&quot;知识库&quot;])</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L478 | <code>async def upload_knowledge(file: UploadFile = File(...)):</code> | 定义异步函数 <code>upload_knowledge</code>；输入参数见签名，下方导读解释调用目的。 |
| L479 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L480 | <code>&nbsp;&nbsp;&nbsp;&nbsp;上传文件导入知识库。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L481 | （空行） | 空行，分隔逻辑。 |
| L482 | <code>&nbsp;&nbsp;&nbsp;&nbsp;支持格式：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L483 | <code>&nbsp;&nbsp;&nbsp;&nbsp;- `.txt` / `.md`：整个文件作为一篇文档，文件名作为标题</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L484 | <code>&nbsp;&nbsp;&nbsp;&nbsp;- `.json`：JSON 数组格式 `[{&quot;title&quot;: &quot;...&quot;, &quot;content&quot;: &quot;...&quot;}, ...]`</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L485 | （空行） | 空行，分隔逻辑。 |
| L486 | <code>&nbsp;&nbsp;&nbsp;&nbsp;文件大小限制：10MB</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L487 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L488 | <code>&nbsp;&nbsp;&nbsp;&nbsp;tool = _tool_manager._tools.get(&quot;knowledge_search&quot;) if _tool_manager else None</code> | 将结果保存到 <code>tool</code>：条件 <code>_tool_manager</code> 成立选前值，否则选 else 后值。 |
| L489 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if tool is None:</code> | 判断 <code>tool is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L490 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;知识库未初始化&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;知识库未初始化&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L491 | <code>&nbsp;&nbsp;&nbsp;&nbsp;kb = tool.handler.__self__</code> | 将结果保存到 <code>kb</code>：读取 <code>tool.handler.__self__</code>。 |
| L492 | （空行） | 空行，分隔逻辑。 |
| L493 | <code>&nbsp;&nbsp;&nbsp;&nbsp;content = await file.read()</code> | 将结果保存到 <code>content</code>：等待完成后继续；调用 <code>file.read</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L494 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if len(content) &gt; 10 * 1024 * 1024:</code> | 判断 <code>len(content) &gt; 10 * 1024 * 1024</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L495 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(413, &quot;文件大小超过 10MB 限制&quot;)</code> | 抛出 <code>HTTPException(413, &#x27;文件大小超过 10MB 限制&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L496 | （空行） | 空行，分隔逻辑。 |
| L497 | <code>&nbsp;&nbsp;&nbsp;&nbsp;text = content.decode(&quot;utf-8&quot;, errors=&quot;ignore&quot;)</code> | 将结果保存到 <code>text</code>：调用 <code>content.decode</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L498 | <code>&nbsp;&nbsp;&nbsp;&nbsp;filename = file.filename or &quot;unknown&quot;</code> | 将结果保存到 <code>filename</code>：读取 <code>file.filename or &#x27;unknown&#x27;</code>。 |
| L499 | （空行） | 空行，分隔逻辑。 |
| L500 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if filename.endswith(&quot;.json&quot;):</code> | 判断 <code>filename.endswith(&#x27;.json&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L501 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;import json as _json</code> | 导入 <code>import json as _json</code>；只建立名称依赖，真正业务调用见后文。 |
| L502 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L503 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docs = _json.loads(text)</code> | 将结果保存到 <code>docs</code>：调用 <code>_json.loads</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L504 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(docs, list):</code> | 判断 <code>not isinstance(docs, list)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L505 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(400, &quot;JSON 文件应为数组格式: [{title, content}, ...]&quot;)</code> | 抛出 <code>HTTPException(400, &#x27;JSON 文件应为数组格式: [{title, content}, ...]&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L506 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except _json.JSONDecodeError as e:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L507 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(400, f&quot;JSON 解析失败: {e}&quot;)</code> | 抛出 <code>HTTPException(400, f&#x27;JSON 解析失败: {e}&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L508 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L509 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# txt / md：整个文件作为一篇文档</code> | 源码注释：txt / md：整个文件作为一篇文档 |
| L510 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;title = filename.rsplit(&quot;.&quot;, 1)[0] if &quot;.&quot; in filename else filename</code> | 将结果保存到 <code>title</code>：条件 <code>&#x27;.&#x27; in filename</code> 成立选前值，否则选 else 后值。 |
| L511 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docs = [{&quot;title&quot;: title, &quot;content&quot;: text}]</code> | 将结果保存到 <code>docs</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L512 | （空行） | 空行，分隔逻辑。 |
| L513 | <code>&nbsp;&nbsp;&nbsp;&nbsp;count = await kb.add_documents_async(docs)</code> | 将结果保存到 <code>count</code>：等待完成后继续；进入 <code>kb.add_documents_async</code>：把同步导入放线程，HTTP await 不阻塞主事件循环，但 CPU/线程资源仍会消耗。 |
| L514 | <code>&nbsp;&nbsp;&nbsp;&nbsp;total = await kb.doc_count_async()</code> | 将结果保存到 <code>total</code>：等待完成后继续；进入 <code>kb.doc_count_async</code>：线程中执行 collection.count，用于 API 的启动日志/统计。 |
| L515 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L516 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: f&quot;文件 {filename} 导入成功&quot;,</code> | 字段 <code>message</code>（本轮用户消息）：将变量插入模板，构造提示词、标识或可读说明。 |
| L517 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;added_chunks&quot;: count,</code> | 字段 <code>added_chunks</code>（当前映射中的键）：读取 <code>count</code>。 |
| L518 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;total_chunks&quot;: total,</code> | 字段 <code>total_chunks</code>（当前映射中的键）：读取 <code>total</code>。 |
| L519 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L520 | （空行） | 空行，分隔逻辑。 |
| L521 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-522"></a>

### L522–L529 · knowledge_stats

从注册工具中获得 KnowledgeBase，再在线 count；比 health 更接近知识库存储连通性检查。

**签名输入：** <code></code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L522 | <code>@app.get(&quot;/knowledge/stats&quot;, tags=[&quot;知识库&quot;])</code> | 装饰器 <code>@app.get(&quot;/knowledge/stats&quot;, tags=[&quot;知识库&quot;])</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L523 | <code>async def knowledge_stats():</code> | 定义异步函数 <code>knowledge_stats</code>；输入参数见签名，下方导读解释调用目的。 |
| L524 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;查看知识库统计信息（文档片段总数）。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L525 | <code>&nbsp;&nbsp;&nbsp;&nbsp;tool = _tool_manager._tools.get(&quot;knowledge_search&quot;) if _tool_manager else None</code> | 将结果保存到 <code>tool</code>：条件 <code>_tool_manager</code> 成立选前值，否则选 else 后值。 |
| L526 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if tool is None:</code> | 判断 <code>tool is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L527 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;知识库未初始化&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;知识库未初始化&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L528 | <code>&nbsp;&nbsp;&nbsp;&nbsp;kb = tool.handler.__self__</code> | 将结果保存到 <code>kb</code>：读取 <code>tool.handler.__self__</code>。 |
| L529 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return {&quot;total_chunks&quot;: await kb.doc_count_async()}</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L530 | （空行） | 空行，分隔逻辑。 |
| L531 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-532"></a>

### L532–L580 · run_eval

允许覆盖默认意图与对话用例，再调用评测器。运行会消耗模型请求、改变 Agent 在线统计并覆盖基线文件；不是只读报表接口。

**签名输入：** <code>body: Optional[EvalRunInput]=None</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L532 | <code>@app.post(&quot;/eval/run&quot;)</code> | 装饰器 <code>@app.post(&quot;/eval/run&quot;)</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L533 | <code>async def run_eval(body: Optional[EvalRunInput] = None):</code> | 定义异步函数 <code>run_eval</code>；输入参数见签名，下方导读解释调用目的。 |
| L534 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;运行内置评测用例，返回评测报告。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L535 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if _evaluator is None:</code> | 判断 <code>_evaluator is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L536 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(503, &quot;服务未就绪&quot;)</code> | 抛出 <code>HTTPException(503, &#x27;服务未就绪&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L537 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from evaluation.evaluator import DEFAULT_DIALOG_CASES, DEFAULT_INTENT_CASES, IntentTestCase</code> | 导入 <code>from evaluation.evaluator import DEFAULT_DIALOG_CASES, DEFAULT_INTENT_CASES, IntentTestCase</code>；只建立名称依赖，真正业务调用见后文。 |
| L538 | （空行） | 空行，分隔逻辑。 |
| L539 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if body and body.intent_cases is not None:</code> | 判断 <code>body and body.intent_cases is not None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L540 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_cases = [</code> | 将结果保存到 <code>intent_cases</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L541 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IntentTestCase(</code> | 续接 L540 的表达式：按前述语句组装参数、条件或集合。 |
| L542 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message=c.message,</code> | 参数 <code>message</code>（本轮用户消息）：读取 <code>c.message</code>。 |
| L543 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;expected_intent=c.expected_intent,</code> | 参数 <code>expected_intent</code>（expected_intent）：读取 <code>c.expected_intent</code>。 |
| L544 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context=c.context,</code> | 参数 <code>context</code>（背景上下文）：读取 <code>c.context</code>。 |
| L545 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L546 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for c in body.intent_cases</code> | 续接 L540 的表达式：按前述语句组装参数、条件或集合。 |
| L547 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L548 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L549 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_cases = DEFAULT_INTENT_CASES</code> | 将结果保存到 <code>intent_cases</code>：读取 <code>DEFAULT_INTENT_CASES</code>。 |
| L550 | （空行） | 空行，分隔逻辑。 |
| L551 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if body and body.dialog_cases is not None:</code> | 判断 <code>body and body.dialog_cases is not None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L552 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog_cases = [</code> | 将结果保存到 <code>dialog_cases</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L553 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;c.model_dump(exclude_none=True)</code> | 参数 <code>exclude_none</code>（exclude_none）：使用这里写明的固定值。 |
| L554 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for c in body.dialog_cases</code> | 续接 L552 的表达式：按前述语句组装参数、条件或集合。 |
| L555 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L556 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L557 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog_cases = DEFAULT_DIALOG_CASES</code> | 将结果保存到 <code>dialog_cases</code>：读取 <code>DEFAULT_DIALOG_CASES</code>。 |
| L558 | （空行） | 空行，分隔逻辑。 |
| L559 | <code>&nbsp;&nbsp;&nbsp;&nbsp;report = await _evaluator.run(</code> | 将结果保存到 <code>report</code>：等待完成后继续；调用 <code>_evaluator.run</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L560 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;intent_cases=intent_cases,</code> | 参数 <code>intent_cases</code>（intent_cases）：读取 <code>intent_cases</code>。 |
| L561 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialog_cases=dialog_cases,</code> | 参数 <code>dialog_cases</code>（dialog_cases）：读取 <code>dialog_cases</code>。 |
| L562 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L563 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L564 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;pass_rate&quot;:       report.pass_rate,</code> | 字段 <code>pass_rate</code>（当前映射中的键）：读取 <code>report.pass_rate</code>。 |
| L565 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;total&quot;:           report.total,</code> | 字段 <code>total</code>（当前映射中的键）：读取 <code>report.total</code>。 |
| L566 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;:          report.passed,</code> | 字段 <code>passed</code>（当前映射中的键）：读取 <code>report.passed</code>。 |
| L567 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;avg_scores&quot;:      report.avg_scores,</code> | 字段 <code>avg_scores</code>（当前映射中的键）：读取 <code>report.avg_scores</code>。 |
| L568 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;regressions&quot;:     report.regressions,</code> | 字段 <code>regressions</code>（当前映射中的键）：读取 <code>report.regressions</code>。 |
| L569 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;recommendations&quot;: report.recommendations,</code> | 字段 <code>recommendations</code>（当前映射中的键）：读取 <code>report.recommendations</code>。 |
| L570 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;results&quot;: [</code> | 字段 <code>results</code>（当前映射中的键）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L571 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L572 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: r.test_id,</code> | 字段 <code>test_id</code>（当前映射中的键）：读取 <code>r.test_id</code>。 |
| L573 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: r.passed,</code> | 字段 <code>passed</code>（当前映射中的键）：读取 <code>r.passed</code>。 |
| L574 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: r.scores,</code> | 字段 <code>scores</code>（当前映射中的键）：读取 <code>r.scores</code>。 |
| L575 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: r.detail,</code> | 字段 <code>detail</code>（当前映射中的键）：读取 <code>r.detail</code>。 |
| L576 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: r.metadata,</code> | 字段 <code>metadata</code>（附加元信息）：读取 <code>r.metadata</code>。 |
| L577 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L578 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for r in report.results</code> | 续接 L563 的表达式：按前述语句组装参数、条件或集合。 |
| L579 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;],</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L580 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L581 | （空行） | 空行，分隔逻辑。 |
| L582 | （空行） | 空行，分隔逻辑。 |
| L583 | <code># ── 交互式 CLI ────────────────────────────────────────────────────────────────</code> | 源码注释：── 交互式 CLI ──────────────────────────────────────────────────────────────── |

<a id="symbol-584"></a>

### L584–L639 · _cli

从终端读字符串，创建独立编排器和记忆管理器。每轮只拼接记忆和调用 run，不走 HTTP 的 RAG 与 entities 预填逻辑。input 是同步调用，适合单人调试。

**签名输入：** <code></code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L584 | <code>async def _cli():</code> | 定义异步函数 <code>_cli</code>；输入参数见签名，下方导读解释调用目的。 |
| L585 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print(BANNER)</code> | 向终端输出文本。 |
| L586 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print(&quot;EchoMind CLI — 输入 quit 退出\n&quot;)</code> | 向终端输出文本。 |
| L587 | （空行） | 空行，分隔逻辑。 |
| L588 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from agents.agent_orchestrator import AgentOrchestrator, Request</code> | 导入 <code>from agents.agent_orchestrator import AgentOrchestrator, Request</code>；只建立名称依赖，真正业务调用见后文。 |
| L589 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from memory.conversation_memory import MemoryManager, MsgRole</code> | 导入 <code>from memory.conversation_memory import MemoryManager, MsgRole</code>；只建立名称依赖，真正业务调用见后文。 |
| L590 | <code>&nbsp;&nbsp;&nbsp;&nbsp;from core.skill_loader import SkillManager</code> | 导入 <code>from core.skill_loader import SkillManager</code>；只建立名称依赖，真正业务调用见后文。 |
| L591 | （空行） | 空行，分隔逻辑。 |
| L592 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cfg = _anthropic_cfg()</code> | 将结果保存到 <code>cfg</code>：进入 <code>_anthropic_cfg</code>：配置边界：只校验 API Key 非空，再返回模型和可选 base_url；不验证凭据真实可用。 |
| L593 | <code>&nbsp;&nbsp;&nbsp;&nbsp;skill_manager = SkillManager(</code> | 将结果保存到 <code>skill_manager</code>：调用 <code>SkillManager</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L594 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;root_dir=os.getenv(&quot;ECHOMIND_SKILLS_DIR&quot;, str(pathlib.Path(_ROOT) / &quot;skills&quot;)),</code> | 参数 <code>root_dir</code>（root_dir）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L595 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_prompt_chars=int(os.getenv(&quot;ECHOMIND_SKILLS_MAX_PROMPT_CHARS&quot;, &quot;5000&quot;)),</code> | 参数 <code>max_prompt_chars</code>（max_prompt_chars）：转换为整数。 |
| L596 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L597 | <code>&nbsp;&nbsp;&nbsp;&nbsp;skill_manager.load()</code> | 进入 <code>skill_manager.load</code>：目录不存在返回空；逐个解析，某个坏文件只记错不影响其他文件，最后整体替换快照并记日志。 |
| L598 | <code>&nbsp;&nbsp;&nbsp;&nbsp;orch = AgentOrchestrator(</code> | 将结果保存到 <code>orch</code>：调用 <code>AgentOrchestrator</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L599 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key=cfg[&quot;api_key&quot;],</code> | 参数 <code>api_key</code>（模型服务凭据）：按索引/切片取 <code>cfg[&#x27;api_key&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L600 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url=cfg.get(&quot;base_url&quot;),</code> | 参数 <code>base_url</code>（模型服务地址）：按键取值，缺失用给定默认值。 |
| L601 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=cfg[&quot;model&quot;],</code> | 参数 <code>model</code>（模型名称）：按索引/切片取 <code>cfg[&#x27;model&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L602 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;skill_manager=skill_manager,</code> | 参数 <code>skill_manager</code>（skill_manager）：读取 <code>skill_manager</code>。 |
| L603 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L604 | <code>&nbsp;&nbsp;&nbsp;&nbsp;mem  = MemoryManager(</code> | 将结果保存到 <code>mem</code>：调用 <code>MemoryManager</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L605 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;redis_url=os.getenv(&quot;REDIS_URL&quot;, &quot;redis://localhost:6379/0&quot;),</code> | 参数 <code>redis_url</code>（redis_url）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L606 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_host=os.getenv(&quot;CHROMA_HOST&quot;, &quot;localhost&quot;),</code> | 参数 <code>chroma_host</code>（chroma_host）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L607 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_port=int(os.getenv(&quot;CHROMA_PORT&quot;, &quot;8000&quot;)),</code> | 参数 <code>chroma_port</code>（chroma_port）：转换为整数。 |
| L608 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chroma_path=os.getenv(&quot;CHROMA_PERSIST_DIRECTORY&quot;, &quot;/tmp/chroma&quot;),</code> | 参数 <code>chroma_path</code>（chroma_path）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L609 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api_key=cfg[&quot;api_key&quot;],</code> | 参数 <code>api_key</code>（模型服务凭据）：按索引/切片取 <code>cfg[&#x27;api_key&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L610 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;base_url=cfg.get(&quot;base_url&quot;),</code> | 参数 <code>base_url</code>（模型服务地址）：按键取值，缺失用给定默认值。 |
| L611 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;model=cfg[&quot;model&quot;],</code> | 参数 <code>model</code>（模型名称）：按索引/切片取 <code>cfg[&#x27;model&#x27;]</code>，注意是否截掉旧历史或长文本。 |
| L612 | <code>&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L613 | （空行） | 空行，分隔逻辑。 |
| L614 | <code>&nbsp;&nbsp;&nbsp;&nbsp;user_id, conv_id = &quot;cli_user&quot;, str(uuid.uuid4())</code> | 将结果保存到 <code>(user_id, conv_id)</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L615 | （空行） | 空行，分隔逻辑。 |
| L616 | <code>&nbsp;&nbsp;&nbsp;&nbsp;while True:</code> | 条件 <code>True</code> 保持成立时重复循环。 |
| L617 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L618 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg = input(&quot;你: &quot;).strip()</code> | 将结果保存到 <code>msg</code>：去除两端指定字符或空白。 |
| L619 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except (EOFError, KeyboardInterrupt):</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L620 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(&quot;\n再见 ʕ•ᴥ•ʔ&quot;)</code> | 向终端输出文本。 |
| L621 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;break</code> | 结束当前循环，不再处理剩余候选。 |
| L622 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not msg or msg.lower() in (&quot;quit&quot;, &quot;exit&quot;, &quot;退出&quot;):</code> | 判断 <code>not msg or msg.lower() in (&#x27;quit&#x27;, &#x27;exit&#x27;, &#x27;退出&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L623 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(&quot;再见 ʕ•ᴥ•ʔ&quot;)</code> | 向终端输出文本。 |
| L624 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;break</code> | 结束当前循环，不再处理剩余候选。 |
| L625 | （空行） | 空行，分隔逻辑。 |
| L626 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ctx = await mem.get_context(user_id, conv_id, query=msg)</code> | 将结果保存到 <code>ctx</code>：等待完成后继续；进入 <code>mem.get_context</code>：四步串行读数据。 |
| L627 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;history = [</code> | 将结果保存到 <code>history</code>：条件 <code>ctx.recent_messages</code> 成立选前值，否则选 else 后值。 |
| L628 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{&quot;role&quot;: m.role.value, &quot;content&quot;: m.content}</code> | 字段 <code>content</code>（文本正文）：读取 <code>m.content</code>。 |
| L629 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for m in ctx.recent_messages[-5:]</code> | 续接 L627 的表达式：按前述语句组装参数、条件或集合。 |
| L630 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;] if ctx.recent_messages else None</code> | 续接 L627 的表达式：按前述语句组装参数、条件或集合。 |
| L631 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;req = Request(message=msg, user_id=user_id, conv_id=conv_id, context=ctx.to_prompt_text(), history=history)</code> | 将结果保存到 <code>req</code>：进入 <code>Request</code>：内部请求对象把意图/记忆/实体汇合。 |
| L632 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;result = await orch.run(req)</code> | 将结果保存到 <code>result</code>：等待完成后继续；调用 <code>orch.run</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L633 | （空行） | 空行，分隔逻辑。 |
| L634 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await mem.add_message(user_id, conv_id, MsgRole.USER, msg)</code> | 等待完成后继续；进入 <code>mem.add_message</code>：消息序列化后 LPUSH 放列表头，最新在前；每写一条延长 TTL，到 15 条就同步等待压缩。 |
| L635 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;await mem.add_message(user_id, conv_id, MsgRole.ASSISTANT, result.response)</code> | 等待完成后继续；进入 <code>mem.add_message</code>：消息序列化后 LPUSH 放列表头，最新在前；每写一条延长 TTL，到 15 条就同步等待压缩。 |
| L636 | （空行） | 空行，分隔逻辑。 |
| L637 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(f&quot;\nEchoMind [{result.agent_type.value}]: {result.response}\n&quot;)</code> | 向终端输出文本。 |
| L638 | （空行） | 空行，分隔逻辑。 |
| L639 | <code>&nbsp;&nbsp;&nbsp;&nbsp;await mem.close()</code> | 等待完成后继续；进入 <code>mem.close</code>：只关闭 Redis；LLM 客户端未在这里关闭。 |
| L640 | （空行） | 空行，分隔逻辑。 |
| L641 | （空行） | 空行，分隔逻辑。 |
| L642 | <code>if __name__ == &quot;__main__&quot;:</code> | 判断 <code>__name__ == &#x27;__main__&#x27;</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L643 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if &quot;--cli&quot; in sys.argv:</code> | 判断 <code>&#x27;--cli&#x27; in sys.argv</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L644 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;asyncio.run(_cli())</code> | 调用 <code>asyncio.run</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L645 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L646 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;uvicorn.run(</code> | 调用 <code>uvicorn.run</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L647 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;api.main:app&quot;,</code> | 续接 L646 的表达式：构造文本/参数值。 |
| L648 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;host=os.getenv(&quot;API_HOST&quot;, &quot;0.0.0.0&quot;),</code> | 参数 <code>host</code>（host）：读取进程环境配置，缺失时采用这里写的默认值。 |
| L649 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;port=int(os.getenv(&quot;API_PORT&quot;, &quot;8000&quot;)),</code> | 参数 <code>port</code>（port）：转换为整数。 |
| L650 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;reload=os.getenv(&quot;APP_ENV&quot;) == &quot;development&quot;,</code> | **关键：**只影响 python api/main.py 启动路径；Docker CMD 直接用 uvicorn 不经过此 if。 |
| L651 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |

## 结合全项目：设计缺口与增强方向

- L234 的 health 只检查编排器引用，不能证明 Redis、LLM 或知识库可用。
- L305–309 写记忆仍在响应之前；画像后台化不代表所有记忆操作都不阻塞响应。压缩会追加 LLM 延迟，Redis 写失败可能让已生成回答无法返回。
- L323 暴露的 latency_ms 仅是编排器计时，HTTP 前置记忆/意图/RAG 与后置写入不在其中；不能据此声称端到端延迟。
- 请求模型没有消息长度、top_k 范围、身份认证与会话所有权校验。匿名用户共用 user_id，长期记忆按该值过滤，不是可信身份隔离。
- L468–471 通过私有 _tools 和绑定方法 __self__ 反向取知识库，破坏模块封装；应显式注入 KnowledgeBase 服务。
- L493 是整文件读入后才检查 10MB；非 JSON 扩展名全部按文本处理，JSON 数组元素也未走 DocInput 校验。
- L309 后台任务没有持有引用、统一回收/限流；退出只关 Redis 和 Monitor，多个 LLM 客户端未显式关闭。
- CLI 没有 RAG、画像更新、Monitor、评测装配；评测也不调用 chat。建议抽取共享 ChatService，并让三个入口复用。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
