# core\llm_utils.py

## 输入输出流

用户消息、历史、实体与模型/Skills 依赖进入原核心组件；输出意图、Agent 路由、技能上下文或模型结果。

## 先理解设计

这部分是新版复用的原始核心。v2 在 ChatService 与 ToolAgent 中接入事务、权限与完整工具循环。

源码 SHA256：`b0bf4cc194787b059a02c2049a773dceb1ff92df95f5d7d7bdc492ba355e93e7`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""LLM response helpers shared by Anthropic-compatible providers."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L2**

```python
from typing import Any, Iterable, List
```

导入本段使用的标准库、依赖或项目组件。

### L5 · extract_text_content

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L5**

```python
def extract_text_content(content: Iterable[Any]) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L6**

```python
    """Return text blocks from Anthropic-style response content."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```python
    texts: List[str] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L8**

```python
    for block in content or []:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L9**

```python
        if isinstance(block, str):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L10**

```python
            texts.append(block)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L11**

```python
            continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```python
        block_type = getattr(block, "type", None)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L14**

```python
        text = getattr(block, "text", None)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```python
        if isinstance(block, dict):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L16**

```python
            block_type = block.get("type", block_type)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L17**

```python
            text = block.get("text", text)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
        if isinstance(text, str) and (block_type in (None, "text")):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L20**

```python
            texts.append(text)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L22**

```python
    return "\n".join(t for t in texts if t)
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

单独运行旧编排方法与新版 HTTP 链路不同；置信度校准、真正多实例调度和路由消融仍需验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
