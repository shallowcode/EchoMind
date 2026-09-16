# tests\test_supportflow_payments.py

## 输入输出流

隔离的测试目录、身份、请求或模拟依赖进入测试；输出断言通过/失败与 pytest 结果。

## 先理解设计

测试替身验证工程行为，不能充当真实模型准确率或生产性能证据。

源码 SHA256：`500e2a3fab638f617a69554bfa7afa9105fdb1e294115bf607425a0604062ad8`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L2**

```python
import hmac
```

导入本段使用的标准库、依赖或项目组件。

**L3**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import httpx
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
import pytest
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
from supportflow.contracts import Principal, Settings
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
from supportflow.store import Store
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from supportflow.payments import Payments
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L13 · test_outbox_signed_settlement_and_replay

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L13**

```python
async def test_outbox_signed_settlement_and_replay(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L14**

```python
    s = Store(tmp_path / "payments.sqlite")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```python
    a = Principal("t", "admin", frozenset({"admin"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L16**

```python
    p = Principal("t", "alice")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L17**

```python
    s.seed_order(a, "ORD1", 1000, "alice")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
    r = s.refund_request(p, "ORD1", 500, "test", "key")
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L19**

```python
    s.approve_refund(a, r["id"])
```

要求财务权限并禁止申请者自批，pending 才能转审核结果。

**L20**

```python
    cfg = Settings(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L21**

```python
        business_mode="external",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L22**

```python
        payment_url="https://provider.test",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L23**

```python
        payment_key="test",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
        payment_webhook_secret="test-secret",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```python
    pay = Payments(s, cfg)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
    pay.enqueue(a, r["id"])
```

把批准退款和待发送消息在同一事务内写入，保证崩溃后仍知道要发送什么。

**L28**

```python
    with pytest.raises(ValueError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L29**

```python
        s.refund_request(p, "ORD1", 600, "test", "other")
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

### L31 · respond

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L31**

```python
    def respond(req):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L32**

```python
        assert req.headers["Idempotency-Key"] == r["id"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
        return httpx.Response(202, json={"accepted": True})
```

结束当前函数并把本行构造的结果交给调用方。

**L35**

```python
    assert (await pay.dispatch(a, httpx.MockTransport(respond)))[0]["sent"]
```

领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。

**L36**

```python
    assert s.order(p, "ORD1")["refunded"] == 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
    event = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
        "event_id": "evt1",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
        "refund_id": r["id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
        "tenant": "t",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
        "order_id": "ORD1",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L42**

```python
        "amount_cents": 500,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
        "currency": "CNY",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
        "status": "settled",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
        "payment_ref": "test-ref",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
    raw = json.dumps(event).encode()
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L48**

```python
    ts = str(int(time.time()))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L49**

```python
    sig = hmac.new(b"test-secret", ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
    with pytest.raises(PermissionError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L51**

```python
        pay.event(raw, ts, "bad")
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L52**

```python
    assert pay.event(raw, ts, sig)["status"] == "settled"
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L53**

```python
    assert pay.event(raw, ts, sig)["duplicate"]
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L54**

```python
    assert s.order(p, "ORD1")["refunded"] == 500
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L55**

```python
    bad = json.dumps({**event, "event_id": "evt2", "amount_cents": 400}).encode()
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L56**

```python
    sign = hmac.new(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L57**

```python
        b"test-secret", ts.encode() + b"." + bad, hashlib.sha256
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
    ).hexdigest()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
    with pytest.raises(ValueError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L60**

```python
        pay.event(bad, ts, sign)
```

先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。

**L63**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L64 · test_lost_callback_reconciliation

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L64**

```python
async def test_lost_callback_reconciliation(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L65**

```python
    s = Store(tmp_path / "reconcile.sqlite")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L66**

```python
    a = Principal("t", "admin", frozenset({"admin"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L67**

```python
    p = Principal("t", "alice")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L68**

```python
    s.seed_order(a, "ORD1", 1000, "alice")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
    r = s.refund_request(p, "ORD1", 100, "test", "key")
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L70**

```python
    s.approve_refund(a, r["id"])
```

要求财务权限并禁止申请者自批，pending 才能转审核结果。

**L71**

```python
    pay = Payments(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
        s,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
        Settings(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
            business_mode="external",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
            payment_url="https://provider.test",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L76**

```python
            payment_key="test",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L77**

```python
            payment_webhook_secret="secret",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L78**

```python
        ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
    pay.enqueue(a, r["id"])
```

把批准退款和待发送消息在同一事务内写入，保证崩溃后仍知道要发送什么。

**L81**

```python
    await pay.dispatch(a, httpx.MockTransport(lambda req: httpx.Response(202)))
```

领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。

**L82**

```python
    event = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L83**

```python
        "event_id": "lost-event",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
        "refund_id": r["id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L85**

```python
        "tenant": "t",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
        "order_id": "ORD1",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
        "amount_cents": 100,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
        "currency": "CNY",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
        "status": "settled",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L90**

```python
        "payment_ref": "provider-ref",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
    raw = json.dumps(event).encode()
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L93**

```python
    ts = str(int(time.time()))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L94**

```python
    sig = hmac.new(b"secret", ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L95**

```python
    result = await pay.reconcile(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L96**

```python
        a,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
        httpx.MockTransport(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
            lambda req: httpx.Response(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
                200, content=raw, headers={"x-timestamp": ts, "x-signature": sig}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L100**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
        ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L103**

```python
    assert result[0]["status"] == "settled" and s.order(p, "ORD1")["refunded"] == 100
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

## 结合全项目看：边界与增强

增加真实供应商、并发进程、故障恢复和独立业务标签验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
