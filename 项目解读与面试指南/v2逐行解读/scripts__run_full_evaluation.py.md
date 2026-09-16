# scripts\run_full_evaluation.py

## 输入输出流

私有GLM配置、固定业务三分区和公开意图三分区进入独立后台脚本；输出源码/数据快照、逐例原子JSON、status.json及最终REPORT.md/report.json。

## 先理解设计

业务并发2、意图串行1；完成记录包含失败且不重跑。恢复时核对源码/数据/配置哈希，未落盘的任务用新沙箱重启；身份令牌提前刷新，不依赖Codex持续检查。

源码 SHA256：`85d2cd3d23b06789d40efbc8dc138859ee741ce3a6a263312ab256fd06df5c28`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Unattended frozen GLM evaluation. Checkpoint each result, resume without cherry-picking.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
Runs all three splits; acceptance is exposed when executed. No model-based Judge.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
Business concurrency two; one concurrent serial public-intent stream.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```python
import argparse
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
import asyncio
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
from collections import Counter, defaultdict
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
from dataclasses import asdict
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
from datetime import datetime, timezone
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L14**

```python
import os
```

导入本段使用的标准库、依赖或项目组件。

**L15**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L16**

```python
import random
```

导入本段使用的标准库、依赖或项目组件。

**L17**

```python
import shutil
```

导入本段使用的标准库、依赖或项目组件。

**L18**

```python
import statistics
```

导入本段使用的标准库、依赖或项目组件。

**L19**

```python
import sys
```

导入本段使用的标准库、依赖或项目组件。

**L20**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L21**

```python
from types import SimpleNamespace
```

导入本段使用的标准库、依赖或项目组件。

**L23**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
sys.path.insert(0, str(ROOT))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```python
import httpx
```

导入本段使用的标准库、依赖或项目组件。

**L26**

```python
from evaluation.full_chain import aggregate, run_case
```

导入本段使用的标准库、依赖或项目组件。

**L27**

```python
from evaluation.public_intents import MAP
```

导入本段使用的标准库、依赖或项目组件。

**L28**

```python
from supportflow.api import create_app
```

导入本段使用的标准库、依赖或项目组件。

**L29**

```python
from supportflow.contracts import Principal, Settings, Trace
```

导入本段使用的标准库、依赖或项目组件。

**L30**

```python
from supportflow.model import Model, active_trace
```

导入本段使用的标准库、依赖或项目组件。

**L32**

```python
SPLITS = ("development", "validation", "acceptance")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L35 · atomic

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L35**

