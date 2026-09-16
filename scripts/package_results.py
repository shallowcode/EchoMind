"""Package small audit artifacts; omit databases, tokens, model weights and public raw text."""

import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--public", required=True)
    a = p.parse_args()
    source = Path(a.run).resolve()
    public = Path(a.public).resolve()
    if not source.is_relative_to(ROOT / "artifacts") or not public.is_relative_to(
        ROOT / "artifacts"
    ):
        raise ValueError("Only local benchmark artifacts may be packaged")
    report = json.loads((source / "report.json").read_text(encoding="utf-8"))
    if report["source_changed_during_run"]:
        raise ValueError("Cannot publish measurements with changing source")
    dest = ROOT / "评测结果" / source.name
    dest.mkdir(parents=True, exist_ok=True)
    for f in source.glob("*.json"):
        shutil.copy2(f, dest / f.name)
    shutil.copy2(source / "REPORT.md", dest / "原始报告.md")
    external = json.loads((public / "report.json").read_text(encoding="utf-8"))
    external.pop("records", None)
    (dest / "public-intents-summary.json").write_text(
        json.dumps(external, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    b = report["summaries"]["single"]
    m = report["summaries"]["multi"]
    ci = report["paired_bootstrap_95"]
    text = f"""# SupportFlow：本地实测交付

## 实测结论

使用本地 Qwen3-1.7B-Q8_0、真实 Chroma、任务并发 {report["concurrency_tasks"]}，在固定 24 条中文合成开发回归任务上执行两个方案。参评源码运行中没有变化。

| 指标 | 单 Agent | 多 Agent |
|---|---:|---:|
| 全部任务完成率 | {b["completed"]}/24（{b["completion_rate"]:.2%}） | {m["completed"]}/24（{m["completion_rate"]:.2%}） |
| 复合任务完成率 | {b["groups"]["compound"]["completed"]}/8 | {m["groups"]["compound"]["completed"]}/8 |
| HTTP 请求 P95 | {b["request_p95_ms"] / 1000:.2f} 秒 | {m["request_p95_ms"] / 1000:.2f} 秒 |
| 平均输入 token / 任务 | {b["mean_input_tokens"]:.1f} | {m["mean_input_tokens"]:.1f} |
| 平均输出 token / 任务 | {b["mean_output_tokens"]:.1f} | {m["mean_output_tokens"]:.1f} |
| 外部模型 API 费用 | 0 元 | 0 元 |

全部任务完成率的观测差为 {(m["completion_rate"] - b["completion_rate"]) * 100:+.2f} 个百分点，配对 bootstrap 95% 区间为 [{ci[0] * 100:.2f}, {ci[1] * 100:.2f}] 个百分点。区间跨 0，不能称为已证明的稳定提升。尤其复合任务仍均为 0/8，**不能将全部任务的差异改写成“复合任务完成率提升”**。

机器：Intel Core i5-14500、16 GB 内存、CPU 推理；llama.cpp 6 线程、2 推理槽位、总上下文 16384。ASGI 进程内 HTTP 计时不含公网与反向代理，桌面机器并非隔离压测环境。0 元是本地调用不产生外部模型 API 账单；总任务成本没有电费、折旧与利用率数据，仍未知。

Bitext 外部意图样本：抽取 {external["sampled"]} 条，映射后评估 {external["evaluated"]} 条，准确率 {external["accuracy"]:.2%}，macro-F1 {external["macro_f1"]:.4f}。该报告只评估意图，不与事务完成率混算。

## 交付内容与验证边界

- 已实现订单查询、幂等退款申请、财务审批、沙箱结算及额度预留。
- 已实现外部支付 outbox、签名回调、幂等入账与回调丢失的主动对账契约，使用模拟 HTTP 验证；真实支付商尚未选择和接通。
- 已实现工单接单、解决、关闭、版本冲突检查与原会话回写。
- 已实现租户/属主/角色隔离、token 过期与撤销，HTTP/MCP 共用权限。
- 已通过真实 MCP SDK 客户端的 HTTP 握手、工具发现、调用与鉴权测试。
- 已通过真实 Chroma 租户隔离、文档替换、历史摘要召回与画像投影检查。
- 21 项自动化测试通过；Redis 测试使用 fakeredis，Docker 只做静态检查，尚无本机容器部署证据。
- 已完成两轮 24 条任务的全链路对照（每轮 48 次任务执行），以及公开意图评测。第一轮与第二轮并发/验证口径不同，不把跨轮变化包装成提升。

## 如何查证与复跑

`report.json` 保存数据、模型与源码哈希、预算、依赖和全部汇总；每个 `任务ID-single/multi.json` 保存真实回答、模型/工具 trace、最终退款与工单记录以及逐项判定。公共样本文本未复制到此目录，来源、映射和指标在 `public-intents-summary.json`。

运行说明见 [SUPPORTFLOW.md](../../SUPPORTFLOW.md)，学习路径见 [新版架构与面试说明](../../项目解读与面试指南/08_SupportFlow实现与评测.md)，口径见 [数据与实验卡](../../项目解读与面试指南/09_数据与实验卡.md)。

## 当前适合的简历表达

“实现带事务工具、人工工单闭环与 MCP 接入的多 Agent 客服系统；建立固定 24 条业务回归任务和 48 条公开意图样本的评测流程，覆盖状态核验、调用追踪、P95、token 成本与回归检测，定位小模型在复合任务规划上的瓶颈。”

若需要写提升成果，应更换/确认模型 API 后重新开展同条件对照，并补充独立隐藏测试集。当前不能声称生产质量或复合任务能力已达标。
"""
    (dest / "README.md").write_text(text, encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
