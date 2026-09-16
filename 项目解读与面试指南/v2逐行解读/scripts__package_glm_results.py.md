# scripts\package_glm_results.py

## 输入输出流

命令行参数、工作区文件或固定下载源进入维护脚本；输出明确的本地模型、数据集、身份文件、验证记录或学习文档。

## 先理解设计

下载源与结果哈希、文件落点和被忽略的敏感/大文件需一并核对；脚本不会隐式调用付费模型。

源码 SHA256：`23400246ddf71764bf3a1dfc98461195f1b0f7e8d8c14e2fdef7f6c96b172a10`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Publish reproducible GLM reports and traces without copying private configs/databases."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import argparse
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
import shutil
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L12 · main

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L12**

```python
def main():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L13**

```python
    parser = argparse.ArgumentParser()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L14**

```python
    parser.add_argument("runs", nargs="+")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```python
    parser.add_argument(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```python
        "--summary",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```python
        default="GLM-复合任务实测.md",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L18**

```python
        help="Summary filename inside 评测结果; use a separate file for new dataset versions",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
    args = parser.parse_args()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L21**

```python
    if Path(args.summary).name != args.summary:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L22**

```python
        parser.error("summary must be a filename")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L23**

```python
    summary = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
        "# GLM-4.5-Air：复合任务实测",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```python
        "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```python
        "以下来自真实 GLM API、Chroma 检索、鉴权 HTTP 和沙箱账本。每条任务的原始结果、工具证据与状态保留在各实验目录；没有使用 fixture 生成质量指标。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```python
        "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```python
        "| 实验 | 基线 | 增强版 | 增强版复合任务 | HTTP P95 | 每任务模型费估算 |",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```python
        "|---|---:|---:|---:|---:|---:|",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```python
    ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
    for run in args.runs:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L32**

```python
        source = ROOT / run
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
        report = json.loads((source / "report.json").read_text(encoding="utf-8"))
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L34**

```python
        if report["source_changed_during_run"]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L35**

```python
            raise ValueError("Source changed during run: " + run)
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L36**

```python
        if report["settings"]["model_name"] != "glm-4.5-air":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L37**

```python
            raise ValueError("Not the requested model")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L38**

```python
        destination = ROOT / "评测结果" / ("GLM-" + source.name)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
        destination.mkdir(parents=True, exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
        for relative, digest in report["source_sha256"].items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L41**

```python
            path = (ROOT / relative).resolve()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L42**

```python
            if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L43**

```python
                not path.is_relative_to(ROOT)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L45**

```python
            ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
                raise ValueError(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L47**

```python
                    "Cannot archive a different source revision: " + relative
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
                )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
            archived = destination / "source" / relative
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
            archived.parent.mkdir(parents=True, exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L51**

```python
            shutil.copy2(path, archived)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
        for name in [
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L53**

```python
            "requirements.txt",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
            "requirements-dev.txt",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
            ".env.supportflow.example",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L56**

```python
        ]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
            shutil.copy2(ROOT / name, destination / "source" / name)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
        for path in source.glob("*.json"):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L59**

```python
            shutil.copy2(path, destination / path.name)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
        shutil.copy2(source / "REPORT.md", destination / "REPORT.md")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
        report_md = destination / "REPORT.md"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L62**

```python
        report_md.write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
            report_md.read_text(encoding="utf-8").replace(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L64**

```python
                "平均模型调用成本", "按未命中缓存价目表估算的平均模型调用费用"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
            + "\n同目录 source/ 保存与 report.json 哈希相符的源码快照；不含模型密钥。正确拒绝超额退款属于预期处理结果，技术排障建议和 pending 退款申请不等于实际故障修复或资金到账。\n",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
            encoding="utf-8",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L68**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
        base = report["summaries"][report["baseline"]]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L70**

```python
        multi = report["summaries"]["multi"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L71**

```python
        compound_groups = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
            v for k, v in multi["groups"].items() if k.startswith("compound")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
        compound = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
            key: sum(v[key] for v in compound_groups) for key in ["n", "completed"]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
        cost = multi["mean_model_cost"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L78**

```python
        cost_text = f"约 {cost:.5f} 元" if cost is not None else "不可用"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L79**

```python
        summary.append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L80**

```python
            f"| [{report['dataset_version']}，{report['evaluated_tasks']} 条](GLM-{source.name}/REPORT.md) | {report['baseline']}：{base['completed']}/{base['tasks']} | {multi['completed']}/{multi['tasks']} | {compound['completed']}/{compound['n']} | {multi['request_p95_ms'] / 1000:.2f} 秒 | {cost_text} |"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
    summary.extend(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L83**

```python
        [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L85**

```python
            "所有实验任务并发条件见报告；ASGI 进程内 HTTP 包含鉴权、业务、数据库与外部模型 HTTP，不含公网入口/反向代理延迟。模型价目表估算按单次 token 分档，未扣缓存优惠、套餐及赠额，主表不含辅助评委与基础设施费用；评委 token 单列。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
            "v1 是已用于调试的固定开发回归集；v2 为开发后新增的复合回归用例。小样本单次结果不是独立盲测、生产 SLA 或稳定性证明。legacy_multi 使用与新版相同的公共工具保护和 GLM 适配，仅消融任务拆分与合并方式。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
            "任务完成率包含正确拒绝超额退款等预期处理结果。技术任务完成是给出有来源的排查步骤，退款任务完成是建立待审核申请，都不代表实际故障修复或资金到账。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L90**

```python
            "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
            "运行源码 SHA256、数据集 SHA256、配对区间和逐例失败均可在 report.json 与案例 JSON 复核。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
        ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
    target = ROOT / "评测结果" / args.summary
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L95**

```python
    target.write_text("\n".join(summary) + "\n", encoding="utf-8")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L96**

```python
    print(target)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L100**

```python
    main()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

跨平台运行与远程服务配置应在目标环境复验；学习文档行号需在源码变化后重新生成。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
