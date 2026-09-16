# evaluation\compare_runs.py

## 输入输出流

显式旧/新报告路径进入可比性检查；输出相对退化事件并用退出码支持 CI。

## 先理解设计

从不覆写基线；5% 是工程门槛，不是统计显著性的证明。

源码 SHA256：`99492c862659a777d5b89be784a0d551fe44125ec23dca0aa265e5ea5a806c8c`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Explicit immutable report comparison; 5% is a configured gate, not proof of significance."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import argparse
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

### L8 · compare

先验证两个报告可比较，再按方向检测相对退化，保留原报告不变。

**L8**

```python
def compare(old, new, threshold=0.05):
```

先验证两个报告可比较，再按方向检测相对退化，保留原报告不变。

**L9**

```python
    for key in ["dataset_sha256", "evaluated_tasks", "transport", "concurrency_tasks"]:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L10**

```python
        if old[key] != new[key]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L11**

```python
            raise ValueError("Incomparable report field: " + key)
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L12**

```python
    if old["settings"]["storage"] != new["settings"]["storage"]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L13**

```python
        raise ValueError("Storage backend differs")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L14**

```python
    events = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```python
    for arm in ["single", "multi"]:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L16**

```python
        for metric, higher in [
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L17**

```python
            ("completion_rate", True),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
            ("request_p95_ms", False),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L19**

```python
            ("mean_model_cost", False),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
        ]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
            a = old["summaries"][arm][metric]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L22**

```python
            b = new["summaries"][arm][metric]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L23**

```python
            if a is None or b is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L24**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```python
            relative = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L26**

```python
                ((a - b) if higher else (b - a)) / abs(a)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```python
                if a
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L28**

```python
                else (float("inf") if (b > a and not higher) else 0)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```python
            if relative > threshold:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L31**

```python
                events.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L32**

```python
                    {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```python
                        "variant": arm,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
                        "metric": metric,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
                        "before": a,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L36**

```python
                        "after": b,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
                        "relative_regression": relative,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
                    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
    return events
```

结束当前函数并把本行构造的结果交给调用方。

**L43**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L44**

```python
    p = argparse.ArgumentParser()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L45**

```python
    p.add_argument("--baseline", required=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L46**

```python
    p.add_argument("--candidate", required=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L47**

```python
    p.add_argument("--threshold", type=float, default=0.05)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L48**

```python
    a = p.parse_args()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L49**

```python
    events = compare(
```

先验证两个报告可比较，再按方向检测相对退化，保留原报告不变。

**L50**

```python
        json.loads(Path(a.baseline).read_text()),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L51**

```python
        json.loads(Path(a.candidate).read_text()),
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L52**

```python
        a.threshold,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
    print(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
        json.dumps(
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L56**

```python
            {"regressions": events, "baseline_overwritten": False},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
            ensure_ascii=False,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L58**

```python
            indent=2,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L59**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
    raise SystemExit(bool(events))
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

## 结合全项目看：边界与增强

应加入多次重复、稳定性区间与更细的配置兼容约束。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
