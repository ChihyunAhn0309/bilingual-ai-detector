"""Download pinned public model files; no inference service, API key, or submitted text."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

REPO = "wasitaigeneratedcom/ai-text-detector-small"
REVISION = "f1795c86806e6838d4afa33d0b1427f8430c9615"
WEIGHT_SHA256 = "4a1561fadf44ec72934edd6158ff8c76e9388ade1384dbeeea6eb15f93251087"
FILES = ["config.json", "model.safetensors", "serving_head.json", "tokenizer.json",
         "tokenizer_config.json", "README.md", "NOTICE"]


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        while block := f.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def download(destination):
    dest = Path(destination).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in FILES:
        target = dest / name
        url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{name}"
        if not target.exists():
            temporary = dest / (name + ".part")
            if temporary.exists():
                raise ValueError(f"Incomplete download exists: {temporary}; inspect before retrying")
            print(f"Downloading {name}", flush=True)
            with urllib.request.urlopen(url, timeout=60) as response, temporary.open("xb") as out:
                while block := response.read(4 * 1024 * 1024):
                    out.write(block)
            if name == "model.safetensors" and file_hash(temporary) != WEIGHT_SHA256:
                raise ValueError("Weight SHA256 mismatch; model not installed")
            temporary.rename(target)
        hashes[name] = file_hash(target)
        if name == "model.safetensors" and hashes[name] != WEIGHT_SHA256:
            raise ValueError("Existing model weight hash mismatch")
    # The download is public and unauthenticated; its license is recorded, not accepted on a user's behalf.
    manifest = {"repo": REPO, "revision": REVISION, "license": "Apache-2.0",
                "files_sha256": hashes, "inference_location": "local_only",
                "source": f"https://huggingface.co/{REPO}/tree/{REVISION}"}
    (dest / "download-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    args = parser.parse_args()
    print(json.dumps(download(args.destination), indent=2))
