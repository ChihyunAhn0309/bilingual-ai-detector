"""Offline Korean classifier with learned coefficients and held-out sigmoid calibration.

Inference uses only the Python standard library. It never downloads, uploads, or invents scores.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import statistics
import sys

from detector import read_text, text_hash, ensure_new_output, write_json, is_hangul
from evidence import paragraphs, anchor

DEFAULT_MODEL = Path(__file__).resolve().parents[1] / "models" / "korean-linear-v1.json"
RELEASE_MODEL_SHA256 = "f3048088269f293b5f54b131a26571eefcdb9ffd57d86acfd41b4d8d71d41e1f"
FEATURE_NAMES = ["comma_per_1000", "period_per_1000", "question_per_1000", "exclamation_per_1000",
                 "newline_per_1000", "digit_share", "latin_share", "whitespace_share", "quote_per_1000",
                 "unit_mean_length", "surface_type_token_ratio", "repeated_bigram_share",
                 "rough_sentence_length_cv", "formal_ending_share", "sentence_per_1000", "colon_per_1000"]


def sigmoid(x):
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    z = math.exp(x)
    return z / (1 + z)


def normalize_for_features(text):
    # Matches sklearn's char analyzer preprocessing with lowercase=False.
    return re.sub(r"\s\s+", " ", text)


def ngram_counts(text):
    normalized = normalize_for_features(text)
    return Counter(normalized[i:i+n] for n in range(2, 6) for i in range(max(0, len(normalized)-n+1)))


def normalized_offsets(text):
    """Map each feature character back to its exact original range, including whitespace runs."""
    chars, offsets, cursor = [], [], 0
    for match in re.finditer(r"\s\s+", text):
        chars.extend(text[cursor:match.start()])
        offsets.extend((i, i+1) for i in range(cursor, match.start()))
        chars.append(" "); offsets.append((match.start(), match.end()))
        cursor = match.end()
    chars.extend(text[cursor:])
    offsets.extend((i, i+1) for i in range(cursor, len(text)))
    return "".join(chars), offsets


def style_features(text):
    n = max(1, len(text))
    units = text.split()
    spans = [s.strip() for s in re.findall(r"[^.!?。！？\r\n]+(?:[.!?。！？]+|(?=[\r\n]|$))", text) if s.strip()]
    lengths = [len(s) for s in spans]
    mean = statistics.mean(lengths) if lengths else 0
    pairs = list(zip(units, units[1:]))
    formals = sum(bool(re.search(r"(?:합니다|습니다|됩니다|입니다)[.!?。！？]*$", s)) for s in spans)
    return [1000*text.count(",")/n, 1000*text.count(".")/n, 1000*text.count("?")/n,
            1000*text.count("!")/n, 1000*text.count("\n")/n,
            sum(c.isdigit() for c in text)/n, sum(c.isascii() and c.isalpha() for c in text)/n,
            sum(c.isspace() for c in text)/n, 1000*sum(c in '\"\'“”‘’' for c in text)/n,
            sum(map(len, units))/len(units) if units else 0,
            len(set(units))/len(units) if units else 0,
            1-len(set(pairs))/len(pairs) if pairs else 0,
            statistics.pstdev(lengths)/mean if mean else 0,
            formals/len(spans) if spans else 0, 1000*len(spans)/n, 1000*text.count(":")/n]


class KoreanDetector:
    def __init__(self, path=DEFAULT_MODEL):
        source = Path(path).read_bytes()
        self.model_sha256 = __import__("hashlib").sha256(source).hexdigest()
        if Path(path).resolve() == DEFAULT_MODEL.resolve() and self.model_sha256 != RELEASE_MODEL_SHA256:
            raise ValueError("Bundled Korean model hash mismatch; restore the reviewed model artifact")
        self.m = json.loads(source.decode("utf-8"))
        if not isinstance(self.m, dict) or self.m.get("schema_version") != 1 or self.m.get("labels") != ["human", "ai"]:
            raise ValueError("Unsupported Korean model schema/class order")
        size = len(self.m["vocabulary"])
        if (len(self.m["idf"]) != size or len(self.m["coefficients"]) != size + len(FEATURE_NAMES)
                or len(self.m["style_mean"]) != len(FEATURE_NAMES) or len(self.m["style_scale"]) != len(FEATURE_NAMES)):
            raise ValueError("Model dimensions do not match")
        self.vocab = {term: i for i, term in enumerate(self.m["vocabulary"])}
        if len(self.vocab) != size or any(not isinstance(t, str) or not 2 <= len(t) <= 5 for t in self.vocab) or self.m.get("style_feature_names") != FEATURE_NAMES:
            raise ValueError("Duplicate vocabulary or incompatible style features")
        arrays = [self.m["idf"], self.m["coefficients"], self.m["style_mean"], self.m["style_scale"]]
        if any(type(v) not in (int, float) or not math.isfinite(v) for values in arrays for v in values) or any(v <= 0 for v in self.m["style_scale"]+self.m["idf"]):
            raise ValueError("Invalid model values")
        for value in (self.m["intercept"], self.m["style_weight"], self.m["calibration"]["slope"], self.m["calibration"]["intercept"]):
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError("Invalid scalar model value")
        if self.m["calibration"]["slope"] <= 0:
            raise ValueError("Invalid calibration direction")

    def components(self, text):
        counts = ngram_counts(text)
        values = {self.vocab[g]: (1+math.log(c))*self.m["idf"][self.vocab[g]] for g, c in counts.items() if g in self.vocab}
        norm = math.sqrt(sum(v*v for v in values.values()))
        if norm:
            values = {i: v/norm for i, v in values.items()}
        base = len(self.vocab)
        styles = style_features(text)
        for i, value in enumerate(styles):
            values[base+i] = ((value-self.m["style_mean"][i])/self.m["style_scale"][i])*self.m["style_weight"]
        contributions = {i: value*self.m["coefficients"][i] for i, value in values.items()}
        score = self.m["intercept"] + sum(contributions.values())
        coverage = sum(c for g, c in counts.items() if g in self.vocab)/max(1, sum(counts.values()))
        return score, contributions, styles, coverage

    def predict(self, text):
        score, _, _, _ = self.components(text)
        return sigmoid(self.m["calibration"]["slope"]*score+self.m["calibration"]["intercept"])

    def analyze(self, text, genre="unknown", explain=True, max_occlusions=60):
        if genre not in ("essay", "abstract", "poetry", "unknown") or type(max_occlusions) is not int or not 0 <= max_occlusions <= 200:
            raise ValueError("Unsupported genre or invalid occlusion limit")
        if not text.strip():
            raise ValueError("Empty text")
        if len(text) > 200000:
            raise ValueError("Input exceeds 200,000 codepoints; no silent truncation")
        hangul = sum(is_hangul(c) for c in text)
        letters = sum(c.isalpha() for c in text)
        if hangul < 10 or hangul/max(1, letters) < .5:
            raise ValueError("Korean-dominant prose is required; mixed/other languages need separate analysis")
        score, contributions, styles, coverage = self.components(text)
        slope = self.m["calibration"]["slope"]
        calibrated_logit = slope*score + self.m["calibration"]["intercept"]
        p_ai = sigmoid(calibrated_logit)
        bounds = self.m["training_length_codepoints"]
        cautions = []
        if self.model_sha256 != RELEASE_MODEL_SHA256:
            cautions.append("Custom model artifact: published benchmark results do not apply to these weights.")
        if len(text) < bounds["p05"] or len(text) > bounds["p95"]:
            cautions.append("Input length is outside the training 5th–95th percentile; probability reliability may differ.")
        if genre not in ("essay", "abstract", "poetry"):
            cautions.append("Genre is not explicitly within the evaluated essay/abstract/poetry scope; treat the numeric result as an extrapolation.")
        if coverage < self.m["training_ngram_coverage_p05"]:
            cautions.append("Learned character-pattern coverage is below the training reference range.")
        result = {"mode": "offline_korean_calibrated_classifier", "model_id": self.m["model_id"],
                  "measured_at_utc": datetime.now(timezone.utc).isoformat(),
                  "model_sha256": self.model_sha256, "text_sha256": text_hash(text),
                  "characters_codepoints": len(text), "all_input_scored": True,
                  "class_probabilities": {"human": 1-p_ai, "ai": p_ai},
                  "percentages": {"human": round(100*(1-p_ai), 2), "ai": round(100*p_ai, 2)},
                  "probability_semantics": "Estimated Human/AI class probabilities conditional on the documented calibration reference, not a verified person's writing history.",
                  "calibration": self.m["calibration"], "genre_requested": genre,
                  "applicability_cautions": cautions, "ngram_coverage": coverage,
                  "raw_logit": score, "calibrated_logit": calibrated_logit,
                  "external_detector_calls": 0, "authorship_verified": False,
                  "known_limits": ["No validated Mixed/AI-assisted class; complementary probabilities are for the two training labels only.",
                                   "Unknown modern generators, editing, translation and humanizers may change error rates.",
                                   "Calibration is population-dependent; the declared 50% class prior is not a measured prevalence for the user's document."]}
        if explain:
            normalized, source_offsets = normalized_offsets(text)
            lexical = [(i, slope*v) for i, v in contributions.items() if i < len(self.vocab)]
            lexical.sort(key=lambda x: abs(x[1]), reverse=True)
            observed = []
            for i, value in lexical[:30]:
                gram = self.m["vocabulary"][i]
                matches, cursor = [], 0
                while len(matches) < 5:
                    pos = normalized.find(gram, cursor)
                    if pos < 0:
                        break
                    start, end = source_offsets[pos][0], source_offsets[pos+len(gram)-1][1]
                    matches.append(anchor(text, start, end, text[start:end]))
                    cursor = pos+1
                observed.append({"feature": gram, "contribution_to_calibrated_logit": value,
                                 "direction": "ai" if value > 0 else "human", "occurrences": matches,
                                 "interpretation": "Learned statistical contribution, not a universal AI phrase or causal authorship proof."})
            base = len(self.vocab)
            result["feature_explanation"] = {"lexical": observed,
                "style": [{"feature": name, "observed_value": styles[i],
                           "contribution_to_calibrated_logit": slope*contributions.get(base+i, 0)} for i, name in enumerate(FEATURE_NAMES)],
                "intercept_contribution": slope*self.m["intercept"]+self.m["calibration"]["intercept"],
                "all_feature_contributions_sum": slope*sum(contributions.values()),
                "note": "All contributions plus intercept reconstruct calibrated logit. Only the largest lexical contributions are displayed; correlated overlapping ngrams are not independent votes."}
            occlusions = []
            ps = paragraphs(text)
            for p in ps[:max_occlusions]:
                modified = text[:p["start"]]+text[p["end"]:]
                record = {"paragraph_id": p["id"], "start": p["start"], "end": p["end"], "quote": p["text"]}
                if not modified.strip():
                    occlusions.append(record | {"status": "not_measurable"})
                    continue
                after = self.predict(modified)
                occlusions.append(record | {"status": "measured", "after_removal_p_ai": after,
                                             "delta_percentage_points": 100*(p_ai-after)})
            result["paragraph_sensitivity"] = {"baseline_p_ai": p_ai, "paragraphs": occlusions,
                "total_paragraphs": len(ps), "unmeasured_due_to_limit": max(0, len(ps)-max_occlusions),
                "meaning": "Deletion sensitivity only. Length, context and normalization also change; this is not a paragraph authorship probability."}
        return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input"); p.add_argument("--model", default=str(DEFAULT_MODEL))
    p.add_argument("--genre", choices=["essay", "abstract", "poetry", "unknown"], default="unknown")
    p.add_argument("--no-explain", action="store_true"); p.add_argument("--max-occlusions", type=int, default=60)
    p.add_argument("--out"); args = p.parse_args(argv)
    try:
        ensure_new_output(args.out, [args.input, args.model])
        if not 0 <= args.max_occlusions <= 200:
            raise ValueError("max-occlusions must be between 0 and 200")
        text, _ = read_text(args.input)
        write_json(KoreanDetector(args.model).analyze(text, args.genre, not args.no_explain, args.max_occlusions), args.out)
        return 0
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc), "authorship_probabilities": None}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
