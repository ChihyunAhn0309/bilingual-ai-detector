"""Contract and numerical tests with synthetic inputs; these do not test detection accuracy."""
import contextlib
import copy
import io
import json
import random
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import detector
import evaluate


def response(ai=0.6, human=0.1, mixed=0.3):
    return {"documents": [{"class_probabilities": {"ai": ai, "human": human, "mixed": mixed},
                            "document_classification": "AI_ONLY"}]}


def row(i, label, p, language="en", split="test"):
    return {"doc_id": str(i), "group_id": "group-" + str(i), "language": language,
            "genre": "essay", "provenance": "synthetic unit test", "detector_version": "test-v1",
            "split": split, "label": label, "p_ai": p}


class ProfileTests(unittest.TestCase):
    def test_empty_has_no_probabilities(self):
        p = detector.inspect_text("")
        self.assertIsNone(p["authorship_probabilities"])
        self.assertIsNone(p["surface_type_token_ratio"])
        self.assertEqual(p["characters_codepoints"], 0)

    def test_korean_and_english_counts(self):
        p = detector.inspect_text("가나다 abc, abc.")
        self.assertEqual(p["hangul_letters"], 3)
        self.assertEqual(p["latin_letters"], 6)
        self.assertEqual(p["comma_count"], 1)
        self.assertEqual(p["whitespace_units"], 3)

    def test_unicode_offsets_and_crlf(self):
        p = detector.inspect_text("가\r\n나\u200b")
        self.assertEqual(p["rough_sentence_count"], 2)
        self.assertEqual(p["unicode_observations"][0]["offset_codepoints"], 4)
        self.assertEqual(p["unicode_observations"][0]["line"], 2)
        self.assertIsNone(p["authorship_probabilities"])

    def test_nfd_hangul_not_misidentified_as_latin(self):
        p = detector.inspect_text("\u1100\u1161")
        self.assertEqual(p["hangul_letters"], 2)

    def test_leading_bom_preserved_in_offsets_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bom.txt"
            original = "\ufeff가\u200b나."
            path.write_bytes(original.encode("utf-8"))
            text, file_hash = detector.read_text(path)
            profile = detector.inspect_text(text, file_hash)
            self.assertEqual(text, original)
            self.assertEqual(profile["characters_codepoints"], 5)
            self.assertEqual(profile["unicode_observations"][1]["offset_codepoints"], 2)
            self.assertEqual(profile["text_sha256"], file_hash)

    def test_file_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = Path(tmp) / "text.txt"
            out = Path(tmp) / "profile.json"
            original = b"\xef\xbb\xbf" + "오늘, 회의합니다.\r\nTomorrow.".encode("utf-8")
            inp.write_bytes(original)
            self.assertEqual(detector.main(["inspect", str(inp), "--out", str(out)]), 0)
            self.assertEqual(inp.read_bytes(), original)
            self.assertIsNone(json.loads(out.read_text(encoding="utf-8"))["authorship_probabilities"])


