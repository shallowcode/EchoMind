import json

import pytest
from pathlib import Path

from scripts.run_full_evaluation import (
    atomic,
    failure_record,
    freeze,
    paired,
    summarize_public,
)
from supportflow.contracts import Settings


def test_windows_replace_retries_and_progress_is_best_effort(tmp_path, monkeypatch):
    import scripts.run_full_evaluation as module

    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    original = Path.replace
    calls = []

    def transient(self, target):
        calls.append(target)
        if len(calls) == 1:
            raise PermissionError("sharing violation")
        return original(self, target)

    monkeypatch.setattr(Path, "replace", transient)
    assert atomic(tmp_path / "result.json", {"saved": True})
    assert len(calls) == 2

    def blocked(self, target):
        raise PermissionError("held open")

    monkeypatch.setattr(Path, "replace", blocked)
    assert atomic(tmp_path / "progress.json", {}, best_effort=True) is False
    with pytest.raises(PermissionError):
        atomic(tmp_path / "required-result.json", {})


def test_checkpoints_keep_failures_and_public_errors_in_denominator(tmp_path):
    c = {"id": "c", "group": "g", "family": "f", "split": "development"}
    row = failure_record(c, "multi", TimeoutError(), 5)
    path = tmp_path / "result.json"
    atomic(path, row)
    assert json.loads(path.read_text())["complete"] is False
    assert not path.with_suffix(".json.tmp").exists()
    base = {
        "expected": "refund",
        "http_status": 200,
        "model_failed": False,
        "trace": {"input_tokens": 1, "output_tokens": 1},
    }
    metrics = summarize_public(
        [
            {**base, "predicted": "refund"},
            {**base, "predicted": "ERROR", "http_status": 0},
        ]
    )
    assert (
        metrics["evaluated"] == 2
        and metrics["accuracy"] == 0.5
        and metrics["http_errors"] == 1
    )


def test_resume_freeze_rejects_changed_source_or_settings(tmp_path, monkeypatch):
    import scripts.run_full_evaluation as module

    monkeypatch.setattr(module, "ROOT", tmp_path)
    source = tmp_path / "scripts/a.py"
    source.parent.mkdir()
    source.write_text("x=1")
    for split in module.SPLITS:
        p = tmp_path / f".runtime/datasets/bitext-v2/{split}.json"
        atomic(p, {"examples": []})
    out = tmp_path / "output"
    out.mkdir()
    s = Settings(model_key="private")
    frozen = freeze(out, s)
    assert "model_key" not in frozen["settings"]
    assert freeze(out, s) == frozen
    with pytest.raises(ValueError, match="changed"):
        freeze(out, s.model_copy(update={"model_name": "other"}))
    source.write_text("x=2")
    with pytest.raises(ValueError, match="changed"):
        freeze(out, s)


def test_paired_family_weights_and_missing_arm():
    rows = []
    for i in range(25):
        rows += [
            {"id": str(i), "family": "a", "variant": a, "complete": a == "multi"}
            for a in ["single", "multi"]
        ]
    rows += [
        {"id": "b", "family": "b", "variant": a, "complete": a == "single"}
        for a in ["single", "multi"]
    ]
    rows += [{"id": "incomplete", "family": "c", "variant": "single", "complete": True}]
    assert paired(rows)["family_count"] == 2
    assert paired(rows)["family_macro_delta"] == 0
