"""Bounded CPU training and held-out calibration for the Korean detector.

Requires numpy/scipy/scikit-learn only for training. Reads cached public data; no API requests.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import time
import unicodedata

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss
from threadpoolctl import threadpool_limits

from korean_model import KoreanDetector, FEATURE_NAMES, style_features
from evaluate import metrics

SEED = 20261003
MODEL_ID = "korean-char-style-logistic-v1"


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def norm(value):
    return re.sub(r"\W+", "", unicodedata.normalize("NFKC", str(value))).casefold()


def load_data(root):
    root = Path(root)
    rows, sources = [], []
    for file in ("df_final_train_v1.csv", "df_final_valid_v1.csv", "df_final_test_v2.csv"):
        path = root / "ko-detect" / file
        raw = path.read_bytes()
        sources.append({"file": "ko-detect/"+file, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        for i, r in enumerate(csv.DictReader(path.open(encoding="utf-8-sig", newline=""))):
            label = int(r["label"])
            rows.append({"doc_id": f"kodetect/{file}/{i}", "source": "ko-detect", "genre": "essay",
                         "group": "essay-prompt/"+digest(norm(r["essay_main_subject"])),
                         "text": r["text"], "label": label, "external_test_only": file.endswith("test_v2.csv"),
                         "generator": r.get("model") or ("human" if label == 0 else "gpt-4o-mini")})
    for genre in ("essay", "abstract", "poetry"):
        path = root / (genre+".jsonl")
        raw = path.read_bytes()
        sources.append({"file": genre+".jsonl", "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        for i, r in enumerate(json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()):
            key = r["topic"] if genre == "essay" else r["title"] if genre == "abstract" else str(r["poet_number"])
            rows.append({"doc_id": f"katfish/{genre}/{i}", "source": "katfish", "genre": genre,
                         "group": f"katfish-{genre}/"+digest(norm(key)), "text": r["text"], "label": int(r["label"]),
                         "external_test_only": False, "generator": r["written_by"]})
    if any(r["label"] not in (0, 1) or not r["text"].strip() for r in rows):
        raise ValueError("Invalid labels or empty source text")
    # Connect duplicated source texts across datasets before assigning any split.
    parent = {r["group"]: r["group"] for r in rows}
    def find(g):
        while parent[g] != g:
            parent[g] = parent[parent[g]]
            g = parent[g]
        return g
    fingerprints, conflicts = {}, set()
    for r in rows:
        fp = digest(norm(r["text"]))
        r["normalized_text_sha256"] = fp
        if fp in fingerprints:
            previous = fingerprints[fp]
            a, b = find(r["group"]), find(previous["group"])
            parent[max(a, b)] = min(a, b)
            if previous["label"] != r["label"]:
                conflicts.add(fp)
        else:
            fingerprints[fp] = r
    seen, kept, duplicate_count = set(), [], 0
    # Keep external-test identities in preference to an otherwise identical training record.
    for r in sorted(rows, key=lambda r: (not r["external_test_only"], r["doc_id"])):
        fp = r["normalized_text_sha256"]
        if fp in conflicts:
            continue
        if fp in seen:
            duplicate_count += 1
            continue
        seen.add(fp)
        r["group_id"] = find(r["group"])
        kept.append(r)
    groups = defaultdict(set)
    group_genres = defaultdict(set)
    for r in kept:
        group_genres[r["group_id"]].add(r["genre"])
    for group, genres in group_genres.items():
        if len(genres) != 1:
            raise ValueError("A duplicate-connected group spans genres; inspect before training")
        groups[next(iter(genres))].add(group)
    assignment = {}
    rng = random.Random(SEED)
    for genre in sorted(groups):
        gs = sorted(groups[genre]); rng.shuffle(gs)
        n = len(gs)
        cuts = [int(n*.60), int(n*.75), int(n*.90)]
        for i, g in enumerate(gs):
            assignment[g] = "train" if i < cuts[0] else "selection" if i < cuts[1] else "calibration" if i < cuts[2] else "test"
    for r in kept:
        assigned = assignment[r["group_id"]]
        r["split"] = "transfer_test" if r["external_test_only"] and assigned != "test" else assigned
        r["text_sha256"] = digest(r["text"])
    audit = {"source_rows": len(rows), "retained_rows": len(kept), "normalized_duplicates_removed": duplicate_count,
             "conflicting_normalized_texts_removed": len(conflicts), "groups_per_genre": {k: len(v) for k,v in groups.items()},
             "split_counts": dict(Counter(r["split"] for r in kept)),
             "grouping": "Entire essay topic, abstract title, or source poem group, plus cross-dataset normalized duplicate unions.",
             "near_duplicate_audit": "Normalized exact duplicates checked; semantic near-duplicates and hidden shared authors are not fully observable.",
             "external_test_rule": "Ko-Detect test-v2 rows never enter train, selection or calibration. Test rows with already-used topics form a separately labelled transfer test."}
    return kept, sources, audit


def balanced_weights(rows):
    counts = Counter((r["genre"], r["label"]) for r in rows)
    if len(counts) != 2*len({r["genre"] for r in rows}):
        raise ValueError("Every genre needs both classes")
    return np.array([len(rows)/(len(counts)*counts[(r["genre"], r["label"])]) for r in rows])


def summarize(rows, p):
    prepared = [{"label": r["label"], "p_ai": float(v)} for r, v in zip(rows, p)]
    overall = metrics(prepared, .5)
    weights = balanced_weights(rows)
    overall["genre_class_balanced_brier"] = float(np.average((np.array(p)-np.array([r["label"] for r in rows]))**2, weights=weights))
    overall["genre_class_balanced_log_loss"] = float(log_loss([r["label"] for r in rows], p, sample_weight=weights))
    overall["balanced_accuracy"] = .5*(overall["recall"]+1-overall["false_positive_rate"])
    by_genre = {g: metrics([p for r,p in zip(rows,prepared) if r["genre"] == g], .5) for g in sorted({r["genre"] for r in rows})}
    by_generator = {g: metrics([p for r,p in zip(rows,prepared) if r["generator"] == g], .5) for g in sorted({r["generator"] for r in rows})}
    return {"overall": overall, "by_genre": by_genre, "by_generator": by_generator}


def bootstrap_groups(rows, p, iterations=300):
    groups = defaultdict(list)
    for r, value in zip(rows, p):
        groups[r["group_id"]].append((r["label"], value))
    keys = sorted(groups)
    rng = random.Random(SEED+1)
    accuracies, fprs = [], []
    for _ in range(iterations):
        sample = [x for key in rng.choices(keys, k=len(keys)) for x in groups[key]]
        accuracies.append(sum((p >= .5) == y for y,p in sample)/len(sample))
        humans = [p for y,p in sample if y == 0]
        if humans:
            fprs.append(sum(p >= .5 for p in humans)/len(humans))
    return {"iterations": iterations, "unit": "source/prompt group", "groups": len(keys),
            "accuracy_percentile_95": np.quantile(accuracies, [.025,.975]).tolist(),
            "fpr_percentile_95": np.quantile(fprs, [.025,.975]).tolist()}


def train(data_root, output_dir):
    start = time.monotonic()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=False)
    rows, sources, audit = load_data(data_root)
    sets = {name: [r for r in rows if r["split"] == name] for name in ("train", "selection", "calibration", "test", "transfer_test")}
    for name in ("train", "selection", "calibration", "test"):
        if not sets[name] or len({r["label"] for r in sets[name]}) != 2:
            raise ValueError("Invalid split: "+name)
    # Every fitting/primary holdout stage must use separate groups.
    split_names = ("train", "selection", "calibration", "test")
    for i, a in enumerate(split_names):
        for b in split_names[i+1:]:
            if {r["group_id"] for r in sets[a]} & {r["group_id"] for r in sets[b]}:
                raise ValueError("Group leakage between "+a+" and "+b)
    print(json.dumps(audit, ensure_ascii=False), flush=True)
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2,5), min_df=3, max_features=40000,
                                 lowercase=False, sublinear_tf=True, dtype=np.float64)
    train_x = vectorizer.fit_transform([r["text"] for r in sets["train"]])
    matrices = {"train": train_x}
    for name in sets:
        if name != "train":
            matrices[name] = vectorizer.transform([r["text"] for r in sets[name]])
    scaler = StandardScaler()
    train_style = scaler.fit_transform([style_features(r["text"]) for r in sets["train"]])
    styles = {"train": train_style}
    for name in sets:
        if name != "train":
            styles[name] = scaler.transform([style_features(r["text"]) for r in sets[name]])
    y = {name: np.array([r["label"] for r in subset]) for name, subset in sets.items()}
    weights = {name: balanced_weights(subset) for name, subset in sets.items() if name != "transfer_test"}
    trials, best = [], None
    with threadpool_limits(limits=2):
        for style_weight in (0.0, 0.25):
            tx = hstack([matrices["train"], csr_matrix(styles["train"]*style_weight)], format="csr")
            vx = hstack([matrices["selection"], csr_matrix(styles["selection"]*style_weight)], format="csr")
            for c in (.5, 2.0, 8.0):
                model = LogisticRegression(C=c, max_iter=500, solver="liblinear", random_state=SEED)
                model.fit(tx, y["train"], sample_weight=weights["train"])
                probs = model.predict_proba(vx)[:,1]
                loss = float(log_loss(y["selection"], probs, sample_weight=weights["selection"]))
                trial = {"C": c, "style_weight": style_weight, "selection_balanced_log_loss": loss, "iterations": int(model.n_iter_[0])}
                trials.append(trial)
                print("Candidate", json.dumps(trial), flush=True)
                if best is None or loss < best[0]:
                    best = (loss, model, style_weight, c)
        _, model, sw, c = best
        xs = {name: hstack([matrices[name], csr_matrix(styles[name]*sw)], format="csr") for name in sets}
        calibration_scores = model.decision_function(xs["calibration"])
        # The sigmoid is fit only on separate calibration groups, never on selection or test.
        calibrator = LogisticRegression(C=10.0, solver="lbfgs", max_iter=500, random_state=SEED)
        calibrator.fit(calibration_scores.reshape(-1,1), y["calibration"], sample_weight=weights["calibration"])
        slope, intercept = float(calibrator.coef_[0,0]), float(calibrator.intercept_[0])
        if slope <= 0:
            raise ValueError("Calibration slope is nonpositive; do not release an inverted detector")
    lengths = np.array([len(r["text"]) for r in sets["train"]])
    artifact = {"schema_version": 1, "model_id": MODEL_ID, "labels": ["human", "ai"],
        "vocabulary": vectorizer.get_feature_names_out().tolist(), "idf": vectorizer.idf_.tolist(),
        "coefficients": model.coef_[0].tolist(), "intercept": float(model.intercept_[0]),
        "style_feature_names": FEATURE_NAMES, "style_mean": scaler.mean_.tolist(), "style_scale": scaler.scale_.tolist(),
        "style_weight": sw, "training_length_codepoints": {"min": int(lengths.min()), "max": int(lengths.max()),
            "p05": float(np.quantile(lengths,.05)), "p95": float(np.quantile(lengths,.95))},
        "training_ngram_coverage_p05": 0.0,
        "calibration": {"method": "held_out_regularized_sigmoid", "slope": slope, "intercept": intercept,
            "n": len(sets["calibration"]), "group_n": len({r["group_id"] for r in sets["calibration"]}),
            "reference_ai_prior": .5, "genre_weighting": "Equal essay/abstract/poetry and equal Human/AI within each genre",
            "scope": "Korean public benchmark genres; no universal authorship guarantee"},
        "training_seed": SEED, "selected_C": c, "sources": sources}
    model_path = out / "korean-linear-v1.json"
    model_path.write_text(json.dumps(artifact, ensure_ascii=False, separators=(",",":"), allow_nan=False), encoding="utf-8")
    local = KoreanDetector(model_path)
    coverages = [local.components(r["text"])[3] for r in sets["train"]]
    artifact["training_ngram_coverage_p05"] = float(np.quantile(coverages,.05))
    model_path.write_text(json.dumps(artifact, ensure_ascii=False, separators=(",",":"), allow_nan=False), encoding="utf-8")
    local = KoreanDetector(model_path)
    report = {"model_id": MODEL_ID, "seed": SEED, "audit": audit, "source_files": sources,
              "selection_trials": trials, "selected": {"C": c, "style_weight": sw},
              "calibration": artifact["calibration"], "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
              "test_metrics": {}, "probability_calibration_performed": True,
              "limitations": ["Public datasets and older generators do not establish current universal Korean accuracy.",
                              "No author IDs for all sources; normalized duplicates and topic/source groups are controlled but all semantic duplicates cannot be excluded.",
                              "Transfer test shares topics with fitting stages and is reported separately.",
                              "Binary class probabilities cannot certify AI assistance, mixed authorship or the writing history of an individual."]}
    predictions = []
    # All choices are now frozen. No fitting follows test evaluation.
    for name in ("test", "transfer_test"):
        raw_probs = model.predict_proba(xs[name])[:,1]
        calibrated = calibrator.predict_proba(model.decision_function(xs[name]).reshape(-1,1))[:,1]
        report["test_metrics"][name] = {"uncalibrated": summarize(sets[name], raw_probs), "calibrated": summarize(sets[name], calibrated),
                                      "group_bootstrap": bootstrap_groups(sets[name], calibrated)}
        for r, p, raw in zip(sets[name], calibrated, raw_probs):
            predictions.append({k:r[k] for k in ("doc_id", "group_id", "split", "genre", "source", "generator", "label", "text_sha256")} |
                               {"p_ai": float(p), "p_ai_before_calibration": float(raw)})
        # Pure standard-library inference must numerically match the trained pipeline.
        diffs = [abs(local.predict(r["text"])-float(p)) for r,p in list(zip(sets[name],calibrated))[:25]]
        if max(diffs, default=0) > 1e-8:
            raise ValueError("Exported inference parity check failed")
        report["test_metrics"][name]["export_parity_max_abs_error"] = max(diffs, default=0)
    report["elapsed_seconds"] = time.monotonic()-start
    report["external_detector_calls"] = 0
    (out/"korean-validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    with (out/"korean-test-predictions.jsonl").open("w",encoding="utf-8") as f:
        for r in predictions: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    with (out/"korean-split-manifest.jsonl").open("w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps({k:r[k] for k in ("doc_id","group_id","split","genre","source","label","text_sha256","generator")},ensure_ascii=False)+"\n")
    print("TRAINING_COMPLETE", json.dumps({name:report["test_metrics"][name]["calibrated"]["overall"] for name in report["test_metrics"]},ensure_ascii=False),flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-root", required=True); p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    train(args.data_root,args.output_dir)
