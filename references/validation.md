# Execution, evaluation, and calibration

## Running the bundled tools

The profile, evidence, evaluation, and Korean inference tools use Python's standard library. Only the optional English classifier needs torch/transformers/safetensors and public weights. Resolve input/output paths relative to the skill directory. Use UTF-8 text and inspect PDF/DOCX extraction quality first.

```text
python scripts/detector.py inspect manuscript.txt --out work/profile.json
python scripts/evidence.py index manuscript.txt --out work/index.json
python scripts/evidence.py validate manuscript.txt work/ledger.json --out work/evidence.json --html work/review.html
python scripts/detector.py import-gptzero response.json --out work/imported.json
python -B -X utf8 scripts/run_english.py manuscript.txt --language en --explain --out work/local.json
python scripts/evaluate.py labeled-scores.jsonl --threshold 0.5 --data-kind real --out work/metrics.json
python -m unittest discover -s scripts -p "test_*.py" -v
```

Live commercial API calls are prohibited and blocked in code. Even `gptzero --allow-upload` fails without a network request. Public model and benchmark downloads are separate HTTP operations; manuscripts are not sent to external detectors. Existing output and input files are protected from overwriting.

A saved GPTZero response fails validation if any of its three classes are missing or its numbers are invalid. A legacy single score is not a substitute. Importing does not authenticate input binding. Correct evidence coordinates and report authenticity are separate checks.

## Labels and evaluation records

Define the target first. AI-only versus Human-only differs from AI involvement versus no involvement. Preserve distinct history labels for spelling correction of human drafts, translation, AI paraphrasing, and human editing of generated drafts. Document any binary mapping before evaluation. Do not assign ambiguous real cases to 0 or 1 for convenience.

Recommended fields: document ID, source hash, group ID linking source/author/topic/prompt, language, genre, length, generation/editing model and version, generation settings, transformation type/count, provenance evidence, detector version, raw scores/probabilities, and completion/error status. Use author-related attributes only when supplied for the evaluation purpose.

**These JSONL records illustrate synthetic test data, not measured performance.** Each line is one JSON object:

```json
{"doc_id":"demo-human-1","group_id":"source-1","language":"ko","genre":"essay","provenance":"synthetic test fixture","detector_version":"demo-v1","split":"test","label":0,"p_ai":0.2}
{"doc_id":"demo-ai-1","group_id":"source-2","language":"en","genre":"essay","provenance":"synthetic test fixture","detector_version":"demo-v1","split":"test","label":1,"p_ai":0.8}
```

The evaluator accepts `p_ai` for a defined binary target. Do not substitute Turnitin's flagged fraction or raw perplexity. Use GPTZero's three-class results only under a predefined mapping appropriate to the target. Count failed checks separately and report missing coverage; do not present performance on successful cases alone as overall performance.

## Splits and scope

1. Separate training, model/feature selection, calibration, and final testing. Paragraphs, translations, or humanized versions of one source crossing splits cause leakage. Group connected authors, sources, topics, and prompts. The tool rejects calibration/test overlap in supplied group IDs but does not discover hidden duplication or pretraining leakage automatically.
2. Evaluate English and Korean separately, then by genre, length, generator, generation date, and transformation. Include difficult negative samples: mixed-language text, short messages, abstracts, official prose, non-native English, OCR, and human writing edited by people.
3. Reserve unseen generators, humanizers, and domains for testing. Do not evaluate only passages selected by the same detector. Distinguish existing public data from newly collected private holdouts.
4. Preserve input hashes, versions, and timestamps for supplied API results. A model update can invalidate earlier calibration.

## Metrics

- `false_positive_rate`: fraction of human-labeled samples flagged as AI. `recall`: fraction of AI-labeled samples detected. `precision`: fraction of AI verdicts that are truly AI-labeled; it depends on the dataset's AI prevalence.
- AUROC measures ranking. Calibrated 90% outputs and low FPR at a chosen threshold are separate properties. Ties contribute 0.5; AUROC is unavailable for a single-class group.
- Examine Brier score, log loss, reliability bins, and ECE together. ECE depends on binning and sample size. The script uses 10 equal-width bins and a 1e-15 numerical floor for log loss.
- Zero observed false positives does not prove a 0% population FPR. The script provides 95% Wilson intervals for FPR and recall. Dependent documents violate their independence assumption; use approaches such as group bootstrap where appropriate.
- Low-FPR applications also need TPR at FPR 1% or 0.1%. Select a threshold on calibration data, freeze it, and report the achieved test FPR/TPR and uncertainty intervals. Rare-error validation needs enough human samples. This script does not select thresholds or optimize TPR at a target FPR.
- If abstention is used, report coverage and errors including abstained cases. Accuracy at low coverage is not performance on all documents.

## Calibration and combination

Post-hoc calibration requires separate samples and explicit label definitions. Choose Platt, temperature, isotonic, or another suitable method for the target/model, then test on untouched data. Version 3 includes the Korean sigmoid fitted by `train_korean.py`; see the [Korean model card](korean-model.md) and run JSON for sources, splits, and measurements. The English checkpoint remains independently uncalibrated.

Combining detectors requires matched inputs, a common target, score directions/versions, missing-result handling, and training/calibration accounting for correlated errors. Averaging vendor percentages or flagged fractions is not a substitute. Do not invent language-specific weights without data.

## Release and follow-up criteria

The [performance comparison](performance-comparison.md) and [verification record](verification.md) distinguish scope from actual execution. Do not generalize a small English pilot or historical public results to universal Korean/English accuracy. Published accuracy claims need a real holdout, label provenance, split manifest, run records, language/genre metrics, failure cases, and model versions in a shareable form. Use abstention or an out-of-scope label when appropriate.

Passing unit tests supports software invariants. Scores computed from synthetic responses or labels are not detector-accuracy evidence. Source checks, tests, and corrections are recorded in the [verification history](verification.md).
