# core/llm_utils.py 解读

## 输入、输出与流向

**定位：** 统一提取模型响应中的可显示文本，屏蔽对象与字典格式差异。

**输入：** 可迭代 content：字符串、带 type/text 属性的对象或字典。

**输出 / 副作用：** 去掉空文本后用换行拼接的字符串；无外部 I/O 和存储副作用。

**流向：** 遍历 block→直接字符串收集→对象属性读取→字典字段覆盖→只接受 text/无类型文本→join。

[返回阅读入口](../../README.md) · [对照原文件](../../../core/llm_utils.py)

当前工作区快照：22 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`b0bf4cc194787b059a02c2049a773dceb1ff92df95f5d7d7bdc492ba355e93e7`。

## 类与函数导航

[extract_text_content](#symbol-5)

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&quot;&quot;&quot;LLM response helpers shared by Anthropic-compatible providers.&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L2 | <code>from typing import Any, Iterable, List</code> | 导入 <code>from typing import Any, Iterable, List</code>；只建立名称依赖，真正业务调用见后文。 |
| L3 | （空行） | 空行，分隔逻辑。 |
| L4 | （空行） | 空行，分隔逻辑。 |

<a id="symbol-5"></a>

### L5–L22 · extract_text_content

多个使用模型的模块复用一个格式适配函数，避免每处假定 response.content[0].text。兼容性目标是文本提取，不是完整模型协议解析。

**签名输入：** <code>content: Iterable[Any]</code>；**返回契约：** <code>str</code>。

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L5 | <code>def extract_text_content(content: Iterable[Any]) -&gt; str:</code> | 定义函数 <code>extract_text_content</code>；输入参数见签名，下方导读解释调用目的。 |
| L6 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&quot;&quot;Return text blocks from Anthropic-style response content.&quot;&quot;&quot;</code> | 说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。 |
| L7 | <code>&nbsp;&nbsp;&nbsp;&nbsp;texts: List[str] = []</code> | 将结果保存到 <code>texts</code>：组装有序值或集合，元素在后续逻辑中消费。 |
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;for block in content or []:</code> | **关键：**content=None 用空列表，安全返回空字符串；整个字符串却会按字符遍历。 |
| L9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(block, str):</code> | 判断 <code>isinstance(block, str)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;texts.append(block)</code> | 追加一个元素到当前列表。 |
| L11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue</code> | **关键：**字符串块已处理，跳过后面的属性检测。 |
| L12 | （空行） | 空行，分隔逻辑。 |
| L13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;block_type = getattr(block, &quot;type&quot;, None)</code> | 将结果保存到 <code>block_type</code>：读取对象指定属性，不存在时返回这里给出的默认值。 |
| L14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text = getattr(block, &quot;text&quot;, None)</code> | 将结果保存到 <code>text</code>：读取对象指定属性，不存在时返回这里给出的默认值。 |
| L15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(block, dict):</code> | 判断 <code>isinstance(block, dict)</code>；成立才执行下一层，else（若有）处理另一情况。 |
| L16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;block_type = block.get(&quot;type&quot;, block_type)</code> | 将结果保存到 <code>block_type</code>：按键取值，缺失用给定默认值。 |
| L17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text = block.get(&quot;text&quot;, text)</code> | 将结果保存到 <code>text</code>：按键取值，缺失用给定默认值。 |
| L18 | （空行） | 空行，分隔逻辑。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if isinstance(text, str) and (block_type in (None, &quot;text&quot;)):</code> | **关键：**仅 text 类型或缺省类型文本进入输出；tool_use 不被执行。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;texts.append(text)</code> | 追加一个元素到当前列表。 |
| L21 | （空行） | 空行，分隔逻辑。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;return &quot;\n&quot;.join(t for t in texts if t)</code> | 结束当前函数并返回；把字符串片段按分隔符合并。 |

## 结合全项目：设计缺口与增强方向

- 工具调用、思考、图片等非文本块被忽略；这与 Agent 未实现工具循环一致，不能靠本函数获得 tool_use 能力。
- 若调用方传整个字符串而非内容块列表，会被按字符迭代后换行拼接；可增加输入规范检查。空文本现在也可能被 BaseAgent 计为成功。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
