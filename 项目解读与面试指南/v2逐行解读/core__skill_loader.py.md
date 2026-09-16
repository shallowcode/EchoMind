# core\skill_loader.py

## 输入输出流

用户消息、历史、实体与模型/Skills 依赖进入原核心组件；输出意图、Agent 路由、技能上下文或模型结果。

## 先理解设计

这部分是新版复用的原始核心。v2 在 ChatService 与 ToolAgent 中接入事务、权限与完整工具循环。

源码 SHA256：`5eda757f964705e9e2e91ce73b0d9ceb6dc06c5dabaa4e306d6cb0186f4b5d24`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L2**

```python
EchoMind Skill 加载器。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
Skill 是一段可热加载的业务能力说明，用来补充 Agent 的 system prompt。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
它适合放置企业话术、处理流程、合规边界、排障 SOP 等需要运营侧快速调整的规则。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L6**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
import logging
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from dataclasses import dataclass, field
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
from typing import Any, Dict, Iterable, List, Optional
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
logger = logging.getLogger(__name__)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L16**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L17**

```python
class Skill:
```

定义一组状态和行为，或定义可校验的数据契约。

**L18**

```python
    """单个 Skill 的标准化表示，屏蔽 Markdown/JSON 等不同文件格式差异。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L19**

```python
    name: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
    description: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
    content: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L22**

```python
    path: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L23**

```python
    keywords: List[str] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
    agents: List[str] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
    enabled: bool = True
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L27 · matches

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L27**

```python
    def matches(self, message: str, agent_type: Optional[str] = None) -> bool:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L28**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```python
        判断当前请求是否应该注入这个 Skill。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
        - agents 为空：适用于所有 Agent；否则只匹配指定 Agent。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
        - keywords 为空：作为全局 Skill 注入；否则只有命中关键词才注入。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
        if not self.enabled:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L35**

```python
            return False
```

结束当前函数并把本行构造的结果交给调用方。

**L37**

```python
        if self.agents and agent_type and agent_type.lower() not in self.agents:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L38**

```python
            return False
```

结束当前函数并把本行构造的结果交给调用方。

**L40**

```python
        if not self.keywords:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L41**

```python
            return True
```

结束当前函数并把本行构造的结果交给调用方。

**L43**

```python
        lowered = (message or "").lower()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
        return any(keyword.lower() in lowered for keyword in self.keywords)
```

结束当前函数并把本行构造的结果交给调用方。

### L46 · to_prompt_block

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L46**

```python
    def to_prompt_block(self, max_chars: int = 3200) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L47**

```python
        """格式化为可直接拼入 system prompt 的文本块，并限制单个 Skill 长度。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
        body = self.content.strip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L49**

```python
        if len(body) > max_chars:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L50**

```python
            body = body[:max_chars].rstrip() + "\n..."
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L51**

```python
        description = f"\n说明: {self.description}" if self.description else ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L52**

```python
        return f"### {self.name}{description}\n{body}"
```

结束当前函数并把本行构造的结果交给调用方。

### L54 · to_summary

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L54**

```python
    def to_summary(self) -> Dict[str, Any]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L55**

```python
        """返回 API 可序列化摘要，避免把完整长文本默认暴露给健康检查。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L56**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L57**

```python
            "name": self.name,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
            "description": self.description,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
            "path": self.path,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
            "keywords": self.keywords,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
            "agents": self.agents,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
            "enabled": self.enabled,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
            "content_chars": len(self.content),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
