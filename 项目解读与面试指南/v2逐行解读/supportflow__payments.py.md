# supportflow\payments.py

## 输入输出流

已审批退款进入外部 outbox；HTTPS 接收确认与签名最终事件进入结算核验；输出 processing/settled/rejected。

## 先理解设计

网络收到成功响应仅表示已受理。只有匹配租户、订单和金额的最终事件，才能更新退款账本。

源码 SHA256：`1cac4cc90c3b66cdcfd40ea2768159d40a99ec7ea3289a80ba156d8ba20a86a5`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Provider-neutral outbox contract; activation requires explicit external configuration.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
POST /refunds must honor Idempotency-Key and return no assumption of settlement.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
Only a signed terminal event matching tenant/order/amount can book settled funds.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
Network ambiguity retains the reservation. Never retry with a new business key.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L6**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L8**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
import hmac
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
import httpx
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
from pydantic import BaseModel, ConfigDict, Field
```

导入本段使用的标准库、依赖或项目组件。

**L14**

```python
from typing import Literal
```

导入本段使用的标准库、依赖或项目组件。

**L17**

```python
class PaymentEvent(BaseModel):
```

定义一组状态和行为，或定义可校验的数据契约。

**L18**

```python
    model_config = ConfigDict(extra="forbid")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
    event_id: str = Field(min_length=1, max_length=200)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L20**

```python
    refund_id: str = Field(min_length=1, max_length=100)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L21**

```python
    tenant: str = Field(min_length=1, max_length=100)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L22**

