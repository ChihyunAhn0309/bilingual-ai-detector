"""Supervised offline English CLI: serialize workers and never turn a crash into a score."""
import argparse
from datetime import datetime, timedelta
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

from detector import ensure_new_output, read_text, text_hash, write_json, valid_probability
from local_model import DEFAULT_MODEL, LABELS, validate_english_input
from prepare_local_model import REPO, REVISION, WEIGHT_SHA256


def validate_worker_result(result, original):
    """Check the pinned worker's output contract; this is not an authenticity signature."""
    expected = {'schema_version': 2, 'mode': 'offline_local_model', 'model': REPO,
                'revision': REVISION, 'weight_sha256': WEIGHT_SHA256,
                'text_sha256': text_hash(original),
                'validation_status': 'experimental_auxiliary_score_not_a_validated_authorship_detector'}
    if not isinstance(result, dict) or any(type(result.get(k)) is not type(v) or result[k] != v for k, v in expected.items()):
        raise ValueError('English worker result has missing or inconsistent model/input metadata.')
    if (result.get('authorship_verified') is not False or result.get('independently_calibrated_here') is not False
            or result.get('all_input_tokens_scored') is not True or type(result.get('external_detector_calls')) is not int
            or result['external_detector_calls'] != 0 or not isinstance(result.get('known_limitations'), str)
            or not result['known_limitations']):
        raise ValueError('English worker result is missing required scope and limitation metadata.')
    timestamp = result.get('measured_at_utc')
    if not isinstance(timestamp, str) or datetime.fromisoformat(timestamp).utcoffset() != timedelta(0):
        raise ValueError('English worker result requires a UTC measurement timestamp.')

    def probabilities(value):
        if (not isinstance(value, dict) or set(value) != set(LABELS)
                or not all(valid_probability(p) for p in value.values())
                or not math.isclose(sum(value.values()), 1, rel_tol=0, abs_tol=1e-5)):
            raise ValueError('English worker result has invalid class probabilities.')

    def span(value):
        a, b = value.get('start'), value.get('end')
        if (type(a) is not int or type(b) is not int or not 0 <= a < b <= len(original)
                or value.get('quote') != original[a:b]):
            raise ValueError('English worker result has invalid original-text coordinates.')

    total = result.get('token_count')
    windows = result.get('windows')
    if type(total) is not int or total <= 0 or not isinstance(windows, list) or not windows:
        raise ValueError('English worker result lacks token coverage.')
    covered = 0
    previous_start = -1
    for window in windows:
        if not isinstance(window, dict):
            raise ValueError('English worker result has an invalid window.')
        a, b = window.get('token_start'), window.get('token_end')
        if (type(a) is not int or type(b) is not int or not previous_start < a <= covered
                or not covered < b <= total or b - a > 766):
            raise ValueError('English worker result has incomplete or invalid token coverage.')
        span(window)
        probabilities(window.get('class_probabilities'))
        score = window.get('ai_involvement_class_score')
        if not valid_probability(score) or not math.isclose(score, 1-window['class_probabilities']['human'], rel_tol=0, abs_tol=1e-7):
            raise ValueError('English worker result has an inconsistent AI involvement score.')
        covered, previous_start = b, a
    if covered != total:
        raise ValueError('English worker result did not cover every token.')
    document = result.get('document_class_probabilities')
    if len(windows) == 1:
        probabilities(document)
        if document != windows[0]['class_probabilities']:
            raise ValueError('English document and single-window probabilities differ.')
    elif 'document_class_probabilities' not in result or document is not None:
        raise ValueError('Multi-window English input must not have a document probability.')
    occlusion = result.get('occlusion')
    if (not isinstance(occlusion, dict) or type(occlusion.get('performed')) is not bool
            or not isinstance(occlusion.get('paragraphs'), list)):
        raise ValueError('English worker result has invalid explanation metadata.')
    if (occlusion['performed'] and document is None) or (not occlusion['performed'] and occlusion['paragraphs']):
        raise ValueError('English worker result has inconsistent explanation coverage.')
    for record in occlusion['paragraphs']:
        if not isinstance(record, dict) or record.get('status') not in ('measured', 'not_measurable'):
            raise ValueError('English worker result has an invalid paragraph measurement.')
        span(record)
        if record['status'] == 'measured':
            before, after, delta = (record.get(k) for k in ('baseline_ai_involvement', 'after_removal_ai_involvement', 'delta_percentage_points'))
            if (document is None or not valid_probability(before) or not valid_probability(after)
                    or type(delta) not in (float, int) or not math.isfinite(delta)
                    or not math.isclose(before, 1-document['human'], rel_tol=0, abs_tol=1e-7)
                    or not math.isclose(delta, 100*(before-after), rel_tol=0, abs_tol=1e-7)):
                raise ValueError('English worker result has an invalid paragraph score change.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--model-dir', default=str(DEFAULT_MODEL))
    parser.add_argument('--language', choices=['en', 'ko', 'mixed'], required=True)
    parser.add_argument('--explain', action='store_true')
    parser.add_argument('--max-occlusions', type=int, default=40)
    parser.add_argument('--out')
    args = parser.parse_args(argv)
    worker_exit_code = None
    try:
        ensure_new_output(args.out, [args.input])
        if not 0 <= args.max_occlusions <= 200:
            raise ValueError('max-occlusions must be between 0 and 200')
        original, _ = read_text(args.input)
        validate_english_input(original, args.language)
        with tempfile.TemporaryDirectory(prefix='bilingual-ai-worker-') as temporary:
            result_path = Path(temporary) / 'result.json'
            command = [sys.executable, '-B', '-X', 'utf8', '-X', 'faulthandler', str(Path(__file__).with_name('local_model.py')),
                       str(Path(args.input).resolve()), '--language', args.language,
                       '--model-dir', str(Path(args.model_dir).resolve()),
                       '--max-occlusions', str(args.max_occlusions), '--out', str(result_path)]
            if args.explain:
                command.append('--explain')
            worker = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
            worker_exit_code = worker.returncode
            if worker.returncode:
                detail = worker.stderr[-4000:].strip()
                raise ValueError(f'English worker failed (exit {worker.returncode}); no authorship score is available. {detail}')
            if not result_path.is_file():
                raise ValueError('English worker returned no result; no authorship score is available.')
            result = json.loads(result_path.read_text(encoding='utf-8'))
            validate_worker_result(result, original)
            result['execution_guard'] = {'worker_exit_code': 0, 'serialized_cli': True,
                                         'native_runtime_stability_guaranteed': False}
            write_json(result, args.out)
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({'error': str(exc), 'authorship_probabilities': None,
                          'worker_exit_code': worker_exit_code}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
