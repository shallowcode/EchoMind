# core\intent_recognizer.py

## 输入输出流

用户消息、历史、实体与模型/Skills 依赖进入原核心组件；输出意图、Agent 路由、技能上下文或模型结果。

## 先理解设计

这部分是新版复用的原始核心。v2 在 ChatService 与 ToolAgent 中接入事务、权限与完整工具循环。

源码 SHA256：`ce3dfb4eef87ab7f84bec3d2ed8df1a1fa8ab959de57b044438a9636dd808d95`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L2**

```python
亮点：端到端意图识别
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
三路融合策略：
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
  1. LLM 语义理解（权重 70%）—— 主力，理解复杂语义和上下文
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L6**

```python
  2. Embedding 向量相似度（权重 20%）—— 快速匹配常见表达
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```python
  3. 关键词模式匹配（权重 10%）—— 零延迟兜底
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L9**

```python
三路结果通过加权投票合并，置信度低于阈值时降级为 OTHER。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L10**

```python
LLM 和 Embedding 并行调用，不串行等待。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L12**

```python
import asyncio
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L14**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L15**

```python
import logging
```

导入本段使用的标准库、依赖或项目组件。

**L16**

```python
import re
```

导入本段使用的标准库、依赖或项目组件。

**L17**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L18**

```python
from dataclasses import dataclass, field
```

导入本段使用的标准库、依赖或项目组件。

**L19**

```python
from enum import Enum
```

导入本段使用的标准库、依赖或项目组件。

**L20**

```python
from typing import Any, Dict, List, Optional
```

导入本段使用的标准库、依赖或项目组件。

**L22**

```python
from anthropic import AsyncAnthropic
```

导入本段使用的标准库、依赖或项目组件。

**L24**

```python
from core.llm_utils import extract_text_content
```

导入本段使用的标准库、依赖或项目组件。

**L26**

```python
logger = logging.getLogger(__name__)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
class IntentCategory(Enum):
```

定义一组状态和行为，或定义可校验的数据契约。

**L30**

```python
    QUERY      = "query"       # 查询信息
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L31**

```python
    COMPLAINT  = "complaint"   # 投诉不满
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L32**

```python
    REQUEST    = "request"     # 请求操作
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
    GREETING   = "greeting"    # 问候
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L34**

```python
    ESCALATION = "escalation"  # 要求升级/转人工
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L35**

```python
    TECHNICAL  = "technical"   # 技术问题
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
    BILLING    = "billing"     # 账单/退款
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
    ACCOUNT    = "account"     # 账户管理
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
    FEEDBACK   = "feedback"    # 正面反馈
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
    ORDER_STATUS = "order_status"        # 订单状态
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
    LOGISTICS = "logistics"              # 物流配送
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
    REFUND = "refund"                    # 退款/退货
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L42**

```python
    INVOICE = "invoice"                  # 发票
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L43**

```python
    PAYMENT_ISSUE = "payment_issue"      # 支付/扣款异常
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
    ACCOUNT_SECURITY = "account_security" # 账户安全
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L45**

```python
    TECHNICAL_LOGIN = "technical_login"  # 登录认证故障
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L46**

```python
    TECHNICAL_CRASH = "technical_crash"  # 崩溃/错误码
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L47**

```python
    HUMAN_HANDOFF = "human_handoff"      # 转人工
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L48**

```python
    OTHER      = "other"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L51**

```python
class UrgencyLevel(Enum):
```

定义一组状态和行为，或定义可校验的数据契约。

**L52**

```python
    LOW      = 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L53**

```python
    MEDIUM   = 2
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L54**

```python
    HIGH     = 3
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L55**

```python
    CRITICAL = 4
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L58**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L59**

```python
class IntentResult:
```

定义一组状态和行为，或定义可校验的数据契约。

**L60**

```python
    intent:     IntentCategory
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
    confidence: float
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
    urgency:    UrgencyLevel
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
    intent_group: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
    entities:   Dict[str, List[str]]   # 从消息中提取的实体
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
    reasoning:  str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
    latency_ms: float
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
    source_scores: Dict[str, float] = field(default_factory=dict)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L70**