```python
    order_id: str = Field(min_length=1, max_length=100)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L23**

```python
    amount_cents: int = Field(strict=True, gt=0)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
    currency: Literal["CNY"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```python
    status: Literal["settled", "rejected"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```python
    payment_ref: str = Field(min_length=1, max_length=200)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
class Payments:
```

定义一组状态和行为，或定义可校验的数据契约。

### L30 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L30**

```python
    def __init__(self, store, settings):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L31**

```python
        self.store = store
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L32**

```python
        self.settings = settings
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L34 · enqueue

把批准退款和待发送消息在同一事务内写入，保证崩溃后仍知道要发送什么。

**L34**

```python
    def enqueue(self, p, rid):
```

把批准退款和待发送消息在同一事务内写入，保证崩溃后仍知道要发送什么。

**L35**

```python
        p.require("finance")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L36**

```python
        if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L37**

```python
            not self.settings.payment_url.startswith("https://")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
            or not self.settings.payment_key
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
            or not self.settings.payment_webhook_secret
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
            raise ValueError(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L42**

```python
                "External payment provider must be configured before execution"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
        with self.store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L45**

```python
            row = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L46**

```python
                "SELECT * FROM refunds WHERE tenant=? AND id=?", (p.tenant, rid)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L47**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
            if not row:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L49**

```python
                raise PermissionError("Refund not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L50**

```python
            if row["user"] == p.user:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L51**

```python
                raise PermissionError("Requester cannot execute own refund")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L52**

```python
            if row["status"] in {"processing", "settled"}:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L53**

```python
                return dict(row)
```

结束当前函数并把本行构造的结果交给调用方。

**L54**

```python
            if row["status"] != "approved":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L55**

```python
                raise ValueError("Approval required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L56**

```python
            payload = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L57**

```python
                "refund_id": rid,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
                "tenant": p.tenant,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
                "order_id": row["order_id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
                "amount_cents": row["amount"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
                "currency": self.settings.business_currency,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
            }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L64**

```python
                "INSERT INTO payment_outbox(refund_id,tenant,payload,status) VALUES(?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
                (rid, p.tenant, json.dumps(payload), "pending"),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L66**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
            c.execute("UPDATE refunds SET status='processing' WHERE id=?", (rid,))
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L68**

```python
            self.store.audit(c, p, "payment.enqueue", rid, payload)
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L69**

```python
            return {"id": rid, "status": "processing"}
```

结束当前函数并把本行构造的结果交给调用方。

### L71 · dispatch

领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。

**L71**

```python
    async def dispatch(self, p, transport=None):
```

领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。

**L72**

```python
        p.require("ops")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L73**

```python
        now = time.time()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L74**

```python
        with self.store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L75**

```python
            rows = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L76**

```python
                dict(r)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
                for r in c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L78**

```python
                    "SELECT * FROM payment_outbox WHERE tenant=? AND status='pending' AND lease_until<? LIMIT 20",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L79**

```python
                    (p.tenant, now),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
            ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
            for r in rows:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L83**

```python
                c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L84**

```python
                    "UPDATE payment_outbox SET lease_until=?,attempts=attempts+1 WHERE refund_id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L85**

```python
                    (now + 15 * len(rows) + 30, r["refund_id"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
        results = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L88**

```python
        async with httpx.AsyncClient(
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L89**

```python
            timeout=15, transport=transport, follow_redirects=False
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L90**

```python
        ) as client:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
            for row in rows:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L92**

```python
                try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
                    response = await client.post(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L94**

```python
                        self.settings.payment_url.rstrip("/") + "/refunds",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
                        json=json.loads(row["payload"]),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L96**

```python
                        headers={
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L97**

```python
                            "Authorization": "Bearer " + self.settings.payment_key,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
                            "Idempotency-Key": row["refund_id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
                        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L100**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
                    response.raise_for_status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
                    # Accepted is deliberately not settled. Query/callback reconciles eventual result.
```

作者注释，说明约束或设计意图；本行不执行。

**L103**

```python
                    results.append({"id": row["refund_id"], "sent": True})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L104**

```python
                    with self.store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L105**

```python
                        c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L106**

```python
                            "UPDATE payment_outbox SET status='accepted',last_error=NULL WHERE refund_id=? AND status='pending'",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L107**

```python
                            (row["refund_id"],),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L108**

```python
                        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
                except Exception as e:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L110**

```python
                    results.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L111**

```python
                        {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
                            "id": row["refund_id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
                            "sent": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
                            "error": type(e).__name__,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
                        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
                    with self.store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L118**

```python
                        c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L119**

```python
                            "UPDATE payment_outbox SET last_error=? WHERE refund_id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L120**

```python
                            (type(e).__name__, row["refund_id"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L121**

```python
                        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L122**

```python
        return results
```

结束当前函数并把本行构造的结果交给调用方。

### L124 · reconcile

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L124**

```python
    async def reconcile(self, p, transport=None):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L125**

```python
        """Query accepted operations whose final callback may have been lost.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L127**

```python
        Provider GET /refunds/{id} returns the same signed event contract as webhooks.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
        Pending (202) is not treated as failure or success. Authentication/signature and
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
        exact amount/order checks are identical to the push callback path.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L130**

```python
        """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L131**

```python
        p.require("ops")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L132**

```python
        with self.store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L133**

```python
            rows = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L134**

```python
                dict(r)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L135**

```python
                for r in c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L136**

```python
                    "SELECT * FROM payment_outbox WHERE tenant=? AND status='accepted' LIMIT 20",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L137**

```python
                    (p.tenant,),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L138**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L139**

```python
            ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
        results = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L141**

```python
        async with httpx.AsyncClient(
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L142**

```python
            timeout=15, transport=transport, follow_redirects=False
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L143**

```python
        ) as client:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L144**

```python
            for row in rows:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L145**

```python
                try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L146**

```python
                    response = await client.get(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L147**

```python
                        self.settings.payment_url.rstrip("/")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L148**

```python
                        + "/refunds/"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L149**

```python
                        + row["refund_id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L150**

```python
                        headers={
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L151**

```python
                            "Authorization": "Bearer " + self.settings.payment_key
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L152**

```python
                        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L153**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L154**

```python
                    if response.status_code == 202:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L155**

```python
                        results.append({"id": row["refund_id"], "status": "pending"})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L156**

```python
                        continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L157**

```python
                    response.raise_for_status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L158**

```python
                    event = json.loads(response.content)
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L159**

```python
                    if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L160**

```python
                        event.get("refund_id") != row["refund_id"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L161**

```python
                        or event.get("tenant") != p.tenant
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L162**

```python
                    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L163**

```python
                        raise ValueError("Reconciliation identity mismatch")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L164**

```python
                    result = self.event(
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L165**

```python
                        response.content,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L166**

```python
                        response.headers.get("x-timestamp", ""),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L167**

```python
                        response.headers.get("x-signature", ""),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L168**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L169**

```python
                    results.append({"id": row["refund_id"], **result})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L170**

```python
                except Exception as e:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L171**

```python
                    results.append({"id": row["refund_id"], "error": type(e).__name__})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L172**

```python
        return results
```

结束当前函数并把本行构造的结果交给调用方。

### L174 · event

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L174**

```python
    def event(self, raw, timestamp, signature):
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L175**

```python
        if not self.settings.payment_webhook_secret:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L176**

```python
            raise PermissionError("Webhook not configured")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L177**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L178**

```python
            if abs(time.time() - int(timestamp)) > 300:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L179**

```python
                raise PermissionError("Webhook expired")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L180**

```python
        except (ValueError, TypeError):
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L181**

```python
            raise PermissionError("Invalid timestamp")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L182**

```python
        expected = hmac.new(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L183**

```python
            self.settings.payment_webhook_secret.encode(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L184**

```python
            timestamp.encode() + b"." + raw,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L185**

```python
            hashlib.sha256,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L186**

```python
        ).hexdigest()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L187**

```python
        if not hmac.compare_digest(expected, signature):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L188**

```python
            raise PermissionError("Invalid webhook signature")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L189**

```python
        event = PaymentEvent.model_validate_json(raw).model_dump()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L190**

```python
        with self.store.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L191**

```python
            prior = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L192**

```python
                "SELECT refund_id FROM payment_events WHERE id=?", (event["event_id"],)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L193**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L194**

```python
            if prior:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L195**

```python
                if prior["refund_id"] != event["refund_id"]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L196**

```python
                    raise ValueError("Event id conflict")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L197**

```python
                return {"duplicate": True}
```

结束当前函数并把本行构造的结果交给调用方。

**L198**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L199**

```python
                "SELECT * FROM refunds WHERE id=? AND tenant=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L200**

```python
                (event["refund_id"], event["tenant"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L201**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L202**

```python
            if not r:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L203**

```python
                raise PermissionError("Refund not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L204**

```python
            if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L205**

```python
                r["order_id"] != event["order_id"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L206**

```python
                or type(event["amount_cents"]) is not int
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L207**

```python
                or r["amount"] != event["amount_cents"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L208**

```python
            ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L209**

```python
                raise ValueError("Payment event amount/order mismatch")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L210**

```python
            if r["status"] not in {"processing", event["status"]}:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L211**

```python
                raise ValueError("Unexpected refund state")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L212**

```python
            if event["status"] == "settled" and r["status"] != "settled":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L213**

```python
                c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L214**

```python
                    "UPDATE orders SET refunded=refunded+? WHERE tenant=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L215**

```python
                    (r["amount"], r["tenant"], r["order_id"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L216**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L217**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L218**

```python
                "UPDATE refunds SET status=?,payment_ref=? WHERE id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L219**

```python
                (event["status"], event["payment_ref"], r["id"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L220**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L221**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L222**

```python
                "UPDATE payment_outbox SET status='completed' WHERE refund_id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L223**

```python
                (r["id"],),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L224**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L225**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L226**

```python
                "INSERT INTO payment_events VALUES(?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L227**

```python
                (event["event_id"], r["id"], time.time()),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L228**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L229**

```python
            from supportflow.contracts import Principal
```

导入本段使用的标准库、依赖或项目组件。

**L231**

```python
            self.store.audit(
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L232**

```python
                c,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L233**

```python
                Principal(r["tenant"], "payment-provider"),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L234**

```python
                "payment." + event["status"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L235**

```python
                r["id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L236**

```python
                event,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L237**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L238**

```python
        return {"status": event["status"]}
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

模拟回调丢失对账已测试；真实支付商契约、凭证轮换、调度与人工核对需要最终集成。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
