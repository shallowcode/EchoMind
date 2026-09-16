# core/skill_loader.py 解读

## 输入、输出与流向

**定位：** 从业务说明文件生成当前请求的动态 system prompt 补充。

**输入：** root_dir 内 Markdown/TXT/JSON；message、agent_type；max_prompt_chars。

**输出 / 副作用：** Skill 列表、加载错误、summary JSON、匹配的 prompt；只读业务文件、修改进程内快照。

**流向：** load→发现文件→按格式解析→Skill；prompt_for→enabled/agents/keywords 匹配→每项裁剪→总预算裁剪→业务说明拼接。

[返回阅读入口](../../README.md) · [对照原文件](../../../core/skill_loader.py)

当前工作区快照：338 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`26618d02cde5592955bd45b7a6752e6fbfa3e06de76ed325658f5257f142aaaf`。

## 类与函数导航

[Skill](#symbol-16) → [Skill.matches](#symbol-27) → [Skill.to_prompt_block](#symbol-46) → [Skill.to_summary](#symbol-54) → [SkillManager](#symbol-67) → [SkillManager.__init__](#symbol-78) → [SkillManager.skills](#symbol-84) → [SkillManager.errors](#symbol-88) → [SkillManager.load](#symbol-92) → [SkillManager.reload](#symbol-118) → [SkillManager.prompt_for](#symbol-122) → [SkillManager.summary](#symbol-174) → [SkillManager._log_loaded_skills](#symbol-183) → [SkillManager._discover_files](#symbol-214) → [SkillManager._load_file](#symbol-230) → [SkillManager._load_json](#symbol-235) → [SkillManager._load_text](#symbol-254) → [SkillManager._split_front_matter](#symbol-277) → [SkillManager._first_heading](#symbol-306) → [SkillManager._strip_first_heading](#symbol-314) → [SkillManager._as_list](#symbol-324) → [SkillManager._as_bool](#symbol-332)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>EchoMind Skill 加载器。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | <code>Skill 是一段可热加载的业务能力说明，用来补充 Agent 的 system prompt。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L5 | <code>它适合放置企业话术、处理流程、合规边界、排障 SOP 等需要运营侧快速调整的规则。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L6 | <code>&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>import json</code> | 导入 <code>import json</code>；只建立名称依赖，真正业务调用见后文。 |
| L8 | <code>import logging</code> | 导入 <code>import logging</code>；只建立名称依赖，真正业务调用见后文。 |
| L9 | <code>from dataclasses import dataclass, field</code> | 导入 <code>from dataclasses import dataclass, field</code>；只建立名称依赖，真正业务调用见后文。 |
| L10 | <code>from pathlib import Path</code> | 导入 <code>from pathlib import Path</code>；只建立名称依赖，真正业务调用见后文。 |
| L11 | <code>from typing import Any, Dict, Iterable, List, Optional</code> | 导入 <code>from typing import Any, Dict, Iterable, List, Optional</code>；只建立名称依赖，真正业务调用见后文。 |
| L12 | （空行） | 空行，分隔逻辑。 |
| L13 | <code>logger = logging.getLogger(__name__)</code> | 将结果保存到 <code>logger</code>：获得当前模块的日志记录器。 |
| L14 | （空行） | 空行，分隔逻辑。 |
| L15 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-16"></a>

### L16–L64 · Skill

统一不同文件格式为 name/description/content/path/keywords/agents/enabled，运行时只处理这个对象。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L16 | <code>@dataclass</code> | 装饰器 <code>@dataclass</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L17 | <code>class Skill:</code> | 定义 <code>Skill</code> 的数据契约/行为；继承与字段见本段。 |
| L18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;单个 Skill 的标准化表示，屏蔽 Markdown/JSON 等不同文件格式差异。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;name: str</code> | 声明字段 <code>name</code> 的类型，赋值由构造方完成。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;description: str</code> | 声明字段 <code>description</code> 的类型，赋值由构造方完成。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;content: str</code> | 声明字段 <code>content</code> 的类型，赋值由构造方完成。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;path: str</code> | 声明字段 <code>path</code> 的类型，赋值由构造方完成。 |
| L23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;keywords: List[str] = field(default_factory=list)</code> | 将结果保存到 <code>keywords</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;agents: List[str] = field(default_factory=list)</code> | 将结果保存到 <code>agents</code>：调用 <code>field</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;enabled: bool = True</code> | 将结果保存到 <code>enabled</code>：使用这里写明的固定值。 |
| L26 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-27"></a>

### L27–L44 · Skill.matches

先 enabled，再 agent 类型，再关键词。空关键词代表该类型下全局；如果调用方 agent_type=None，agents 限制不会生效。

**签名输入：** <code>self, message: str, agent_type: Optional[str]=None</code>；**返回契约：** <code>bool</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def matches(self, message: str, agent_type: Optional[str] = None) -&gt; bool:</code> | 定义函数 <code>matches</code>；输入参数见签名，下方导读解释调用目的。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;判断当前请求是否应该注入这个 Skill。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L30 | （空行） | 空行，分隔逻辑。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- agents 为空：适用于所有 Agent；否则只匹配指定 Agent。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- keywords 为空：作为全局 Skill 注入；否则只有命中关键词才注入。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not self.enabled:</code> | 判断 <code>not self.enabled</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L36 | （空行） | 空行，分隔逻辑。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.agents and agent_type and agent_type.lower() not in self.agents:</code> | **关键：**仅在调用方传了 agent_type 时才检查类型限制。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return False</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L39 | （空行） | 空行，分隔逻辑。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not self.keywords:</code> | 判断 <code>not self.keywords</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return True</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L42 | （空行） | 空行，分隔逻辑。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lowered = (message or &quot;&quot;).lower()</code> | 将结果保存到 <code>lowered</code>：转小写进行大小写无关比较。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return any(keyword.lower() in lowered for keyword in self.keywords)</code> | 结束当前函数并返回；至少一项为真就返回True，并可提前结束迭代。 |
| L45 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-46"></a>

### L46–L52 · Skill.to_prompt_block

单 Skill 正文默认 3200 字符，添加标题和说明。正文裁剪后追加省略号，整个 block 会大于 3200。

**签名输入：** <code>self, max_chars: int=3200</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def to_prompt_block(self, max_chars: int = 3200) -&gt; str:</code> | 定义函数 <code>to_prompt_block</code>；输入参数见签名，下方导读解释调用目的。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;格式化为可直接拼入 system prompt 的文本块，并限制单个 Skill 长度。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;body = self.content.strip()</code> | 将结果保存到 <code>body</code>：去除两端指定字符或空白。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(body) &gt; max_chars:</code> | 判断 <code>len(body) &gt; max_chars</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;body = body[:max_chars].rstrip() + &quot;\n...&quot;</code> | 将结果保存到 <code>body</code>：按此表达式计算 <code>body[:max_chars].rstrip() + &#x27;\n...&#x27;</code>。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;description = f&quot;\n说明: {self.description}&quot; if self.description else &quot;&quot;</code> | 将结果保存到 <code>description</code>：条件 <code>self.description</code> 成立选前值，否则选 else 后值。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return f&quot;### {self.name}{description}\n{body}&quot;</code> | 结束当前函数并返回；将变量插入模板，构造提示词、标识或可读说明。 |
| L53 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-54"></a>

### L54–L64 · Skill.to_summary

返回配置元信息和正文字符数，避免管理接口一次返回全部长规则。

**签名输入：** <code>self</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def to_summary(self) -&gt; Dict[str, Any]:</code> | 定义函数 <code>to_summary</code>；输入参数见签名，下方导读解释调用目的。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;返回 API 可序列化摘要，避免把完整长文本默认暴露给健康检查。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;name&quot;: self.name,</code> | 字段 <code>name</code>（当前映射中的键）：读取 <code>self.name</code>。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;description&quot;: self.description,</code> | 字段 <code>description</code>（当前映射中的键）：读取 <code>self.description</code>。 |
| L59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;path&quot;: self.path,</code> | 字段 <code>path</code>（当前映射中的键）：读取 <code>self.path</code>。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;keywords&quot;: self.keywords,</code> | 字段 <code>keywords</code>（子串触发词）：读取 <code>self.keywords</code>。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agents&quot;: self.agents,</code> | 字段 <code>agents</code>（允许匹配的 Agent 类型）：读取 <code>self.agents</code>。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;enabled&quot;: self.enabled,</code> | 字段 <code>enabled</code>（是否启用）：读取 <code>self.enabled</code>。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;content_chars&quot;: len(self.content),</code> | 字段 <code>content_chars</code>（当前映射中的键）：计算当前容器或字符串长度。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L65 | （空行） | 空行，分隔逻辑。 |
| L66 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-67"></a>

### L67–L338 · SkillManager

从业务说明文件生成当前请求的动态 system prompt 补充。 下方逐个方法说明该类如何实现职责。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L67 | <code>class SkillManager:</code> | 定义 <code>SkillManager</code> 的数据契约/行为；继承与字段见本段。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;从目录中发现、解析并管理 Skills。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L70 | （空行） | 空行，分隔逻辑。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;支持两种常用结构：</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. skills/refund/SKILL.md</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. skills/refund.json / skills/refund.md / skills/refund.txt</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L75 | （空行） | 空行，分隔逻辑。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;SUPPORTED_SUFFIXES = {&quot;.md&quot;, &quot;.txt&quot;, &quot;.json&quot;}</code> | 将结果保存到 <code>SUPPORTED_SUFFIXES</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L77 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-78"></a>

### L78–L82 · SkillManager.__init__

把根目录变绝对路径，初始化空快照；构造本身不读取文件，必须 load。

**签名输入：** <code>self, root_dir: str, max_prompt_chars: int=5000</code>；**返回契约：** <code>源码未标注；参照 return 和本段解释</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, root_dir: str, max_prompt_chars: int = 5000):</code> | 定义函数 <code>__init__</code>；输入参数见签名，下方导读解释调用目的。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.root_dir = Path(root_dir).expanduser().resolve()</code> | 将结果保存到 <code>self.root_dir</code>：调用 <code>Path(root_dir).expanduser().resolve</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.max_prompt_chars = max_prompt_chars</code> | 将结果保存到 <code>self.max_prompt_chars</code>：读取 <code>max_prompt_chars</code>。 |
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._skills: List[Skill] = []</code> | 将结果保存到 <code>self._skills</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._errors: List[str] = []</code> | 将结果保存到 <code>self._errors</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L83 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-84"></a>

