"""Explicit immutable report comparison; 5% is a configured gate, not proof of significance."""

import argparse
import json
from pathlib import Path


def compare(old, new, threshold=0.05):
    for key in ["dataset_sha256", "evaluated_tasks", "transport", "concurrency_tasks"]:
        if old[key] != new[key]:
            raise ValueError("Incomparable report field: " + key)
    if old["settings"]["storage"] != new["settings"]["storage"]:
        raise ValueError("Storage backend differs")
    events = []
    for arm in ["single", "multi"]:
        for metric, higher in [
            ("completion_rate", True),
            ("request_p95_ms", False),
            ("mean_model_cost", False),
        ]:
            a = old["summaries"][arm][metric]
            b = new["summaries"][arm][metric]
            if a is None or b is None:
                continue
            relative = (
                ((a - b) if higher else (b - a)) / abs(a)
                if a
                else (float("inf") if (b > a and not higher) else 0)
            )
            if relative > threshold:
                events.append(
                    {
                        "variant": arm,
                        "metric": metric,
                        "before": a,
                        "after": b,
                        "relative_regression": relative,
                    }
                )
    return events


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--threshold", type=float, default=0.05)
    a = p.parse_args()
    events = compare(
        json.loads(Path(a.baseline).read_text()),
        json.loads(Path(a.candidate).read_text()),
        a.threshold,
    )
    print(
        json.dumps(
            {"regressions": events, "baseline_overwritten": False},
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(bool(events))