class ProviderTests(unittest.TestCase):
    def test_mixed_is_preserved(self):
        normalized = detector.normalize_gptzero(response())
        self.assertEqual(normalized["percentages"], {"ai": 60, "human": 10, "mixed": 30})
        self.assertFalse(normalized["independently_calibrated_here"])

    def test_rejects_legacy_score(self):
        with self.assertRaises(ValueError):
            detector.normalize_gptzero({"documents": [{"completely_generated_prob": 0.8}]})

    def test_rejects_bad_numbers(self):
        for value in [float("nan"), float("inf"), -0.1, 1.1, True, "0.6"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                detector.normalize_gptzero(response(ai=value))

    def test_rejects_bad_sum_or_extra_class(self):
        for raw in [response(0.7, 0.2, 0.3), response()]:
            if raw["documents"][0]["class_probabilities"]["ai"] == 0.6:
                raw["documents"][0]["class_probabilities"]["unknown"] = 0
            with self.assertRaises(ValueError):
                detector.normalize_gptzero(raw)

    def test_rejects_pending_and_error(self):
        for status in ["processing", "failed", "unknown"]:
            raw = response()
            raw["status"] = status
            with self.assertRaises(ValueError):
                detector.normalize_gptzero(raw)
        raw = response()
        raw["success"] = False
        with self.assertRaises(ValueError):
            detector.normalize_gptzero(raw)

    def test_no_request_without_key_or_valid_length(self):
        def never(*args, **kwargs):
            self.fail("Network opener must not be called")
        for text, key in [("text", None), ("", "fake"), ("x" * 50001, "fake")]:
            with self.assertRaises(ValueError):
                detector.request_gptzero(text, key, opener=never)

    def test_live_request_disabled_even_with_key_and_flag(self):
        with self.assertRaisesRegex(ValueError, "zero-additional-fee"):
            detector.request_gptzero("한글 English", "synthetic-key", opener=lambda *a: self.fail("Network call"))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(detector.main(["gptzero", "not-needed.txt", "--allow-upload"]), 2)

    def test_output_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file.txt"
            path.write_text("preserve", encoding="utf-8")
            with self.assertRaises(ValueError):
                detector.ensure_new_output(path)
            self.assertEqual(path.read_text(), "preserve")


class MetricTests(unittest.TestCase):
    def test_known_metrics(self):
        m = evaluate.metrics([row(1, 0, 0.1), row(2, 0, 0.7), row(3, 1, 0.8), row(4, 1, 0.9)], 0.5)
        self.assertEqual(m["false_positive_rate"], 0.5)
        self.assertEqual(m["recall"], 1)
        self.assertEqual(m["accuracy"], 0.75)
        self.assertEqual(m["auroc"], 1)
        self.assertAlmostEqual(m["brier"], 0.1375)

    def test_auroc_agrees_with_pairwise_definition_including_ties(self):
        rng = random.Random(42)
        for _ in range(30):
            rows = [row(i, i % 2, rng.choice([0.1, 0.3, 0.5, 0.9])) for i in range(20)]
            pos = [r["p_ai"] for r in rows if r["label"] == 1]
            neg = [r["p_ai"] for r in rows if r["label"] == 0]
            expected = sum(1 if p > n else 0.5 if p == n else 0 for p in pos for n in neg) / (len(pos) * len(neg))
            self.assertAlmostEqual(evaluate.auroc(rows), expected)

    def test_no_false_positive_does_not_mean_certain_zero(self):
        low, high = evaluate.wilson(0, 100)
        self.assertAlmostEqual(low, 0)
        self.assertGreater(high, 0.03)

    def test_single_class_auc_unavailable(self):
        self.assertIsNone(evaluate.auroc([row(1, 0, 0.4)]))

    def test_language_slices_and_no_calibration_claim(self):
        report = evaluate.evaluate([row(1, 0, 0.1, "ko"), row(2, 1, 0.9, "en")], data_kind="synthetic")
        self.assertEqual(set(report["by_language"]), {"ko", "en"})
        self.assertFalse(report["calibration_performed"])

    def test_group_leakage_refused(self):
        a, b = row(1, 0, 0.1), row(2, 1, 0.9, split="calibration")
        b["group_id"] = a["group_id"]
        with self.assertRaises(ValueError):
            evaluate.evaluate([a, b])

    def test_duplicate_ids_mixed_labels_and_nonfinite_values_refused(self):
        a = row(1, 0, 0.1)
        for changes in [{"doc_id": "1"}, {"label": "mixed"}, {"p_ai": float("nan")},
                        {"detector_version": "other-v2"}, {"label": True}]:
            b = row(2, 1, 0.9)
            b.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                evaluate.evaluate([copy.deepcopy(a), b])


if __name__ == "__main__":
    unittest.main()
