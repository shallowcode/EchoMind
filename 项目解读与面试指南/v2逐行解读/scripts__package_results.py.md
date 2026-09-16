# scripts\package_results.py

## 输入输出流

命令行参数、工作区文件或固定下载源进入维护脚本；输出明确的本地模型、数据集、身份文件、验证记录或学习文档。

## 先理解设计

下载源与结果哈希、文件落点和被忽略的敏感/大文件需一并核对；脚本不会隐式调用付费模型。

源码 SHA256：`b5bde5e138580637a0e479d2edb3e10536f4f5f6688c769977bb65147c2a8cb7`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Package small audit artifacts; omit databases, tokens, model weights and public raw text."""
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

**L6**

```python
import shutil
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L11 · main

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L11**

```python
def main():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L12**

```python
    p = argparse.ArgumentParser()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```python
    p.add_argument("--run", required=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L14**

```python
    p.add_argument("--public", required=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```python
    a = p.parse_args()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L16**

```python
    source = Path(a.run).resolve()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L17**

```python
    public = Path(a.public).resolve()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L18**

```python
    if not source.is_relative_to(ROOT / "artifacts") or not public.is_relative_to(
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L19**

```python
        ROOT / "artifacts"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
        raise ValueError("Only local benchmark artifacts may be packaged")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L22**

```python
    report = json.loads((source / "report.json").read_text(encoding="utf-8"))
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L23**

```python
    if report["source_changed_during_run"]:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L24**

```python
        raise ValueError("Cannot publish measurements with changing source")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L25**

```python
    dest = ROOT / "评测结果" / source.name
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L26**

```python
    dest.mkdir(parents=True, exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
    for f in source.glob("*.json"):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L28**

```python
        shutil.copy2(f, dest / f.name)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```python
    shutil.copy2(source / "REPORT.md", dest / "原始报告.md")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```python
    external = json.loads((public / "report.json").read_text(encoding="utf-8"))
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L31**

```python
    external.pop("records", None)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
    (dest / "public-intents-summary.json").write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```python
        json.dumps(external, ensure_ascii=False, indent=2), encoding="utf-8"
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L34**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
    b = report["summaries"]["single"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
    m = report["summaries"]["multi"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
    ci = report["paired_bootstrap_95"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
    text = f"""# SupportFlow：本地实测交付
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
## 实测结论
```

作者注释，说明约束或设计意图；本行不执行。

**L42**

```python
使用本地 Qwen3-1.7B-Q8_0、真实 Chroma、任务并发 {report["concurrency_tasks"]}，在固定 24 条中文合成开发回归任务上执行两个方案。参评源码运行中没有变化。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
| 指标 | 单 Agent | 多 Agent |
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
|---|---:|---:|
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
| 全部任务完成率 | {b["completed"]}/24（{b["completion_rate"]:.2%}） | {m["completed"]}/24（{m["completion_rate"]:.2%}） |
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
| 复合任务完成率 | {b["groups"]["compound"]["completed"]}/8 | {m["groups"]["compound"]["completed"]}/8 |
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
| HTTP 请求 P95 | {b["request_p95_ms"] / 1000:.2f} 秒 | {m["request_p95_ms"] / 1000:.2f} 秒 |
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
| 平均输入 token / 任务 | {b["mean_input_tokens"]:.1f} | {m["mean_input_tokens"]:.1f} |
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L50**

```python
| 平均输出 token / 任务 | {b["mean_output_tokens"]:.1f} | {m["mean_output_tokens"]:.1f} |
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L51**

```python
| 外部模型 API 费用 | 0 元 | 0 元 |
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
全部任务完成率的观测差为 {(m["completion_rate"] - b["completion_rate"]) * 100:+.2f} 个百分点，配对 bootstrap 95% 区间为 [{ci[0] * 100:.2f}, {ci[1] * 100:.2f}] 个百分点。区间跨 0，不能称为已证明的稳定提升。尤其复合任务仍均为 0/8，**不能将全部任务的差异改写成“复合任务完成率提升”**。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
机器：Intel Core i5-14500、16 GB 内存、CPU 推理；llama.cpp 6 线程、2 推理槽位、总上下文 16384。ASGI 进程内 HTTP 计时不含公网与反向代理，桌面机器并非隔离压测环境。0 元是本地调用不产生外部模型 API 账单；总任务成本没有电费、折旧与利用率数据，仍未知。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
Bitext 外部意图样本：抽取 {external["sampled"]} 条，映射后评估 {external["evaluated"]} 条，准确率 {external["accuracy"]:.2%}，macro-F1 {external["macro_f1"]:.4f}。该报告只评估意图，不与事务完成率混算。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
## 交付内容与验证边界
```

作者注释，说明约束或设计意图；本行不执行。

**L61**

```python
- 已实现订单查询、幂等退款申请、财务审批、沙箱结算及额度预留。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
- 已实现外部支付 outbox、签名回调、幂等入账与回调丢失的主动对账契约，使用模拟 HTTP 验证；真实支付商尚未选择和接通。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
- 已实现工单接单、解决、关闭、版本冲突检查与原会话回写。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
- 已实现租户/属主/角色隔离、token 过期与撤销，HTTP/MCP 共用权限。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
- 已通过真实 MCP SDK 客户端的 HTTP 握手、工具发现、调用与鉴权测试。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
- 已通过真实 Chroma 租户隔离、文档替换、历史摘要召回与画像投影检查。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
- 21 项自动化测试通过；Redis 测试使用 fakeredis，Docker 只做静态检查，尚无本机容器部署证据。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
- 已完成两轮 24 条任务的全链路对照（每轮 48 次任务执行），以及公开意图评测。第一轮与第二轮并发/验证口径不同，不把跨轮变化包装成提升。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```python
## 如何查证与复跑
```

作者注释，说明约束或设计意图；本行不执行。

**L72**

```python
`report.json` 保存数据、模型与源码哈希、预算、依赖和全部汇总；每个 `任务ID-single/multi.json` 保存真实回答、模型/工具 trace、最终退款与工单记录以及逐项判定。公共样本文本未复制到此目录，来源、映射和指标在 `public-intents-summary.json`。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
运行说明见 [SUPPORTFLOW.md](../../SUPPORTFLOW.md)，学习路径见 [新版架构与面试说明](../../项目解读与面试指南/08_SupportFlow实现与评测.md)，口径见 [数据与实验卡](../../项目解读与面试指南/09_数据与实验卡.md)。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
## 当前适合的简历表达
```

作者注释，说明约束或设计意图；本行不执行。

**L78**

```python
“实现带事务工具、人工工单闭环与 MCP 接入的多 Agent 客服系统；建立固定 24 条业务回归任务和 48 条公开意图样本的评测流程，覆盖状态核验、调用追踪、P95、token 成本与回归检测，定位小模型在复合任务规划上的瓶颈。”
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
若需要写提升成果，应更换/确认模型 API 后重新开展同条件对照，并补充独立隐藏测试集。当前不能声称生产质量或复合任务能力已达标。
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
    (dest / "README.md").write_text(text, encoding="utf-8")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L83**

```python
    print(dest)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L87**

```python
    main()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

跨平台运行与远程服务配置应在目标环境复验；学习文档行号需在源码变化后重新生成。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
