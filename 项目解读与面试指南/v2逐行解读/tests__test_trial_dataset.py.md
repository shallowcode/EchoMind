# tests\test_trial_dataset.py

## 输入输出流

冻结数据与独立数据库/知识故障夹具进入pytest；输出数据隔离、金额标签、参数核验、错误订单、权限、故障和族级权重断言。

## 先理解设计

反例验证判分不会被流畅文字、正确金额但错误订单、或同族大量复制所误导。测试不调用验收集模型响应。

源码 SHA256：`9e0fb9c8ac55e01ac95a224916f617e0259461986bce05f284bbb83b6d2bf460`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Verify data isolation and state-based evaluation, without evaluating holdout answers."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
from collections import Counter
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
from types import SimpleNamespace
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
import pytest
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
from evaluation.full_chain import aggregate, answer_contains, prepare_fixture, verify
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
from scripts.build_acceptance_dataset import build, canonical
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
from supportflow.contracts import Principal, Trace
```

导入本段使用的标准库、依赖或项目组件。

**L14**

```python
from supportflow.model import active_trace
```

导入本段使用的标准库、依赖或项目组件。

**L15**

```python
from supportflow.store import Store
```

导入本段使用的标准库、依赖或项目组件。

**L16**

```python
from supportflow.tools import Tools
```

导入本段使用的标准库、依赖或项目组件。

**L18**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L21 · test_reviewer_qualifier_is_not_a_different_refund_state

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L21**

```python
def test_reviewer_qualifier_is_not_a_different_refund_state():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L22**

```python
    assert answer_contains("申请已提交，当前待财务审核", "待审核")
```

保留原词匹配，同时规范待财务/人工/客服审核的状态表达；这是开发期修正的关键词判分，不是独立语义评委。

**L23**

```python
    assert answer_contains("当前待人工审核", "待审核")
```

保留原词匹配，同时规范待财务/人工/客服审核的状态表达；这是开发期修正的关键词判分，不是独立语义评委。

**L24**

```python
    assert answer_contains("当前待财务审核", "待财务审核")
```

保留原词匹配，同时规范待财务/人工/客服审核的状态表达；这是开发期修正的关键词判分，不是独立语义评委。

**L25**

```python
    assert not answer_contains("申请尚未建立，请先提供金额", "待审核")
```

保留原词匹配，同时规范待财务/人工/客服审核的状态表达；这是开发期修正的关键词判分，不是独立语义评委。

### L28 · test_frozen_splits_and_business_labels

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L28**

```python
def test_frozen_splits_and_business_labels():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L29**

```python
    splits = build()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
    manifest = json.loads(
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L31**

```python
        (ROOT / "evaluation/datasets/trial-v3/manifest.json").read_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
            encoding="utf-8"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
    ids, families, texts = set(), {}, {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
    for split, count in [
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L37**

```python
        ("development", 600),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
        ("validation", 200),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
        ("acceptance", 400),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
    ]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
        raw = (ROOT / f"evaluation/datasets/trial-v3/{split}.json").read_bytes()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L42**

```python
        assert hashlib.sha256(raw).hexdigest() == manifest["splits"][split]["sha256"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L43**

```python
        assert json.loads(raw)["cases"] == splits[split]
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L44**

```python
        assert len(splits[split]) == count
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L45**

```python
        for case in splits[split]:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L46**

```python
            assert case["id"] not in ids
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
            ids.add(case["id"])
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
            for value, registry in [
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L49**

```python
                (case["family"], families),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L50**

```python
                (canonical(case["turns"]), texts),
```

去除消息中的订单/咨询编号及金额，检查模板换参数后是否跨分区重复；不等于语义相似度判定。

**L51**

