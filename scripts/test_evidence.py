import copy
import unittest

import detector
import evidence
from local_model import windows
from local_model import validate_english_input


def ledger(text):
    quote = "같은 표현"
    start = text.index(quote)
    return {"text_sha256": detector.text_hash(text), "summary": "Illustrative analysis, not a detector verdict.",
            "findings": [{"id": "E1", "basis": "style_observation", "direction": "ai_like", "strength": "weak",
                          "spans": [{"start": start, "end": start+len(quote), "quote": quote}],
                          "observation": "A phrase repeats.", "interpretation": "Could be templated writing.",
                          "human_alternative": "Could be intentional parallelism.",
                          "discriminating_evidence": "Comparable writing samples."}],
            "paragraph_reviews": [{"paragraph_id": "P1", "status": "reviewed", "assessment": "Weak observation only.", "finding_ids": ["E1"]}]}


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.text = "\ufeff😀 같은 표현.\r\n\r\n같은 표현. <script>alert(1)</script>"

    def test_paragraphs_preserve_bom_emoji_and_crlf(self):
        ps = evidence.paragraphs(self.text)
        self.assertEqual(len(ps), 2)
        self.assertEqual(ps[1]["line"], 3)
        for p in ps:
            self.assertEqual(p["text"], self.text[p["start"]:p["end"]])

    def test_ambiguous_repeated_quote_is_not_guessed(self):
        self.assertEqual(evidence.unique_match(self.text, "같은 표현")["mapping"], "ambiguous_repeated_quote")
        self.assertEqual(evidence.unique_match(self.text, "없는 표현")["mapping"], "not_found")

    def test_mismatch_or_unsupported_offsets_rejected(self):
        for span in [(0, 2, "다름"), (True, 2, "😀"), (-1, 2, "x"), (0, 1000, self.text)]:
            with self.assertRaises(ValueError):
                evidence.anchor(self.text, *span)

    def test_hash_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            evidence.validate_ledger(self.text+"!", ledger(self.text))

    def test_missing_review_exposed_not_assumed_complete(self):
        result = evidence.validate_ledger(self.text, ledger(self.text))
        self.assertEqual(result["coverage"]["review_fraction"], .5)
        self.assertEqual(result["paragraph_reviews"][1]["status"], "not_reviewed")
        self.assertIsNone(result["authorship_probabilities"])

    def test_missing_human_alternative_and_source_rejected(self):
        for change in [{"human_alternative": ""}, {"basis": "local_occlusion"}]:
            data = ledger(self.text)
            data["findings"][0].update(change)
            with self.assertRaises(ValueError):
                evidence.validate_ledger(self.text, data)

    def test_paragraph_link_must_overlap(self):
        data = ledger(self.text)
        data["paragraph_reviews"][0]["paragraph_id"] = "P2"
        with self.assertRaises(ValueError):
            evidence.validate_ledger(self.text, data)

    def test_ledger_cannot_override_original_coordinates(self):
        data = ledger(self.text)
        data["paragraph_reviews"][0].update({"start": 999, "text": "fabricated", "id": "fake"})
        result = evidence.validate_ledger(self.text, data)
        self.assertEqual(result["paragraph_reviews"][0]["start"], 0)
        self.assertEqual(result["paragraph_reviews"][0]["id"], "P1")
        self.assertNotEqual(result["paragraph_reviews"][0]["text"], "fabricated")

    def test_html_escapes_original_and_explanation(self):
        data = ledger(self.text); data["summary"] = '<img src=x onerror="alert(1)">'
        result = evidence.validate_ledger(self.text, data)
        html = evidence.render_html(self.text, result)
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img ", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("미검토", html)

    def test_provider_score_is_not_authorship_explanation(self):
        result = evidence.provider_highlights(self.text, {"documents": [{"sentences": [
            {"sentence": "같은 표현", "generated_prob": .9}, {"sentence": "없는 표현", "generated_prob": .7}]}]})
        self.assertEqual(result["input_binding"], "unverified_import")
        self.assertEqual(result["sentences"][0]["mapping"], "ambiguous_repeated_quote")
        self.assertEqual(result["sentences"][1]["mapping"], "not_found")

    def test_windows_cover_every_token_without_truncation(self):
        for n in (1, 766, 767, 1600):
            ids = list(range(n)); offsets = [(i*2, i*2+1) for i in ids]
            chunks = windows(ids, offsets)
            self.assertEqual(set(t for c in chunks for t in c["ids"]), set(ids))
            self.assertTrue(all(len(c["ids"]) <= 766 for c in chunks))
            self.assertEqual(chunks[-1]["end"], offsets[-1][1])

    def test_english_report_preserves_uncalibrated_warning_and_metadata(self):
        text = "The report has two observations."
        report = evidence.validate_ledger(text, {"text_sha256":detector.text_hash(text), "summary":"Neutral review."})
        result = {"text_sha256":detector.text_hash(text),"mode":"offline_local_model","model":"test-model",
                  "document_class_probabilities":{"human":.1,"ai":.8,"ai_edited":.05,"humanized":.05},
                  "known_limitations":"High-score false positives occurred.","validation_status":"experimental",
                  "independently_calibrated_here":False,"language_scope":"English only", "revision":"revision-1",
                  "measured_at_utc":"2026-10-03T00:00:00+00:00"}
        attached = evidence.attach_model_result(text,report,result)
        for key in ("known_limitations","validation_status","independently_calibrated_here","language_scope","revision","measured_at_utc"):
            self.assertEqual(attached['measured_output'][key],result[key])
        html = evidence.render_html(text,attached)
        self.assertIn('보정되지 않은',html)
        self.assertIn('12개 중 3개',html)
        self.assertNotIn('별도 데이터로 보정한',html)

    def test_english_script_screen_rejects_obviously_unsupported_inputs(self):
        for text in ('這是一段中文測試文字。這段文章不應該被當成英文進行判斷。', 'Пример русского текста.', '12345 !!!', ' \n'):
            with self.assertRaises(ValueError):
                validate_english_input(text)
        checked = validate_english_input('The reviewer met Zoë at the café.')
        self.assertEqual(checked['declared_language'],'en')
        self.assertIn('not automatically distinguished',checked['method'])


if __name__ == "__main__":
    unittest.main()
