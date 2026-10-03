#!/usr/bin/env python3
"""Offline text profiling and saved GPTZero report interpretation. Python 3.10+, stdlib only."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys
import unicodedata



def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_text(path):
    raw = Path(path).read_bytes()
    return raw.decode("utf-8"), sha256(raw)


def text_hash(text):
    return sha256(text.encode("utf-8"))


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def is_hangul(char):
    n = ord(char)
    return (0xAC00 <= n <= 0xD7A3 or 0x1100 <= n <= 0x11FF
            or 0x3130 <= n <= 0x318F or 0xA960 <= n <= 0xA97F
            or 0xD7B0 <= n <= 0xD7FF)


def inspect_text(text, file_hash=None):
    units = text.split()
    letters = [c for c in text if c.isalpha()]
    hangul = sum(is_hangul(c) for c in letters)
    latin = sum("LATIN" in unicodedata.name(c, "") for c in letters)
    # A deliberately rough splitter; abbreviations, decimals, lists and poetry can break it.
    spans = [m for m in re.finditer(r"[^.!?。！？\r\n]+(?:[.!?。！？]+|(?=[\r\n]|$))", text)
             if m.group().strip()]
    lengths = [len(m.group().strip()) for m in spans]
    avg = statistics.mean(lengths) if lengths else None
    controls = []
    line = 1
    for offset, char in enumerate(text):
        if unicodedata.category(char) == "Cf" or 0xFE00 <= ord(char) <= 0xFE0F or 0xE0100 <= ord(char) <= 0xE01EF:
            controls.append({"offset_codepoints": offset, "line": line,
                             "codepoint": f"U+{ord(char):04X}",
                             "name": unicodedata.name(char, "UNNAMED")})
        if char == "\n":
            line += 1
    repeats = Counter(u.casefold() for u in units)
    repeated = [{"surface_form": key, "count": count}
                for key, count in repeats.most_common(15) if count > 1]
    return {
        "schema_version": 1, "mode": "observations_only", "text_sha256": text_hash(text),
        "file_sha256": file_hash, "characters_codepoints": len(text),
        "non_whitespace_characters": sum(not c.isspace() for c in text),
        "whitespace_units": len(units), "hangul_letters": hangul, "latin_letters": latin,
        "other_letters": len(letters) - hangul - latin,
        "hangul_share_of_letters": hangul / len(letters) if letters else None,
        "latin_share_of_letters": latin / len(letters) if letters else None,
        "rough_sentence_count": len(spans), "rough_sentence_mean_characters": avg,
        "rough_sentence_length_cv": statistics.pstdev(lengths) / avg if avg else None,
        "comma_count": text.count(","),
        "commas_per_1000_codepoints": 1000 * text.count(",") / len(text) if text else None,
        "surface_type_token_ratio": len(repeats) / len(units) if units else None,
        "repeated_surface_forms": repeated,
        "unicode_observations": controls[:100], "unicode_observation_count": len(controls),
        "unicode_observations_truncated": len(controls) > 100,
        "authorship_probabilities": None,
        "notes": ["Counts are observations, not authorship evidence or a detector score.",
                  "Whitespace units are neither model tokens nor Korean morphemes.",
                  "Sentence splitting is approximate; inspect punctuation context.",
                  "Script counts do not establish language, fluency or identity.",
                  "Unicode controls are not proof of an AI watermark."]}


def valid_probability(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def normalize_gptzero(raw):
    if not isinstance(raw, dict):
        raise ValueError("Response must be a JSON object")
    if raw.get("error") or raw.get("success") is False:
        raise ValueError("Provider returned an error, not a detection result")
    documents = raw.get("documents")
    if not isinstance(documents, list) or len(documents) != 1 or not isinstance(documents[0], dict):
        raise ValueError("Expected exactly one document in the provider response")
    document = documents[0]
    for obj in (raw, document):
        if "status" in obj and obj["status"] not in ("completed", "success", "succeeded"):
            raise ValueError("Response is not a recognized completed result")
    if document.get("error"):
        raise ValueError("Document has a provider error")
    probabilities = document.get("class_probabilities")
    if not isinstance(probabilities, dict) or set(probabilities) != {"human", "ai", "mixed"}:
        raise ValueError("Expected Human/AI/Mixed class_probabilities; legacy scores cannot substitute")
    if not all(valid_probability(p) for p in probabilities.values()):
        raise ValueError("Probabilities must be finite numbers between 0 and 1")
    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-4, rel_tol=0):
        raise ValueError("Class probabilities do not sum to 1; no renormalization performed")
    return {
        "provider": "GPTZero", "score_semantics": "provider_reported_three_class_probabilities",
        "probabilities": probabilities,
        "percentages": {key: round(value * 100, 2) for key, value in probabilities.items()},
        "document_classification": document.get("document_classification"),
        "predicted_class": document.get("predicted_class"),
        "confidence_category": document.get("confidence_category"),
        "independently_calibrated_here": False,
        "authorship_verified": False,
        "coverage_verified": False,
        "notes": ["Probabilities describe provider classes, not word percentages.",
                  "Missing or mixed probability is never converted into human probability.",
                  "Check language, genre, length, model version and returned input coverage."]}


def request_gptzero(*args, **kwargs):
    """Retained only to fail closed for callers of version 1."""
    raise ValueError("Live commercial detection is disabled by the zero-additional-fee policy; import an existing report instead")


def ensure_new_output(path, inputs=()):
    if not path:
        return
    target = Path(path).resolve()
    if target in [Path(p).resolve() for p in inputs]:
        raise ValueError("Output must not overwrite an input")
    if target.exists():
        raise ValueError("Output already exists; choose a new file to preserve run history")
    target.parent.mkdir(parents=True, exist_ok=True)


def write_json(data, path=None):
    encoded = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    if path:
        with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded + "\n")
    else:
        print(encoded)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "gptzero", "import-gptzero"):
        cmd = sub.add_parser(name)
        cmd.add_argument("input")
        cmd.add_argument("--out")
        if name == "gptzero":
            cmd.add_argument("--allow-upload", action="store_true", help="Deprecated; live uploads are disabled")
            cmd.add_argument("--version", help="Provider model version; omit to use provider default")
    args = parser.parse_args(argv)
    try:
        ensure_new_output(args.out, [args.input])
        if args.command == "inspect":
            text, file_hash = read_text(args.input)
            result = inspect_text(text, file_hash)
        elif args.command == "import-gptzero":
            source = Path(args.input).read_bytes()
            raw = json.loads(source.decode("utf-8-sig"))
            result = {"mode": "imported_result", "imported_at_utc": utc_now(),
                      "response_file_sha256": sha256(source), "input_binding": "unverified",
                      "normalized": normalize_gptzero(raw), "raw_response": raw}
        else:
            request_gptzero()
        write_json(result, args.out)
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc), "authorship_probabilities": None}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
