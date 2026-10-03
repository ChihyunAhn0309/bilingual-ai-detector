"""Recount public saved detector verdicts; optionally compare the local model on a fixed sample.

Downloads public research artifacts only. Never calls a detector service or regenerates text.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import io
import json
from pathlib import Path
import random
import statistics
import urllib.request

from detector import ensure_new_output, write_json

REVISION = "3f5ed200e212ef5ca957b6f5675d99ed29ff3c3c"
BASE = f"https://raw.githubusercontent.com/jaeholee-brown/ai-text-detectors/{REVISION}/"


def cached_file(cache, relative):
    # All paths originate in the pinned public index; reject traversal before constructing local paths.
    if Path(relative).is_absolute() or ".." in Path(relative).parts or "\\" in relative or ":" in relative:
        raise ValueError("Invalid public artifact path")
    root = Path(cache).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise ValueError("Artifact escapes cache")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        data = urllib.request.urlopen(BASE + relative, timeout=45).read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError("Unexpected artifact size")
        with target.open("xb") as out:
            out.write(data)
    return target.read_bytes()


def public_counts(rows):
    result = {}
    for detector in ("pangram", "gptzero", "originality"):
        result[detector] = {}
        for condition in ("human", "vanilla", "style_transfer"):
            subset = [r for r in rows if r["condition"] == condition]
            vals = [r[detector + "_pred"].lower() for r in subset]
            if not all(v in ("human", "ai", "mixed") for v in vals):
                raise ValueError("Unknown stored detector verdict")
            errors = sum(v != ("human" if condition == "human" else "ai") for v in vals)
            result[detector][condition] = {"errors": errors, "n": len(subset),
                                          "rate": errors / len(subset) if subset else None,
                                          "metric": "FPR" if condition == "human" else "FNR"}
    return result


def select_sample(rows, per_genre=4, seed=20261003):
    rng = random.Random(seed)
    chosen = []
    for genre in sorted({r["genre"] for r in rows}):
        authors = sorted({r["author_key"] for r in rows if r["genre"] == genre})
        for index, author in enumerate(rng.sample(authors, per_genre)):
            # One human, one vanilla, one style imitation per author; model balanced by cycling.
            unit = ["claude", "gemini", "gpt"][index % 3]
            candidates = [r for r in rows if r["genre"] == genre and r["author_key"] == author]
            ai_units = sorted({r["unit"] for r in candidates if r["condition"] == "vanilla"})
            # Use actual sorted model identifiers if the repository calls GPT "openai", etc.
            unit = ai_units[index % len(ai_units)]
            for condition in ("human", "vanilla", "style_transfer"):
                subset = [r for r in candidates if r["condition"] == condition]
                chosen.append(next(r for r in subset if r["unit"] == ("snippet_1" if condition == "human" else unit)))
    return chosen


def paired_metrics(predictions, column):
    available = [r for r in predictions if r.get(column) is not None]
    result = {"completed": len(available), "requested": len(predictions),
              "coverage": len(available) / len(predictions) if predictions else None}
    for condition in ("human", "vanilla", "style_transfer"):
        subset = [r for r in available if r["condition"] == condition]
        errors = sum(r[column] != (condition != "human") for r in subset)
        result[condition] = {"errors": errors, "n": len(subset), "rate": errors / len(subset) if subset else None}
    result["accuracy_on_completed"] = (sum(r[column] == (r["condition"] != "human") for r in available) / len(available)) if available else None
    return result


def run(cache, model_dir=None, per_genre=4):
    raw = cached_file(cache, "results/all_detectors.csv")
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    report = {"source": "https://epoch.ai/data-insights/ai-detectors-false-negatives",
              "repository_revision": REVISION, "csv_sha256": hashlib.sha256(raw).hexdigest(),
              "external_detector_calls": 0, "public_original_strict_verdict_metrics": public_counts(rows),
              "public_rule": "Only clean AI counts as detecting fully AI text. Mixed is an error on both pure classes.",
              "versions": {"GPTZero": "2026-05-11-base", "Pangram": "3.3.2", "Originality": "Turbo 3.0.2"}}
    if model_dir:
        from local_model import LocalDetector
        selected = select_sample(rows, per_genre)
        # The sample is selected before local scores are observed; no threshold tuning.
        with ThreadPoolExecutor(max_workers=6) as pool:
            texts = list(pool.map(lambda r: cached_file(cache, r["file"]).decode("utf-8"), selected))
        model = LocalDetector(model_dir)
        predictions = []
        for i, (r, text) in enumerate(zip(selected, texts), 1):
            record = {"file": r["file"], "genre": r["genre"], "condition": r["condition"],
                      "author_key": r["author_key"], "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                      "gptzero_ai_involvement": r["gptzero_pred"] in ("ai", "mixed"),
                      "pangram_ai_involvement": r["pangram_pred"] in ("AI", "Mixed"),
                      "originality_ai": r["originality_pred"] == "ai"}
            try:
                result = model.analyze(text, "en")
                score = statistics.mean(w["ai_involvement_class_score"] for w in result["windows"])
                record.update({"local_mean_window_score": score, "windows": len(result["windows"]),
                               "local_at_0_5": score >= .5,
                               "local_at_card_threshold": score >= .9755912190656111})
            except (ValueError, RuntimeError) as exc:
                record["local_error"] = str(exc)
            predictions.append(record)
            print(f"Local benchmark {i}/{len(selected)}", flush=True)
        # Compare on identical completed documents, while retaining all failures in the report.
        common = [r for r in predictions if "local_at_0_5" in r]
        report["paired_pilot"] = {"seed": 20261003, "authors_per_genre": per_genre,
            "selection": "One human snippet and matched vanilla/style passages per randomly sampled author; models cycled.",
            "target": "Any AI involvement; unlike the published strict rule, mixed counts as AI here for every detector.",
            "local_aggregation": "Unweighted mean of all overlapping 768-token-window AI-involvement scores; ranking statistic, not calibrated document probability.",
            "thresholds": "0.5 and the model-card threshold 0.9755912190656111 fixed before scoring; no fitting or selection.",
            "requested": len(predictions), "common_completed": len(common),
            "metrics_common_rows": {key: paired_metrics(common, key) for key in (
                "local_at_0_5", "local_at_card_threshold", "gptzero_ai_involvement", "pangram_ai_involvement", "originality_ai")},
            "predictions": predictions,
            "limitations": ["Small English pilot with correlated author groups, not general-purpose accuracy.",
                            "Training contamination of the local checkpoint cannot be ruled out.",
                            "Commercial verdicts are archived July 2026 versions, not freshly called current models.",
                            "No Korean comparison, probability calibration, or statistical superiority claim."]}
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True); parser.add_argument("--model-dir")
    parser.add_argument("--authors-per-genre", type=int, default=4); parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not 1 <= args.authors_per_genre <= 33:
        parser.error("authors-per-genre must be 1..33")
    ensure_new_output(args.out)
    write_json(run(args.cache, args.model_dir, args.authors_per_genre), args.out)
