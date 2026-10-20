"""Stratified public intent samples, kept separate from authored transaction tasks.

Use one representative per near-duplicate cluster; split only after clustering.
Raw/derived Bitext text stays under .runtime with source/license metadata.
"""

import argparse
import csv
import hashlib
import io
import json
import random
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_acceptance_dataset import write_frozen
from scripts.build_supportflow_dataset import REV, URL


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


SOURCE_SHA256 = "6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434"


def prepare_source(download=False):
    directory = ROOT / ".runtime/datasets"
    raw_path = directory / "bitext.csv"
    if not raw_path.exists():
        if not download:
            raise FileNotFoundError("Run scripts/prepare_public_intents.py --download to restore the pinned public data")
        directory.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=60) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
            raise ValueError("Downloaded source hash does not match the historical revision")
        raw_path.write_bytes(raw)
    raw = raw_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Public source hash changed; fetch the pinned revision first")
    # Reconstruct the originally exposed 54-example sample before cluster filtering.
    old_path = directory / "bitext-sample.json"
    if not old_path.exists():
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        rng = random.Random(20260908)
        examples = []
        for label in sorted({r["intent"] for r in rows}):
            subset = [r for r in rows if r["intent"] == label]
            rng.shuffle(subset)
            examples.extend({"message": r["instruction"], "label": label} for r in subset[:2])
        write_frozen(old_path, {"source": URL, "revision": REV, "license": "CDLA-Sharing-1.0",
                               "source_sha256": SOURCE_SHA256, "seed": 20260908,
                               "purpose": "Historical exposure filter; not new model results", "examples": examples})
    return raw_path


def main(download=False):
    raw_path = prepare_source(download)
    raw = raw_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
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
    manifest_path = ROOT / "evaluation/datasets/trial-v3/public-manifest.json"
    if manifest_path.exists():
        # Git may use CRLF for the tracked manifest; retain its bytes and hash.
        if json.loads(manifest_path.read_text(encoding="utf-8")) != manifest:
            raise ValueError("Restored dataset differs from the historical manifest; create a new version")
    else:
        write_frozen(manifest_path, manifest)
    print(
        json.dumps(
            {"sampled": manifest["sampled"], "splits": manifest["splits"]},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Restore pinned public CSV and exposure sample if missing; no model calls")
    main(parser.parse_args().download)
