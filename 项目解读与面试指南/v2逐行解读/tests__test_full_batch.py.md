# tests\test_full_batch.py

## 输入输出流

临时文件和合成结果进入测试；输出断点保留失败、错误分母、配置/源码冻结与族级配对统计断言。

## 先理解设计

关注长跑恢复与可比性，拒绝源码改变后混入同一报告；不使用真实模型或消费验收响应。

源码 SHA256：`6bfb5100b4cce27940d13102729d145bfab3dc3e8e01e8216fe07221af671cb6`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L3**

```python
import pytest
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from scripts.run_full_evaluation import (
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
    atomic,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L8**

```python
    failure_record,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L9**

```python
    freeze,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L10**

```python
    paired,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```python
    summarize_public,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L12**

```python
)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```python
from supportflow.contracts import Settings
```

导入本段使用的标准库、依赖或项目组件。

### L16 · test_windows_replace_retries_and_progress_is_best_effort

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L16**

```python
def test_windows_replace_retries_and_progress_is_best_effort(tmp_path, monkeypatch):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L17**

```python
    import scripts.run_full_evaluation as module
```

导入本段使用的标准库、依赖或项目组件。

**L19**

```python
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
    original = Path.replace
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L21**

```python
    calls = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L23 · transient

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L23**

```python
    def transient(self, target):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L24**

```python
        calls.append(target)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L25**

```python
        if len(calls) == 1:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L26**

```python
            raise PermissionError("sharing violation")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L27**

```python
        return original(self, target)
```

结束当前函数并把本行构造的结果交给调用方。

**L29**

```python
    monkeypatch.setattr(Path, "replace", transient)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```python
    assert atomic(tmp_path / "result.json", {"saved": True})
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
    assert len(calls) == 2
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L33 · blocked

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L33**

```python
    def blocked(self, target):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L34**

```python
        raise PermissionError("held open")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L36**

```python
    monkeypatch.setattr(Path, "replace", blocked)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
    assert atomic(tmp_path / "progress.json", {}, best_effort=True) is False
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
    with pytest.raises(PermissionError):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L39**

```python
        atomic(tmp_path / "required-result.json", {})
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L42 · test_checkpoints_keep_failures_and_public_errors_in_denominator

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L42**

```python
def test_checkpoints_keep_failures_and_public_errors_in_denominator(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L43**

```python
    c = {"id": "c", "group": "g", "family": "f", "split": "development"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
    row = failure_record(c, "multi", TimeoutError(), 5)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L45**

```python
    path = tmp_path / "result.json"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L46**

```python
    atomic(path, row)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
    assert json.loads(path.read_text())["complete"] is False
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L48**

```python
    assert not path.with_suffix(".json.tmp").exists()
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L49**

```python
    base = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
        "expected": "refund",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L51**

```python
        "http_status": 200,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
        "model_failed": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
        "trace": {"input_tokens": 1, "output_tokens": 1},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
    metrics = summarize_public(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
        [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
            {**base, "predicted": "refund"},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
            {**base, "predicted": "ERROR", "http_status": 0},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
    assert (
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
        metrics["evaluated"] == 2
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L63**

```python
        and metrics["accuracy"] == 0.5
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L64**

```python
        and metrics["http_errors"] == 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L65**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L68 · test_resume_freeze_rejects_changed_source_or_settings

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L68**

```python
def test_resume_freeze_rejects_changed_source_or_settings(tmp_path, monkeypatch):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L69**

```python
    import scripts.run_full_evaluation as module
```

导入本段使用的标准库、依赖或项目组件。

**L71**

```python
    monkeypatch.setattr(module, "ROOT", tmp_path)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
    source = tmp_path / "scripts/a.py"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
    source.parent.mkdir()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
    source.write_text("x=1")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
    for split in module.SPLITS:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L76**

```python
        p = tmp_path / f".runtime/datasets/bitext-v2/{split}.json"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L77**

```python
        atomic(p, {"examples": []})
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L78**

```python
    out = tmp_path / "output"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L79**

```python
    out.mkdir()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
    s = Settings(model_key="private")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L81**

```python
    frozen = freeze(out, s)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L82**

```python
    assert "model_key" not in frozen["settings"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
    assert freeze(out, s) == frozen
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
    with pytest.raises(ValueError, match="changed"):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L85**

```python
        freeze(out, s.model_copy(update={"model_name": "other"}))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L86**

```python
    source.write_text("x=2")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L87**

```python
    with pytest.raises(ValueError, match="changed"):
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L88**

```python
        freeze(out, s)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L91 · test_paired_family_weights_and_missing_arm

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L91**

```python
def test_paired_family_weights_and_missing_arm():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L92**

```python
    rows = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L93**

```python
    for i in range(25):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L94**

```python
        rows += [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L95**

```python
            {"id": str(i), "family": "a", "variant": a, "complete": a == "multi"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L96**

```python
            for a in ["single", "multi"]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L97**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
    rows += [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L99**

```python
        {"id": "b", "family": "b", "variant": a, "complete": a == "single"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L100**

```python
        for a in ["single", "multi"]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L101**

```python
    ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
    rows += [{"id": "incomplete", "family": "c", "variant": "single", "complete": True}]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L103**

```python
    assert paired(rows)["family_count"] == 2
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L104**

```python
    assert paired(rows)["family_macro_delta"] == 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

## 结合全项目看：边界与增强

测试通过不证明网络全天稳定；后台状态、最终报告和逐例原始数据才是实际执行证据。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