class SkillManager:
```

定义一组状态和行为，或定义可校验的数据契约。

**L68**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
    从目录中发现、解析并管理 Skills。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L71**

```python
    支持两种常用结构：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
      1. skills/refund/SKILL.md
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
      2. skills/refund.json / skills/refund.md / skills/refund.txt
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
    SUPPORTED_SUFFIXES = {".md", ".txt", ".json"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L78 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L78**

```python
    def __init__(self, root_dir: str, max_prompt_chars: int = 5000):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L79**

```python
        self.root_dir = Path(root_dir).expanduser().resolve()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L80**

```python
        self.max_prompt_chars = max_prompt_chars
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L81**

```python
        self._skills: List[Skill] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L82**

```python
        self._errors: List[str] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L85 · skills

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L85**

```python
    def skills(self) -> List[Skill]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L86**

```python
        return list(self._skills)
```

结束当前函数并把本行构造的结果交给调用方。

**L88**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L89 · errors

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L89**

```python
    def errors(self) -> List[str]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L90**

```python
        return list(self._errors)
```

结束当前函数并把本行构造的结果交给调用方。

### L92 · load

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L92**

```python
    def load(self) -> List[Skill]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L93**

```python
        """重新扫描目录并加载 Skills；单个文件失败不会影响其他 Skill 生效。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
        loaded: List[Skill] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L95**

```python
        errors: List[str] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L97**

```python
        if not self.root_dir.exists():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L98**

```python
            logger.info(f"Skill 目录不存在，跳过加载: {self.root_dir}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
            self._skills = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L100**

```python
            self._errors = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L101**

```python
            return []
```

结束当前函数并把本行构造的结果交给调用方。

**L103**

```python
        for path in self._discover_files(self.root_dir):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L104**

```python
            try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L105**

```python
                skill = self._load_file(path)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L106**

```python
                if skill is not None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L107**

```python
                    loaded.append(skill)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L108**

```python
            except Exception as ex:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L109**

```python
                msg = f"{path}: {ex}"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L110**

```python
                errors.append(msg)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L111**

```python
                logger.warning(f"Skill 加载失败: {msg}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
        self._skills = loaded
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L114**

```python
        self._errors = errors
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L115**

```python
        self._log_loaded_skills()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
        return self.skills
```

结束当前函数并把本行构造的结果交给调用方。

### L118 · reload

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L118**

```python
    def reload(self) -> List[Skill]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L119**

```python
        """运行时热加载入口，供 API 调用。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
        return self.load()
```

结束当前函数并把本行构造的结果交给调用方。

### L122 · prompt_for

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L122**

```python
    def prompt_for(self, message: str, agent_type: Optional[str] = None) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L123**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L124**

```python
        为当前用户请求构建 Skill prompt。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L126**

```python
        只注入匹配的 Skill，并按总长度截断，避免挤占主对话上下文。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L127**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
        blocks: List[str] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L129**

```python
        matched: List[tuple[Skill, List[str]]] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L130**

```python
        remaining = self.max_prompt_chars
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L131**

```python
        lowered_message = (message or "").lower()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L133**

```python
        for skill in self._skills:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L134**

```python
            if not skill.matches(message, agent_type):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L135**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L136**

```python
            matched_keywords = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L137**

```python
                keyword for keyword in skill.keywords
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L138**

```python
                if keyword.lower() in lowered_message
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L139**

```python
            ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
            block = skill.to_prompt_block()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L141**

```python
            if len(block) > remaining:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L142**

```python
                block = block[:remaining].rstrip() + "\n..."
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L143**

```python
            blocks.append(block)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L144**

```python
            matched.append((skill, matched_keywords))
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L145**

```python
            remaining -= len(block)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L146**

```python
            if remaining <= 0:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L147**

```python
                break
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L149**

```python
        if not blocks:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L150**

```python
            logger.debug(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L151**

```python
                "Skills 未命中: agent=%s message=%r",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L152**

```python
                agent_type or "all",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L153**

```python
                (message or "")[:80],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L154**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L155**

```python
            return ""
```

结束当前函数并把本行构造的结果交给调用方。

**L157**

```python
        detail = "; ".join(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L158**

```python
            f"{skill.name}(keywords={', '.join(keywords) if keywords else 'all'})"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L159**

```python
            for skill, keywords in matched
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L160**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L161**

```python
        logger.info(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L162**

```python
            "Skills 已注入: agent=%s matched=%s message=%r",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L163**

```python
            agent_type or "all",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L164**

```python
            detail,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L165**

```python
            (message or "")[:80],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L166**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L168**

```python
        return (
```

结束当前函数并把本行构造的结果交给调用方。

**L169**

```python
            "以下是当前请求可用的 EchoMind Skills。"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L170**

```python
            "请优先遵循这些业务规则；如果与系统角色冲突，以系统角色和安全边界为准。\n\n"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L171**

```python
            + "\n\n".join(blocks)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L172**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L174 · summary

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L174**

```python
    def summary(self) -> Dict[str, Any]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L175**

```python
        """返回 Skill 管理器状态，用于 /skills 接口和排障。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L176**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L177**

```python
            "root_dir": str(self.root_dir),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L178**

```python
            "count": len(self._skills),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L179**

```python
            "skills": [skill.to_summary() for skill in self._skills],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L180**

```python
            "errors": self.errors,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L181**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L183 · _log_loaded_skills

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L183**

```python
    def _log_loaded_skills(self) -> None:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L184**

```python
        """在控制台输出醒目的 Skill 加载结果，方便启动和热加载时确认生效状态。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L185**

```python
        lines = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L186**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L187**

```python
            "================ EchoMind Skills Loaded ================",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L188**

```python
            f"目录: {self.root_dir}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L189**

```python
            f"数量: {len(self._skills)}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L190**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L192**

```python
        if self._skills:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L193**

```python
            for index, skill in enumerate(self._skills, start=1):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L194**

```python
                agents = ", ".join(skill.agents) if skill.agents else "all"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L195**

```python
                keywords = ", ".join(skill.keywords[:8]) if skill.keywords else "all"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L196**

```python
                if len(skill.keywords) > 8:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L197**

```python
                    keywords += ", ..."
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L198**

```python
                lines.extend([
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L199**

```python
                    f"{index}. {skill.name}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L200**

```python
                    f"   agents: {agents}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L201**

```python
                    f"   keywords: {keywords}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L202**

```python
                    f"   path: {skill.path}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L203**

```python
                ])
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L204**

```python
        else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L205**

```python
            lines.append("未加载任何 Skill。")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L207**

```python
        if self._errors:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L208**

```python
            lines.append("解析错误:")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L209**

```python
            lines.extend(f"  - {error}" for error in self._errors)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L211**

```python
        lines.append("========================================================")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L212**

```python
        logger.info("\n".join(lines))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L214 · _discover_files

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L214**

```python
    def _discover_files(self, root_dir: Path) -> Iterable[Path]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L215**

```python
        """发现可加载文件，优先读取目录规范文件 SKILL.md。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L216**

```python
        skill_md_files = sorted(root_dir.rglob("SKILL.md"))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L217**

```python
        yielded = {path.resolve() for path in skill_md_files}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L218**

```python
        for path in skill_md_files:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L219**

```python
            yield path
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L221**

```python
        for path in sorted(root_dir.rglob("*")):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L222**

```python
            resolved = path.resolve()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L223**

```python
            if resolved in yielded or not path.is_file():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L224**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L225**

```python
            if path.name.startswith(".") or path.name.upper() == "README.MD":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L226**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L227**

```python
            if path.suffix.lower() in self.SUPPORTED_SUFFIXES:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L228**

```python
                yield path
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L230 · _load_file

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L230**

```python
    def _load_file(self, path: Path) -> Optional[Skill]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L231**

```python
        if path.suffix.lower() == ".json":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L232**

```python
            return self._load_json(path)
```

结束当前函数并把本行构造的结果交给调用方。

**L233**

```python
        return self._load_text(path)
```

结束当前函数并把本行构造的结果交给调用方。

### L235 · _load_json

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L235**

```python
    def _load_json(self, path: Path) -> Optional[Skill]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L236**

```python
        raw = json.loads(path.read_text(encoding="utf-8"))
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L237**

```python
        if not isinstance(raw, dict):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L238**

```python
            raise ValueError("JSON Skill 必须是对象格式")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L240**

```python
        content = str(raw.get("content") or raw.get("instructions") or "").strip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L241**

```python
        if not content:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L242**

```python
            raise ValueError("缺少 content 或 instructions")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L244**

```python
        return Skill(
```

结束当前函数并把本行构造的结果交给调用方。

**L245**

```python
            name=str(raw.get("name") or path.stem),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L246**

```python
            description=str(raw.get("description") or ""),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L247**

```python
            content=content,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L248**

```python
            path=str(path),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L249**

```python
            keywords=self._as_list(raw.get("keywords")),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L250**

```python
            agents=[item.lower() for item in self._as_list(raw.get("agents"))],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L251**

```python
            enabled=self._as_bool(raw.get("enabled"), default=True),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L252**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L254 · _load_text

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L254**

```python
    def _load_text(self, path: Path) -> Optional[Skill]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L255**

```python
        raw = path.read_text(encoding="utf-8")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L256**

```python
        meta, body = self._split_front_matter(raw)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L257**

```python
        body = body.strip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L258**

```python
        if not body:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L259**

```python
            return None
```

结束当前函数并把本行构造的结果交给调用方。

**L261**

```python
        default_name = path.parent.name if path.name == "SKILL.md" else path.stem
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L262**

```python
        name = str(meta.get("name") or self._first_heading(body) or default_name)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L264**

```python
        # 如果首行标题只是 Skill 名称，注入 prompt 时去掉它，减少重复噪音。
```

作者注释，说明约束或设计意图；本行不执行。

**L265**

```python
        body = self._strip_first_heading(body, name)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L267**

```python
        return Skill(
```

结束当前函数并把本行构造的结果交给调用方。

**L268**

```python
            name=name,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L269**

```python
            description=str(meta.get("description") or ""),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L270**

```python
            content=body,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L271**

```python
            path=str(path),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L272**

```python
            keywords=self._as_list(meta.get("keywords")),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L273**

```python
            agents=[item.lower() for item in self._as_list(meta.get("agents"))],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L274**

```python
            enabled=self._as_bool(meta.get("enabled"), default=True),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L275**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L277 · _split_front_matter

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L277**

```python
    def _split_front_matter(self, raw: str) -> tuple[Dict[str, Any], str]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L278**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L279**

```python
        解析 Markdown 顶部的简单 front matter。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L281**

```python
        这里刻意不用 PyYAML，避免为一个轻量配置格式新增运行时依赖。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L282**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L283**

```python
        text = raw.lstrip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L284**

```python
        if not text.startswith("---"):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L285**

```python
            return {}, raw
```

结束当前函数并把本行构造的结果交给调用方。

**L287**

```python
        lines = text.splitlines()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L288**

```python
        if not lines or lines[0].strip() != "---":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L289**

```python
            return {}, raw
```

结束当前函数并把本行构造的结果交给调用方。

**L291**

```python
        meta: Dict[str, Any] = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L292**

```python
        end_idx: Optional[int] = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L293**

```python
        for idx, line in enumerate(lines[1:], start=1):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L294**

```python
            if line.strip() == "---":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L295**

```python
                end_idx = idx
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L296**

```python
                break
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L297**

```python
            if ":" not in line:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L298**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L299**

```python
            key, value = line.split(":", 1)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L300**

```python
            meta[key.strip()] = value.strip().strip("\"'")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L302**

```python
        if end_idx is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L303**

```python
            return {}, raw
```

结束当前函数并把本行构造的结果交给调用方。

**L304**

```python
        return meta, "\n".join(lines[end_idx + 1:])
```

结束当前函数并把本行构造的结果交给调用方。

**L306**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L307 · _first_heading

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L307**

```python
    def _first_heading(body: str) -> Optional[str]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L308**

```python
        for line in body.splitlines():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L309**

```python
            stripped = line.strip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L310**

```python
            if stripped.startswith("#"):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L311**

```python
                return stripped.lstrip("#").strip() or None
```

结束当前函数并把本行构造的结果交给调用方。

**L312**

```python
        return None
```

结束当前函数并把本行构造的结果交给调用方。

**L314**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L315 · _strip_first_heading

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L315**

```python
    def _strip_first_heading(body: str, name: str) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L316**

```python
        lines = body.splitlines()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L317**

```python
        if not lines:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L318**

```python
            return body
```

结束当前函数并把本行构造的结果交给调用方。

**L319**

```python
        first = lines[0].strip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L320**

```python
        if first.startswith("#") and first.lstrip("#").strip() == name:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L321**

```python
            return "\n".join(lines[1:]).strip()
```

结束当前函数并把本行构造的结果交给调用方。

**L322**

```python
        return body
```

结束当前函数并把本行构造的结果交给调用方。

**L324**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L325 · _as_list

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L325**

```python
    def _as_list(value: Any) -> List[str]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L326**

```python
        if value is None or value == "":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L327**

```python
            return []
```

结束当前函数并把本行构造的结果交给调用方。

**L328**

```python
        if isinstance(value, list):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L329**

```python
            return [str(item).strip() for item in value if str(item).strip()]
```

结束当前函数并把本行构造的结果交给调用方。

**L330**

```python
        return [item.strip() for item in str(value).replace('，', ',').replace('、', ',').split(",") if item.strip()]
```

结束当前函数并把本行构造的结果交给调用方。

**L332**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L333 · _as_bool

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L333**

```python
    def _as_bool(value: Any, default: bool = False) -> bool:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L334**

```python
        if value is None or value == "":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L335**

```python
            return default
```

结束当前函数并把本行构造的结果交给调用方。

**L336**

```python
        if isinstance(value, bool):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L337**

```python
            return value
```

结束当前函数并把本行构造的结果交给调用方。

**L338**

```python
        return str(value).strip().lower() not in {"0", "false", "no", "off", "disabled"}
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

单独运行旧编排方法与新版 HTTP 链路不同；置信度校准、真正多实例调度和路由消融仍需验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