```python
            ]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
                assert registry.setdefault(value, split) == split
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L53**

```python
            expected = case["expected"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L54**

```python
            if expected["refund_count"]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L55**

```python
                assert 0 < expected["refund_amount"] <= case["order"]["total_cents"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
                assert expected["refund_order_id"] == case["order"]["id"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L57**

```python
    assert len(ids) == 1200 and len(families) == 48
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L58**

```python
    assert set(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
        Counter(c["family"] for cases in splits.values() for c in cases).values()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
    ) == {25}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L61**

```python
    smoke = json.loads(
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L62**

```python
        (ROOT / "evaluation/datasets/trial-v3/smoke.json").read_text(encoding="utf-8")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L63**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
    assert len(smoke["cases"]) == 8
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L65**

```python
    assert all(c in splits["development"] for c in smoke["cases"])
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L68 · test_variable_order_and_answer_components

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L68**

```python
def test_variable_order_and_answer_components(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L69**

```python
    store = Store(tmp_path / "db")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L70**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L71**

```python
    admin = Principal("t", "a", frozenset({"admin"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
    store.seed_order(admin, "ORD9999", 5000, p.user)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
    case = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L74**

```python
        "order": {"id": "ORD9999"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
        "expected": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
            "tools": ["order_lookup"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
            "refunded_cents": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L78**

```python
            "answer_groups": [["401"], ["已支付"]],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
            "tool_arguments": [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
                {"name": "order_lookup", "arguments": {"order_id": "ORD9999"}}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
            ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
    response = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L85**

```python
        "_http_status": 200,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
        "response": "401 需要排查，订单已支付。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
        "trace": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
            "tools": [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
                {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L90**

```python
                    "name": "order_lookup",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
                    "arguments": {"order_id": "ORD9999"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
                    "success": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
            ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
    assert verify(case, [response], store, p)["complete"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L98**

```python
    response["response"] = "401 需要排查。"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L99**

```python
    assert not verify(case, [response], store, p)["checks"]["answer_group_1"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L100**

```python
    response["trace"]["tools"][0]["arguments"]["order_id"] = "ORD1001"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L101**

```python
    assert not verify(case, [response], store, p)["checks"]["tool_arguments_0"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

### L104 · test_refund_on_wrong_order_is_failure

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L104**

```python
def test_refund_on_wrong_order_is_failure(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L105**

```python
    store = Store(tmp_path / "db")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L106**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L107**

```python
    admin = Principal("t", "a", frozenset({"admin"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L108**

```python
    store.seed_order(admin, "ORD9999", 5000, p.user)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
    store.refund_request(p, "ORD9999", 100, "test", "idempotency")
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L110**

```python
    case = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L111**

```python
        "expected": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
            "tools": [],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
            "refund_count": 1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
            "refund_amount": 100,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
            "refund_order_id": "ORD8888",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
    result = verify(case, [{"_http_status": 200, "response": "待审核"}], store, p)
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L119**

```python
    assert result["checks"]["refund_amount"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
    assert not result["checks"]["refund_order"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L123 · test_expected_denial_does_not_skip_evidence

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L123**

```python
def test_expected_denial_does_not_skip_evidence(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L124**

```python
    store = Store(tmp_path / "db")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L125**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L126**

```python
    case = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L127**

```python
        "expected": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
            "tools": [],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
            "allow_blocked": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L130**

```python
            "refund_count": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L131**

```python
            "forbidden_success_tools": ["order_lookup"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L132**

```python
            "answer_groups": [["无权"]],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L133**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L134**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L135**

```python
    response = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L136**

```python
        "_http_status": 200,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L137**

```python
        "response": "无权访问",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L138**

```python
        "tasks": [{"status": "blocked"}],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L139**

```python
        "trace": {"tools": []},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L141**

```python
    assert verify(case, [response], store, p)["complete"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L142**

```python
    response["trace"]["tools"].append({"name": "order_lookup", "success": True})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L143**

```python
    assert not verify(case, [response], store, p)["checks"]["no_forbidden_access"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L144**

```python
    response["trace"]["tools"] = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L145**

```python
    response["response"] = "已查到"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L146**

```python
    assert not verify(case, [response], store, p)["complete"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L149**

```python
@pytest.mark.asyncio
```

注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。

### L150 · test_fixture_ownership_and_outage_use_real_tool_guard

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L150**

```python
async def test_fixture_ownership_and_outage_use_real_tool_guard(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L151**

```python
    class Knowledge:
```

定义一组状态和行为，或定义可校验的数据契约。

### L152 · seed

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L152**

```python
        def seed(self, tenant):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L153**

```python
            pass
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L155 · version

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L155**

```python
        def version(self, tenant):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L156**

```python
            return 1
```

结束当前函数并把本行构造的结果交给调用方。

**L158**

```python
    store = Store(tmp_path / "db")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L159**

```python
    service = SimpleNamespace(store=store, knowledge=Knowledge())
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L160**

```python
    p = Principal("tenant", "caller")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L161**

```python
    # Independent evaluator fixture: do not execute any acceptance case or model response.
```

作者注释，说明约束或设计意图；本行不执行。

**L162**

```python
    case = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L163**

```python
        "order": {"id": "ORD9999", "total_cents": 5000},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L164**

```python
        "fixture": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L165**

```python
            "order_tenant": "elsewhere",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L166**

```python
            "order_owner": "someone",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L167**

```python
            "knowledge_unavailable": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L168**

```python
        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L169**

```python
        "expected": {"tools": [], "refunded_cents": 0},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L170**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L171**

```python
    await prepare_fixture(service, case, p)
```

根据评测标签建立不同订单、属主和租户；可只在本例应用注入知识不可用。客户Agent只收到用户消息，不读取夹具与金标。

**L172**

```python
    with pytest.raises(PermissionError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L173**

```python
        store.order(p, "ORD9999")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L174**

```python
    assert verify(case, [{"_http_status": 200}], store, p)["checks"]["settled_balance"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L175**

```python
    trace = Trace("fault-test")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L176**

```python
    marker = active_trace.set(trace)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L177**

```python
    try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L178**

```python
        with pytest.raises(RuntimeError, match="Injected knowledge"):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L179**

```python
            await Tools(store, service.knowledge).call(
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L180**

```python
                p, "technical", "knowledge_search", {"query": "401"}, "conv", "request"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L181**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L182**

```python
    finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L183**

```python
        active_trace.reset(marker)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L184**

```python
    assert trace.tools[0]["success"] is False
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L185**

```python
    assert "Injected knowledge" in trace.tools[0]["error"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L188 · test_family_weighting_does_not_count_copies_as_new_families

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L188**

```python
def test_family_weighting_does_not_count_copies_as_new_families():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

### L189 · row

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L189**

```python
    def row(family, complete):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L190**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L191**

```python
            "family": family,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L192**

```python
            "complete": complete,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L193**

```python
            "model_cost": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L194**

```python
            "task_ms": 1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L195**

```python
            "request_ms": [1],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L196**

```python
            "input_tokens": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L197**

```python
            "output_tokens": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L198**

```python
            "judge": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L199**

```python
            "judge_error": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L200**

```python
            "group": "g",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L201**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L203**

```python
    result = aggregate([row("a", True)] * 25 + [row("b", False)])
```

以全部任务为分母聚合完成率、nearest-rank P95、真实token与可用成本；另按模板族等权汇总，避免把同族重复实例当作新独立场景。

**L204**

```python
    assert result["completion_rate"] == 25 / 26
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L205**

```python
    assert result["family_count"] == 2
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L206**

```python
    assert result["family_macro_completion"] == 0.5
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

## 结合全项目看：边界与增强

测试替身只能证明评测工程行为。自然语言同义表达、否定和跨句事实仍需人工审核。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
