"""Stratified public intent samples, kept separate from authored transaction tasks.

Use one representative per near-duplicate cluster; split only after clustering.
Raw/derived Bitext text stays under .runtime with source/license metadata.
"""

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_supportflow_dataset import REV, URL
from scripts.build_acceptance_dataset import write_frozen


def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def grams(text):
    return {text[i : i + 3] for i in range(max(1, len(text) - 2))}


def representatives(rows):
    """Connected components at character-trigram Jaccard >= .82, within source intent.

    One representative per component means selected representatives never meet this
    lexical threshold with each other. This does not establish semantic independence.
    """
    parents = list(range(len(rows)))

    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    sets = [grams(normalize(r["instruction"])) for r in rows]
    for i, a in enumerate(sets):
        for j in range(i):
            b = sets[j]
            if min(len(a), len(b)) < 0.82 * max(len(a), len(b)):
                continue
            common = len(a & b)
            if common / max(1, len(a) + len(b) - common) >= 0.82:
                parents[root(i)] = root(j)
    groups = {}
    for i, row in enumerate(rows):
        groups.setdefault(root(i), row)
    return list(groups.values())


def main():
    raw_path = ROOT / ".runtime/datasets/bitext.csv"
    raw = raw_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != "6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434":
        raise ValueError("Public source hash changed; fetch the pinned revision first")
    old = json.loads(
        (ROOT / ".runtime/datasets/bitext-sample.json").read_text(encoding="utf-8")
    )
    exposed = [grams(normalize(r["message"])) for r in old["examples"]]

    def previously_exposed(text):
        a = grams(normalize(text))
        return any(len(a & b) / max(1, len(a | b)) >= 0.82 for b in exposed)

    by_label = defaultdict(list)
    with raw_path.open(encoding="utf-8-sig", newline="") as f:
        for index, row in enumerate(csv.DictReader(f)):
            if not previously_exposed(row["instruction"]):
                by_label[row["intent"]].append({**row, "source_row": index})
    examples = {s: [] for s in ["development", "validation", "acceptance"]}
    rng = random.Random(20260909)
    counts = {}
    for label, rows in sorted(by_label.items()):
        rng.shuffle(rows)
        selected = representatives(rows[:400])
        if len(selected) < 100:
            selected = representatives(rows)
        if len(selected) < 100:
            raise ValueError("Insufficient distinct clusters for " + label)
        rng.shuffle(selected)
        counts[label] = {
            "available_rows_after_exposure_filter": len(rows),
            "candidate_clusters": len(selected),
            "selected": 100,
        }
        for i, row in enumerate(selected[:100]):
            split = (
                "development" if i < 60 else "validation" if i < 80 else "acceptance"
            )
            examples[split].append(
                {
                    "message": row["instruction"],
                    "label": label,
                    "source_row": row["source_row"],
                    "text_sha256": hashlib.sha256(
                        row["instruction"].encode()
                    ).hexdigest(),
                }
            )
    common = {
        "source": URL,
        "revision": REV,
        "license": "CDLA-Sharing-1.0",
        "license_url": "https://cdla.dev/sharing-1-0/",
        "attribution": "Bitext Innovations, 2024",
        "source_sha256": digest,
        "source_type": "public hybrid synthetic training corpus, not customer traffic",
        "purpose": "English intent evaluation only; not transactional or Chinese task completion",
        "near_duplicate_method": "one representative per within-intent connected component, character-trigram Jaccard >= .82; old 54-example sample and lexical near matches excluded",
        "limitations": [
            "Semantic duplicates and cross-label lexical neighbors may remain",
            "Model pretraining overlap unknown",
            "No independent human adjudication of ontology mapping",
        ],
    }
    manifest = {
        **common,
        "source_rows": 26872,
        "sampled": 2700,
        "per_label": counts,
        "splits": {},
    }
    for split, rows in examples.items():
        path = ROOT / ".runtime/datasets/bitext-v2" / (split + ".json")
        sha = write_frozen(path, {**common, "split": split, "examples": rows})
        manifest["splits"][split] = {
            "path": str(path.relative_to(ROOT)),
            "count": len(rows),
            "sha256": sha,
        }
    write_frozen(ROOT / "evaluation/datasets/trial-v3/public-manifest.json", manifest)
    print(
        json.dumps(
            {"sampled": manifest["sampled"], "splits": manifest["splits"]},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
