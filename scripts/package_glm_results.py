"""Publish reproducible GLM reports and traces without copying private configs/databases."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="+")
    parser.add_argument(
        "--summary",
        default="GLM-复合任务实测.md",
        help="Summary filename inside 评测结果; use a separate file for new dataset versions",
    )
    args = parser.parse_args()
    if Path(args.summary).name != args.summary:
        parser.error("summary must be a filename")
    summary = [
        "# GLM-4.5-Air：复合任务实测",
        "",
        "以下来自真实 GLM API、Chroma 检索、鉴权 HTTP 和沙箱账本。每条任务的原始结果、工具证据与状态保留在各实验目录；没有使用 fixture 生成质量指标。",
        "",
        "| 实验 | 基线 | 增强版 | 增强版复合任务 | HTTP P95 | 每任务模型费估算 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for run in args.runs:
        source = ROOT / run
        report = json.loads((source / "report.json").read_text(encoding="utf-8"))
        if report["source_changed_during_run"]:
            raise ValueError("Source changed during run: " + run)
        if report["settings"]["model_name"] != "glm-4.5-air":
            raise ValueError("Not the requested model")
        destination = ROOT / "评测结果" / ("GLM-" + source.name)
        destination.mkdir(parents=True, exist_ok=True)
        for relative, digest in report["source_sha256"].items():
            path = (ROOT / relative).resolve()
            if (
                not path.is_relative_to(ROOT)
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest
            ):
                raise ValueError(
                    "Cannot archive a different source revision: " + relative
                )
            archived = destination / "source" / relative
            archived.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, archived)
        for name in [
            "requirements.txt",
            "requirements-dev.txt",
            ".env.supportflow.example",
        ]:
            shutil.copy2(ROOT / name, destination / "source" / name)
        for path in source.glob("*.json"):
            shutil.copy2(path, destination / path.name)
        shutil.copy2(source / "REPORT.md", destination / "REPORT.md")
        report_md = destination / "REPORT.md"
        report_md.write_text(
            report_md.read_text(encoding="utf-8").replace(
                "平均模型调用成本", "按未命中缓存价目表估算的平均模型调用费用"
            )
            + "\n同目录 source/ 保存与 report.json 哈希相符的源码快照；不含模型密钥。正确拒绝超额退款属于预期处理结果，技术排障建议和 pending 退款申请不等于实际故障修复或资金到账。\n",
            encoding="utf-8",
        )
        base = report["summaries"][report["baseline"]]
        multi = report["summaries"]["multi"]
        compound_groups = [
            v for k, v in multi["groups"].items() if k.startswith("compound")
        ]
        compound = {
            key: sum(v[key] for v in compound_groups) for key in ["n", "completed"]
        }
        cost = multi["mean_model_cost"]
        cost_text = f"约 {cost:.5f} 元" if cost is not None else "不可用"
        summary.append(
            f"| [{report['dataset_version']}，{report['evaluated_tasks']} 条](GLM-{source.name}/REPORT.md) | {report['baseline']}：{base['completed']}/{base['tasks']} | {multi['completed']}/{multi['tasks']} | {compound['completed']}/{compound['n']} | {multi['request_p95_ms'] / 1000:.2f} 秒 | {cost_text} |"
        )
    summary.extend(
        [
            "",
            "所有实验任务并发条件见报告；ASGI 进程内 HTTP 包含鉴权、业务、数据库与外部模型 HTTP，不含公网入口/反向代理延迟。模型价目表估算按单次 token 分档，未扣缓存优惠、套餐及赠额，主表不含辅助评委与基础设施费用；评委 token 单列。",
            "",
            "v1 是已用于调试的固定开发回归集；v2 为开发后新增的复合回归用例。小样本单次结果不是独立盲测、生产 SLA 或稳定性证明。legacy_multi 使用与新版相同的公共工具保护和 GLM 适配，仅消融任务拆分与合并方式。",
            "",
            "任务完成率包含正确拒绝超额退款等预期处理结果。技术任务完成是给出有来源的排查步骤，退款任务完成是建立待审核申请，都不代表实际故障修复或资金到账。",
            "",
            "运行源码 SHA256、数据集 SHA256、配对区间和逐例失败均可在 report.json 与案例 JSON 复核。",
        ]
    )
    target = ROOT / "评测结果" / args.summary
    target.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
