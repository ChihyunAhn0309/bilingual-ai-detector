import contextlib
import copy
import io
import json
from pathlib import Path
from subprocess import CompletedProcess
import tempfile
import unittest
from unittest.mock import patch

from detector import text_hash
import run_english
from runtime_guard import runtime_lock


class EnglishRunnerTests(unittest.TestCase):
    def valid_result(self):
        original = 'A short English example for testing.'
        probabilities = {'human': .1, 'ai': .6, 'ai_edited': .2, 'humanized': .1}
        return {'schema_version': 2, 'mode': 'offline_local_model', 'model': run_english.REPO,
                'revision': run_english.REVISION, 'weight_sha256': run_english.WEIGHT_SHA256,
                'text_sha256': text_hash(original), 'measured_at_utc': '2026-10-03T00:00:00+00:00',
                'authorship_verified': False, 'independently_calibrated_here': False,
                'validation_status': 'experimental_auxiliary_score_not_a_validated_authorship_detector',
                'known_limitations': 'Experimental and uncalibrated.', 'external_detector_calls': 0,
                'all_input_tokens_scored': True, 'token_count': 7,
                'windows': [{'token_start': 0, 'token_end': 7, 'start': 0, 'end': len(original),
                             'quote': original, 'class_probabilities': probabilities,
                             'ai_involvement_class_score': .9}],
                'document_class_probabilities': probabilities,
                'occlusion': {'performed': False, 'paragraphs': []}}

    def invoke(self, worker, expected, preexisting=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manuscript = root / 'input.txt'
            manuscript.write_text('A short English example for testing.', encoding='utf-8')
            output = root / 'result.json'
            if preexisting:
                output.write_text('unchanged', encoding='utf-8')
            stderr = io.StringIO()
            with patch('run_english.subprocess.run', side_effect=worker) as process, \
                    contextlib.redirect_stderr(stderr):
                status = run_english.main([str(manuscript), '--language', 'en', '--out', str(output)])
            self.assertEqual(status, expected)
            if expected == 0:
                result = json.loads(output.read_text(encoding='utf-8'))
                self.assertEqual(result['execution_guard']['worker_exit_code'], 0)
                self.assertFalse(result['execution_guard']['native_runtime_stability_guaranteed'])
            else:
                self.assertIsNone(json.loads(stderr.getvalue())['authorship_probabilities'])
                if preexisting:
                    self.assertEqual(output.read_text(), 'unchanged')
                    process.assert_not_called()
                else:
                    self.assertFalse(output.exists())
            self.assertEqual(manuscript.read_text(), 'A short English example for testing.')

    def test_native_failure_has_no_score_or_final_output(self):
        self.invoke(lambda command, **kwargs: CompletedProcess(command, 3221225477, '', 'native failure'), 2)

    def test_success_without_output_is_failure(self):
        self.invoke(lambda command, **kwargs: CompletedProcess(command, 0, '', ''), 2)

    def test_wrong_input_result_is_failure(self):
        def worker(command, **kwargs):
            Path(command[command.index('--out') + 1]).write_text(json.dumps({'mode': 'offline_local_model', 'text_sha256': 'wrong'}))
            return CompletedProcess(command, 0, '', '')
        self.invoke(worker, 2)

    def test_valid_worker_result_is_published(self):
        def worker(command, **kwargs):
            result = self.valid_result()
            Path(command[command.index('--out') + 1]).write_text(json.dumps(result))
            return CompletedProcess(command, 0, '', '')
        self.invoke(worker, 0)

    def test_existing_result_is_preserved(self):
        self.invoke(lambda *args, **kwargs: self.fail('Must not run'), 2, preexisting=True)

    def test_concurrent_lock_rejects_and_then_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'worker.lock'
            with runtime_lock(path):
                with self.assertRaisesRegex(ValueError, 'Another English'):
                    with runtime_lock(path):
                        self.fail('Lock must reject concurrent worker')
            with runtime_lock(path):
                pass

    def test_incomplete_or_corrupt_worker_results_are_rejected(self):
        records = []
        for key in ('measured_at_utc', 'known_limitations', 'document_class_probabilities', 'occlusion'):
            item = self.valid_result()
            del item[key]
            records.append(item)
        for score in (float('nan'), float('inf'), -1, True, .95):
            item = self.valid_result()
            item['windows'][0]['class_probabilities']['human'] = score
            records.append(item)
        for key, value in (('token_start', 1), ('token_end', 8), ('quote', 'wrong'), ('ai_involvement_class_score', .2)):
            item = self.valid_result()
            item['windows'][0][key] = value
            records.append(item)
        for item in records:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    run_english.validate_worker_result(item, 'A short English example for testing.')

    def test_mult_window_document_probability_must_be_null(self):
        item = self.valid_result()
        item['windows'].append(copy.deepcopy(item['windows'][0]))
        item['windows'][1].update(token_start=5, token_end=10)
        item['token_count'] = 10
        with self.assertRaises(ValueError):
            run_english.validate_worker_result(item, 'A short English example for testing.')
        item['document_class_probabilities'] = None
        run_english.validate_worker_result(item, 'A short English example for testing.')


if __name__ == '__main__':
    unittest.main()