```python
def atomic(path, value, best_effort=False):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L36**

```python
    path.parent.mkdir(parents=True, exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
    temp = path.with_suffix(path.suffix + ".tmp")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
    with temp.open("w", encoding="utf-8") as stream:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L39**

```python
        json.dump(value, stream, ensure_ascii=False, indent=2)
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L40**

```python
        stream.flush()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
        os.fsync(stream.fileno())
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L42**

```python
    for attempt in range(3 if best_effort else 20):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L43**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
            temp.replace(path)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
            return True
```

结束当前函数并把本行构造的结果交给调用方。

**L46**

```python
        except PermissionError:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L47**

```python
            if attempt == (2 if best_effort else 19):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L48**

```python
                if best_effort:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L49**

```python
                    return False
```

结束当前函数并把本行构造的结果交给调用方。

**L50**

```python
                raise
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L51**

```python
            time.sleep(0.1)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L54 · read

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L54**

```python
def read(path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L55**

```python
    return json.loads(path.read_text(encoding="utf-8"))
```

结束当前函数并把本行构造的结果交给调用方。

### L58 · freeze

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L58**

```python
def freeze(out, settings):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L59**

```python
    paths = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L60**

```python
        p
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
        for folder in (
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L62**

```python
            "supportflow",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
            "agents",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
            "core",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            "evaluation",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
            "skills",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
            "scripts",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
        for p in (ROOT / folder).rglob("*")
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L70**

```python
        if p.is_file()
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L71**

```python
        and p.suffix in {".py", ".json", ".md"}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
        and "__pycache__" not in p.parts
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
    ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
    paths += [ROOT / ".runtime/datasets/bitext-v2" / (s + ".json") for s in SPLITS]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
    manifest = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L76**

```python
        "hashes": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L78**

```python
            for p in paths
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L79**

```python
        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
        "settings": settings.model_dump(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
            exclude={"model_key", "redis_url", "payment_key", "payment_webhook_secret"}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L82**

```python
        ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
        "business_concurrency": 2,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
        "public_concurrency": 1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L85**

```python
        "judge": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
        "acceptance_policy": "Authorized full run of all splits; results expose acceptance. No tuning during execution.",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
    saved = out / "manifest.json"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L89**

```python
    if saved.exists():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L90**

```python
        if read(saved) != manifest:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L91**

```python
            raise ValueError(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L92**

```python
                "Source, data or model settings changed; use a new output directory"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
    else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L95**

```python
        for p in paths:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L96**

```python
            target = out / "source" / p.relative_to(ROOT)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L97**

```python
            target.parent.mkdir(parents=True, exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L98**

```python
            shutil.copy2(p, target)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
        atomic(saved, manifest)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L100**

```python
    return manifest
```

结束当前函数并把本行构造的结果交给调用方。

### L103 · failure_record

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L103**

```python
def failure_record(case, arm, error, elapsed):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L104**

```python
    return {
```

结束当前函数并把本行构造的结果交给调用方。

**L105**

```python
        "id": case["id"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
        "group": case["group"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L107**

```python
        "family": case["family"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L108**

```python
        "split": case["split"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
        "variant": arm,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L110**

```python
        "complete": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L111**

```python
        "checks": {"harness_execution": False},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
        "error": type(error).__name__,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
        "task_ms": elapsed * 1000,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
        "request_ms": [],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
        "input_tokens": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
        "output_tokens": 0,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
        "model_cost": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
        "judge": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L119**

```python
        "judge_error": None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
        "responses": [],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L121**

```python
        "usage_complete": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L122**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L125 · summarize_public

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L125**

```python
def summarize_public(rows):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L126**

```python
    labels = sorted(set(MAP.values()))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L127**

```python
    f1 = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L128**

```python
    for label in labels:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L129**

```python
        tp = sum(r["expected"] == r["predicted"] == label for r in rows)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L130**

```python
        fp = sum(r["expected"] != label and r["predicted"] == label for r in rows)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L131**

```python
        fn = sum(r["expected"] == label and r["predicted"] != label for r in rows)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L132**

```python
        f1[label] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L133**

```python
    return {
```

结束当前函数并把本行构造的结果交给调用方。

**L134**

```python
        "evaluated": len(rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L135**

```python
        "accuracy": sum(r["expected"] == r["predicted"] for r in rows) / len(rows)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L136**

```python
        if rows
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L137**

```python
        else None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L138**

```python
        "macro_f1": statistics.mean(f1.values()) if rows else None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L139**

```python
        "per_class_f1": f1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
        "http_errors": sum(r["http_status"] != 200 for r in rows),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L141**

```python
        "model_failures": sum(r["model_failed"] for r in rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L142**

```python
        "input_tokens": sum(r["trace"]["input_tokens"] for r in rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L143**

```python
        "output_tokens": sum(r["trace"]["output_tokens"] for r in rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L144**

```python
        "confusion": [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L145**

```python
            {"expected": a, "predicted": b, "n": n}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L146**

```python
            for (a, b), n in Counter(
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L147**

```python
                (r["expected"], r["predicted"]) for r in rows
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L148**

```python
            ).items()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L149**

```python
        ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L150**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L153 · paired

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L153**

```python
def paired(rows):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L154**

```python
    pairs = defaultdict(dict)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L155**

```python
    for row in rows:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L156**

```python
        pairs[row["id"]][row["variant"]] = row
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L157**

```python
    families = defaultdict(list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L158**

```python
    for arms in pairs.values():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L159**

```python
        if set(arms) == {"single", "multi"}:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L160**

```python
            families[arms["multi"]["family"]].append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L161**

```python
                int(arms["multi"]["complete"]) - int(arms["single"]["complete"])
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L162**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L163**

```python
    means = [statistics.mean(v) for v in families.values()]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L164**

```python
    rng = random.Random(42)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L165**

```python
    boots = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L166**

```python
        sorted(statistics.mean(rng.choices(means, k=len(means))) for _ in range(2000))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L167**

```python
        if means
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L168**

```python
        else []
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L169**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L170**

```python
    return {
```

结束当前函数并把本行构造的结果交给调用方。

**L171**

```python
        "family_count": len(means),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L172**

```python
        "family_macro_delta": statistics.mean(means) if means else None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L173**

```python
        "family_bootstrap_95": [boots[49], boots[1949]] if boots else None,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L174**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L177 · run

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L177**

```python
async def run(out):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L178**

```python
    out.mkdir(parents=True, exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L179**

```python
    settings = Settings.from_env()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L180**

```python
    if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L181**

```python
        settings.model_name != "glm-4.5-air"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L182**

```python
        or settings.model_backend == "fixture"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L183**

```python
        or settings.business_mode != "sandbox"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L184**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L185**

```python
        raise ValueError("Requires GLM-4.5-Air real model and sandbox business backend")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L186**

```python
    # An OS lock prevents two processes from racing checkpoints; it releases on crash.
```

作者注释，说明约束或设计意图；本行不执行。

**L187**

```python
    lock = (out / "run.lock").open("a+b")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L188**

```python
    lock.seek(0)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L189**

```python
    if os.name == "nt":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L190**

```python
        import msvcrt
```

导入本段使用的标准库、依赖或项目组件。

**L192**

```python
        if not lock.read(1):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L193**

```python
            lock.write(b"0")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L194**

```python
            lock.flush()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L195**

```python
        lock.seek(0)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L196**

```python
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L197**

```python
    else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L198**

```python
        import fcntl
```

导入本段使用的标准库、依赖或项目组件。

**L200**

```python
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L201**

```python
    manifest = freeze(out, settings)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L202**

```python
    records_dir = out / "records"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L203**

```python
    records_dir.mkdir(exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L204**

```python
    business = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L205**

```python
        c
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L206**

```python
        for split in SPLITS
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L207**

```python
        for c in read(ROOT / f"evaluation/datasets/trial-v3/{split}.json")["cases"]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L208**

```python
    ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L209**

```python
    public = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L210**

```python
        (split, row)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L211**

```python
        for split in SPLITS
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L212**

```python
        for row in read(ROOT / f".runtime/datasets/bitext-v2/{split}.json")["examples"]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L213**

```python
    ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L214**

```python
    assert len(business) == 1200 and len(public) == 2700
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L215**

```python
    # User reduced execution budget after launch. Keep the existing ordered prefix;
```

作者注释，说明约束或设计意图；本行不执行。

**L216**

```python
    # never choose the subset based on observed scores.
```

作者注释，说明约束或设计意图；本行不执行。

**L217**

```python
    business = business[:600]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L218**

```python
    public = [(split, row) for split, row in public if row["label"] in MAP][:1200]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L219**

```python
    business_rows, public_rows = {}, {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L220**

```python
    for p in records_dir.glob("business-*.json"):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L221**

```python
        row = read(p)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L222**

```python
        business_rows[(row["id"], row["variant"])] = row
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L223**

```python
    for p in records_dir.glob("public-*.json"):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L224**

```python
        row = read(p)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L225**

```python
        public_rows[row["source_row"]] = row
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L226**

```python
    started = time.time()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L227**

```python
    session = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L228**

```python
    work = out / "work" / session
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L229**

```python
    work.mkdir(parents=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L231 · status

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L231**

```python
    def status(state="running", error=None):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L232**

```python
        payload = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L233**

```python
            "state": state,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L234**

```python
            "pid": os.getpid(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L235**

```python
            "updated_utc": datetime.now(timezone.utc).isoformat(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L236**

```python
            "session_elapsed_seconds": time.time() - started,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L237**

```python
            "business_done": len(business_rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L238**

```python
            "business_total": len(business) * 2,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L239**

```python
            "public_done": len(public_rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L240**

```python
            "public_total": len(public),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L241**

```python
            "public_excluded": 300,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L242**

```python
            "judge": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L243**

```python
            "error": error,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L244**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L245**

```python
        # A viewer/antivirus may hold a Windows file handle. Progress is advisory;
```

作者注释，说明约束或设计意图；本行不执行。

**L246**

```python
        # failures here must never abort already-checkpointed model work.
```

作者注释，说明约束或设计意图；本行不执行。

**L247**

```python
        for filename in ("progress.json", "status.json"):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L248**

```python
            try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L249**

```python
                atomic(out / filename, payload, best_effort=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L250**

```python
            except OSError:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L251**

```python
                pass
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L253 · business_stream

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L253**

```python
    async def business_stream():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L254**

```python
        queue = asyncio.Queue()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L255**

```python
        # Finish each split before exposing the next; no adaptive tuning between splits.
```

作者注释，说明约束或设计意图；本行不执行。

**L256**

```python
        for split in SPLITS:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L257**

```python
            cases = [c for c in business if c["split"] == split]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L258**

```python
            random.Random(20260909).shuffle(cases)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L259**

```python
            for i, c in enumerate(cases):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L260**

```python
                queue.put_nowait(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L261**

```python
                    (c, ["single", "multi"] if i % 2 == 0 else ["multi", "single"])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L262**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L264 · worker

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L264**

```python
            async def worker():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L265**

```python
                while not queue.empty():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L266**

```python
                    case, arms = queue.get_nowait()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L267**

```python
                    try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L268**

```python
                        for arm in arms:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L269**

```python
                            if (case["id"], arm) in business_rows:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L270**

```python
                                continue  # Keep failures too: never rerun until a pass.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L271**

```python
                            t = time.perf_counter()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L272**

```python
                            try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L273**

```python
                                row = await run_case(
```

为每个案例与实验组隔离用户和账本，通过 HTTP 执行每轮消息及人工流程。

**L274**

```python
                                    case, arm, SimpleNamespace(judge=False), work
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L275**

```python
                                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L276**

```python
                            except Exception as exc:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L277**

```python
                                row = failure_record(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L278**

```python
                                    case, arm, exc, time.perf_counter() - t
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L279**

```python
                                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L280**

```python
                            atomic(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L281**

```python
                                records_dir / f"business-{case['id']}-{arm}.json", row
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L282**

```python
                            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L283**

```python
                            business_rows[(case["id"], arm)] = row
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L284**

```python
                            status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L285**

```python
                    finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L286**

```python
                        queue.task_done()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L288**

```python
            await asyncio.gather(worker(), worker())
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

### L290 · public_stream

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L290**

```python
    async def public_stream():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L291**

```python
        app = create_app(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L292**

```python
            settings.model_copy(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L293**

```python
                update={
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L294**

```python
                    "db_path": str(work / "public.sqlite3"),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L295**

```python
                    "chroma_path": str(work / "public-chroma"),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L296**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L297**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L298**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L299**

```python
        p = Principal("public-full-eval", "evaluator")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L300**

```python
        token = None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L301**

```python
        issued = 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L302**

```python
        async with (
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L303**

```python
            app.router.lifespan_context(app),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L304**

```python
            httpx.AsyncClient(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L305**

```python
                transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L306**

```python
                base_url="http://localhost",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L307**

```python
                timeout=settings.model_timeout + 30,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L308**

```python
            ) as client,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L309**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L310**

```python
            for split, row in public:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L311**

```python
                if row["label"] not in MAP or row["source_row"] in public_rows:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L312**

```python
                    continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L313**

```python
                if time.monotonic() - issued > 1800 or token is None:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L314**

```python
                    token = app.state.store.issue_token(p, ttl=3600)
```

签发随机不透明 token，数据库只保存摘要、租户、角色和到期时间。

**L315**

```python
                    issued = time.monotonic()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L316**

```python
                trace = Trace("public-" + str(row["source_row"]))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L317**

```python
                marker = active_trace.set(trace)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L318**

```python
                t = time.perf_counter()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L319**

```python
                body, http_status, error = {}, 0, None
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L320**

```python
                try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L321**

```python
                    r = await client.post(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L322**

```python
                        "/intents",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L323**

```python
                        headers={"Authorization": "Bearer " + token},
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L324**

```python
                        json={
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L325**

```python
                            "message": row["message"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L326**

```python
                            "request_id": trace.request_id,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L327**

```python
                        },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L328**

```python
                    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L329**

```python
                    http_status = r.status_code
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L330**

```python
                    body = r.json()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L331**

```python
                except Exception as exc:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L332**

```python
                    error = type(exc).__name__
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L333**

```python
                finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L334**

```python
                    active_trace.reset(marker)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L335**

```python
                record = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L336**

```python
                    **row,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L337**

```python
                    "split": split,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L338**

```python
                    "expected": MAP[row["label"]],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L339**

```python
                    "predicted": body.get("intent", "ERROR")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L340**

```python
                    if http_status == 200
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L341**

```python
                    else "ERROR",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L342**

```python
                    "http_status": http_status,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L343**

```python
                    "error": error,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L344**

```python
                    "model_failed": bool(trace.failures)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L345**

```python
                    or "LLM 失败" in body.get("reasoning", ""),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L346**

```python
                    "latency_ms": (time.perf_counter() - t) * 1000,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L347**

```python
                    "trace": asdict(trace),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L348**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L349**

```python
                atomic(records_dir / f"public-{row['source_row']}.json", record)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L350**

```python
                public_rows[row["source_row"]] = record
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L351**

```python
                status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L353 · heartbeat

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L353**

```python
    async def heartbeat():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L354**

```python
        while True:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L355**

```python
            status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L356**

```python
            await asyncio.sleep(30)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L358**

```python
    status()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L359**

```python
    beat = asyncio.create_task(heartbeat())
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L360**

```python
    try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L361**

```python
        # One excluded warmup. Authentication/provider failures stop before the paid batch.
```

作者注释，说明约束或设计意图；本行不执行。

**L362**

```python
        warm = Model(settings)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L363**

```python
        try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L364**

```python
            await warm.complete(
```

执行一次真实模型 HTTP 请求；把供应商返回的 usage 累加到当前请求 trace。

**L365**

```python
                [{"role": "user", "content": "回复准备好了"}], max_tokens=16
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L366**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L367**

```python
        finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L368**

```python
            await warm.close()
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L369**

```python
        await asyncio.gather(business_stream(), public_stream())
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L370**

```python
        rows = list(business_rows.values())
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L371**

```python
        report = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L372**

```python
            "model": settings.model_name,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L373**

```python
            "manifest": "manifest.json",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L374**

```python
            "business": {},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L375**

```python
            "public": {},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L376**

```python
            "paired": {},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L377**

```python
            "scope": {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L378**

```python
                "business_cases": 600,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L379**

```python
                "business_executions": 1200,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L380**

```python
                "public_executions": 1200,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L381**

```python
                "selection": "Development business split and first 1200 mapped development public rows; reduced by user mid-run, not score-selected",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L382**

```python
                "validation_executed": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L383**

```python
                "acceptance_executed": False,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L384**

```python
            },
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L385**

```python
            "source_changed": any(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L386**

```python
                hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L387**

```python
                for path, digest in manifest["hashes"].items()
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L388**

```python
            ),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L389**

```python
            "limitations": [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L390**

```python
                "Authored parameterized sandbox tasks and public synthetic intent corpus; no enterprise traffic",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L391**

```python
                "Reduced run: development only. Public prefix is not label-balanced; do not generalize its score to the full 2700 samples. Validation and acceptance not executed.",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L392**

```python
                "Concurrent public stream shares model quota and local machine; P95 includes this contention",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L393**

```python
                "ASGI HTTP excludes external front proxy; no Judge calls",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L394**

```python
                "Failed cases remain in denominators and are never automatically retried; interrupted uncheckpointed work restarts in fresh sandbox and can incur extra cost",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L395**

```python
                "Costs are uncached versioned estimates, not invoices; latency excludes fixture setup",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L396**

```python
                "Keyword state and reply checks are not complete semantic proof",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L397**

```python
            ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L398**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L399**

```python
        for split in ("development", "all"):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L400**

```python
            selected = [r for r in rows if split == "all" or r["split"] == split]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L401**

```python
            report["business"][split] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L402**

```python
                a: aggregate([r for r in selected if r["variant"] == a])
```

以全部任务为分母聚合完成率、nearest-rank P95、真实token与可用成本；另按模板族等权汇总，避免把同族重复实例当作新独立场景。

**L403**

```python
                for a in ["single", "multi"]
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L404**

```python
            }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L405**

```python
            report["paired"][split] = paired(selected)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L406**

```python
            report["public"][split] = summarize_public(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L407**

```python
                [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L408**

```python
                    r
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L409**

```python
                    for r in public_rows.values()
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L410**

```python
                    if split == "all" or r["split"] == split
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L411**

```python
                ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L412**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L413**

```python
        report["runner_maintenance"] = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L414**

```python
            read(out / "runner-maintenance.json")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L415**

```python
            if (out / "runner-maintenance.json").exists()
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L416**

```python
            else []
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L417**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L418**

```python
        atomic(out / "report.json", report)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L419**

```python
        lines = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L420**

```python
            "# GLM 全量评测",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L421**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L422**

```python
            "按用户要求缩减：600条开发业务任务各运行single/multi，共1200次；公开意图取开发集前1200条可映射样本。未执行验证/验收集。意图前缀子集不保证标签均衡。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L423**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L424**

```python
            "| 分区 | single完成 | multi完成 | multi请求P95 | 意图准确率 | 意图宏F1 |",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L425**

```python
            "|---|---:|---:|---:|---:|---:|",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L426**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L427**

```python
        for split in ("development", "all"):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L428**

```python
            a, b = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L429**

```python
                report["business"][split]["single"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L430**

```python
                report["business"][split]["multi"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L431**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L432**

```python
            public_metrics = report["public"][split]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L433**

```python
            latency = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L434**

```python
                f"{b['request_p95_ms'] / 1000:.2f}秒"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L435**

```python
                if b["request_p95_ms"] is not None
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L436**

```python
                else "不可用"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L437**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L438**

```python
            lines.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L439**

```python
                f"| {split} | {a['completed']}/{a['tasks']} | {b['completed']}/{b['tasks']} | {latency} | {public_metrics['accuracy']:.2%} | {public_metrics['macro_f1']:.3f} |"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L440**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L441**

```python
        lines += [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L442**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L443**

```python
            "完整指标、失败、族级区间、真实用量及费用估算见 report.json 与 records/。同目录 source/ 为开跑前源码及数据快照，排除密钥。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L444**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L445**

```python
            "本次业务并发2，同时运行1条串行意图评测流，不能与无竞争环境的历史P95直接比较。没有运行额外LLM评委。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L446**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L447**

```python
            f"运行期间源码改变：{report['source_changed']}。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L448**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L449**

```python
        (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L450**

```python
        status("completed")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L451**

```python
    except BaseException as exc:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L452**

```python
        status("failed", type(exc).__name__)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L453**

```python
        raise
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L454**

```python
    finally:
```

无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。

**L455**

```python
        beat.cancel()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L456**

```python
        lock.close()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L459**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L460**

```python
    parser = argparse.ArgumentParser()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L461**

```python
    parser.add_argument("--output", default="artifacts/glm-full-20260909")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L462**

```python
    args = parser.parse_args()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L463**

```python
    asyncio.run(run(Path(args.output).resolve()))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

运行全部分区意味着验收样本暴露；公共意图流会竞争模型额度与本机资源，P95不能直接与旧单独运行对比。暂不开Judge，重复付费仅可能发生在中断但尚未落盘的任务。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
