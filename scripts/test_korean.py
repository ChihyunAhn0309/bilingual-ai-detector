"""Release invariants for actual Korean model inference, evidence and holdout provenance."""
import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from detector import text_hash
import evidence
from evaluate import metrics
from korean_model import KoreanDetector, DEFAULT_MODEL, normalized_offsets, normalize_for_features, sigmoid

ROOT = Path(__file__).resolve().parents[1]


class KoreanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = KoreanDetector()
        cls.text = '\ufeff😀 지난달 우리 팀은 새 절차를 도입했습니다.\r\n\r\n재작업이 줄었다.  하지만 원인은 더 살펴봐야 한다.'

    def test_offline_real_model_probabilities_and_logit_reconstruction(self):
        with patch('socket.socket', side_effect=AssertionError('Network is forbidden')):
            result = self.model.analyze(self.text)
        probs = result['class_probabilities']
        self.assertAlmostEqual(sum(probs.values()), 1)
        self.assertTrue(all(0 < p < 1 for p in probs.values()))
        self.assertEqual(result['text_sha256'], text_hash(self.text))
        self.assertEqual(result['external_detector_calls'], 0)
        self.assertTrue(result['all_input_scored'])
        exp = result['feature_explanation']
        reconstructed = exp['intercept_contribution']+exp['all_feature_contributions_sum']
        self.assertAlmostEqual(sigmoid(reconstructed), probs['ai'], places=12)
        self.assertAlmostEqual(reconstructed, result['calibrated_logit'], places=12)

    def test_exact_model_explanations_survive_unicode_and_whitespace(self):
        result = self.model.analyze(self.text)
        for feature in result['feature_explanation']['lexical']:
            self.assertTrue(feature['occurrences'])
            for span in feature['occurrences']:
                self.assertEqual(self.text[span['start']:span['end']], span['quote'])
                self.assertEqual(normalize_for_features(span['quote']), feature['feature'])
        normalized, offsets = normalized_offsets(self.text)
        self.assertEqual(normalized, normalize_for_features(self.text))
        for character, (start,end) in zip(normalized,offsets):
            self.assertEqual(normalize_for_features(self.text[start:end]),character)

    def test_occlusion_delta_uses_full_model_and_discloses_limit(self):
        result = self.model.analyze(self.text,max_occlusions=1)
        sensitivity = result['paragraph_sensitivity']
        self.assertEqual(sensitivity['unmeasured_due_to_limit'],1)
        p = sensitivity['paragraphs'][0]
        after = self.model.predict(self.text[:p['start']]+self.text[p['end']:])
        self.assertAlmostEqual(p['delta_percentage_points'],100*(result['class_probabilities']['ai']-after),places=10)
        single = self.model.analyze('모든 사람이 같은 방식으로 생각하는 것은 아닙니다.')
        self.assertEqual(single['paragraph_sensitivity']['paragraphs'][0]['status'],'not_measurable')

    def test_wrong_language_empty_and_oversize_do_not_return_human_scores(self):
        for value in ['', 'This is an English text with no Korean letters.', '가'*200001]:
            with self.assertRaises(ValueError):
                self.model.analyze(value)
        with self.assertRaises(ValueError):
            self.model.analyze(self.text,max_occlusions=-1)
        with self.assertRaises(OSError):
            KoreanDetector(ROOT/'models'/'nonexistent-model.json')

    def test_genre_does_not_secretly_modify_probability(self):
        unknown = self.model.analyze(self.text,genre='unknown',explain=False)
        essay = self.model.analyze(self.text,genre='essay',explain=False)
        self.assertEqual(unknown['class_probabilities'],essay['class_probabilities'])
        self.assertGreater(len(unknown['applicability_cautions']),len(essay['applicability_cautions']))

    def test_modified_nonfinite_model_rejected(self):
        model = copy.deepcopy(self.model.m)
        model['coefficients'][0] = float('nan')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'invalid.json'; path.write_text(json.dumps(model),encoding='utf-8')
            with self.assertRaises(ValueError):
                KoreanDetector(path)

    def test_invalid_root_and_modified_bundled_weights_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'invalid.json'; path.write_text('[]',encoding='utf-8')
            with self.assertRaises(ValueError):
                KoreanDetector(path)
        with patch('korean_model.Path.read_bytes',return_value=DEFAULT_MODEL.read_bytes()+b' '):
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                KoreanDetector()

    def test_local_result_attachment_rejects_wrong_text_or_bad_probabilities(self):
        result = self.model.analyze(self.text,explain=False)
        ledger={'text_sha256':text_hash(self.text),'summary':'Measured test.','findings':[]}
        report=evidence.validate_ledger(self.text,ledger)
        attached=evidence.attach_model_result(self.text,report,result)
        self.assertEqual(attached['measured_output']['class_probabilities'],result['class_probabilities'])
        html=evidence.render_html(self.text,attached)
        self.assertIn(f"사람 {100*result['class_probabilities']['human']:.1f}%",html)
        self.assertIn('검증 범위를 벗어난 추정',html)
        for change in [{'text_sha256':text_hash(self.text+' ')},
                       {'class_probabilities':{'human':.2,'ai':.9}},
                       {'class_probabilities':{'human':float('nan'),'ai':.5}},
                       {'class_probabilities':{'human':.2,'ai':.3,'mixed':.5}}]:
            with self.assertRaises(ValueError):
                evidence.attach_model_result(self.text,report,result|change)

    def test_multwindow_english_cannot_become_document_probability(self):
        with self.assertRaises(ValueError):
            evidence.attach_model_result(self.text,{}, {'text_sha256':text_hash(self.text),
                'mode':'offline_local_model','document_class_probabilities':None})

    def test_release_model_hash_and_holdout_results_recompute(self):
        report=json.loads((ROOT/'references'/'korean-validation.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256(DEFAULT_MODEL.read_bytes()).hexdigest(),report['model_sha256'])
        predictions=[json.loads(line) for line in (ROOT/'references'/'korean-test-predictions.jsonl').read_text(encoding='utf-8').splitlines()]
        for split in ('test','transfer_test'):
            actual=metrics([r for r in predictions if r['split']==split],.5)
            expected=report['test_metrics'][split]['calibrated']['overall']
            for key in ['accuracy','false_positive_rate','brier','log_loss_clipped_1e_15','ece_10_equal_width_bins','auroc']:
                self.assertAlmostEqual(actual[key],expected[key],places=12)

    def test_split_groups_are_separate_and_original_test_is_never_fitted(self):
        manifest=[json.loads(line) for line in (ROOT/'references'/'korean-split-manifest.jsonl').read_text(encoding='utf-8').splitlines()]
        names=['train','selection','calibration','test']
        groups={name:{r['group_id'] for r in manifest if r['split']==name} for name in names}
        hashes={name:{r['text_sha256'] for r in manifest if r['split']==name} for name in names}
        for i,a in enumerate(names):
            for b in names[i+1:]:
                self.assertFalse(groups[a]&groups[b])
                self.assertFalse(hashes[a]&hashes[b])
        for r in manifest:
            if 'test_v2.csv' in r['doc_id']:
                self.assertIn(r['split'],('test','transfer_test'))


if __name__ == '__main__':
    unittest.main()
