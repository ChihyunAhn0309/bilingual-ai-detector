"""Offline English classifier and paragraph-removal sensitivity. No network or paid API."""
import argparse
import json
import math
import os
from pathlib import Path
import sys
import unicodedata

from detector import read_text, text_hash, ensure_new_output, write_json, is_hangul, utc_now
from evidence import paragraphs
from prepare_local_model import REVISION, REPO, WEIGHT_SHA256, file_hash
from runtime_guard import runtime_lock

LABELS = ["human", "ai", "ai_edited", "humanized"]
DEFAULT_MODEL = Path(__file__).resolve().parents[1] / "models" / "tropa-mini"


def validate_english_input(text, language="en"):
    if not text.strip():
        raise ValueError("Empty text")
    if language != "en" or any(is_hangul(c) for c in text):
        raise ValueError("English-only checkpoint; use korean_model.py for Korean or the mixed-language review workflow")
    letters = [c for c in text if c.isalpha()]
    latin = sum("LATIN" in unicodedata.name(c, "") for c in letters)
    if not letters or latin / len(letters) < .8:
        raise ValueError("English prose is required; predominantly non-Latin text is outside this checkpoint's scope")
    return {"declared_language": language, "latin_share_of_letters": latin/len(letters),
            "method": "Script screen only; Latin-script languages are not automatically distinguished from English."}


def windows(ids, offsets, size=766, overlap=128):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Invalid window size/overlap")
    result = []
    start = 0
    while start < len(ids):
        end = min(len(ids), start + size)
        result.append({"token_start": start, "token_end": end, "ids": ids[start:end],
                       "start": offsets[start][0], "end": offsets[end-1][1]})
        if end == len(ids):
            break
        start = end - overlap
    return result


