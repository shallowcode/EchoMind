"""Audit frozen dataset integrity, exposure filters and split balance; never call an LLM."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluation.public_intents import MAP
from scripts.build_acceptance_dataset import canonical
from scripts.prepare_public_intents import grams, normalize


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit():
    folder = ROOT / "evaluation/datasets/trial-v3"
    manifest = read(folder / "manifest.json")
    public = read(folder / "public-manifest.json")
    families, texts, ids = {}, {}, set()
    source_rows, public_texts = set(), set()
    by_label = {}
    old = read(ROOT / ".runtime/datasets/bitext-sample.json")
    exposed = [grams(normalize(r["message"])) for r in old["examples"]]
    result = {
        "method": "Offline integrity and lexical leakage checks; no model quality evaluation or human review",
        "authored": {},
        "public_intents": {},
    }
    for split in ["development", "validation", "acceptance"]:
        raw = (folder / (split + ".json")).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == manifest["splits"][split]["sha256"]
        cases = json.loads(raw)["cases"]
        for c in cases:
            assert c["id"] not in ids
            ids.add(c["id"])
            assert families.setdefault(c["family"], split) == split
            assert texts.setdefault(canonical(c["turns"]), split) == split
        result["authored"][split] = {
            "cases": len(cases),
            "families": len({c["family"] for c in cases}),
            "groups": dict(Counter(c["group"] for c in cases)),
        }
        raw = (ROOT / public["splits"][split]["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == public["splits"][split]["sha256"]
        rows = json.loads(raw)["examples"]
        for r in rows:
            normalized = normalize(r["message"])
            assert r["source_row"] not in source_rows
            assert normalized not in public_texts
            assert hashlib.sha256(r["message"].encode()).hexdigest() == r["text_sha256"]
            source_rows.add(r["source_row"])
            public_texts.add(normalized)
            a = grams(normalized)
            assert all(len(a & b) / max(1, len(a | b)) < 0.82 for b in exposed)
            by_label.setdefault(r["label"], []).append(a)
        counts = Counter(r["label"] for r in rows)
        assert len(counts) == 27 and len(set(counts.values())) == 1
        result["public_intents"][split] = {
            "rows": len(rows),
            "source_labels": len(counts),
            "mapped_rows": sum(r["label"] in MAP for r in rows),
            "excluded_rows": sum(r["label"] not in MAP for r in rows),
        }
    for items in by_label.values():
        for i, a in enumerate(items):
            assert all(len(a & b) / max(1, len(a | b)) < 0.82 for b in items[:i])
    assert len(ids) == 1200 and len(families) == 48 and len(source_rows) == 2700
    result["checks"] = {
        "frozen_hashes": True,
        "authored_ids_unique": True,
        "family_splits_disjoint": True,
        "normalized_authored_templates_disjoint": True,
        "public_source_rows_unique": True,
        "public_normalized_text_unique": True,
        "public_old_sample_and_near_matches_excluded": True,
        "public_within_label_near_duplicate_threshold": 0.82,
    }
    result["limitations"] = [
        "Semantic similarity may cross splits",
        "Same author knows scenario design; not independent blind acceptance",
        "Public training corpus may overlap model pretraining",
        "No enterprise customer records or enterprise sign-off",
    ]
    path = folder / "integrity-audit.json"
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    audit()
