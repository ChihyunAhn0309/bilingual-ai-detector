#!/usr/bin/env python3
"""Evaluate labeled binary detector probabilities; never trains or calibrates a model."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import sys
from detector import valid_probability, ensure_new_output, write_json


def wilson(successes, n):
    if not n:
        return None
    z = 1.959963984540054
    p = successes / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0, center - half), min(1, center + half)]


def auroc(rows):
    ordered = sorted(rows, key=lambda r: r["p_ai"])
    positive = sum(r["label"] for r in rows)
    negative = len(rows) - positive
    if not positive or not negative:
        return None
    rank_sum, i = 0.0, 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j]["p_ai"] == ordered[i]["p_ai"]:
            j += 1
        rank_sum += ((i + 1 + j) / 2) * sum(r["label"] for r in ordered[i:j])
        i = j
    return (rank_sum - positive * (positive + 1) / 2) / (positive * negative)


def validate_rows(rows):
    if not rows:
        raise ValueError("No rows")
    seen, versions, splits_by_group = set(), set(), defaultdict(set)
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each row must be an object")
        for field in ("doc_id", "group_id", "language", "genre", "detector_version", "provenance"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Missing nonempty {field}")
        if row["doc_id"] in seen:
            raise ValueError("Duplicate doc_id; revisions must be grouped and independently identified")
        seen.add(row["doc_id"])
        if row.get("split") not in ("calibration", "test"):
            raise ValueError("split must be calibration or test")
        if type(row.get("label")) is not int or row["label"] not in (0, 1):
            raise ValueError("Binary labels must be integers 0 or 1; mixed labels need a separate task definition")
        if not valid_probability(row.get("p_ai")):
            raise ValueError("p_ai must be a finite probability in [0,1]")
        versions.add(row["detector_version"])
        splits_by_group[row["group_id"]].add(row["split"])
    if len(versions) != 1:
        raise ValueError("Evaluate one detector version at a time")
    if any(len(splits) > 1 for splits in splits_by_group.values()):
        raise ValueError("group_id leakage across calibration and test")
    if not any(row["split"] == "test" for row in rows):
        raise ValueError("An untouched test split is required")


def metrics(rows, threshold):
    n = len(rows)
    if not n:
        return None
    tp = sum(r["label"] == 1 and r["p_ai"] >= threshold for r in rows)
    fp = sum(r["label"] == 0 and r["p_ai"] >= threshold for r in rows)
    positives = sum(r["label"] for r in rows)
    negatives = n - positives
    tn, fn = negatives - fp, positives - tp
    bins = []
    ece = 0.0
    for i in range(10):
        group = [r for r in rows if min(int(r["p_ai"] * 10), 9) == i]
        if group:
            mean = sum(r["p_ai"] for r in group) / len(group)
            rate = sum(r["label"] for r in group) / len(group)
            ece += len(group) / n * abs(mean - rate)
            bins.append({"lower": i / 10, "upper": (i + 1) / 10, "n": len(group),
                         "mean_probability": mean, "observed_ai_rate": rate})
    losses = []
    for row in rows:
        probability_of_truth = row["p_ai"] if row["label"] else 1 - row["p_ai"]
        losses.append(-math.log(max(1e-15, probability_of_truth)))
    return {"n": n, "human_n": negatives, "ai_n": positives, "ai_prevalence": positives / n,
            "threshold": threshold, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "accuracy": (tp + tn) / n, "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / positives if positives else None,
            "false_positive_rate": fp / negatives if negatives else None,
            "fpr_wilson_95": wilson(fp, negatives),
            "recall_wilson_95": wilson(tp, positives), "auroc": auroc(rows),
            "brier": sum((r["p_ai"] - r["label"]) ** 2 for r in rows) / n,
            "log_loss_clipped_1e_15": sum(losses) / n,
            "ece_10_equal_width_bins": ece, "reliability_bins": bins}


def evaluate(rows, threshold=0.5, data_kind="unspecified"):
    validate_rows(rows)
    if not valid_probability(threshold):
        raise ValueError("threshold must lie in [0,1]")
    test = [r for r in rows if r["split"] == "test"]
    result = {"data_kind": data_kind, "detector_version": rows[0]["detector_version"],
              "test": metrics(test, threshold), "by_language": {}, "by_language_and_genre": {},
              "calibration_performed": False,
              "notes": ["Metrics are descriptive of supplied labels; provenance was not independently authenticated.",
                        "Wilson intervals assume independent observations; use group bootstrap for correlated documents.",
                        "ECE is binning/sample-size dependent and does not establish per-document calibration.",
                        "No model selection or threshold tuning is performed on the test set."]}
    languages = sorted(set(r["language"] for r in test))
    for language in languages:
        result["by_language"][language] = metrics([r for r in test if r["language"] == language], threshold)
    pairs = sorted(set((r["language"], r["genre"]) for r in test))
    for language, genre in pairs:
        result["by_language_and_genre"][f"{language}/{genre}"] = metrics(
            [r for r in test if r["language"] == language and r["genre"] == genre], threshold)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSONL with doc_id, group_id, language, genre, provenance, detector_version, split, label, p_ai")
    parser.add_argument("--threshold", type=float, default=0.5, help="Prespecified threshold; do not tune on the test results")
    parser.add_argument("--data-kind", choices=["real", "synthetic", "unspecified"], default="unspecified")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        ensure_new_output(args.out, [args.input])
        rows = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        write_json(evaluate(rows, args.threshold, args.data_kind), args.out)
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