class LocalDetector:
    def __init__(self, model_dir=DEFAULT_MODEL, threads=2):
        directory = Path(model_dir).resolve()
        if not (directory / "model.safetensors").is_file():
            raise ValueError("Local weights are missing. Run prepare_local_model.py separately; no hosted fallback is allowed.")
        # Offline loading only. The separate downloader does not receive user text.
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        # Bound native-library thread pools before importing the numerical stack.
        os.environ.setdefault("OMP_NUM_THREADS", str(max(1, min(threads, 16))))
        os.environ.setdefault("MKL_NUM_THREADS", str(max(1, min(threads, 16))))
        os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
        import torch
        from safetensors.torch import load_file
        from transformers import AutoConfig, AutoModel, AutoTokenizer
        print("Local runtime loaded; verifying model files", file=sys.stderr, flush=True)
        self.torch = torch
        torch.set_num_threads(max(1, min(threads, 16)))
        if file_hash(directory / "model.safetensors") != WEIGHT_SHA256:
            raise ValueError("Weight hash differs from the pinned public model")
        cfg = AutoConfig.from_pretrained(directory, local_files_only=True, trust_remote_code=False)
        if [cfg.id2label.get(i) for i in range(4)] != LABELS or cfg.model_type != "deberta-v2":
            raise ValueError("Unsupported class mapping or architecture")
        self.tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True, trust_remote_code=False, use_fast=True)
        if not self.tokenizer.is_fast:
            raise ValueError("A fast tokenizer with exact source offsets is required")
        if (self.tokenizer.num_special_tokens_to_add(pair=False) != 2
                or self.tokenizer.cls_token_id is None or self.tokenizer.sep_token_id is None):
            raise ValueError("Unexpected DeBERTa single-sequence special-token scheme")
        # Architecture reimplemented locally from the model card; never execute downloaded Python.
        class Network(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.model = AutoModel.from_config(cfg, trust_remote_code=False)
                self.classifier = torch.nn.Linear(cfg.hidden_size, 4)

            def forward(self, input_ids, attention_mask):
                h = self.model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
                mask = attention_mask.unsqueeze(-1).to(h.dtype)
                pooled = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
                return self.classifier(pooled)
        # Build shapes without allocating a second 1.7 GB copy of the weights.
        with torch.device("meta"):
            self.model = Network()
        self.model.load_state_dict(load_file(str(directory / "model.safetensors")), strict=True, assign=True)
        self.model.eval()
        print("Offline model ready", file=sys.stderr, flush=True)

    def tokenized(self, text):
        encoded = self.tokenizer(text, add_special_tokens=False, truncation=False, return_offsets_mapping=True)
        return encoded["input_ids"], encoded["offset_mapping"]

    def score_ids(self, ids):
        torch = self.torch
        # prepare_for_model was removed in Transformers 5. The pinned DeBERTa
        # single-sequence template is [CLS] tokens [SEP], verified above.
        input_ids = [self.tokenizer.cls_token_id] + list(ids) + [self.tokenizer.sep_token_id]
        if len(input_ids) > 768:
            raise ValueError("Window exceeds the published 768-token inference setting")
        inputs = {"input_ids": torch.tensor([input_ids], dtype=torch.long),
                  "attention_mask": torch.ones((1, len(input_ids)), dtype=torch.long)}
        with torch.inference_mode():
            probs = torch.softmax(self.model(**inputs), dim=-1)[0].tolist()
        if not all(math.isfinite(p) and 0 <= p <= 1 for p in probs):
            raise ValueError("Nonfinite local model output")
        return dict(zip(LABELS, probs))

    def analyze(self, text, language="en", explain=False, max_occlusions=40):
        language_check = validate_english_input(text, language)
        if type(max_occlusions) is not int or not 0 <= max_occlusions <= 200:
            raise ValueError("max-occlusions must be between 0 and 200")
        ids, offsets = self.tokenized(text)
        if not ids:
            raise ValueError("No model tokens")
        capacity = 768 - self.tokenizer.num_special_tokens_to_add(pair=False)
        chunks = windows(ids, offsets, size=capacity)
        scored = []
        for w in chunks:
            probs = self.score_ids(w["ids"])
            scored.append({k: v for k, v in w.items() if k != "ids"} | {
                "quote": text[w["start"]:w["end"]], "class_probabilities": probs,
                "ai_involvement_class_score": 1 - probs["human"]})
        document_probs = scored[0]["class_probabilities"] if len(scored) == 1 else None
        result = {"schema_version": 2, "mode": "offline_local_model", "model": REPO,
                  "measured_at_utc": utc_now(),
                  "language_check": language_check,
                  "revision": REVISION, "weight_sha256": WEIGHT_SHA256,
                  "language_scope": "English only; independently uncalibrated",
                  "text_sha256": text_hash(text), "token_count": len(ids), "windows": scored,
                  "all_input_tokens_scored": True, "document_class_probabilities": document_probs,
                  "authorship_verified": False, "independently_calibrated_here": False,
                  "validation_status": "experimental_auxiliary_score_not_a_validated_authorship_detector",
                  "known_limitations": "In the saved 36-document English pilot, high-score false positives occurred on human writing. Do not treat a near-1 score as established authorship.",
                  "external_detector_calls": 0,
                  "notes": ["Four-class model outputs are not proof of authorship or percentages of words.",
                            "AI involvement = ai + ai_edited + humanized; human is the mutually exclusive class.",
                            "Multi-window document aggregation has not been calibrated; document probability is unavailable.",
                            "The model card's threshold at 0.5% FPR is a vendor benchmark setting, not a local guarantee.",
                            "Short passages, translations and unfamiliar domains can be unreliable."]}
        result["occlusion"] = {"performed": False, "paragraphs": []}
        if explain and document_probs is not None:
            baseline = 1 - document_probs["human"]
            ps = paragraphs(text)
            findings = []
            for p in ps[:max_occlusions]:
                changed = text[:p["start"]] + text[p["end"]:]
                changed_ids, _ = self.tokenized(changed)
                record = {"paragraph_id": p["id"], "start": p["start"], "end": p["end"], "quote": p["text"]}
                if not changed.strip() or not changed_ids or len(changed_ids) > capacity:
                    findings.append(record | {"status": "not_measurable"})
                    continue
                after = 1 - self.score_ids(changed_ids)["human"]
                findings.append(record | {"status": "measured", "baseline_ai_involvement": baseline,
                                          "after_removal_ai_involvement": after,
                                          "delta_percentage_points": 100 * (baseline - after)})
            result["occlusion"] = {"performed": True, "paragraphs": findings, "total_paragraphs": len(ps),
                                   "unmeasured_due_to_limit": max(0, len(ps) - max_occlusions),
                                   "interpretation": "Sensitivity to deleting a paragraph. Positive delta means removal lowered the score; length/context changes confound this. This is not causal authorship evidence or a sentence probability."}
        elif explain:
            result["occlusion"]["reason"] = "No calibrated whole-document score for multi-window input"
        return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input"); p.add_argument("--model-dir", default=str(DEFAULT_MODEL))
    p.add_argument("--language", choices=["en", "ko", "mixed"], required=True)
    p.add_argument("--explain", action="store_true"); p.add_argument("--max-occlusions", type=int, default=40)
    p.add_argument("--out"); args = p.parse_args(argv)
    try:
        ensure_new_output(args.out, [args.input])
        if not 0 <= args.max_occlusions <= 200:
            raise ValueError("max-occlusions must be between 0 and 200")
        text, _ = read_text(args.input)
        # Avoid loading a large model for an unsupported language.
        validate_english_input(text, args.language)
        # The model process owns the lock, so it survives loss of a supervising parent.
        with runtime_lock():
            result = LocalDetector(args.model_dir).analyze(text, args.language, args.explain, args.max_occlusions)
            write_json(result, args.out)
        return 0
    except (ValueError, OSError, ImportError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc), "authorship_probabilities": None}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
