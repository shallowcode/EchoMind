# supportflow\store.py

## 输入输出流

可信 Principal、业务参数和幂等键进入 SQL 事务；输出订单、退款、工单、会话状态和审计记录。

## 先理解设计

SQL 是权威状态。退款额度检查与预留在同一事务内完成；会话提交把消息、状态、幂等响应一起保存。

源码 SHA256：`1869368f9dba6b98c7a063335f13d16809bb99bb486c981d98e21b6d83b7eced`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Transactional business source of truth. No credentials or money leave this sandbox ledger.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
SQLite WAL transactions reserve pending refunds, enforce ownership and persist idempotency,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
conversation state and audit events. Redis/Chroma are optional projections, never the authority.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
import secrets
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
import sqlite3
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
import uuid
```

导入本段使用的标准库、依赖或项目组件。

**L14**

```python
from contextlib import contextmanager
```

导入本段使用的标准库、依赖或项目组件。

**L15**

```python
from supportflow.contracts import Principal, BusinessRejection
```

导入本段使用的标准库、依赖或项目组件。

**L18**

```python
class Store:
```

定义一组状态和行为，或定义可校验的数据契约。

### L19 · __init__

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L19**

```python
    def __init__(self, path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L20**

```python
        self.path = str(path)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L21**

```python
        Path(path).parent.mkdir(parents=True, exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L22**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L23**

```python
            c.executescript("""
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L24**

```python
            CREATE TABLE IF NOT EXISTS tokens (hash TEXT PRIMARY KEY, tenant TEXT, user TEXT, roles TEXT, expires REAL, revoked INTEGER DEFAULT 0);
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L25**

```python
            CREATE TABLE IF NOT EXISTS orders (tenant TEXT, id TEXT, user TEXT, total INTEGER, refunded INTEGER DEFAULT 0, status TEXT, PRIMARY KEY(tenant,id));
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L26**

```python
            CREATE TABLE IF NOT EXISTS refunds (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, order_id TEXT, amount INTEGER, status TEXT, idem TEXT, reason TEXT, payment_ref TEXT, UNIQUE(tenant,user,idem));
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L27**

```python
            CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY, tenant TEXT, user TEXT, conv TEXT, summary TEXT, status TEXT, assignee TEXT, resolution TEXT, idem TEXT, version INTEGER DEFAULT 0, UNIQUE(tenant,user,idem));
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L28**

```python
            CREATE TABLE IF NOT EXISTS conversations (tenant TEXT, id TEXT, user TEXT, state TEXT, version INTEGER DEFAULT 0, lease_owner TEXT, lease_until REAL DEFAULT 0, PRIMARY KEY(tenant,id));
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L29**

```python
            CREATE TABLE IF NOT EXISTS messages (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, conv TEXT, role TEXT, content TEXT, created REAL);
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L30**

```python
            CREATE TABLE IF NOT EXISTS requests (tenant TEXT, user TEXT, id TEXT, fingerprint TEXT, response TEXT, PRIMARY KEY(tenant,user,id));
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L31**

```python
            CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT, actor TEXT, action TEXT, target TEXT, detail TEXT, created REAL);
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L32**

```python
            CREATE TABLE IF NOT EXISTS knowledge (tenant TEXT, id TEXT, title TEXT, content TEXT, version TEXT, PRIMARY KEY(tenant,id));
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L33**

```python
            CREATE TABLE IF NOT EXISTS traces (tenant TEXT, user TEXT, id TEXT PRIMARY KEY, payload TEXT);
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L34**

```python
            CREATE TABLE IF NOT EXISTS payment_outbox (refund_id TEXT PRIMARY KEY, tenant TEXT, payload TEXT, status TEXT, attempts INTEGER DEFAULT 0, lease_until REAL DEFAULT 0, last_error TEXT);
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L35**

```python
            CREATE TABLE IF NOT EXISTS payment_events (id TEXT PRIMARY KEY, refund_id TEXT, created REAL);
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L36**

```python
            CREATE TABLE IF NOT EXISTS profiles (tenant TEXT, user TEXT, payload TEXT, PRIMARY KEY(tenant,user));
```

声明持久化表与唯一键，供后续事务约束状态与重放。

**L37**

```python
            """)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
    @contextmanager
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L40 · tx

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L40**

```python
    def tx(self):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L41**

```python
        c = sqlite3.connect(self.path, timeout=10)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L42**

```python
        c.row_factory = sqlite3.Row
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L43**

```python
        c.execute("PRAGMA journal_mode=WAL")
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L44**

```python
        c.execute("PRAGMA foreign_keys=ON")
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L45**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
            c.execute("BEGIN IMMEDIATE")
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L47**

```python
            yield c
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
            c.commit()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
        except BaseException:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L50**

```python
            c.rollback()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L51**

```python
            raise
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
        finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L53**

```python
            c.close()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L55 · audit

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L55**

```python
    def audit(self, c, p, action, target, detail):
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L56**

```python
        c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L57**

```python
            "INSERT INTO audit(tenant,actor,action,target,detail,created) VALUES(?,?,?,?,?,?)",
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L58**

```python
            (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
                p.tenant,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
                p.user,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
                action,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
                target,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
                json.dumps(detail, ensure_ascii=False),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L64**

```python
                time.time(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L68 · issue_token

签发随机不透明 token，数据库只保存摘要、租户、角色和到期时间。

**L68**

```python
    def issue_token(self, p, ttl=3600):
```

签发随机不透明 token，数据库只保存摘要、租户、角色和到期时间。

**L69**

```python
        token = secrets.token_urlsafe(32)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L70**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L71**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L72**

```python
                "INSERT INTO tokens(hash,tenant,user,roles,expires) VALUES(?,?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
                (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
                    hashlib.sha256(token.encode()).hexdigest(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
                    p.tenant,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
                    p.user,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
                    json.dumps(sorted(p.roles)),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L78**

```python
                    time.time() + ttl,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
                ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
        return token
```

结束当前函数并把本行构造的结果交给调用方。

### L83 · authenticate

把 token 摘要转换成可信 Principal，同时检查撤销和过期。

**L83**

```python
    def authenticate(self, token):
```

把 token 摘要转换成可信 Principal，同时检查撤销和过期。

**L84**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L85**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L86**

```python
                "SELECT * FROM tokens WHERE hash=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L87**

```python
                (hashlib.sha256(token.encode()).hexdigest(),),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
        if not r or r["revoked"] or r["expires"] <= time.time():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L90**

```python
            raise PermissionError("Invalid or expired token")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L91**

```python
        return Principal(r["tenant"], r["user"], frozenset(json.loads(r["roles"])))
```

结束当前函数并把本行构造的结果交给调用方。

### L93 · revoke

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L93**

```python
    def revoke(self, p, token):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L94**

```python
        p.require("admin")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L95**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L96**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L97**

```python
                "UPDATE tokens SET revoked=1 WHERE tenant=? AND hash=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L98**

```python
                (p.tenant, hashlib.sha256(token.encode()).hexdigest()),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L101 · seed_order

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L101**

```python
    def seed_order(self, p, order_id, total=5000, user=None):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L102**

```python
        p.require("admin")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L103**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L104**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L105**

```python
                "INSERT INTO orders(tenant,id,user,total,status) VALUES(?,?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
                (p.tenant, order_id, user or p.user, total, "paid"),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L107**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L109 · order

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L109**

```python
    def order(self, p, order_id):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L110**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L111**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L112**

```python
                "SELECT * FROM orders WHERE tenant=? AND id=?", (p.tenant, order_id)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L113**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
        if not r or (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L115**

```python
            r["user"] != p.user
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L116**

```python
            and not p.roles.intersection({"staff", "finance", "admin"})
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
            raise PermissionError("Order not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L119**

```python
        return dict(r)
```

结束当前函数并把本行构造的结果交给调用方。

### L121 · refund_request

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L121**

```python
    def refund_request(self, p, order_id, amount, reason, idem):
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L122**

```python
        if type(amount) is not int or amount <= 0:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L123**

```python
            raise ValueError("amount_cents must be positive integer")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L124**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L125**

```python
            old = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L126**

```python
                "SELECT * FROM refunds WHERE tenant=? AND user=? AND idem=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L127**

```python
                (p.tenant, p.user, idem),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
            if old:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L130**

```python
                if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L131**

```python
                    old["order_id"] != order_id
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L132**

```python
                    or old["amount"] != amount
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L133**

```python
                    or old["reason"] != reason
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L134**

```python
                ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L135**

```python
                    raise ValueError("Idempotency key payload mismatch")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L136**

```python
                return dict(old)
```

结束当前函数并把本行构造的结果交给调用方。

**L137**

```python
            order = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L138**

```python
                "SELECT * FROM orders WHERE tenant=? AND id=? AND user=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L139**

```python
                (p.tenant, order_id, p.user),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L141**

```python
            if not order:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L142**

```python
                raise PermissionError("Order not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L143**

```python
            reserved = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L144**

```python
                "SELECT COALESCE(SUM(amount),0) FROM refunds WHERE tenant=? AND order_id=? AND status IN ('pending','approved','processing')",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L145**

```python
                (p.tenant, order_id),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L146**

```python
            ).fetchone()[0]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L147**

```python
            if order["refunded"] + reserved + amount > order["total"]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L148**

```python
                raise BusinessRejection(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L149**

```python
                    "insufficient_refundable_balance",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L150**

```python
                    "Refund exceeds unreserved balance",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L151**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L152**

```python
            rid = "rf_" + uuid.uuid4().hex
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L153**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L154**

```python
                "INSERT INTO refunds VALUES(?,?,?,?,?,?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L155**

```python
                (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L156**

```python
                    rid,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L157**

```python
                    p.tenant,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L158**

```python
                    p.user,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L159**

```python
                    order_id,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L160**

```python
                    amount,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L161**

```python
                    "pending",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L162**

```python
                    idem,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L163**

```python
                    reason,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L164**

```python
                    None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L165**

```python
                ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L166**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L167**

```python
            self.audit(
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L168**

```python
                c, p, "refund.request", rid, {"amount_cents": amount, "mode": "sandbox"}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L169**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L170**

```python
            return dict(
```

结束当前函数并把本行构造的结果交给调用方。

**L171**

```python
                c.execute("SELECT * FROM refunds WHERE id=?", (rid,)).fetchone()
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L172**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L174 · approve_refund

要求财务权限并禁止申请者自批，pending 才能转审核结果。

**L174**

```python
    def approve_refund(self, p, rid, approve=True):
```

要求财务权限并禁止申请者自批，pending 才能转审核结果。

**L175**

```python
        p.require("finance")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L176**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L177**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L178**

```python
                "SELECT * FROM refunds WHERE tenant=? AND id=?", (p.tenant, rid)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L179**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L180**

```python
            if not r:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L181**

```python
                raise PermissionError("Refund not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L182**

```python
            if r["status"] != "pending":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L183**

```python
                raise ValueError("Refund must be pending")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L184**

```python
            if r["user"] == p.user:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L185**

```python
                raise PermissionError("Requester cannot approve own refund")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L186**

```python
            status = "approved" if approve else "rejected"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L187**

```python
            c.execute("UPDATE refunds SET status=? WHERE id=?", (status, rid))
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L188**

```python
            self.audit(c, p, "refund." + status, rid, {})
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L189**

```python
        return {"id": rid, "status": status}
```

结束当前函数并把本行构造的结果交给调用方。

### L191 · settle_refund

沙箱内核验审批、幂等更新退款与订单；不向外部支付商发请求。

**L191**

```python
    def settle_refund(self, p, rid):
```

沙箱内核验审批、幂等更新退款与订单；不向外部支付商发请求。

**L192**

```python
        p.require("finance")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L193**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L194**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L195**

```python
                "SELECT * FROM refunds WHERE tenant=? AND id=?", (p.tenant, rid)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L196**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L197**

```python
            if not r:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L198**

```python
                raise PermissionError("Refund not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L199**

```python
            if r["status"] == "settled":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L200**

```python
                return dict(r)
```

结束当前函数并把本行构造的结果交给调用方。

**L201**

```python
            if r["status"] != "approved":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L202**

```python
                raise ValueError("Approval required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L203**

```python
            if r["user"] == p.user:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L204**

```python
                raise PermissionError("Requester cannot settle own refund")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L205**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L206**

```python
                "UPDATE orders SET refunded=refunded+? WHERE tenant=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L207**

```python
                (r["amount"], p.tenant, r["order_id"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L208**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L209**

```python
            ref = "sandbox_" + rid
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L210**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L211**

```python
                "UPDATE refunds SET status='settled',payment_ref=? WHERE id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L212**

```python
                (ref, rid),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L213**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L214**

```python
            self.audit(
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L215**

```python
                c, p, "refund.settle", rid, {"mode": "sandbox", "payment_ref": ref}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L216**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L217**

```python
            return dict(
```

结束当前函数并把本行构造的结果交给调用方。

**L218**

```python
                c.execute("SELECT * FROM refunds WHERE id=?", (rid,)).fetchone()
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L219**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L221 · create_ticket

要求会话属主，使用持久幂等键创建 open 工单。

**L221**

```python
    def create_ticket(self, p, conv, summary, idem):
```

要求会话属主，使用持久幂等键创建 open 工单。

**L222**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L223**

```python
            conversation = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L224**

```python
                "SELECT user FROM conversations WHERE tenant=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L225**

```python
                (p.tenant, conv),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L226**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L227**

```python
            if not conversation or conversation["user"] != p.user:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L228**

```python
                raise PermissionError("Owned conversation required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L229**

```python
            old = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L230**

```python
                "SELECT * FROM tickets WHERE tenant=? AND user=? AND idem=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L231**

```python
                (p.tenant, p.user, idem),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L232**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L233**

```python
            if old:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L234**

```python
                if old["conv"] != conv or old["summary"] != summary:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L235**

```python
                    raise ValueError("Ticket idempotency payload mismatch")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L236**

```python
                return dict(old)
```

结束当前函数并把本行构造的结果交给调用方。

**L237**

```python
            tid = "tk_" + uuid.uuid4().hex
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L238**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L239**

```python
                "INSERT INTO tickets(id,tenant,user,conv,summary,status,idem) VALUES(?,?,?,?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L240**

```python
                (tid, p.tenant, p.user, conv, summary, "open", idem),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L241**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L242**

```python
            self.audit(c, p, "ticket.create", tid, {"conv": conv})
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L243**

```python
            return dict(
```

结束当前函数并把本行构造的结果交给调用方。

**L244**

```python
                c.execute("SELECT * FROM tickets WHERE id=?", (tid,)).fetchone()
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L245**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L247 · ticket

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L247**

```python
    def ticket(self, p, tid):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L248**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L249**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L250**

```python
                "SELECT * FROM tickets WHERE tenant=? AND id=?", (p.tenant, tid)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L251**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L252**

```python
        if not r or (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L253**

```python
            r["user"] != p.user and not p.roles.intersection({"staff", "admin"})
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L254**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L255**

```python
            raise PermissionError("Ticket not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L256**

```python
        return dict(r)
```

结束当前函数并把本行构造的结果交给调用方。

### L258 · update_ticket

校验状态机、受理人和乐观版本；解决说明写回原会话。

**L258**

```python
    def update_ticket(self, p, tid, status, assignee="", resolution="", version=0):
```

校验状态机、受理人和乐观版本；解决说明写回原会话。

**L259**

```python
        p.require("staff")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L260**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L261**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L262**

```python
                "SELECT * FROM tickets WHERE tenant=? AND id=?", (p.tenant, tid)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L263**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L264**

```python
            if not r:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L265**

```python
                raise PermissionError("Ticket not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L266**

```python
            transitions = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L267**

```python
                "open": {"assigned"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L268**

```python
                "assigned": {"resolved"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L269**

```python
                "resolved": {"closed"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L270**

```python
                "closed": set(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L271**

```python
            }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L272**

```python
            if status not in transitions[r["status"]]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L273**

```python
                raise ValueError("Invalid ticket transition")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L274**

```python
            if status == "assigned" and not assignee:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L275**

```python
                raise ValueError("Assignee required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L276**

```python
            if status == "resolved" and (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L277**

```python
                not resolution or (r["assignee"] != p.user and "admin" not in p.roles)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L278**

```python
            ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L279**

```python
                raise PermissionError("Assigned staff and resolution required")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L280**

```python
            cur = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L281**

```python
                "UPDATE tickets SET status=?,assignee=?,resolution=?,version=version+1 WHERE id=? AND version=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L282**

```python
                (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L283**

```python
                    status,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L284**

```python
                    assignee or r["assignee"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L285**

```python
                    resolution or r["resolution"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L286**

```python
                    tid,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L287**

```python
                    version,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L288**

```python
                ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L289**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L290**

```python
            if cur.rowcount != 1:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L291**

```python
                raise ValueError("Ticket version conflict")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L292**

```python
            if status == "resolved":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L293**

```python
                c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L294**

```python
                    "INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L295**

```python
                    (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L296**

```python
                        p.tenant,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L297**

```python
                        r["conv"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L298**

```python
                        "system",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L299**

```python
                        f"工单 {tid} 已解决：{resolution}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L300**

```python
                        time.time(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L301**

```python
                    ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L302**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L303**

```python
            self.audit(c, p, "ticket." + status, tid, {"resolution": resolution})
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L304**

```python
        return self.ticket(p, tid)
```

结束当前函数并把本行构造的结果交给调用方。

### L306 · acquire_conversation

校验会话属主并抢占有期限的会话租约，防止两个聊天轮次覆盖状态。

**L306**

```python
    def acquire_conversation(self, p, conv, owner, ttl):
```

校验会话属主并抢占有期限的会话租约，防止两个聊天轮次覆盖状态。

**L307**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L308**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L309**

```python
                "INSERT OR IGNORE INTO conversations(tenant,id,user,state) VALUES(?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L310**

```python
                (p.tenant, conv, p.user, "{}"),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L311**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L312**

```python
            row = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L313**

```python
                "SELECT * FROM conversations WHERE tenant=? AND id=?", (p.tenant, conv)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L314**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L315**

```python
            if row["user"] != p.user:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L316**

```python
                raise PermissionError("Conversation belongs to another user")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L317**

```python
            if row["lease_until"] > time.time():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L318**

```python
                raise ValueError("Conversation busy; retry with same request_id")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L319**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L320**

```python
                "UPDATE conversations SET lease_owner=?,lease_until=? WHERE tenant=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L321**

```python
                (owner, time.time() + ttl, p.tenant, conv),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L322**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L323**

```python
            return json.loads(row["state"])
```

结束当前函数并把本行构造的结果交给调用方。

### L325 · release

只允许当前租约持有者释放，错误请求不能解锁别人的会话。

**L325**

```python
    def release(self, p, conv, owner):
```

只允许当前租约持有者释放，错误请求不能解锁别人的会话。

**L326**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L327**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L328**

```python
                "UPDATE conversations SET lease_until=0 WHERE tenant=? AND id=? AND lease_owner=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L329**

```python
                (p.tenant, conv, owner),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L330**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L332 · history

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L332**

```python
    def history(self, p, conv, limit=20):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L333**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L334**

```python
            row = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L335**

```python
                "SELECT user FROM conversations WHERE tenant=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L336**

```python
                (p.tenant, conv),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L337**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L338**

```python
            if row and row["user"] != p.user:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L339**

```python
                raise PermissionError("Conversation not accessible")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L340**

```python
            rows = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L341**

```python
                "SELECT role,content FROM messages WHERE tenant=? AND conv=? ORDER BY seq DESC LIMIT ?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L342**

```python
                (p.tenant, conv, limit),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L343**

```python
            ).fetchall()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L344**

```python
        return [dict(x) for x in reversed(rows)]
```

结束当前函数并把本行构造的结果交给调用方。

### L346 · cached_request

校验请求指纹并读取已完成响应，使网络重试不重做业务。

**L346**

```python
    def cached_request(self, p, rid, fingerprint):
```

校验请求指纹并读取已完成响应，使网络重试不重做业务。

**L347**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L348**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L349**

```python
                "SELECT * FROM requests WHERE tenant=? AND user=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L350**

```python
                (p.tenant, p.user, rid),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L351**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L352**

```python
        if r and r["fingerprint"] != fingerprint:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L353**

```python
            raise ValueError("request_id reused with different payload")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L354**

```python
        return json.loads(r["response"]) if r else None
```

结束当前函数并把本行构造的结果交给调用方。

### L356 · commit_turn

在同一事务里提交原始消息、会话状态、画像、幂等响应和 trace，避免只保存了回答却没保存状态。

**L356**

```python
    def commit_turn(self, p, conv, owner, rid, fingerprint, message, response, state):
```

在同一事务里提交原始消息、会话状态、画像、幂等响应和 trace，避免只保存了回答却没保存状态。

**L357**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L358**

```python
            row = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L359**

```python
                "SELECT lease_owner FROM conversations WHERE tenant=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L360**

```python
                (p.tenant, conv),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L361**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L362**

```python
            if not row or row["lease_owner"] != owner:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L363**

```python
                raise ValueError("Conversation lease lost")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L364**

```python
            for role, content in [
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L365**

```python
                ("user", message),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L366**

```python
                ("assistant", response["response"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L367**

```python
            ]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L368**

```python
                c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L369**

```python
                    "INSERT INTO messages(tenant,conv,role,content,created) VALUES(?,?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L370**

```python
                    (p.tenant, conv, role, content, time.time()),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L371**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L372**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L373**

```python
                "UPDATE conversations SET state=?,version=version+1 WHERE tenant=? AND id=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L374**

```python
                (json.dumps(state, ensure_ascii=False), p.tenant, conv),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L375**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L376**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L377**

```python
                "INSERT INTO profiles VALUES(?,?,?) ON CONFLICT(tenant,user) DO UPDATE SET payload=excluded.payload",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L378**

```python
                (p.tenant, p.user, json.dumps(state.get("profile", {}))),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L379**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L380**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L381**

```python
                "INSERT INTO requests VALUES(?,?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L382**

```python
                (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L383**

```python
                    p.tenant,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L384**

```python
                    p.user,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L385**

```python
                    rid,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L386**

```python
                    fingerprint,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L387**

```python
                    json.dumps(response, ensure_ascii=False),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L388**

```python
                ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L389**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L390**

```python
            c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L391**

```python
                "INSERT INTO traces VALUES(?,?,?,?)",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L392**

```python
                (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L393**

```python
                    p.tenant,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L394**

```python
                    p.user,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L395**

```python
                    p.tenant + ":" + p.user + ":" + rid,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L396**

```python
                    json.dumps(response["trace"], ensure_ascii=False),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L397**

```python
                ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L398**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L400 · audit_log

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L400**

```python
    def audit_log(self, p):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L401**

```python
        p.require("admin")
```

在服务器检查角色；admin 的继承规则由 Principal.require 定义。

**L402**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L403**

```python
            return [
```

结束当前函数并把本行构造的结果交给调用方。

**L404**

```python
                dict(x)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L405**

```python
                for x in c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L406**

```python
                    "SELECT * FROM audit WHERE tenant=? ORDER BY seq DESC LIMIT 200",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L407**

```python
                    (p.tenant,),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L408**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L409**

```python
            ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L411 · profile

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L411**

```python
    def profile(self, p):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L412**

```python
        with self.tx() as c:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L413**

```python
            r = c.execute(
```

执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。

**L414**

```python
                "SELECT payload FROM profiles WHERE tenant=? AND user=?",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L415**

```python
                (p.tenant, p.user),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L416**

```python
            ).fetchone()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L417**

```python
        return json.loads(r["payload"]) if r else {}
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

SQLite 串行写入、跨会话画像合并、数据保留与恢复演练需要进一步验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
