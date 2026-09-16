# tests\test_supportflow_evaluation.py

## 输入输出流

隔离的测试目录、身份、请求或模拟依赖进入测试；输出断言通过/失败与 pytest 结果。

## 先理解设计

测试替身验证工程行为，不能充当真实模型准确率或生产性能证据。

源码 SHA256：`5813425782e9e8f85d33bfd6c79773f4af32e4d6c31693ddd09a65c229c1b11b`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
from evaluation.full_chain import aggregate, wilson, verify
```

导入本段使用的标准库、依赖或项目组件。

**L2**

```python
from evaluation.compare_runs import compare
```

导入本段使用的标准库、依赖或项目组件。

**L3**

```python
from supportflow.contracts import Principal
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
from supportflow.store import Store
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import pytest
```

导入本段使用的标准库、依赖或项目组件。

### L8 · test_metric_denominators_latency_cost_unknown

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L8**

```python
def test_metric_denominators_latency_cost_unknown():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

### L9 · row

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L9**

```python
    def row(ok, ms, cost):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L10**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L11**

```python
            "complete": ok,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L12**

```python
            "task_ms": ms,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```python
            "request_ms": [ms],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L14**

```python
            "input_tokens": 1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L15**

```python
            "output_tokens": 1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```python
            "model_cost": cost,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```python
            "judge": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
            "judge_error": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L19**

```python
            "group": "g",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L22**

```python
    a = aggregate([row(True, 10, 0), row(False, 100, None)])
```

以全部任务为分母聚合完成率、nearest-rank P95、真实token与可用成本；另按模板族等权汇总，避免把同族重复实例当作新独立场景。

**L23**

```python
    assert (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```python
        a["completion_rate"] == 0.5
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
        and a["request_p95_ms"] == 100
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L26**

```python
        and a["mean_model_cost"] is None
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```python
    lo, hi = wilson(1, 2)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
    assert lo < 0.5 < hi
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L32 · test_response_claim_does_not_substitute_for_database_state

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L32**

```python
def test_response_claim_does_not_substitute_for_database_state(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L33**

```python
    s = Store(tmp_path / "db")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L34**

```python
    p = Principal("t", "u")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L35**

```python
    a = Principal("t", "a", frozenset({"admin"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
    s.seed_order(a, "ORD1001", 5000, "u")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
    case = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
        "expected": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
            "tools": ["refund_request"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
            "refund_amount": 2000,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
            "refund_status": "pending",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L42**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
    fake_response = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L45**

```python
        "response": "我已完成退款",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
        "_http_status": 200,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
        "trace": {"tools": []},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
    assert not verify(case, [fake_response], s, p)["complete"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

**L50**

```python
    refund = s.refund_request(p, "ORD1001", 2000, "test", "key")
```

检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。

**L51**

```python
    false_claim = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L52**

```python
        "response": "退款成功，已到账",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
        "_http_status": 200,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
        "trace": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
            "tools": [{"name": "refund_request", "success": True, "result": refund}]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L56**

```python
        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
    assert not verify(case, [false_claim], s, p)["checks"]["no_false_settlement_claim"]
```

只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。

### L61 · test_regression_does_not_overwrite_or_mix_datasets

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L61**

```python
def test_regression_does_not_overwrite_or_mix_datasets():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

### L62 · report

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L62**

```python
    def report(rate):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L63**

```python
        return {
```

结束当前函数并把本行构造的结果交给调用方。

**L64**

```python
            "dataset_sha256": "same",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            "evaluated_tasks": 10,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
            "transport": "http",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
            "concurrency_tasks": 1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
            "settings": {"storage": "sqlite"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
            "summaries": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```python
                a: {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L71**

```python
                    "completion_rate": rate,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
                    "request_p95_ms": 10,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
                    "mean_model_cost": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
                for a in ["single", "multi"]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L76**

```python
            },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
    old = report(1)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L80**

```python
    new = report(0.9)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L81**

```python
    assert len(compare(old, new)) == 2
```

先验证两个报告可比较，再按方向检测相对退化，保留原报告不变。

**L82**

```python
    assert old["summaries"]["single"]["completion_rate"] == 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L83**

```python
    new["dataset_sha256"] = "other"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
    with pytest.raises(ValueError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L85**

```python
        compare(old, new)
```

先验证两个报告可比较，再按方向检测相对退化，保留原报告不变。

## 结合全项目看：边界与增强

增加真实供应商、并发进程、故障恢复和独立业务标签验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
