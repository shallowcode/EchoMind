"""Unattended frozen GLM evaluation. Checkpoint each result, resume without cherry-picking.

Runs all three splits; acceptance is exposed when executed. No model-based Judge.
Business concurrency two; one concurrent serial public-intent stream.
"""

import argparse
import asyncio
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import statistics
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import httpx
from evaluation.full_chain import aggregate, run_case
from evaluation.public_intents import MAP
from supportflow.api import create_app
from supportflow.contracts import Principal, Settings, Trace
from supportflow.model import Model, active_trace

SPLITS = ("development", "validation", "acceptance")


def atomic(path, value, best_effort=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    for attempt in range(3 if best_effort else 20):
        try:
            temp.replace(path)
            return True
        except PermissionError:
            if attempt == (2 if best_effort else 19):
                if best_effort:
                    return False
                raise
            time.sleep(0.1)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def freeze(out, settings):
    paths = [
        p
        for folder in (
            "supportflow",
            "agents",
            "core",
            "evaluation",
            "skills",
            "scripts",
        )
        for p in (ROOT / folder).rglob("*")
        if p.is_file()
        and p.suffix in {".py", ".json", ".md"}
        and "__pycache__" not in p.parts
    ]
    paths += [ROOT / ".runtime/datasets/bitext-v2" / (s + ".json") for s in SPLITS]
    manifest = {
        "hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths
        },
        "settings": settings.model_dump(
            exclude={"model_key", "redis_url", "payment_key", "payment_webhook_secret"}
        ),
        "business_concurrency": 2,
        "public_concurrency": 1,
        "judge": False,
        "acceptance_policy": "Authorized full run of all splits; results expose acceptance. No tuning during execution.",
    }
    saved = out / "manifest.json"
    if saved.exists():
        if read(saved) != manifest:
            raise ValueError(
                "Source, data or model settings changed; use a new output directory"
            )
    else:
        for p in paths:
            target = out / "source" / p.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
        atomic(saved, manifest)
    return manifest


def failure_record(case, arm, error, elapsed):
    return {
        "id": case["id"],
        "group": case["group"],
        "family": case["family"],
        "split": case["split"],
        "variant": arm,
        "complete": False,
        "checks": {"harness_execution": False},
        "error": type(error).__name__,
        "task_ms": elapsed * 1000,
        "request_ms": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "model_cost": None,
        "judge": None,
        "judge_error": None,
        "responses": [],
        "usage_complete": False,
    }


def summarize_public(rows):
    labels = sorted(set(MAP.values()))
    f1 = {}
    for label in labels:
        tp = sum(r["expected"] == r["predicted"] == label for r in rows)
        fp = sum(r["expected"] != label and r["predicted"] == label for r in rows)
        fn = sum(r["expected"] == label and r["predicted"] != label for r in rows)
        f1[label] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0
    return {
        "evaluated": len(rows),
        "accuracy": sum(r["expected"] == r["predicted"] for r in rows) / len(rows)
        if rows
        else None,
        "macro_f1": statistics.mean(f1.values()) if rows else None,
        "per_class_f1": f1,
        "http_errors": sum(r["http_status"] != 200 for r in rows),
        "model_failures": sum(r["model_failed"] for r in rows),
        "input_tokens": sum(r["trace"]["input_tokens"] for r in rows),
        "output_tokens": sum(r["trace"]["output_tokens"] for r in rows),
        "confusion": [
            {"expected": a, "predicted": b, "n": n}
            for (a, b), n in Counter(
                (r["expected"], r["predicted"]) for r in rows
            ).items()
        ],
    }


def paired(rows):
    pairs = defaultdict(dict)
    for row in rows:
        pairs[row["id"]][row["variant"]] = row
    families = defaultdict(list)
    for arms in pairs.values():
        if set(arms) == {"single", "multi"}:
            families[arms["multi"]["family"]].append(
                int(arms["multi"]["complete"]) - int(arms["single"]["complete"])
            )
    means = [statistics.mean(v) for v in families.values()]
    rng = random.Random(42)
    boots = (
        sorted(statistics.mean(rng.choices(means, k=len(means))) for _ in range(2000))
        if means
        else []
    )
    return {
        "family_count": len(means),
        "family_macro_delta": statistics.mean(means) if means else None,
        "family_bootstrap_95": [boots[49], boots[1949]] if boots else None,
    }


