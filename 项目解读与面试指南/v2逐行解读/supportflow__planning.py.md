# supportflow\planning.py

## 输入输出流

原始用户消息、已提取实体和退款授权标志进入规则规划器；输出带负责人、工具门槛和状态的 Subtask 清单。工具观察与答复进入 gaps，输出待补项；任务清单进入 render_tasks，输出逐项完整答复。

## 先理解设计

拆分决定谁负责什么，工具授权决定谁能做什么，证据门槛决定哪些事项可以标完成。技术请求片段从上下文中独立提取，最终不做可能遗漏事项的自由合并。

源码 SHA256：`6bf939bbd34a47fce845d76e025fca3e95f73dfc73eefcdb1f0ad9148be2bb2a`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Request-owned task ledger. Only observed evidence can complete an executable task.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
Rules cover the supported service domains, independently of benchmark cases. A plan is
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
not permission: write authorization always uses the original authenticated request.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
Final rendering preserves every task verbatim, so synthesis cannot erase a result.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L6**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L8**

```python
from dataclasses import dataclass, field
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
import re
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
# Error numbers require HTTP/error context so a 500-yuan refund is not a failure code.
```

作者注释，说明约束或设计意图；本行不执行。

**L12**

```python
TECHNICAL_PATTERN = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```python
    r"登录|登陆|报错|崩溃|无法打开|闪退|故障|超时|login|error|crash"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L14**

```python
    r"|(?:HTTP|接口|返回|弹出|提示|出现|遇到|报(?:错)?|错误(?:码)?|status)\s*[:：]?\s*[45]\d{2}(?!\d|\s*元)"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L15**

```python
    r"|(?<!\d)[45]\d{2}\s*(?:错误|报错)"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```python
)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L19**

```python
@dataclass
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

**L20**

```python
class Subtask:
```

定义一组状态和行为，或定义可校验的数据契约。

**L21**

```python
    id: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L22**

```python
    kind: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L23**

```python
    agent: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```python
    title: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```python
    instruction: str
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```python
    required_tools: list[str] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
    status: str = "pending"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L28**

```python
    answer: str = ""
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
    observations: list[dict] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
    attempts: int = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L31**

```python
    missing: list[str] = field(default_factory=list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L33 · gaps

检查这个任务自己的成功工具结果、可用知识、实质答复与领域要求，不用其他任务的成功替代它。

**L33**

```python
    def gaps(self, answer):
```

检查这个任务自己的成功工具结果、可用知识、实质答复与领域要求，不用其他任务的成功替代它。

**L34**

```python
        successful = [o for o in self.observations if o.get("success")]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L35**

```python
        names = {o["name"] for o in successful}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
        gaps = ["缺少成功工具证据：" + n for n in self.required_tools if n not in names]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
        if self.denied and re.search(r"超出|超过|不足|不能|无法|拒绝", answer):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L38**

```python
            gaps = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
        if "knowledge_search" in self.required_tools and not any(
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L40**

```python
            o["name"] == "knowledge_search" and o["result"].get("items")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
            for o in successful
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L42**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
            gaps.append("没有可用知识来源")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L44**

```python
        if len(answer.strip()) < 10 or answer.strip() in {
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L45**

```python
            "给用户的回答",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
            "处理完成",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
            "已完成",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
        }:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
            gaps.append("没有实质答复")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L50**

```python
        if self.kind == "technical" and not re.search(
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L51**

```python
            r"检查|尝试|重新|清除|更新|确认|配置|重试|重启|保留|记录|联系|提供|check|retry",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
            answer,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
            re.I,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
            gaps.append("技术问题缺少可执行排查步骤")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L56**

```python
        if self.kind == "technical" and re.search(r"订单|退款|工单", answer):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L57**

```python
            gaps.append("仅回答技术排查，不要处理或代其他子任务承诺订单、退款、工单")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L58**

```python
        if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L59**

```python
            self.kind == "refund"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L60**

```python
            and "refund_request" in names
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
            and not re.search(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
                r"待审核|待审批|等待审核|pending|申请已提交|已提交.*申请", answer, re.I
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            gaps.append("必须说明退款申请待审核，不能宣称款项已到账")
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L66**

```python
        return gaps
```

结束当前函数并把本行构造的结果交给调用方。

**L68**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L69 · denied

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L69**

```python
    def denied(self):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L70**

```python
        return any(
```

结束当前函数并把本行构造的结果交给调用方。

**L71**

```python
            o.get("rejection_code") == "insufficient_refundable_balance"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
            for o in self.observations
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L73**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
    @property
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L76 · allowed_tools

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L76**

```python
    def allowed_tools(self):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L77**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L78**

```python
            "technical": {"knowledge_search"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
            "order": {"order_lookup", "knowledge_search"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
            "refund": {"order_lookup", "refund_request", "knowledge_search"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
            "refund_policy": {"knowledge_search"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
            "handoff": {"ticket_create"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
        }.get(self.kind)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L86 · plan_tasks

独立识别技术、订单、退款、人工及发票诉求，为每项指定负责人及完成必须具备的工具证据。

**L86**

```python
def plan_tasks(message, entities, default_agent, consent):
```

独立识别技术、订单、退款、人工及发票诉求，为每项指定负责人及完成必须具备的工具证据。

**L87**

```python
    tasks = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L89 · add

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L89**

```python
    def add(kind, agent, title, instruction, tools):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L90**

```python
        tasks.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L91**