```python
# ── Few-shot 模板（同时用于 LLM 示例和 Embedding 匹配）────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

**L71**

```python
_TEMPLATES: Dict[IntentCategory, List[str]] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
    IntentCategory.QUERY:      ["我的订单状态是什么？", "如何重置密码？", "快递什么时候到？"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
    IntentCategory.COMPLAINT:  ["等了好几个小时！", "服务太差了！", "一直没人处理！"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
    IntentCategory.REQUEST:    ["帮我取消订单", "我需要修改地址", "请协助退款"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
    IntentCategory.GREETING:   ["你好", "嗨，有人吗", "早上好"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
    IntentCategory.ESCALATION: ["我要投诉！", "转人工客服", "找你们经理"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
    IntentCategory.TECHNICAL:  ["应用一直崩溃", "无法登录", "出现500错误"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L78**

```python
    IntentCategory.BILLING:    ["为什么扣了两次款？", "申请退款", "发票问题"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
    IntentCategory.ACCOUNT:    ["修改邮箱", "注销账户", "更新个人信息"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
    IntentCategory.FEEDBACK:   ["服务很棒！", "非常满意", "给个好评"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
    IntentCategory.ORDER_STATUS: ["我的订单现在是什么状态？", "订单有没有发货？", "订单处理到哪一步了？"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
    IntentCategory.LOGISTICS: ["快递什么时候到？", "物流一直不更新", "配送要多久？"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
    IntentCategory.REFUND: ["我要申请退款", "退货退款怎么处理？", "退款多久到账？"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
    IntentCategory.INVOICE: ["帮我开发票", "发票抬头怎么改？", "电子发票在哪里？"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L85**

```python
    IntentCategory.PAYMENT_ISSUE: ["为什么重复扣款？", "支付失败怎么办？", "这个月多扣了钱"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
    IntentCategory.ACCOUNT_SECURITY: ["账户被盗了", "发现异常登录", "我要重置密码"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
    IntentCategory.TECHNICAL_LOGIN: ["登录一直报401", "验证码收不到", "无法登录账号"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
    IntentCategory.TECHNICAL_CRASH: ["应用一直崩溃", "页面报500错误", "系统闪退"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
    IntentCategory.HUMAN_HANDOFF: ["转人工客服", "我要找人工", "请升级处理"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L90**

```python
}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
_SPECIFIC_INTENTS = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L93**

```python
    IntentCategory.ORDER_STATUS,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
    IntentCategory.LOGISTICS,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
    IntentCategory.REFUND,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
    IntentCategory.INVOICE,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
    IntentCategory.PAYMENT_ISSUE,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
    IntentCategory.ACCOUNT_SECURITY,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
    IntentCategory.TECHNICAL_LOGIN,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L100**

```python
    IntentCategory.TECHNICAL_CRASH,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
    IntentCategory.HUMAN_HANDOFF,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L104**

```python
_GENERIC_INTENTS = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L105**

```python
    IntentCategory.QUERY,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
    IntentCategory.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L107**

```python
    IntentCategory.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L108**

```python
    IntentCategory.ACCOUNT,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
    IntentCategory.ESCALATION,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L110**

```python
}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
_INTENT_GROUPS: Dict[IntentCategory, IntentCategory] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L113**

```python
    IntentCategory.ORDER_STATUS: IntentCategory.QUERY,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
    IntentCategory.LOGISTICS: IntentCategory.QUERY,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
    IntentCategory.REFUND: IntentCategory.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
    IntentCategory.INVOICE: IntentCategory.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
    IntentCategory.PAYMENT_ISSUE: IntentCategory.BILLING,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
    IntentCategory.ACCOUNT_SECURITY: IntentCategory.ACCOUNT,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L119**

```python
    IntentCategory.TECHNICAL_LOGIN: IntentCategory.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
    IntentCategory.TECHNICAL_CRASH: IntentCategory.TECHNICAL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L121**

```python
    IntentCategory.HUMAN_HANDOFF: IntentCategory.ESCALATION,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L122**

```python
}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L124**

```python
# 紧急关键词
```

作者注释，说明约束或设计意图；本行不执行。

**L125**

```python
_URGENCY_KEYWORDS = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L126**

```python
    UrgencyLevel.CRITICAL: ["紧急", "emergency", "urgent", "asap", "立刻"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L127**

```python
    UrgencyLevel.HIGH:     ["今天", "马上", "尽快", "hurry", "now"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
    UrgencyLevel.MEDIUM:   ["这周", "soon", "快点"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L132 · _cosine

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L132**

```python
def _cosine(a: List[float], b: List[float]) -> float:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L133**

```python
    """纯 Python 余弦相似度，不依赖 numpy。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L134**

```python
    dot = sum(x * y for x, y in zip(a, b))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L135**

```python
    na  = sum(x * x for x in a) ** 0.5
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L136**

```python
    nb  = sum(x * x for x in b) ** 0.5
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L137**

```python
    return dot / (na * nb) if na and nb else 0.0
```

结束当前函数并把本行构造的结果交给调用方。

**L140**

```python
class IntentRecognizer:
```

定义一组状态和行为，或定义可校验的数据契约。

**L141**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L142**

```python
    端到端意图识别器。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L144**

```python
    初始化时不加载任何本地模型，所有 AI 能力通过 Anthropic API 调用。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L145**

```python
    模板 Embedding 在首次请求时懒加载并缓存，后续复用。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L146**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L148 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L148**

```python
    def __init__(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L149**

```python
        self,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L150**

```python
        api_key: str,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L151**

```python
        base_url: Optional[str] = None,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L152**

```python
        model: str = "claude-3-5-sonnet-20241022",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L153**

```python
        confidence_threshold: float = 0.5,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L154**

```python
        client: Any = None,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L155**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L156**

```python
        kwargs: Dict[str, Any] = {"api_key": api_key}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L157**

```python
        if base_url:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L158**

```python
            kwargs["base_url"] = base_url
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L159**

```python
        self.client    = client or AsyncAnthropic(**kwargs)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L160**

```python
        self.model     = model
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L161**

```python
        self.threshold = confidence_threshold
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L162**

```python
        # 第三方兼容 API（如 DeepSeek）通常不支持 Embedding，禁用该策略。
```

作者注释，说明约束或设计意图；本行不执行。

**L163**

```python
        # 官方 Anthropic SDK 当前没有 embeddings 资源，因此下面会使用稳定的
```

作者注释，说明约束或设计意图；本行不执行。

**L164**

```python
        # 本地字符 n-gram 向量作为轻量兜底，保证三路融合链路真实可跑。
```

作者注释，说明约束或设计意图；本行不执行。

**L165**

```python
        self._embedding_enabled = not bool(base_url)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L167**

```python
        self._tpl_embeddings: Dict[IntentCategory, List[List[float]]] = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L168**

```python
        self._cache: Dict[str, IntentResult] = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L169**

```python
        self.cache_hits   = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L170**

```python
        self.cache_misses = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L172**

```python
    # ── 公开接口 ──────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L174 · recognize

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L174**

```python
    async def recognize(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L175**

```python
        self,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L176**

```python
        message: str,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L177**

```python
        history: Optional[List[Dict[str, str]]] = None,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L178**

```python
    ) -> IntentResult:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L179**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L180**

```python
        识别用户意图。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L182**

```python
        history 格式：[{"role": "user"/"assistant", "content": "..."}]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L183**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L184**

```python
        key = self._cache_key(message, history)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L185**

```python
        if key in self._cache:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L186**

```python
            self.cache_hits += 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L187**

```python
            return self._cache[key]
```

结束当前函数并把本行构造的结果交给调用方。

**L188**

```python
        self.cache_misses += 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L190**

```python
        t0 = time.monotonic()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L192**

```python
        # LLM 和 Embedding 并行（Embedding 不可用时跳过）
```

作者注释，说明约束或设计意图；本行不执行。

**L193**

```python
        llm_task = asyncio.create_task(self._llm_recognize(message, history))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L194**

```python
        emb_task = asyncio.create_task(self._embedding_recognize(message)) if self._embedding_enabled else None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L195**

```python
        pat      = self._pattern_recognize(message)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L197**

```python
        if emb_task:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L198**

```python
            llm, emb = await asyncio.gather(llm_task, emb_task)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L199**

```python
        else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L200**

```python
            llm = await llm_task
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L201**

```python
            emb = {"intent": IntentCategory.OTHER, "confidence": 0.0}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L203**

```python
        intent, confidence, source_scores = self._vote(llm, emb, pat)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L204**

```python
        entities = self._extract_entities(message)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L205**

```python
        urgency  = self._urgency(message, intent)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L207**

```python
        result = IntentResult(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L208**

```python
            intent=intent,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L209**

```python
            confidence=confidence,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L210**

```python
            urgency=urgency,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L211**

```python
            intent_group=self._intent_group(intent),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L212**

```python
            entities=entities,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L213**

```python
            reasoning=llm.get("reasoning", ""),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L214**

```python
            latency_ms=(time.monotonic() - t0) * 1000,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L215**

```python
            source_scores=source_scores,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L216**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L218**

```python
        # LRU 缓存
```

作者注释，说明约束或设计意图；本行不执行。

**L219**

```python
        if len(self._cache) >= 1000:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L220**

```python
            for k in list(self._cache)[:500]:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L221**

```python
                del self._cache[k]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L222**

```python
        self._cache[key] = result
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L223**

```python
        return result
```

结束当前函数并把本行构造的结果交给调用方。

### L225 · learn

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L225**

```python
    def learn(self, message: str, correct: IntentCategory) -> None:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L226**

```python
        """在线学习：将纠正样本加入模板，清除对应 Embedding 缓存。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L227**

```python
        tpls = _TEMPLATES.setdefault(correct, [])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L228**

```python
        if message not in tpls:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L229**

```python
            tpls.append(message)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L230**

```python
            self._tpl_embeddings.pop(correct, None)  # 下次重新计算
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L231**

```python
            self._cache.clear()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L232**

```python
            logger.info(f"学习新样本 → {correct.value}: {message[:40]}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L234**

```python
    # ── 三路识别策略 ──────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L236 · _llm_recognize

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L236**

```python
    async def _llm_recognize(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L237**

```python
        self,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L238**

```python
        message: str,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L239**

```python
        history: Optional[List[Dict[str, str]]],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L240**

```python
    ) -> Dict[str, Any]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L241**

```python
        """策略 1：LLM 语义理解（Few-shot + 上下文）。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L242**

```python
        message = self._clean_text(message)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L243**

```python
        # 构建 Few-shot 示例
```

作者注释，说明约束或设计意图；本行不执行。

**L244**

```python
        examples = "\n".join(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L245**

```python
            f'  消息: "{t}" → 意图: {cat.value}'
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L246**

```python
            for cat, tpls in _TEMPLATES.items()
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L247**

```python
            for t in tpls[:1]  # 每类取 1 条，控制 prompt 长度
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L248**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L249**

```python
        # 最近 3 轮对话上下文
```

作者注释，说明约束或设计意图；本行不执行。

**L250**

```python
        ctx = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L251**

```python
        if history:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L252**

```python
            ctx = "\n最近对话:\n" + "\n".join(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L253**

```python
                f"  {self._clean_text(m.get('role', 'user'))}: {self._clean_text(m.get('content', ''))}"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L254**

```python
                for m in history[-3:]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L255**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L257**

```python
        prompt = f"""你是客服意图分析专家。根据示例判断用户意图，返回 JSON。
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L258**

```python
如果用户问题能匹配细粒度业务意图，请优先返回细粒度意图，而不是宽泛大类。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L259**

```python
例如退款优先返回 refund，发票优先返回 invoice，登录故障优先返回 technical_login。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L261**

```python
示例:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L262**

```python
{examples}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L264**

```python
{ctx}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L265**

```python
用户消息: "{message}"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L267**

```python
返回格式（仅 JSON，不要其他文字）:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L268**

```python
{{"intent": "<意图值>", "confidence": <0-1>, "reasoning": "<一句话说明>"}}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L270**

```python
可选意图: {", ".join(c.value for c in IntentCategory)}"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L271**

```python
        prompt = self._clean_text(prompt)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L273**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L274**

```python
            resp = await self.client.messages.create(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L275**

```python
                model=self.model,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L276**

```python
                max_tokens=256,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L277**

```python
                temperature=0.1,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L278**

```python
                messages=[{"role": "user", "content": prompt}],
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L279**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L280**

```python
            raw = extract_text_content(resp.content)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L281**

```python
            s, e = raw.find("{"), raw.rfind("}") + 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L282**

```python
            data = json.loads(raw[s:e])
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L283**

```python
            try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L284**

```python
                data["intent"] = IntentCategory(data["intent"])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L285**

```python
            except ValueError:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L286**

```python
                data["intent"] = IntentCategory.OTHER
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L287**

```python
            return data
```

结束当前函数并把本行构造的结果交给调用方。

**L288**

```python
        except Exception as ex:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L289**

```python
            logger.warning(f"LLM 识别失败: {ex}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L290**

```python
            return {"intent": IntentCategory.OTHER, "confidence": 0.0, "reasoning": "LLM 失败", "failed": True}
```

结束当前函数并把本行构造的结果交给调用方。

### L292 · _embedding_recognize

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L292**

```python
    async def _embedding_recognize(self, message: str) -> Dict[str, Any]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L293**

```python
        """策略 2：Embedding 向量相似度匹配。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L294**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L295**

```python
            await self._load_template_embeddings()
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L296**

```python
            msg_vec = await self._embed_text(message)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L298**

```python
            best_cat, best_score = IntentCategory.OTHER, 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L299**

```python
            for cat, vecs in self._tpl_embeddings.items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L300**

```python
                score = max(_cosine(msg_vec, v) for v in vecs)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L301**

```python
                if score > best_score:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L302**

```python
                    best_score, best_cat = score, cat
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L304**

```python
            return {"intent": best_cat, "confidence": best_score}
```

结束当前函数并把本行构造的结果交给调用方。

**L305**

```python
        except Exception as ex:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L306**

```python
            logger.warning(f"Embedding 识别失败: {ex}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L307**

```python
            return {"intent": IntentCategory.OTHER, "confidence": 0.0}
```

结束当前函数并把本行构造的结果交给调用方。

### L309 · _pattern_recognize

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L309**

```python
    def _pattern_recognize(self, message: str) -> Dict[str, Any]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L310**

```python
        """策略 3：关键词模式匹配（同步，零延迟兜底）。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L311**

```python
        msg = message.lower()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L312**

```python
        specific_patterns = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L313**

```python
            IntentCategory.HUMAN_HANDOFF: ["转人工", "人工客服", "找人工"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L314**

```python
            IntentCategory.ORDER_STATUS: ["订单状态", "发货了吗", "处理到哪", "order status"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L315**

```python
            IntentCategory.LOGISTICS: ["物流", "快递", "配送", "运单", "delivery", "shipping"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L316**

```python
            IntentCategory.REFUND: ["退款", "退货", "refund", "return"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L317**

```python
            IntentCategory.INVOICE: ["发票", "抬头", "税号", "invoice"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L318**

```python
            IntentCategory.PAYMENT_ISSUE: ["重复扣款", "多扣", "支付失败", "扣费", "payment failed"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L319**

```python
            IntentCategory.ACCOUNT_SECURITY: ["被盗", "异常登录", "重置密码", "两步验证", "安全"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L320**

```python
            IntentCategory.TECHNICAL_LOGIN: ["无法登录", "登录失败", "401", "验证码"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L321**

```python
            IntentCategory.TECHNICAL_CRASH: ["崩溃", "闪退", "500", "报错", "crash"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L322**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L323**

```python
        generic_patterns = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L324**

```python
            IntentCategory.ESCALATION: ["投诉", "经理", "supervisor"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L325**

```python
            IntentCategory.COMPLAINT:  ["太差", "糟糕", "horrible", "等了很久"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L326**

```python
            IntentCategory.QUERY:      ["?", "？", "怎么", "什么", "status"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L327**

```python
            IntentCategory.REQUEST:    ["帮我", "需要", "please", "help"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L328**

```python
            IntentCategory.GREETING:   ["你好", "嗨", "hello", "hi"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L329**

```python
            IntentCategory.BILLING:    ["退款", "扣款", "发票", "refund"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L330**

```python
            IntentCategory.TECHNICAL:  ["崩溃", "报错", "error", "crash"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L331**

```python
            IntentCategory.ACCOUNT:    ["密码", "邮箱", "账户", "password"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L332**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L334**

```python
        best_cat, best_score = self._best_pattern_match(msg, specific_patterns)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L335**

```python
        if best_cat != IntentCategory.OTHER:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L336**

```python
            return {"intent": best_cat, "confidence": best_score}
```

结束当前函数并把本行构造的结果交给调用方。

**L338**

```python
        best_cat, best_score = self._best_pattern_match(msg, generic_patterns)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L339**

```python
        return {"intent": best_cat, "confidence": best_score}
```

结束当前函数并把本行构造的结果交给调用方。

**L341**

```python
    # ── 投票合并 ──────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L343 · _vote

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L343**

```python
    def _vote(self, llm: Dict, emb: Dict, pat: Dict) -> tuple[IntentCategory, float, Dict[str, float]]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L344**

```python
        """加权投票。返回最终意图、融合置信度和各路来源得分。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L345**

```python
        source_scores = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L346**

```python
            "llm": float(llm.get("confidence", 0.0) or 0.0),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L347**

```python
            "embedding": float(emb.get("confidence", 0.0) or 0.0),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L348**

```python
            "pattern": float(pat.get("confidence", 0.0) or 0.0),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L349**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L350**

```python
        if llm.get("failed"):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L351**

```python
            if emb.get("intent") != IntentCategory.OTHER and emb.get("confidence", 0.0) > 0:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L352**

```python
                return emb["intent"], source_scores["embedding"], source_scores
```

结束当前函数并把本行构造的结果交给调用方。

**L353**

```python
            if pat.get("intent") != IntentCategory.OTHER and pat.get("confidence", 0.0) > 0:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L354**

```python
                return pat["intent"], source_scores["pattern"], source_scores
```

结束当前函数并把本行构造的结果交给调用方。

**L355**

```python
            return IntentCategory.OTHER, 0.0, source_scores
```

结束当前函数并把本行构造的结果交给调用方。

**L357**

```python
        if self._embedding_enabled:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L358**

```python
            weights = [(llm, 0.7), (emb, 0.2), (pat, 0.1)]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L359**

```python
        else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L360**

```python
            weights = [(llm, 0.85), (pat, 0.15)]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L361**

```python
        scores: Dict[IntentCategory, float] = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L362**

```python
        for result, w in weights:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L363**

```python
            cat  = result.get("intent", IntentCategory.OTHER)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L364**

```python
            conf = result.get("confidence", 0.0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L365**

```python
            scores[cat] = scores.get(cat, 0.0) + w * conf
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L367**

```python
        best = max(scores, key=scores.get)  # type: ignore
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L368**

```python
        best_score = scores[best]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L369**

```python
        pat_intent = pat.get("intent", IntentCategory.OTHER)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L370**

```python
        pat_conf = float(pat.get("confidence", 0.0) or 0.0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L371**

```python
        if best in _GENERIC_INTENTS and pat_intent in _SPECIFIC_INTENTS and _INTENT_GROUPS.get(pat_intent)==best and pat_conf >= 0.5 and best_score < 0.8:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L372**

```python
            source_scores["refined_by_pattern"] = pat_conf
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L373**

```python
            return pat_intent, max(best_score, pat_conf), source_scores
```

结束当前函数并把本行构造的结果交给调用方。

**L374**

```python
        if best_score < self.threshold:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L375**

```python
            return IntentCategory.OTHER, best_score, source_scores
```

结束当前函数并把本行构造的结果交给调用方。

**L376**

```python
        return best, best_score, source_scores
```

结束当前函数并把本行构造的结果交给调用方。

**L378**

```python
    # ── 实体提取 ──────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L380 · _extract_entities

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L380**

```python
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L381**

```python
        """用规则提取高价值实体，避免每次识别都额外调用 LLM。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L382**

```python
        message = self._clean_text(message)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L383**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L384**

```python
            "order_id": self._unique(re.findall(r"(?:订单(?:编号|号)?(?:是)?|order(?:_id)?|#)\s*[:：#]?\s*([A-Za-z0-9_-]{4,32})", message, re.I)+re.findall(r'\bORD\d{3,20}\b',message,re.I)),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L385**

```python
            "product": [],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L386**

```python
            "date": self._unique(re.findall(r"(今天|明天|昨天|本周|这周|下周|\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2}日?)", message)),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L387**

```python
            "amount": self._unique(re.findall(r"((?:¥|￥)\s*\d+(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?\s*(?:元|块|rmb|cny|usd|美元))", message, re.I)),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L388**

```python
            "error_code": self._unique(re.findall(r"(?<![A-Za-z0-9])([45]\d{2}|ERR[A-Z0-9_-]{1,13})(?![A-Za-z0-9])", message)),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L389**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L391**

```python
    # ── 辅助 ──────────────────────────────────────────────────────────────────
```

作者注释，说明约束或设计意图；本行不执行。

### L393 · _load_template_embeddings

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L393**

```python
    async def _load_template_embeddings(self) -> None:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L394**

```python
        """懒加载所有模板的 Embedding（只在首次调用时执行）。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L395**

```python
        missing = [cat for cat in _TEMPLATES if cat not in self._tpl_embeddings]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L396**

```python
        if not missing:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L397**

```python
            return
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L399**

```python
        all_texts = [t for cat in missing for t in _TEMPLATES[cat]]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L400**

```python
        vecs = [await self._embed_text(text) for text in all_texts]
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L401**

```python
        idx = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L402**

```python
        for cat in missing:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L403**

```python
            n = len(_TEMPLATES[cat])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L404**

```python
            self._tpl_embeddings[cat] = vecs[idx: idx + n]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L405**

```python
            idx += n
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L407 · _embed_text

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L407**

```python
    async def _embed_text(self, text: str) -> List[float]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L408**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L409**

```python
        生成文本向量。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L411**

```python
        如果未来接入的官方/兼容客户端提供 embeddings.create，会优先使用远端向量；
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L412**

```python
        当前 Anthropic SDK 没有该资源时，退化为字符 n-gram 哈希向量。这样不会因为
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L413**

```python
        Embedding 服务缺失导致三路融合中断。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L414**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L415**

```python
        embeddings = getattr(self.client, "embeddings", None)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L416**

```python
        if embeddings is not None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L417**

```python
            try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L418**

```python
                resp = await embeddings.create(model="voyage-3-lite", input=[text])
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L419**

```python
                return list(resp.data[0].embedding)
```

结束当前函数并把本行构造的结果交给调用方。

**L420**

```python
            except Exception as ex:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L421**

```python
                logger.warning(f"远端 Embedding 失败，使用本地向量兜底: {ex}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L423**

```python
        return self._local_embedding(text)
```

结束当前函数并把本行构造的结果交给调用方。

**L425**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L426 · _local_embedding

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L426**

```python
    def _local_embedding(text: str, dims: int = 256) -> List[float]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L427**

```python
        """稳定的字符 n-gram 哈希向量，用于无远端 Embedding 时的语义近似匹配。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L428**

```python
        normalized = text.lower().strip()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L429**

```python
        vec = [0.0] * dims
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L430**

```python
        tokens = set()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L431**

```python
        for n in (1, 2, 3):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L432**

```python
            if len(normalized) >= n:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L433**

```python
                tokens.update(normalized[i:i + n] for i in range(len(normalized) - n + 1))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L434**

```python
        if not tokens:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L435**

```python
            tokens.add(normalized)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L437**

```python
        for token in tokens:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L438**

```python
            digest = hashlib.md5(token.encode("utf-8")).digest()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L439**

```python
            idx = int.from_bytes(digest[:4], "big") % dims
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L440**

```python
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L441**

```python
            vec[idx] += sign
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L442**

```python
        return vec
```

结束当前函数并把本行构造的结果交给调用方。

### L444 · _urgency

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L444**

```python
    def _urgency(self, message: str, intent: IntentCategory) -> UrgencyLevel:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L445**

```python
        msg = message.lower()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L446**

```python
        for level, kws in _URGENCY_KEYWORDS.items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L447**

```python
            if any(kw in msg for kw in kws):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L448**

```python
                return level
```

结束当前函数并把本行构造的结果交给调用方。

**L449**

```python
        if intent in (IntentCategory.ESCALATION, IntentCategory.HUMAN_HANDOFF):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L450**

```python
            return UrgencyLevel.HIGH
```

结束当前函数并把本行构造的结果交给调用方。

**L451**

```python
        if intent == IntentCategory.COMPLAINT:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L452**

```python
            return UrgencyLevel.MEDIUM
```

结束当前函数并把本行构造的结果交给调用方。

**L453**

```python
        return UrgencyLevel.LOW
```

结束当前函数并把本行构造的结果交给调用方。

### L455 · _cache_key

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L455**

```python
    def _cache_key(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L456**

```python
        payload = {"message": self._clean_text(message)}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L457**

```python
        if history:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L458**

```python
            payload["history"] = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L459**

```python
                {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L460**

```python
                    "role": self._clean_text(item.get("role", ""))[:20],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L461**

```python
                    "content": self._clean_text(item.get("content", "")),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L462**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L463**

```python
                for item in history
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L464**

```python
            ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L465**

```python
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L466**

```python
        return hashlib.md5(raw.encode("utf-8")).hexdigest()
```

结束当前函数并把本行构造的结果交给调用方。

**L468**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L469 · _unique

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L469**

```python
    def _unique(values: List[str]) -> List[str]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L470**

```python
        return list(dict.fromkeys(value.strip() for value in values if value and value.strip()))
```

结束当前函数并把本行构造的结果交给调用方。

**L472**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L473 · _best_pattern_match

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L473**

```python
    def _best_pattern_match(
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L474**

```python
        message: str,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L475**

```python
        patterns: Dict[IntentCategory, List[str]],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L476**

```python
    ) -> tuple[IntentCategory, float]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L477**

```python
        best_cat, best_score = IntentCategory.OTHER, 0.0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L478**

```python
        for cat, kws in patterns.items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L479**

```python
            hits = sum(1 for kw in kws if kw in message)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L480**

```python
            if not hits:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L481**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L482**

```python
            # 单个明确业务关键词就给可用置信度；多个关键词命中时提高置信度。
```

作者注释，说明约束或设计意图；本行不执行。

**L483**

```python
            score = min(1.0, 0.5 + 0.25 * (hits - 1))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L484**

```python
            if score > best_score:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L485**

```python
                best_score, best_cat = score, cat
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L486**

```python
        return best_cat, best_score
```

结束当前函数并把本行构造的结果交给调用方。

**L488**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L489 · _intent_group

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L489**

```python
    def _intent_group(intent: IntentCategory) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L490**

```python
        return _INTENT_GROUPS.get(intent, intent).value
```

结束当前函数并把本行构造的结果交给调用方。

**L492**

```python
    @staticmethod
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L493 · _clean_text

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L493**

```python
    def _clean_text(value: Any) -> str:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L494**

```python
        """移除 Unicode 代理字符，避免 HTTP 客户端编码 prompt 时崩溃。"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L495**

```python
        if value is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L496**

```python
            return ""
```

结束当前函数并把本行构造的结果交给调用方。

**L497**

```python
        if not isinstance(value, str):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L498**

```python
            value = str(value)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L499**

```python
        return value.encode("utf-8", errors="ignore").decode("utf-8")
```

结束当前函数并把本行构造的结果交给调用方。

**L501**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L502 · cache_stats

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L502**

```python
    def cache_stats(self) -> Dict[str, Any]:
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L503**

```python
        total = self.cache_hits + self.cache_misses
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L504**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L505**

```python
            "size": len(self._cache),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L506**

```python
            "hits": self.cache_hits,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L507**

```python
            "misses": self.cache_misses,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L508**

```python
            "hit_rate": self.cache_hits / total if total else 0.0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L509**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

单独运行旧编排方法与新版 HTTP 链路不同；置信度校准、真正多实例调度和路由消融仍需验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
