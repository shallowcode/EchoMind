"""Offline evidence inventory; historical aggregates are never new model results."""

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(root=ROOT):
    root = Path(root)
    historical_path = root / "评测结果/GLM-1200复核/audit.json"
    historical = json.loads(historical_path.read_text(encoding="utf-8"))
    for group in ("reviewed_summaries", "reviewed_compound_summaries"):
        for row in historical[group].values():
            if abs(row["completed"] / row["tasks"] - row["completion_rate"]) > 1e-12:
                raise ValueError("Historical aggregate is internally inconsistent")
    datasets = root / "evaluation/datasets/trial-v3"
    hashes = {}
    for name, base in (("manifest.json", datasets), ("public-manifest.json", root)):
        manifest = json.loads((datasets / name).read_text(encoding="utf-8"))
        for split, entry in manifest["splits"].items():
            path = (datasets / (split + ".json")) if name == "manifest.json" else base / entry["path"].replace("\\", "/")
            key = ("business/" if name == "manifest.json" else "public/") + split
            hashes[key] = "missing" if not path.exists() else (
                "verified" if hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"] else "mismatch")
    business = json.loads((datasets / "development.json").read_text(encoding="utf-8"))["cases"]
    public_path = root / ".runtime/datasets/bitext-v2/development.json"
    public = []
    if public_path.exists():
        # This is the archived ordered selection, independent of model predictions.
        import sys

        sys.path.insert(0, str(root))
        from evaluation.public_intents import MAP

        public = [r for r in json.loads(public_path.read_text(encoding="utf-8"))["examples"] if r["label"] in MAP][:1200]
    directory = root / "artifacts/glm-full-20260909"
    return {
        "current_model_evaluation": "not_run",
        "historical_summary": str(historical_path.relative_to(root)),
        "historical_business": historical["reviewed_summaries"],
        "historical_compound": historical["reviewed_compound_summaries"],
        "historical_public_accuracy": historical["public_accuracy"],
        "historical_raw_report_available": (directory / "report.json").is_file(),
        "historical_business_records": len(list((directory / "records").glob("business-*.json"))),
        "historical_public_records": len(list((directory / "records").glob("public-*.json"))),
        "dataset_hashes": hashes,
        "business_development": {"tasks": len(business), "families": len({r["family"] for r in business}),
                                 "compound": sum(r["group"].startswith("compound") for r in business)},
        "public_resume_subset": {"samples": len(public), "source_labels": dict(Counter(r["label"] for r in public))},
        "note": "Historical summaries alone cannot recheck individual predictions or reproduce the current model's quality.",
    }


if __name__ == "__main__":
    result = audit()
    output = ROOT / ".runtime/resume-evidence.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("current_model_evaluation", "historical_raw_report_available",
                     "historical_business_records", "historical_public_records", "dataset_hashes",
                     "business_development", "public_resume_subset")}, ensure_ascii=False, indent=2))
    print("Evidence inventory:", output)
    if "mismatch" in result["dataset_hashes"].values():
        raise SystemExit("Frozen dataset hash mismatch")
