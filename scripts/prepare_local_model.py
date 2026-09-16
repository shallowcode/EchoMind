"""Download pinned official Qwen GGUF and llama.cpp CPU binaries into .runtime only."""

import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile
import argparse

ROOT = Path(__file__).resolve().parents[1] / ".runtime"
ROOT.mkdir(exist_ok=True)
MODEL_REV = "23749fefcc72300e3a2ad315e1317431b06b590a"
parser = argparse.ArgumentParser()
parser.add_argument("--size", choices=["0.6B", "1.7B"], default="0.6B")
args = parser.parse_args()
if args.size == "1.7B":
    MODEL_REV = "90862c4b9d2787eaed51d12237eafdfe7c5f6077"
sources = {
    "llama.zip": "https://github.com/ggml-org/llama.cpp/releases/download/b10853/llama-b10853-bin-win-cpu-x64.zip",
    f"Qwen3-{args.size}-Q8_0.gguf": f"https://huggingface.co/Qwen/Qwen3-{args.size}-GGUF/resolve/{MODEL_REV}/Qwen3-{args.size}-Q8_0.gguf",
}
manifest_path = ROOT / "model_manifest.json"
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
for name, url in sources.items():
    target = ROOT / name
    if not target.exists():
        print("Downloading", name, flush=True)
        urllib.request.urlretrieve(url, target.with_suffix(target.suffix + ".part"))
        target.with_suffix(target.suffix + ".part").replace(target)
    digest = hashlib.file_digest(target.open("rb"), "sha256").hexdigest()
    manifest[name] = {"source": url, "sha256": digest, "bytes": target.stat().st_size}
    print(name, target.stat().st_size, digest, flush=True)
with zipfile.ZipFile(ROOT / "llama.zip") as z:
    for name in z.namelist():
        if (
            not (ROOT / "llama" / name)
            .resolve()
            .is_relative_to((ROOT / "llama").resolve())
        ):
            raise ValueError("Archive traversal")
    if not (ROOT / "llama/llama-server.exe").exists():
        z.extractall(ROOT / "llama")
(ROOT / "model_manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)
