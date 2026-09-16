# evaluation\public_intents.py

## 输入输出流

固定外部样本和显式标签映射进入 /intents；输出准确率、宏 F1、逐类指标及混淆矩阵。

## 先理解设计

公共英文单轮意图结果单独报告，不能混入中文事务完成率。

源码 SHA256：`d5f88482723bf688f922c7c002a38e56641240182026293feabae7284d1eb931`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Public dataset intent evaluation only; never merge with transaction success metrics."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import argparse
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import asyncio
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
from collections import Counter
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
import sys
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```python
import httpx
```

导入本段使用的标准库、依赖或项目组件。

**L14**

```python
from supportflow.api import create_app
```

导入本段使用的标准库、依赖或项目组件。

**L15**

```python
from supportflow.contracts import Settings, Principal
```

导入本段使用的标准库、依赖或项目组件。

**L17**

```python
# Explicit many-to-one ontology mapping; ambiguous labels excluded rather than relabelled OTHER.
```

作者注释，说明约束或设计意图；本行不执行。

**L18**

```python
MAP = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
    "cancel_order": "request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
    "change_order": "request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
    "change_shipping_address": "request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L22**

```python
    "check_cancellation_fee": "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L23**

```python
    "check_invoice": "invoice",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```python
    "check_payment_methods": "billing",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```python
    "check_refund_policy": "refund",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```python
    "complaint": "complaint",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```python
    "contact_human_agent": "human_handoff",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```python
    "create_account": "account",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```python
    "delete_account": "account",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```python
    "delivery_options": "logistics",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
    "delivery_period": "logistics",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
    "edit_account": "account",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```python
    "get_invoice": "invoice",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
    "get_refund": "refund",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
    "payment_issue": "payment_issue",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L36**

```python
    "place_order": "request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
    "recover_password": "account_security",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
    "registration_problems": "account",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
    "set_up_shipping_address": "request",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
    "switch_account": "account",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
    "track_order": "order_status",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L42**

```python
    "track_refund": "refund",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L46 · main

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L46**

```python
async def main(args):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L47**

```python
    raw = Path(args.dataset).read_bytes()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L48**

```python
    dataset = json.loads(raw)
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L49**

```python
    out = Path("artifacts") / ("public-intents-" + str(time.time_ns()))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
    out.mkdir(parents=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L51**

```python
    s = Settings.from_env().model_copy(update={"db_path": str(out / "state.sqlite")})
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L52**

```python
    if s.model_backend == "fixture":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L53**

```python
        raise ValueError("Public evaluation requires a real model")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L54**

```python
    app = create_app(s)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L55**

```python
    token = app.state.store.issue_token(Principal("external-eval", "evaluator"))
```

签发随机不透明 token，数据库只保存摘要、租户、角色和到期时间。

**L56**

```python
    records = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L57**

```python
    excluded = []
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L58**

```python
    async with (
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L59**

```python
        app.router.lifespan_context(app),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
        httpx.AsyncClient(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L62**

```python
            base_url="http://localhost",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L63**

```python
        ) as client,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
        for i, row in enumerate(dataset["examples"]):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L66**

```python
            if row["label"] not in MAP:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L67**

```python
                excluded.append(row)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L68**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
            r = await client.post(
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L70**

```python
                "/intents",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L71**

```python
                headers={"Authorization": "Bearer " + token},
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
                json={"message": row["message"], "request_id": f"public-{i:04d}"},
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
            pred = r.json().get("intent", "ERROR") if r.status_code == 200 else "ERROR"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
            records.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L76**

```python
                {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
                    **row,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L78**

```python
                    "expected": MAP[row["label"]],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
                    "predicted": pred,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
                    "http_status": r.status_code,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
            print(i, row["label"], pred, flush=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
    labels = sorted(set(MAP.values()))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L85**

```python
    f1 = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L86**

```python
    confusion = Counter((r["expected"], r["predicted"]) for r in records)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L87**

```python
    for label in labels:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L88**

```python
        tp = sum(r["expected"] == r["predicted"] == label for r in records)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L89**

```python
        fp = sum(r["expected"] != label and r["predicted"] == label for r in records)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L90**

```python
        fn = sum(r["expected"] == label and r["predicted"] != label for r in records)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L91**

```python
        f1[label] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L92**

```python
    report = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L93**

```python
        "type": "external-intent-only",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
        "model": s.model_name,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
        "source": dataset["source"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
        "license": dataset["license"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
        "source_sha256": dataset["source_sha256"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
        "mapping": MAP,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L100**

```python
        "sampled": len(dataset["examples"]),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
        "evaluated": len(records),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
        "excluded_labels": sorted({r["label"] for r in excluded}),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L103**

```python
        "accuracy": sum(r["expected"] == r["predicted"] for r in records)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L104**

```python
        / len(records),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L105**

```python
        "macro_f1": sum(f1.values()) / len(f1),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
        "per_class_f1": f1,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L107**

```python
        "confusion": [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L108**

```python
            {"expected": a, "predicted": b, "n": n} for (a, b), n in confusion.items()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
        ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L110**

```python
        "records": records,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L111**

```python
        "limitations": [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
            "Synthetic English public training corpus, not live production traffic",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
            "Many-to-one ontology mapping disclosed",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
            "No refund/order execution score in this report",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
        ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
    (out / "report.json").write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L119**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
    print("REPORT", out, flush=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L123**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L124**

```python
    parser = argparse.ArgumentParser()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L125**

```python
    parser.add_argument("--dataset", default=".runtime/datasets/bitext-sample.json")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L126**

```python
    asyncio.run(main(parser.parse_args()))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

需扩大样本并由独立标注者复核映射，评估其他语言与分布偏移。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
