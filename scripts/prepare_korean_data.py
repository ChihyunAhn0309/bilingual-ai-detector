"""Fetch pinned public Korean research data for local training; never sends manuscript text."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

KATFISH_REVISION = "5e3dc89cc31a029be38fb2d871476b0aff7b793c"
KODETECT_REVISION = "b822d8e807298797d45003cc4171f554811cb01c"
EXPECTED_HASHES = {
    "essay.jsonl": "2cec81c53556fda7cbd73838c1802617e4dbc4edfc5318694e382bf012b70f2f",
    "abstract.jsonl": "9ded02f600fc3458e047f2402f98c25058b071f3521ded136b9d443d9a458743",
    "poetry.jsonl": "b537843637743b824a239dd3fdac1d7671c610f019b315247664f6ed02636f02",
    "ko-detect/df_final_train_v1.csv": "cd5c5faa8a2d9e031e9a555547f5e957743be9587492eca3468167c46c3b7d80",
    "ko-detect/df_final_valid_v1.csv": "6ded8657f8acca71c99a64ba86630e507039c10e5411db5c63091a26cbc875ad",
    "ko-detect/df_final_test_v2.csv": "113730cb67d5abd71833d8577cda0053df32c46f483528c534d94432da339f3a",
}


def download(destination):
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    urls = {genre+".jsonl": f"https://raw.githubusercontent.com/Shinwoo-Park/katfishnet/{KATFISH_REVISION}/katfish_dataset/{genre}.jsonl"
            for genre in ("essay", "abstract", "poetry")}
    for name in ("df_final_train_v1.csv", "df_final_valid_v1.csv", "df_final_test_v2.csv"):
        urls["ko-detect/"+name] = f"https://raw.githubusercontent.com/gygUnig/Detect_AI_Generated_Korean_Text/{KODETECT_REVISION}/{name}"
    records = []
    for relative, url in urls.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            data = urllib.request.urlopen(url, timeout=60).read(30_000_001)
            if len(data) > 30_000_000:
                raise ValueError("Unexpectedly large public artifact")
            with path.open("xb") as out:
                out.write(data)
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != EXPECTED_HASHES[relative]:
            raise ValueError("Public data hash differs from pinned source: "+relative)
        records.append({"path": relative, "url": url, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"katfish_revision": KATFISH_REVISION, "kodetect_revision": KODETECT_REVISION,
                "sources": records, "note": "Public availability is not a blanket license. Raw source texts are not included in the skill distribution."}
    (root/"source-manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("destination")
    print(json.dumps(download(p.parse_args().destination),indent=2))
