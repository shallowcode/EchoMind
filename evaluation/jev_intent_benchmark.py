"""Paired, budget-limited intent experiment; never changes the production router."""

import argparse
import asyncio
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import logging
import math
import os
from pathlib import Path
import platform
import random
import statistics
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import httpx
from dotenv import dotenv_values
from core.intent_recognizer import IntentCategory, IntentRecognizer
from supportflow.contracts import Settings
from supportflow.model import Model

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"
LABELS = ["refund", "invoice", "order_status", "human_handoff"]
ZH = {
    "refund": [
        "这件东西不合适，我想退掉拿回钱，应该怎么办？",
        "订单 ORD1001 请申请退还二十元。",
        "不是要买新的，我是想把上周那笔交易退掉。",
        "货已经寄回去了，钱什么时候才能回到我的账户？",
        "先别帮我操作，我只想问退货的条件。",
        "我提交的退款申请现在处理到哪一步了？",
    ],
    "invoice": [
        "报销需要购买凭证，麻烦给这笔订单开一张增值税电子发票。",
        "电子票上的公司名称写错了，可以重新开吗？",
        "我要把发票抬头换成我们公司的名称。",
        "订单完成了，在哪里下载开好的电子发票？",
        "税号已经提供了，为什么还没收到发票？",
        "不是退钱，是要你们补开上个月消费的发票。",
    ],
    "order_status": [
        "ORD1001 这笔订单现在是待付款还是已经完成了？",
        "麻烦核实一下 ORD1002 是否已经被取消。",
        "我昨天买的那一单，你们系统显示的状态是什么？",
        "订单页面一直写着处理中，帮我查查现在走到哪一步。",
        "不用改订单，只查询 ORD1003 当前状态。",
        "我想确认订单是否已经审核通过并开始处理。",
    ],
    "human_handoff": [
        "能找个真人来跟我沟通吗？",
        "机器人解释不清楚，帮我接一位客服人员。",
        "这事我想直接和你们的工作人员聊。",
        "不要再自动回复了，请安排人工接待。",
        "我要把这个问题升级给客服主管处理。",
        "先不用查订单，让人工客服接手这个会话。",
    ],
}
PUBLIC_MAP = {
    "check_refund_policy": "refund", "get_refund": "refund", "track_refund": "refund",
    "check_invoice": "invoice", "get_invoice": "invoice",
    "track_order": "order_status", "contact_human_agent": "human_handoff",
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    return {p: digest(ROOT / p) for p in [
        "evaluation/jev_intent_benchmark.py", "core/intent_recognizer.py",
        "core/llm_utils.py", "supportflow/model.py", "supportflow/contracts.py",
    ]}


def build_dataset():
    source = ROOT / ".runtime/datasets/bitext-v2/validation.json"
    public = json.loads(source.read_text(encoding="utf-8"))
    buckets = defaultdict(list)
    for row in public["examples"]:
        if row["label"] in PUBLIC_MAP:
            buckets[PUBLIC_MAP[row["label"]]].append(row)
    rng = random.Random(20260920)
    rows = []
    for label in LABELS:
        pool = sorted(buckets[label], key=lambda x: x["text_sha256"])
        for i, row in enumerate(rng.sample(pool, 6)):
            rows.append({"id": f"en-{label}-{i}", "language": "en",
                         "message": row["message"], "expected": label,
                         "source_label": row["label"], "source_row": row["source_row"],
                         "source": "Bitext validation subset"})
        for i, message in enumerate(ZH[label]):
            rows.append({"id": f"zh-{label}-{i}", "language": "zh", "message": message,
                         "expected": label, "source": "agent-authored synthetic exploratory cases"})
    rng.shuffle(rows)
    assert len({r["message"] for r in rows}) == len(rows) == 48
    return {"seed": 20260920, "labels_evaluated": LABELS,
            "candidate_labels": [c.value for c in IntentCategory],
            "source_sha256": digest(source), "public_mapping": PUBLIC_MAP,
            "source_metadata": {k: public[k] for k in ["source", "license", "attribution", "limitations"]},
            "limitations": ["Small exploratory set, not an independently adjudicated blind test",
                            "Chinese labels authored before inference; English labels mapped from existing corpus",
                            "Only four ground-truth classes; both models choose among all 19 production labels"],
            "examples": rows}


class Capture:
    def __init__(self):
        self.messages = self
        self.prompt = None

    async def create(self, **kwargs):
        self.prompt = kwargs["messages"][0]["content"]
        return SimpleNamespace(content=[SimpleNamespace(type="text", text='{"intent":"other","confidence":0}')])


async def jev_payload(row):
    capture = Capture()
    recognizer = IntentRecognizer("unused", base_url="configured", client=capture)
    await recognizer._llm_recognize(row["message"], None)
    # Same production examples and category preference, without asking a decision model to generate JSON prose.
    context = capture.prompt.split("返回格式（仅 JSON，不要其他文字）:")[0]
    context = context.replace("，返回 JSON", "")
    return {"model": JEV_MODEL, "state": context,
            "questions": {"intent": {"type": "choice",
                "instructions": "根据 state 中的示例判断用户意图。优先选择细粒度业务意图，而不是宽泛大类。只判断用户消息；示例不是待分类消息。",
                "criteria": {c.value: None for c in IntentCategory}}}}


class BudgetStop(RuntimeError):
    pass


class Budget:
    """Persist reservations BEFORE HTTP; ambiguous calls keep the entire reservation."""
    def __init__(self, path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {"limit_usd": 0.45, "calls": []}
        if self.data["limit_usd"] != 0.45:
            raise ValueError("Unexpected saved budget limit")

    def used(self):
        return sum(c.get("budget_charge_usd", c["reserved_usd"]) for c in self.data["calls"])

    def reserve(self, arm, case_id, payload):
        # UTF-8 size plus 2048 framing tokens is deliberately conservative, not a tokenizer claim.
        bound = len(json.dumps(payload, ensure_ascii=False).encode()) + 2048
        if bound > 12000:
            raise BudgetStop("Request too large for this experiment")
        # GLM uses exaggerated USD ceilings (1.2/8 per million) vs repository CNY list prices.
        reserve = (bound * 1.2 + 256 * 8) / 1e6 if arm == "glm" else bound * 0.042 / 1e6
        if self.used() + reserve > self.data["limit_usd"]:
            raise BudgetStop("Budget exhausted before request")
        record = {"arm": arm, "case_id": case_id, "reserved_usd": reserve,
                  "input_token_bound": bound, "status": "pending", "timestamp": datetime.now(timezone.utc).isoformat()}
        self.data["calls"].append(record)
        dump(self.path, self.data)
        return record

    def settle(self, record, body):
        usage = body.get("usage") or {}
        inp = usage.get("input_tokens", usage.get("prompt_tokens"))
        out = usage.get("output_tokens", usage.get("completion_tokens"))
        record.update(status="responded", usage=usage, returned_model=body.get("model"))
        if type(inp) is int and type(out) is int and inp >= 0 and out >= 0:
            charge = (inp * 1.2 + out * 8) / 1e6 if record["arm"] == "glm" else inp * 0.042 / 1e6
            reported = usage.get("cost")
            if isinstance(reported, (int, float)) and math.isfinite(reported) and reported >= 0:
                charge = max(charge, reported)
                record["reported_cost_usd"] = reported
            record["budget_charge_usd"] = charge
            if record["arm"] == "glm":
                record["estimated_cost_cny_historical_tariff"] = (inp * 0.8 + out * (2 if out < 200 else 6)) / 1e6
        dump(self.path, self.data)
        if record.get("budget_charge_usd", 0) > record["reserved_usd"]:
            raise BudgetStop("Provider usage exceeded reservation; stopping")


class Wire:
    def __init__(self, client, budget, arm, case_id, out):
        self.client, self.budget, self.arm, self.case_id, self.out = client, budget, arm, case_id, out
        self.meta = {}

    async def post(self, url, *, json, headers):
        record = self.budget.reserve(self.arm, self.case_id, json)
        dump(self.out / f"{self.case_id}-{self.arm}-request.json", json)
        started = time.perf_counter()
        try:
            response = await self.client.post(url, json=json, headers=headers)
            self.meta = {"http_status": response.status_code, "api_ms": (time.perf_counter()-started)*1000}
            record["http_status"] = response.status_code
            if response.is_success:
                body = response.json()
                # Save model output and usage, never request headers or keys.
                dump(self.out / f"{self.case_id}-{self.arm}-response.json", body)
                self.budget.settle(record, body)
                self.meta.update(usage=body.get("usage"), returned_model=body.get("model"), provider=body.get("provider"))
            else:
                record["status"] = "http_error_reserved"
                dump(self.budget.path, self.budget.data)
            response.raise_for_status()
            return response
        except Exception as exc:
            self.meta.update(error=type(exc).__name__, api_ms=(time.perf_counter()-started)*1000)
            if record["status"] == "pending":
                record["status"] = "uncertain_reserved"
                dump(self.budget.path, self.budget.data)
            raise


class ObservedRecognizer(IntentRecognizer):
    async def _llm_recognize(self, message, history):
        self.raw_result = await super()._llm_recognize(message, history)
        return self.raw_result


def validate_jev(body):
    answer = body["answers"]["intent"]
    labels = {c.value for c in IntentCategory}
    probs = answer["probabilities"]
    if answer["type"] != "choice" or answer["choice"] not in labels or set(probs) != labels:
        raise ValueError("Invalid Jev choice schema")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in probs.values()):
        raise ValueError("Invalid probabilities")
    if abs(sum(probs.values()) - 1) > 0.02:
        raise ValueError("Probability sum is invalid")
    confidence = answer.get("confidence")
    if type(confidence) not in (int, float) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("Invalid confidence")
    if probs[answer["choice"]] + 1e-6 < max(probs.values()):
        raise ValueError("Choice is not the highest-probability class")
    return answer


async def run_case(row, arm, client, settings, key, budget, out):
    wire = Wire(client, budget, arm, row["id"], out)
    started = time.perf_counter()
    result = {"id": row["id"], "language": row["language"], "expected": row["expected"],
              "arm": arm, "predicted": "ERROR", "pipeline_predicted": "ERROR"}
    try:
        if arm == "glm":
            model = Model(settings)
            await model.client.aclose()
            model.client = wire
            recognizer = ObservedRecognizer("unused", base_url=settings.model_url, client=model)
            full = await recognizer.recognize(row["message"])
            raw = recognizer.raw_result
            result["pipeline_predicted"] = full.intent.value
            result["confidence"] = raw.get("confidence")
            if not raw.get("failed"):
                result["predicted"] = raw["intent"].value
            else:
                result["error"] = "original_llm_branch_failed"
        else:
            response = await wire.post(ENDPOINT, json=await jev_payload(row), headers={"Authorization": "Bearer " + key})
            answer = validate_jev(response.json())
            result.update(predicted=answer["choice"], confidence=answer["confidence"], probabilities=answer["probabilities"])
            # Diagnostic only: reuse existing voting with top-class probability, NOT Jev's entropy-like confidence.
            recognizer = IntentRecognizer("unused", base_url="configured", client=Capture())
            intent, _, _ = recognizer._vote(
                {"intent": IntentCategory(answer["choice"]), "confidence": answer["probabilities"][answer["choice"]]},
                {}, recognizer._pattern_recognize(row["message"]))
            result["pipeline_predicted"] = intent.value
    except BudgetStop:
        raise
    except Exception as exc:
        result["error"] = type(exc).__name__
    result.update(wire.meta)
    result["total_ms"] = (time.perf_counter()-started)*1000
    dump(out / f"{row['id']}-{arm}.json", result)
    return result


def metrics(rows, field="predicted"):
    if not rows:
        return None
    f1 = {}
    for label in LABELS:
        tp = sum(r["expected"] == r[field] == label for r in rows)
        fp = sum(r["expected"] != label and r[field] == label for r in rows)
        fn = sum(r["expected"] == label and r[field] != label for r in rows)
        f1[label] = 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0
    latency = sorted(r["total_ms"] for r in rows)
    confusion = Counter((r["expected"], r[field]) for r in rows)
    return {"n": len(rows), "correct": sum(r["expected"] == r[field] for r in rows),
            "accuracy": sum(r["expected"] == r[field] for r in rows)/len(rows),
            "macro_f1": statistics.mean(f1.values()), "per_class_f1": f1,
            "failure_rate": sum(bool(r.get("error")) for r in rows)/len(rows),
            "median_ms": statistics.median(latency), "p95_ms": latency[math.ceil(.95*len(latency))-1],
            "confusion": [{"expected": a, "predicted": b, "count": n} for (a,b),n in confusion.items()]}


def paired_stats(records):
    pairs = defaultdict(dict)
    for r in records:
        pairs[r["id"]][r["arm"]] = r
    differences = [int(v["jev"]["predicted"] == v["jev"]["expected"])-int(v["glm"]["predicted"] == v["glm"]["expected"])
                   for v in pairs.values() if len(v) == 2]
    if not differences:
        return None
    rng = random.Random(20260920)
    boots = sorted(statistics.mean(rng.choices(differences, k=len(differences))) for _ in range(5000))
    wins, losses = differences.count(1), differences.count(-1)
    discordant = wins + losses
    p = min(1, 2*sum(math.comb(discordant,k) for k in range(min(wins,losses)+1))/2**discordant) if discordant else 1
    return {"n_pairs": len(differences), "jev_only_correct": wins, "glm_only_correct": losses,
            "accuracy_delta": statistics.mean(differences), "paired_bootstrap_95": [boots[124], boots[4874]],
            "mcnemar_exact_p": p}


def report(out, dataset, budget, status):
    records = []
    for row in dataset["examples"]:
        for arm in ["glm", "jev"]:
            p = out / f"{row['id']}-{arm}.json"
            if p.exists():
                records.append(json.loads(p.read_text(encoding="utf-8")))
    groups = {lang: {arm: metrics([r for r in records if r["arm"] == arm and (lang == "all" or r["language"] == lang)])
                    for arm in ["glm", "jev"]} for lang in ["all", "zh", "en"]}
    data = {"status": status, "primary_scope": "original semantic classification branch; no threshold or prompt tuning",
            "metrics": groups, "paired": paired_stats(records),
            "pipeline_diagnostic": {arm: metrics([r for r in records if r["arm"] == arm], "pipeline_predicted") for arm in ["glm", "jev"]},
            "budget_accounted_usd_upper_estimate": budget.used(),
            "openrouter_reported_usd": sum(c.get("reported_cost_usd",0) for c in budget.data["calls"]),
            "glm_estimated_cny_historical_tariff": sum(c.get("estimated_cost_cny_historical_tariff",0) for c in budget.data["calls"]),
            "dataset_sha256": digest(out/"dataset.json"), "records": records,
            "limitations": dataset["limitations"] + [
                "GLM direct China endpoint vs Jev via OpenRouter: latency includes provider/network differences",
                "GLM keeps original prompt and 256-token generation cap; Jev uses the same examples with typed choice",
                "No paid judge, retries, warmup, cross-model fallback, or confidence tuning",
                "Primary score is raw semantic branch; fusion diagnostic retains heuristic rules with non-equivalent confidence sources",
                "Cost estimate is not an invoice; GLM CNY tariff recorded by project on 2026-09-08, cache discounts excluded",
                "Budget treats GLM rates as USD at inflated 1.2/8 per million; uncertain requests retain reservation",
            ]}
    dump(out/"report.json", data)
    lines = ["# Jev 1.13 与 GLM-4.5-Air：意图识别对照", "", f"状态：{status}", "",
             "固定 48 条，中英文各 24 条，退款/发票/订单状态/转人工各 12 条。候选类别仍为 19 类。",
             "主指标比较原方案的模型语义分类分支；融合规则结果另列诊断，不作为公平校准后的结论。", "",
             "| 分组 | 方案 | N | 正确率 | Macro-F1 | 中位延迟 ms | P95 ms | 失败率 |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for lang, arms in groups.items():
        for arm,m in arms.items():
            if m:
                lines.append(f"| {lang} | {arm} | {m['n']} | {m['accuracy']:.1%} | {m['macro_f1']:.3f} | {m['median_ms']:.0f} | {m['p95_ms']:.0f} | {m['failure_rate']:.1%} |")
    lines += ["", f"配对统计：`{json.dumps(data['paired'], ensure_ascii=False)}`", "",
              f"OpenRouter 返回费用：${data['openrouter_reported_usd']:.8f}；GLM 历史价目表估算：¥{data['glm_estimated_cny_historical_tariff']:.6f}。",
              f"保守预算占用（不是实际美元账单）：${budget.used():.6f} / $0.45，另留 $0.05 余量。", "",
              "## 限制", ""] + ["- "+s for s in data["limitations"]]
    (out/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return data


async def main(args):
    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)
    # Exclusive process lock, automatically released by OS even on interruption.
    import msvcrt
    with (out/"run.lock").open("a+b") as lock:
        lock.seek(0); lock.write(b"0"); lock.flush(); lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        hashes = source_hashes()
        meta_path = out/"environment.json"
        if meta_path.exists():
            if json.loads(meta_path.read_text())["source_hashes"] != hashes:
                raise ValueError("Source changed; do not mix a modified runner into this run")
        else:
            dump(meta_path, {"created": datetime.now(timezone.utc).isoformat(), "python": sys.version,
                            "platform": platform.platform(), "source_hashes": hashes,
                            "packages": {p: importlib.metadata.version(p) for p in ["httpx","anthropic","pydantic","python-dotenv"]},
                            "endpoints": {"jev":ENDPOINT,"glm":"https://open.bigmodel.cn/api/paas/v4/chat/completions"}})
        data_path = out/"dataset.json"
        if not data_path.exists():
            dump(data_path, build_dataset())
        dataset = json.loads(data_path.read_text(encoding="utf-8"))
        budget = Budget(out/"budget.json")
        if args.prepare:
            report(out,dataset,budget,"prepared_no_inference")
            print("Prepared",out,"48 cases; no API calls")
            return
        env = dotenv_values(ROOT/".runtime/glm.env")
        settings = Settings(**{k:env["SF_"+k.upper()] for k in Settings.model_fields if "SF_"+k.upper() in env})
        if settings.model_name != "glm-4.5-air" or settings.model_url != "https://open.bigmodel.cn/api/paas/v4":
            raise ValueError("Baseline must be the configured GLM-4.5-Air endpoint")
        key = os.environ.get("OPENROUTER_API_KEY") or dotenv_values(ROOT/".runtime/jev.env").get("OPENROUTER_API_KEY")
        if not key or not settings.model_key:
            raise ValueError("Missing provider credentials")
        status = "running"
        count = 0
        attempted = {(c["case_id"],c["arm"]) for c in budget.data["calls"]}
        async with httpx.AsyncClient(timeout=45, follow_redirects=False, transport=httpx.AsyncHTTPTransport(retries=0)) as client:
            try:
                for i,row in enumerate(dataset["examples"]):
                    for arm in (["jev","glm"] if i%2 == 0 else ["glm","jev"]):
                        if (out/f"{row['id']}-{arm}.json").exists():
                            continue
                        if (row["id"],arm) in attempted:
                            raise BudgetStop("Incomplete previous attempt; inspect ledger before any retry")
                        result = await run_case(row,arm,client,settings,key,budget,out)
                        count += 1
                        print(f"{i+1}/48 {arm} {row['id']} => {result['predicted']} {result['total_ms']:.0f}ms budget=${budget.used():.5f}",flush=True)
                        report(out,dataset,budget,status)
                        if result.get("http_status") in [401,402,403,404,422] or result.get("error") == "BudgetStop":
                            raise BudgetStop("Provider/configuration failure; stopped without retries")
                        if args.max_calls and count >= args.max_calls:
                            status = "partial_call_limit"
                            return
                status = "completed"
            except BudgetStop as exc:
                status = str(exc)
                print("STOP:",status,flush=True)
            finally:
                report(out,dataset,budget,status)


if __name__ == "__main__":
    logging.getLogger("core.intent_recognizer").setLevel(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",default=".runtime/jev-eval/run-20260920")
    parser.add_argument("--prepare",action="store_true")
    parser.add_argument("--max-calls",type=int,default=0)
    asyncio.run(main(parser.parse_args()))