### L84–L86 · SkillManager.skills

返回列表副本，避免外部直接增删内部列表；其中 Skill 对象仍然共享。

**签名输入：** <code>self</code>；**返回契约：** <code>List[Skill]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def skills(self) -&gt; List[Skill]:</code> | 定义函数 <code>skills</code>；输入参数见签名，下方导读解释调用目的。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return list(self._skills)</code> | 结束当前函数并返回；将迭代内容物化成列表。 |
| L87 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-88"></a>

### L88–L90 · SkillManager.errors

同样返回错误列表副本。

**签名输入：** <code>self</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@property</code> | 装饰器 <code>@property</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def errors(self) -&gt; List[str]:</code> | 定义函数 <code>errors</code>；输入参数见签名，下方导读解释调用目的。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return list(self._errors)</code> | 结束当前函数并返回；将迭代内容物化成列表。 |
| L91 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-92"></a>

### L92–L116 · SkillManager.load

目录不存在返回空；逐个解析，某个坏文件只记错不影响其他文件，最后整体替换快照并记日志。

**签名输入：** <code>self</code>；**返回契约：** <code>List[Skill]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def load(self) -&gt; List[Skill]:</code> | 定义函数 <code>load</code>；输入参数见签名，下方导读解释调用目的。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;重新扫描目录并加载 Skills；单个文件失败不会影响其他 Skill 生效。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;loaded: List[Skill] = []</code> | 将结果保存到 <code>loaded</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;errors: List[str] = []</code> | 将结果保存到 <code>errors</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L96 | （空行） | 空行，分隔逻辑。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not self.root_dir.exists():</code> | 判断 <code>not self.root_dir.exists()</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(f&quot;Skill 目录不存在，跳过加载: {self.root_dir}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._skills = []</code> | 将结果保存到 <code>self._skills</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._errors = []</code> | 将结果保存到 <code>self._errors</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return []</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L102 | （空行） | 空行，分隔逻辑。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for path in self._discover_files(self.root_dir):</code> | 遍历 <code>self._discover_files(self.root_dir)</code>，本轮元素绑定 <code>path</code>。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;try:</code> | 进入异常捕获范围，后面的 except 决定失败如何降级。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;skill = self._load_file(path)</code> | 将结果保存到 <code>skill</code>：进入 <code>self._load_file</code>：json 分流至结构化解析，其他支持后缀统一当文本。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if skill is not None:</code> | 判断 <code>skill is not None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;loaded.append(skill)</code> | 追加一个元素到当前列表。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;except Exception as ex:</code> | 捕获此类异常并进入恢复/错误记录分支。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;msg = f&quot;{path}: {ex}&quot;</code> | 将结果保存到 <code>msg</code>：将变量插入模板，构造提示词、标识或可读说明。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;errors.append(msg)</code> | 追加一个元素到当前列表。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.warning(f&quot;Skill 加载失败: {msg}&quot;)</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L112 | （空行） | 空行，分隔逻辑。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._skills = loaded</code> | 将结果保存到 <code>self._skills</code>：读取 <code>loaded</code>。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._errors = errors</code> | 将结果保存到 <code>self._errors</code>：读取 <code>errors</code>。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._log_loaded_skills()</code> | 进入 <code>self._log_loaded_skills</code>：把技能名称、匹配 Agent、关键词、路径组合成启动日志，方便人工确认配置已生效。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.skills</code> | 结束当前函数并返回；读取 <code>self.skills</code>。 |
| L117 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-118"></a>

### L118–L120 · SkillManager.reload

load 的别名；没有文件监听器，只有显式调用才重新读磁盘。

**签名输入：** <code>self</code>；**返回契约：** <code>List[Skill]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def reload(self) -&gt; List[Skill]:</code> | 定义函数 <code>reload</code>；输入参数见签名，下方导读解释调用目的。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;运行时热加载入口，供 API 调用。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.load()</code> | 结束当前函数并返回；进入 <code>self.load</code>：目录不存在返回空；逐个解析，某个坏文件只记错不影响其他文件，最后整体替换快照并记日志。 |
| L121 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-122"></a>

### L122–L172 · SkillManager.prompt_for

按已加载顺序检查匹配，构造块并消耗 remaining，耗尽停止。不是语义检索 Skill；匹配仅靠子串和类型。

**签名输入：** <code>self, message: str, agent_type: Optional[str]=None</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def prompt_for(self, message: str, agent_type: Optional[str] = None) -&gt; str:</code> | 定义函数 <code>prompt_for</code>；输入参数见签名，下方导读解释调用目的。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;为当前用户请求构建 Skill prompt。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L125 | （空行） | 空行，分隔逻辑。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;只注入匹配的 Skill，并按总长度截断，避免挤占主对话上下文。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;blocks: List[str] = []</code> | 将结果保存到 <code>blocks</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;matched: List[tuple[Skill, List[str]]] = []</code> | 将结果保存到 <code>matched</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;remaining = self.max_prompt_chars</code> | 将结果保存到 <code>remaining</code>：读取 <code>self.max_prompt_chars</code>。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lowered_message = (message or &quot;&quot;).lower()</code> | 将结果保存到 <code>lowered_message</code>：转小写进行大小写无关比较。 |
| L132 | （空行） | 空行，分隔逻辑。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for skill in self._skills:</code> | 遍历 <code>self._skills</code>，本轮元素绑定 <code>skill</code>。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not skill.matches(message, agent_type):</code> | 判断 <code>not skill.matches(message, agent_type)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;matched_keywords = [</code> | 将结果保存到 <code>matched_keywords</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keyword for keyword in skill.keywords</code> | 续接 L136 的表达式：按前述语句组装参数、条件或集合。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if keyword.lower() in lowered_message</code> | 续接 L136 的表达式：按前述语句组装参数、条件或集合。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;block = skill.to_prompt_block()</code> | 将结果保存到 <code>block</code>：进入 <code>skill.to_prompt_block</code>：单 Skill 正文默认 3200 字符，添加标题和说明。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(block) &gt; remaining:</code> | 判断 <code>len(block) &gt; remaining</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;block = block[:remaining].rstrip() + &quot;\n...&quot;</code> | **关键：**裁剪 remaining 后又追加 4 字符换行省略号，预算可能超出。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;blocks.append(block)</code> | 追加一个元素到当前列表。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;matched.append((skill, matched_keywords))</code> | 追加一个元素到当前列表。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;remaining -= len(block)</code> | 更新 <code>remaining</code>：<code>remaining -= len(block)</code>；此处会改变累计状态。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if remaining &lt;= 0:</code> | 判断 <code>remaining &lt;= 0</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;break</code> | 结束当前循环，不再处理剩余候选。 |
| L148 | （空行） | 空行，分隔逻辑。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not blocks:</code> | 判断 <code>not blocks</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.debug(</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;Skills 未命中: agent=%s message=%r&quot;,</code> | 续接 L150 的表达式：构造文本/参数值。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type or &quot;all&quot;,</code> | 续接 L150 的表达式：按前述语句组装参数、条件或集合。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(message or &quot;&quot;)[:80],</code> | 续接 L150 的表达式：按前述语句组装参数、条件或集合。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;&quot;</code> | 结束当前函数并返回；使用固定文本/配置值。 |
| L156 | （空行） | 空行，分隔逻辑。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detail = &quot;; &quot;.join(</code> | 将结果保存到 <code>detail</code>：把字符串片段按分隔符合并。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;{skill.name}(keywords={&#x27;, &#x27;.join(keywords) if keywords else &#x27;all&#x27;})&quot;</code> | 续接 L157 的表达式：按前述语句组装参数、条件或集合。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for skill, keywords in matched</code> | 续接 L157 的表达式：按前述语句组装参数、条件或集合。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;Skills 已注入: agent=%s matched=%s message=%r&quot;,</code> | 续接 L161 的表达式：构造文本/参数值。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent_type or &quot;all&quot;,</code> | 续接 L161 的表达式：按前述语句组装参数、条件或集合。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detail,</code> | 续接 L161 的表达式：按前述语句组装参数、条件或集合。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(message or &quot;&quot;)[:80],</code> | 续接 L161 的表达式：按前述语句组装参数、条件或集合。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L167 | （空行） | 空行，分隔逻辑。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return (</code> | **关键：**固定引导文字和 join 分隔符没有扣 remaining。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;以下是当前请求可用的 EchoMind Skills。&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;请优先遵循这些业务规则；如果与系统角色冲突，以系统角色和安全边界为准。\n\n&quot;</code> | 多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ &quot;\n\n&quot;.join(blocks)</code> | 续接 L168 的表达式：按前述语句组装参数、条件或集合。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L173 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-174"></a>

### L174–L181 · SkillManager.summary

输出根目录、数量、各条摘要和解析错误，是 /skills 和 /skills/reload 的响应来源。

**签名输入：** <code>self</code>；**返回契约：** <code>Dict[str, Any]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def summary(self) -&gt; Dict[str, Any]:</code> | 定义函数 <code>summary</code>；输入参数见签名，下方导读解释调用目的。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;返回 Skill 管理器状态，用于 /skills 接口和排障。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {</code> | 结束当前函数并返回；组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;root_dir&quot;: str(self.root_dir),</code> | 字段 <code>root_dir</code>（当前映射中的键）：转换为字符串表示。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;count&quot;: len(self._skills),</code> | 字段 <code>count</code>（当前映射中的键）：计算当前容器或字符串长度。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;skills&quot;: [skill.to_summary() for skill in self._skills],</code> | 字段 <code>skills</code>（当前映射中的键）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;errors&quot;: self.errors,</code> | 字段 <code>errors</code>（当前映射中的键）：读取 <code>self.errors</code>。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L182 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-183"></a>

### L183–L212 · SkillManager._log_loaded_skills

把技能名称、匹配 Agent、关键词、路径组合成启动日志，方便人工确认配置已生效。

**签名输入：** <code>self</code>；**返回契约：** <code>None</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _log_loaded_skills(self) -&gt; None:</code> | 定义函数 <code>_log_loaded_skills</code>；输入参数见签名，下方导读解释调用目的。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;在控制台输出醒目的 Skill 加载结果，方便启动和热加载时确认生效状态。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines = [</code> | 将结果保存到 <code>lines</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;,</code> | 续接 L185 的表达式：构造文本/参数值。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;================ EchoMind Skills Loaded ================&quot;,</code> | 续接 L185 的表达式：构造文本/参数值。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;目录: {self.root_dir}&quot;,</code> | 续接 L185 的表达式：按前述语句组装参数、条件或集合。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;数量: {len(self._skills)}&quot;,</code> | 续接 L185 的表达式：按前述语句组装参数、条件或集合。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L191 | （空行） | 空行，分隔逻辑。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._skills:</code> | 判断 <code>self._skills</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for index, skill in enumerate(self._skills, start=1):</code> | 遍历 <code>enumerate(self._skills, start=1)</code>，本轮元素绑定 <code>(index, skill)</code>。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agents = &quot;, &quot;.join(skill.agents) if skill.agents else &quot;all&quot;</code> | 将结果保存到 <code>agents</code>：条件 <code>skill.agents</code> 成立选前值，否则选 else 后值。 |
| L195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keywords = &quot;, &quot;.join(skill.keywords[:8]) if skill.keywords else &quot;all&quot;</code> | 将结果保存到 <code>keywords</code>：条件 <code>skill.keywords</code> 成立选前值，否则选 else 后值。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(skill.keywords) &gt; 8:</code> | 判断 <code>len(skill.keywords) &gt; 8</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keywords += &quot;, ...&quot;</code> | 更新 <code>keywords</code>：<code>keywords += &#x27;, ...&#x27;</code>；此处会改变累计状态。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines.extend([</code> | 追加一批元素到列表。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;{index}. {skill.name}&quot;,</code> | 续接 L198 的表达式：按前述语句组装参数、条件或集合。 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;   agents: {agents}&quot;,</code> | 续接 L198 的表达式：按前述语句组装参数、条件或集合。 |
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;   keywords: {keywords}&quot;,</code> | 续接 L198 的表达式：按前述语句组装参数、条件或集合。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f&quot;   path: {skill.path}&quot;,</code> | 续接 L198 的表达式：按前述语句组装参数、条件或集合。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;])</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:</code> | 前一条件不成立时走这里。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines.append(&quot;未加载任何 Skill。&quot;)</code> | 追加一个元素到当前列表。 |
| L206 | （空行） | 空行，分隔逻辑。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self._errors:</code> | 判断 <code>self._errors</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines.append(&quot;解析错误:&quot;)</code> | 追加一个元素到当前列表。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines.extend(f&quot;  - {error}&quot; for error in self._errors)</code> | 追加一批元素到列表。 |
| L210 | （空行） | 空行，分隔逻辑。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines.append(&quot;========================================================&quot;)</code> | 追加一个元素到当前列表。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logger.info(&quot;\n&quot;.join(lines))</code> | 输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进。 |
| L213 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-214"></a>

### L214–L228 · SkillManager._discover_files

先递归发现规范名 SKILL.md，避免二次遍历重复；再找其余 md/txt/json，跳过隐藏文件名与 README。

**签名输入：** <code>self, root_dir: Path</code>；**返回契约：** <code>Iterable[Path]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _discover_files(self, root_dir: Path) -&gt; Iterable[Path]:</code> | 定义函数 <code>_discover_files</code>；输入参数见签名，下方导读解释调用目的。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;发现可加载文件，优先读取目录规范文件 SKILL.md。&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;skill_md_files = sorted(root_dir.rglob(&quot;SKILL.md&quot;))</code> | 将结果保存到 <code>skill_md_files</code>：按指定规则排序，不直接改变原列表。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;yielded = {path.resolve() for path in skill_md_files}</code> | 将结果保存到 <code>yielded</code>：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for path in skill_md_files:</code> | 遍历 <code>skill_md_files</code>，本轮元素绑定 <code>path</code>。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;yield path</code> | 读取 <code>(yield path)</code>。 |
| L220 | （空行） | 空行，分隔逻辑。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for path in sorted(root_dir.rglob(&quot;*&quot;)):</code> | 遍历 <code>sorted(root_dir.rglob(&#x27;*&#x27;))</code>，本轮元素绑定 <code>path</code>。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;resolved = path.resolve()</code> | 将结果保存到 <code>resolved</code>：调用 <code>path.resolve</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if resolved in yielded or not path.is_file():</code> | 判断 <code>resolved in yielded or not path.is_file()</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if path.name.startswith(&quot;.&quot;) or path.name.upper() == &quot;README.MD&quot;:</code> | **关键：**README 只作人读文档，不会注入 Agent。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if path.suffix.lower() in self.SUPPORTED_SUFFIXES:</code> | 判断 <code>path.suffix.lower() in self.SUPPORTED_SUFFIXES</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;yield path</code> | 读取 <code>(yield path)</code>。 |
| L229 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-230"></a>

### L230–L233 · SkillManager._load_file

json 分流至结构化解析，其他支持后缀统一当文本。

**签名输入：** <code>self, path: Path</code>；**返回契约：** <code>Optional[Skill]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _load_file(self, path: Path) -&gt; Optional[Skill]:</code> | 定义函数 <code>_load_file</code>；输入参数见签名，下方导读解释调用目的。 |
| L231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if path.suffix.lower() == &quot;.json&quot;:</code> | 判断 <code>path.suffix.lower() == &#x27;.json&#x27;</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self._load_json(path)</code> | 结束当前函数并返回；进入 <code>self._load_json</code>：必须 JSON 对象且有 content 或 instructions。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self._load_text(path)</code> | 结束当前函数并返回；进入 <code>self._load_text</code>：分离简单 front matter，正文为空跳过；名称取 meta、首标题或目录/文件名；移除重复首标题以节省 prompt。 |
| L234 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-235"></a>

### L235–L252 · SkillManager._load_json

必须 JSON 对象且有 content 或 instructions。缺少名称用文件 stem，agents 小写化，关键词和 enabled 统一转换。

**签名输入：** <code>self, path: Path</code>；**返回契约：** <code>Optional[Skill]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _load_json(self, path: Path) -&gt; Optional[Skill]:</code> | 定义函数 <code>_load_json</code>；输入参数见签名，下方导读解释调用目的。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = json.loads(path.read_text(encoding=&quot;utf-8&quot;))</code> | 将结果保存到 <code>raw</code>：将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not isinstance(raw, dict):</code> | 判断 <code>not isinstance(raw, dict)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise ValueError(&quot;JSON Skill 必须是对象格式&quot;)</code> | 抛出 <code>ValueError(&#x27;JSON Skill 必须是对象格式&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L239 | （空行） | 空行，分隔逻辑。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content = str(raw.get(&quot;content&quot;) or raw.get(&quot;instructions&quot;) or &quot;&quot;).strip()</code> | 将结果保存到 <code>content</code>：去除两端指定字符或空白。 |
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not content:</code> | 判断 <code>not content</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise ValueError(&quot;缺少 content 或 instructions&quot;)</code> | 抛出 <code>ValueError(&#x27;缺少 content 或 instructions&#x27;)</code>；由外层异常处理或 HTTP 框架接收。 |
| L243 | （空行） | 空行，分隔逻辑。 |
| L244 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return Skill(</code> | 结束当前函数并返回；进入 <code>Skill</code>：统一不同文件格式为 name/description/content/path/keywords/agents/enabled，运行时只处理这个对象。 |
| L245 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name=str(raw.get(&quot;name&quot;) or path.stem),</code> | 参数 <code>name</code>（name）：转换为字符串表示。 |
| L246 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;description=str(raw.get(&quot;description&quot;) or &quot;&quot;),</code> | 参数 <code>description</code>（description）：转换为字符串表示。 |
| L247 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content=content,</code> | 参数 <code>content</code>（文本正文）：读取 <code>content</code>。 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path=str(path),</code> | 参数 <code>path</code>（path）：转换为字符串表示。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keywords=self._as_list(raw.get(&quot;keywords&quot;)),</code> | 参数 <code>keywords</code>（子串触发词）：进入 <code>self._as_list</code>：None/空→[]，列表→逐项转字符串，否则按英文逗号 split。 |
| L250 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agents=[item.lower() for item in self._as_list(raw.get(&quot;agents&quot;))],</code> | 参数 <code>agents</code>（允许匹配的 Agent 类型）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;enabled=self._as_bool(raw.get(&quot;enabled&quot;), default=True),</code> | 参数 <code>default</code>（default）：使用这里写明的固定值。 |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L253 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-254"></a>

### L254–L275 · SkillManager._load_text

分离简单 front matter，正文为空跳过；名称取 meta、首标题或目录/文件名；移除重复首标题以节省 prompt。

**签名输入：** <code>self, path: Path</code>；**返回契约：** <code>Optional[Skill]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _load_text(self, path: Path) -&gt; Optional[Skill]:</code> | 定义函数 <code>_load_text</code>；输入参数见签名，下方导读解释调用目的。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raw = path.read_text(encoding=&quot;utf-8&quot;)</code> | 将结果保存到 <code>raw</code>：从文件读取文本。 |
| L256 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;meta, body = self._split_front_matter(raw)</code> | 将结果保存到 <code>(meta, body)</code>：进入 <code>self._split_front_matter</code>：要求顶部独立 ---，逐行按第一个冒号切 key/value，再遇 --- 结束。 |
| L257 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;body = body.strip()</code> | 将结果保存到 <code>body</code>：去除两端指定字符或空白。 |
| L258 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not body:</code> | 判断 <code>not body</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L259 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L260 | （空行） | 空行，分隔逻辑。 |
| L261 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;default_name = path.parent.name if path.name == &quot;SKILL.md&quot; else path.stem</code> | 将结果保存到 <code>default_name</code>：条件 <code>path.name == &#x27;SKILL.md&#x27;</code> 成立选前值，否则选 else 后值。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name = str(meta.get(&quot;name&quot;) or self._first_heading(body) or default_name)</code> | 将结果保存到 <code>name</code>：转换为字符串表示。 |
| L263 | （空行） | 空行，分隔逻辑。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 如果首行标题只是 Skill 名称，注入 prompt 时去掉它，减少重复噪音。</code> | 源码注释：如果首行标题只是 Skill 名称，注入 prompt 时去掉它，减少重复噪音。 |
| L265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;body = self._strip_first_heading(body, name)</code> | 将结果保存到 <code>body</code>：进入 <code>self._strip_first_heading</code>：只有第一行标题正好等于 name 才去掉，防止把其他业务标题误删。 |
| L266 | （空行） | 空行，分隔逻辑。 |
| L267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return Skill(</code> | 结束当前函数并返回；进入 <code>Skill</code>：统一不同文件格式为 name/description/content/path/keywords/agents/enabled，运行时只处理这个对象。 |
| L268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name=name,</code> | 参数 <code>name</code>（name）：读取 <code>name</code>。 |
| L269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;description=str(meta.get(&quot;description&quot;) or &quot;&quot;),</code> | 参数 <code>description</code>（description）：转换为字符串表示。 |
| L270 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;content=body,</code> | 参数 <code>content</code>（文本正文）：读取 <code>body</code>。 |
| L271 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;path=str(path),</code> | 参数 <code>path</code>（path）：转换为字符串表示。 |
| L272 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keywords=self._as_list(meta.get(&quot;keywords&quot;)),</code> | 参数 <code>keywords</code>（子串触发词）：进入 <code>self._as_list</code>：None/空→[]，列表→逐项转字符串，否则按英文逗号 split。 |
| L273 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agents=[item.lower() for item in self._as_list(meta.get(&quot;agents&quot;))],</code> | 参数 <code>agents</code>（允许匹配的 Agent 类型）：按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;enabled=self._as_bool(meta.get(&quot;enabled&quot;), default=True),</code> | 参数 <code>default</code>（default）：使用这里写明的固定值。 |
| L275 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</code> | 结束/连接多行结构；本行没有独立业务动作。 |
| L276 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-277"></a>

### L277–L304 · SkillManager._split_front_matter

要求顶部独立 ---，逐行按第一个冒号切 key/value，再遇 --- 结束。不支持嵌套 YAML、多行块或 YAML 数组语义。

**签名输入：** <code>self, raw: str</code>；**返回契约：** <code>tuple[Dict[str, Any], str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L277 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _split_front_matter(self, raw: str) -&gt; tuple[Dict[str, Any], str]:</code> | 定义函数 <code>_split_front_matter</code>；输入参数见签名，下方导读解释调用目的。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;解析 Markdown 顶部的简单 front matter。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L280 | （空行） | 空行，分隔逻辑。 |
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;这里刻意不用 PyYAML，避免为一个轻量配置格式新增运行时依赖。</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L283 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text = raw.lstrip()</code> | 将结果保存到 <code>text</code>：调用 <code>raw.lstrip</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L284 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not text.startswith(&quot;---&quot;):</code> | 判断 <code>not text.startswith(&#x27;---&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L285 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {}, raw</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L286 | （空行） | 空行，分隔逻辑。 |
| L287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines = text.splitlines()</code> | 将结果保存到 <code>lines</code>：调用 <code>text.splitlines</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L288 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not lines or lines[0].strip() != &quot;---&quot;:</code> | 判断 <code>not lines or lines[0].strip() != &#x27;---&#x27;</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {}, raw</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L290 | （空行） | 空行，分隔逻辑。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;meta: Dict[str, Any] = {}</code> | 将结果保存到 <code>meta</code>：组装字段字典，下列各键决定输出/模型请求/存储结构。 |
| L292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;end_idx: Optional[int] = None</code> | 将结果保存到 <code>end_idx</code>：使用这里写明的固定值。 |
| L293 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for idx, line in enumerate(lines[1:], start=1):</code> | 遍历 <code>enumerate(lines[1:], start=1)</code>，本轮元素绑定 <code>(idx, line)</code>。 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if line.strip() == &quot;---&quot;:</code> | 判断 <code>line.strip() == &#x27;---&#x27;</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;end_idx = idx</code> | 将结果保存到 <code>end_idx</code>：读取 <code>idx</code>。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;break</code> | 结束当前循环，不再处理剩余候选。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if &quot;:&quot; not in line:</code> | 判断 <code>&#x27;:&#x27; not in line</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | 跳过本轮剩余代码，处理下一元素。 |
| L299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key, value = line.split(&quot;:&quot;, 1)</code> | 将结果保存到 <code>(key, value)</code>：按分隔符切分字符串。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;meta[key.strip()] = value.strip().strip(&quot;\&quot;&#x27;&quot;)</code> | 将结果保存到 <code>meta[key.strip()]</code>：去除两端指定字符或空白。 |
| L301 | （空行） | 空行，分隔逻辑。 |
| L302 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if end_idx is None:</code> | 判断 <code>end_idx is None</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L303 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {}, raw</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L304 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return meta, &quot;\n&quot;.join(lines[end_idx + 1:])</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L305 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-306"></a>

### L306–L312 · SkillManager._first_heading

找第一条以 # 开头的文本做备用名；不是完整 Markdown 解析。

**签名输入：** <code>body: str</code>；**返回契约：** <code>Optional[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L307 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _first_heading(body: str) -&gt; Optional[str]:</code> | 定义函数 <code>_first_heading</code>；输入参数见签名，下方导读解释调用目的。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for line in body.splitlines():</code> | 遍历 <code>body.splitlines()</code>，本轮元素绑定 <code>line</code>。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stripped = line.strip()</code> | 将结果保存到 <code>stripped</code>：去除两端指定字符或空白。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if stripped.startswith(&quot;#&quot;):</code> | 判断 <code>stripped.startswith(&#x27;#&#x27;)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return stripped.lstrip(&quot;#&quot;).strip() or None</code> | 结束当前函数并返回；读取 <code>stripped.lstrip(&#x27;#&#x27;).strip() or None</code>。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return None</code> | 结束当前函数并返回；使用这里写明的固定值。 |
| L313 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-314"></a>

### L314–L322 · SkillManager._strip_first_heading

只有第一行标题正好等于 name 才去掉，防止把其他业务标题误删。

**签名输入：** <code>body: str, name: str</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _strip_first_heading(body: str, name: str) -&gt; str:</code> | 定义函数 <code>_strip_first_heading</code>；输入参数见签名，下方导读解释调用目的。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lines = body.splitlines()</code> | 将结果保存到 <code>lines</code>：调用 <code>body.splitlines</code>；实参见源码，函数职责见本页导读或对应模块。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not lines:</code> | 判断 <code>not lines</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return body</code> | 结束当前函数并返回；读取 <code>body</code>。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;first = lines[0].strip()</code> | 将结果保存到 <code>first</code>：去除两端指定字符或空白。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if first.startswith(&quot;#&quot;) and first.lstrip(&quot;#&quot;).strip() == name:</code> | 判断 <code>first.startswith(&#x27;#&#x27;) and first.lstrip(&#x27;#&#x27;).strip() == name</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return &quot;\n&quot;.join(lines[1:]).strip()</code> | 结束当前函数并返回；去除两端指定字符或空白。 |
| L322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return body</code> | 结束当前函数并返回；读取 <code>body</code>。 |
| L323 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-324"></a>

### L324–L330 · SkillManager._as_list

None/空→[]，列表→逐项转字符串，否则按英文逗号 split。中文逗号不会分割。

**签名输入：** <code>value: Any</code>；**返回契约：** <code>List[str]</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _as_list(value: Any) -&gt; List[str]:</code> | 定义函数 <code>_as_list</code>；输入参数见签名，下方导读解释调用目的。 |
| L326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if value is None or value == &quot;&quot;:</code> | 判断 <code>value is None or value == &#x27;&#x27;</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return []</code> | 结束当前函数并返回；组装有序值或集合，元素在后续逻辑中消费。 |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(value, list):</code> | 判断 <code>isinstance(value, list)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [str(item).strip() for item in value if str(item).strip()]</code> | 结束当前函数并返回；按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器。 |
| L330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return [item.strip() for item in str(value).split(&quot;,&quot;) if item.strip()]</code> | **关键：**分隔符只有英文逗号，中文逗号支持是文档失配。 |
| L331 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-332"></a>

### L332–L338 · SkillManager._as_bool

只把 0/false/no/off/disabled 等判 False，未识别拼写如 flase 会当 True；严格配置可选择拒绝未知值。

**签名输入：** <code>value: Any, default: bool=False</code>；**返回契约：** <code>bool</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;@staticmethod</code> | 装饰器 <code>@staticmethod</code>；为函数添加路由、属性、静态/类方法或数据类行为。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;def _as_bool(value: Any, default: bool = False) -&gt; bool:</code> | 定义函数 <code>_as_bool</code>；输入参数见签名，下方导读解释调用目的。 |
| L334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if value is None or value == &quot;&quot;:</code> | 判断 <code>value is None or value == &#x27;&#x27;</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L335 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return default</code> | 结束当前函数并返回；读取 <code>default</code>。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(value, bool):</code> | 判断 <code>isinstance(value, bool)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return value</code> | 结束当前函数并返回；读取 <code>value</code>。 |
| L338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return str(value).strip().lower() not in {&quot;0&quot;, &quot;false&quot;, &quot;no&quot;, &quot;off&quot;, &quot;disabled&quot;}</code> | 结束当前函数并返回；读取 <code>str(value).strip().lower() not in {&#x27;0&#x27;, &#x27;false&#x27;, &#x27;no&#x27;, &#x27;off&#x27;, &#x27;disabled&#x27;}</code>。 |

## 结合全项目：设计缺口与增强方向

- front matter 是手写逐行冒号解析，不是完整 YAML；_as_list 只按英文逗号切，与 skills/README 的“中文逗号也支持”不符。
- Skill 内的禁止事项只作为 prompt，没有执行器约束；规则不匹配或被裁剪就不注入。重要底线宜在固定 system prompt 和服务端校验中双重实现。
- 长度是字符数而非 token；裁剪后加省略号，外层提示和分隔符未计入预算，实际可以超 max_prompt_chars。
- 排序按文件路径，无优先级/冲突解决/业务版本；load 用新列表替换旧列表但热更新没有跨进程广播。
- reload 同步扫描/读取文件在 async API 中执行，规则较多时会占用事件循环；接口无访问控制。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