```python
            Subtask(f"task-{len(tasks) + 1}", kind, agent, title, instruction, tools)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
    technical = bool(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L95**

```python
        re.search(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
            TECHNICAL_PATTERN,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
            message,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
            re.I,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L100**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
    refund = bool(re.search(r"退款|退还|refund", message, re.I))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L102**

```python
    order = bool(entities.get("order_id")) and bool(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L103**

```python
        re.search(r"订单|付款|支付|扣款|账单|物流|发货|order|payment", message, re.I)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L104**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L105**

```python
    handoff = bool(re.search(r"转人工|人工客服|human agent|紧急", message, re.I))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L106**

```python
    if technical:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L107**

```python
        add(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L108**

```python
            "technical",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
            "technical",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L110**

```python
            "技术问题",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L111**

```python
            "只处理原始请求中的技术问题。检索相关知识，给出具体排查步骤并引用来源；不能承诺已修复。其他任务由同事负责。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
            ["knowledge_search"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
    if order and (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L115**

```python
        not refund or re.search(r"查询|查一下|核实|状态|是否.{0,4}支付", message)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
        add(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
            "order",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L119**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
            "订单查询",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L121**

```python
            "只核实原始请求中的订单状态，使用已提供订单号查询，并明确告知查得的状态。其他问题由同事负责。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L122**

```python
            ["order_lookup"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L123**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L124**

```python
    if refund:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L125**

```python
        ready = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L126**

```python
            consent
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L127**

```python
            and bool(entities.get("order_id"))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
            and bool(re.search(r"\d+(?:\.\d{1,2})?\s*元", message))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L130**

```python
        add(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L131**

```python
            "refund" if ready else "refund_policy",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L132**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L133**

```python
            "退款申请" if ready else "退款说明",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L134**

```python
            "只处理退款事项。明确申请且订单和金额齐备时提交待审核申请，并报告真实状态；否则只查询规则或追问缺失信息。不得要求已知信息，不得承诺已到账。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L135**

```python
            ["refund_request"] if ready else ["knowledge_search"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L136**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L137**

```python
    if handoff:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L138**

```python
        add(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L139**

```python
            "handoff",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
            "general",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L141**

```python
            "人工工单",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L142**

```python
            "为原始请求创建人工工单，并给出真实工单号和等待接单状态。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L143**

```python
            ["ticket_create"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L144**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L145**

```python
    if re.search(r"发票|开票|invoice", message, re.I):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L146**

```python
        add(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L147**

```python
            "invoice",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L148**

```python
            "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L149**

```python
            "发票办理",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L150**

```python
            "只处理发票诉求，检索发票办理规则，明确当前需人工审核以及缺失信息，不得宣称已经开票。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L151**

```python
            ["knowledge_search"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L152**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L153**

```python
    if not tasks:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L154**

```python
        add(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L155**

```python
            "general",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L156**

```python
            default_agent if default_agent != "escalation" else "general",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L157**

```python
            "处理结果",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L158**

```python
            "完整处理用户请求；业务状态必须依据工具，缺失信息明确追问。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L159**

```python
            [],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L160**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L161**

```python
    return tasks
```

结束当前函数并把本行构造的结果交给调用方。

### L164 · render_tasks

按任务顺序保留每项已验证的答复和未完成原因，不再交给模型自由压缩。

**L164**

```python
def render_tasks(tasks):
```

按任务顺序保留每项已验证的答复和未完成原因，不再交给模型自由压缩。

**L165**

```python
    """No freeform rewriting after validation: one section per task, including failures."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L166**

```python
    return "\n\n".join(
```

结束当前函数并把本行构造的结果交给调用方。

**L167**

```python
        f"【{t.title}】\n{t.answer}"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L168**

```python
        + (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L169**

```python
            "\n尚未完成：" + "；".join(t.missing)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L170**

```python
            if t.status not in {"completed", "denied"}
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L171**

```python
            else ""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L172**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L173**

```python
        for t in tasks
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L174**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L177 · scope_message

将技术片段从完整请求中抽离，降低同一个 Agent 继续回答其他领域问题的概率；原文仍由执行层保留作授权依据。

**L177**

```python
def scope_message(message, task):
```

将技术片段从完整请求中抽离，降低同一个 Agent 继续回答其他领域问题的概率；原文仍由执行层保留作授权依据。

**L178**

```python
    """Keep unrelated requests out of specialist prompts, not just an instruction to ignore.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L180**

```python
    The full unmodified message stays in the request's authorization context. Technical
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L181**

```python
    agents receive the technical clauses; only billing receives order/amount entities.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L182**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L183**

```python
    if task.kind != "technical":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L184**

```python
        return message
```

结束当前函数并把本行构造的结果交给调用方。

**L185**

```python
    clauses = re.split(r"[，,。；;\n]|同时|另外|而且|并且|顺便|还有", message)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L186**

```python
    selected = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L187**

```python
    for clause in clauses:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L188**

```python
        if re.search(
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L189**

```python
            TECHNICAL_PATTERN,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L190**

```python
            clause,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L191**

```python
            re.I,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L192**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L193**

```python
            clause = re.split(r"订单|退款|扣款|账单|ORD\d+", clause, flags=re.I)[0]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L194**

```python
            if clause.strip():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L195**

```python
                selected.append(clause.strip())
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L196**

```python
    return "；".join(selected) or "排查用户报告的技术故障：" + "、".join(
```

结束当前函数并把本行构造的结果交给调用方。

**L197**

```python
        re.findall(TECHNICAL_PATTERN, message, re.I)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L198**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

当前是已支持客服领域的规则规划，不是任意任务 DAG。回复关键词门槛不是完整语义证明；复杂多订单指代、否定范围和跨任务依赖仍需扩大标注与测试。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