async def run(out):
    out.mkdir(parents=True, exist_ok=True)
    settings = Settings.from_env()
    if (
        settings.model_name != "glm-4.5-air"
        or settings.model_backend == "fixture"
        or settings.business_mode != "sandbox"
    ):
        raise ValueError("Requires GLM-4.5-Air real model and sandbox business backend")
    # An OS lock prevents two processes from racing checkpoints; it releases on crash.
    lock = (out / "run.lock").open("a+b")
    lock.seek(0)
    if os.name == "nt":
        import msvcrt

        if not lock.read(1):
            lock.write(b"0")
            lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = freeze(out, settings)
    records_dir = out / "records"
    records_dir.mkdir(exist_ok=True)
    business = [
        c
        for split in SPLITS
        for c in read(ROOT / f"evaluation/datasets/trial-v3/{split}.json")["cases"]
    ]
    public = [
        (split, row)
        for split in SPLITS
        for row in read(ROOT / f".runtime/datasets/bitext-v2/{split}.json")["examples"]
    ]
    assert len(business) == 1200 and len(public) == 2700
    # User reduced execution budget after launch. Keep the existing ordered prefix;
    # never choose the subset based on observed scores.
    business = business[:600]
    public = [(split, row) for split, row in public if row["label"] in MAP][:1200]
    business_rows, public_rows = {}, {}
    for p in records_dir.glob("business-*.json"):
        row = read(p)
        business_rows[(row["id"], row["variant"])] = row
    for p in records_dir.glob("public-*.json"):
        row = read(p)
        public_rows[row["source_row"]] = row
    started = time.time()
    session = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    work = out / "work" / session
    work.mkdir(parents=True)

    def status(state="running", error=None):
        payload = {
            "state": state,
            "pid": os.getpid(),
            "updated_utc": datetime.now(timezone.utc).isoformat(),
            "session_elapsed_seconds": time.time() - started,
            "business_done": len(business_rows),
            "business_total": len(business) * 2,
            "public_done": len(public_rows),
            "public_total": len(public),
            "public_excluded": 300,
            "judge": False,
            "error": error,
        }
        # A viewer/antivirus may hold a Windows file handle. Progress is advisory;
        # failures here must never abort already-checkpointed model work.
        for filename in ("progress.json", "status.json"):
            try:
                atomic(out / filename, payload, best_effort=True)
            except OSError:
                pass

    async def business_stream():
        queue = asyncio.Queue()
        # Finish each split before exposing the next; no adaptive tuning between splits.
        for split in SPLITS:
            cases = [c for c in business if c["split"] == split]
            random.Random(20260909).shuffle(cases)
            for i, c in enumerate(cases):
                queue.put_nowait(
                    (c, ["single", "multi"] if i % 2 == 0 else ["multi", "single"])
                )

            async def worker():
                while not queue.empty():
                    case, arms = queue.get_nowait()
                    try:
                        for arm in arms:
                            if (case["id"], arm) in business_rows:
                                continue  # Keep failures too: never rerun until a pass.
                            t = time.perf_counter()
                            try:
                                row = await run_case(
                                    case, arm, SimpleNamespace(judge=False), work
                                )
                            except Exception as exc:
                                row = failure_record(
                                    case, arm, exc, time.perf_counter() - t
                                )
                            atomic(
                                records_dir / f"business-{case['id']}-{arm}.json", row
                            )
                            business_rows[(case["id"], arm)] = row
                            status()
                    finally:
                        queue.task_done()

            await asyncio.gather(worker(), worker())

    async def public_stream():
        app = create_app(
            settings.model_copy(
                update={
                    "db_path": str(work / "public.sqlite3"),
                    "chroma_path": str(work / "public-chroma"),
                }
            )
        )
        p = Principal("public-full-eval", "evaluator")
        token = None
        issued = 0
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
                base_url="http://localhost",
                timeout=settings.model_timeout + 30,
            ) as client,
        ):
            for split, row in public:
                if row["label"] not in MAP or row["source_row"] in public_rows:
                    continue
                if time.monotonic() - issued > 1800 or token is None:
                    token = app.state.store.issue_token(p, ttl=3600)
                    issued = time.monotonic()
                trace = Trace("public-" + str(row["source_row"]))
                marker = active_trace.set(trace)
                t = time.perf_counter()
                body, http_status, error = {}, 0, None
                try:
                    r = await client.post(
                        "/intents",
                        headers={"Authorization": "Bearer " + token},
                        json={
                            "message": row["message"],
                            "request_id": trace.request_id,
                        },
                    )
                    http_status = r.status_code
                    body = r.json()
                except Exception as exc:
                    error = type(exc).__name__
                finally:
                    active_trace.reset(marker)
                record = {
                    **row,
                    "split": split,
                    "expected": MAP[row["label"]],
                    "predicted": body.get("intent", "ERROR")
                    if http_status == 200
                    else "ERROR",
                    "http_status": http_status,
                    "error": error,
                    "model_failed": bool(trace.failures)
                    or "LLM 失败" in body.get("reasoning", ""),
                    "latency_ms": (time.perf_counter() - t) * 1000,
                    "trace": asdict(trace),
                }
                atomic(records_dir / f"public-{row['source_row']}.json", record)
                public_rows[row["source_row"]] = record
                status()

    async def heartbeat():
        while True:
            status()
            await asyncio.sleep(30)

    status()
    beat = asyncio.create_task(heartbeat())
    try:
        # One excluded warmup. Authentication/provider failures stop before the paid batch.
        warm = Model(settings)
        try:
            await warm.complete(
                [{"role": "user", "content": "回复准备好了"}], max_tokens=16
            )
        finally:
            await warm.close()
        await asyncio.gather(business_stream(), public_stream())
        rows = list(business_rows.values())
        report = {
            "model": settings.model_name,
            "manifest": "manifest.json",
            "business": {},
            "public": {},
            "paired": {},
            "scope": {
                "business_cases": 600,
                "business_executions": 1200,
                "public_executions": 1200,
                "selection": "Development business split and first 1200 mapped development public rows; reduced by user mid-run, not score-selected",
                "validation_executed": False,
                "acceptance_executed": False,
            },
            "source_changed": any(
                hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest
                for path, digest in manifest["hashes"].items()
            ),
            "limitations": [
                "Authored parameterized sandbox tasks and public synthetic intent corpus; no enterprise traffic",
                "Reduced run: development only. Public prefix is not label-balanced; do not generalize its score to the full 2700 samples. Validation and acceptance not executed.",
                "Concurrent public stream shares model quota and local machine; P95 includes this contention",
                "ASGI HTTP excludes external front proxy; no Judge calls",
                "Failed cases remain in denominators and are never automatically retried; interrupted uncheckpointed work restarts in fresh sandbox and can incur extra cost",
                "Costs are uncached versioned estimates, not invoices; latency excludes fixture setup",
                "Keyword state and reply checks are not complete semantic proof",
            ],
        }
        for split in ("development", "all"):
            selected = [r for r in rows if split == "all" or r["split"] == split]
            report["business"][split] = {
                a: aggregate([r for r in selected if r["variant"] == a])
                for a in ["single", "multi"]
            }
            report["paired"][split] = paired(selected)
            report["public"][split] = summarize_public(
                [
                    r
                    for r in public_rows.values()
                    if split == "all" or r["split"] == split
                ]
            )
        report["runner_maintenance"] = (
            read(out / "runner-maintenance.json")
            if (out / "runner-maintenance.json").exists()
            else []
        )
        atomic(out / "report.json", report)
        lines = [
            "# GLM 全量评测",
            "",
            "按用户要求缩减：600条开发业务任务各运行single/multi，共1200次；公开意图取开发集前1200条可映射样本。未执行验证/验收集。意图前缀子集不保证标签均衡。",
            "",
            "| 分区 | single完成 | multi完成 | multi请求P95 | 意图准确率 | 意图宏F1 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for split in ("development", "all"):
            a, b = (
                report["business"][split]["single"],
                report["business"][split]["multi"],
            )
            public_metrics = report["public"][split]
            latency = (
                f"{b['request_p95_ms'] / 1000:.2f}秒"
                if b["request_p95_ms"] is not None
                else "不可用"
            )
            lines.append(
                f"| {split} | {a['completed']}/{a['tasks']} | {b['completed']}/{b['tasks']} | {latency} | {public_metrics['accuracy']:.2%} | {public_metrics['macro_f1']:.3f} |"
            )
        lines += [
            "",
            "完整指标、失败、族级区间、真实用量及费用估算见 report.json 与 records/。同目录 source/ 为开跑前源码及数据快照，排除密钥。",
            "",
            "本次业务并发2，同时运行1条串行意图评测流，不能与无竞争环境的历史P95直接比较。没有运行额外LLM评委。",
            "",
            f"运行期间源码改变：{report['source_changed']}。",
        ]
        (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        status("completed")
    except BaseException as exc:
        status("failed", type(exc).__name__)
        raise
    finally:
        beat.cancel()
        lock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/glm-full-20260909")
    args = parser.parse_args()
    asyncio.run(run(Path(args.output).resolve()))
