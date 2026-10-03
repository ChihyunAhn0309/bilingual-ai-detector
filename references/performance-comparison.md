# Performance comparison with GPTZero and other detectors

Reviewed on 2026-10-03. Separate feature completeness from classification accuracy: detailed explanations do not establish higher accuracy. This skill does not reproduce GPTZero's model.

## Public results recomputed without commercial API calls

The comparison uses [Epoch AI's July 2026 evaluation](https://epoch.ai/data-insights/ai-detectors-false-negatives) and its [pinned results repository](https://github.com/jaeholee-brown/ai-text-detectors/tree/3f5ed200e212ef5ca957b6f5675d99ed29ff3c3c). It contains English texts associated with 99 authors: 495 human passages, 297 AI passages from basic prompts, and 297 AI passages imitating an author's style, across blogs, science writing, and fiction. We reaggregated 1,089 saved verdicts without submitting user text or calling commercial detectors again.

| Detector and recorded version | Human false positives | Basic-AI false negatives | Style-imitation-AI false negatives |
| --- | ---: | ---: | ---: |
| GPTZero 2026-05-11-base | 0/495 (0%) | 2/297 (0.67%) | 32/297 (10.77%) |
| Pangram 3.3.2 | 0/495 (0%) | 0/297 (0%) | 30/297 (10.10%) |
| Originality Turbo 3.0.2 | 19/495 (3.84%) | 1/297 (0.34%) | 53/297 (17.85%) |

The original evaluation uses a strict AI-only target: only AI-only verdicts count as detection for fully generated samples, and Mixed counts as a miss. Mixed on human samples counts as a false positive. These results do not characterize current versions, Korean, or every humanizer. Zero observed errors among 495 human samples does not guarantee zero population FPR. Author dependence and possible training overlap require separate consideration.

The study's perplexity/burstiness description of GPTZero differs from its [official explanation](https://support.gptzero.me/articles/9585228410-how-do-i-interpret-burstiness-or-perplexity). We reuse the recorded measurements and versions, not that outdated account of the method.

```text
python scripts/benchmark_epoch.py --cache work/epoch-public --out work/public-comparison.json
```

## Comparing this skill with a commercial service

| Dimension | This skill | GPTZero and other commercial services |
| --- | --- | --- |
| Additional detector-service fees | Local analysis, public downloads, and supplied reports only | Depend on the service/account; this skill does not call them |
| Detailed Korean explanation | Full-source review, exact locations, rationales, and alternatives | Features and explanation-language coverage vary by product |
| English probabilities | Optional free four-class local checkpoint with explicit calibration/scope limits | Native service outputs |
| Korean probabilities | Bundled character classifier with separately fitted sigmoid; genre/distribution limits retained | Supplied reports from supporting products can be interpreted |
| Explanation validation | Automated source-hash, quotation, coordinate, and coverage checks | Product-specific implementation |
| Measured model sensitivity | Local paragraph-removal rescoring with conditions and limitations | Depends on the exposed feature and model version |
| General accuracy advantage | Not established | Requires matched data, languages, versions, and targets |

If the analyst's stylistic interpretation disagrees with the classifier, report both. Do not alter the model score based on the number of stylistic clues or call a lower score after rewriting an accuracy improvement.

## Reproducible local pilot

```text
python scripts/benchmark_epoch.py --cache work/epoch-public --model-dir models/tropa-mini --authors-per-genre 4 --out work/local-pilot.json
```

Seed 20261003 selects four authors per genre, 12 in total, before classification. For each author, it selects one human original and a basic/imitation pair from the same generator: 36 samples total. Overlap with detector training data is unknown, so this is not claimed as an independent holdout.

This pilot targets **AI involvement**, counting GPTZero/Pangram Mixed as AI. Do not combine it directly with the strict AI-only table above. The local evaluation score is the mean AI-involvement score across overlapping windows covering all input. That is an evaluation statistic, not a calibrated document probability. Both predefined thresholds, 0.5 and the model card's 0.9755912190656111, are reported rather than selecting the better result afterward. Record failures, coverage, and the matched-document intersection.

If a pilot was not completed, report no result rather than a projected number. A small sample's ranking cannot establish Korean performance, the latest GPTZero's performance, or a universal ranking.

## Observed 36-document English pilot

All 36 samples completed, with zero execution failures. The table uses the same documents and AI-involvement target. The local model was actually run; commercial entries come from archived upstream verdicts. Every sample fit one window, so window averaging had no effect in this pilot.

| Model and predefined threshold | Correct | Sample accuracy | Human false positives | Basic-AI misses | Imitation-AI misses |
| --- | ---: | ---: | ---: | ---: | ---: |
| Free local model, 0.5 | 30/36 | 83.33% | 3/12 | 0/12 | 3/12 |
| Free local model, model-card threshold | 28/36 | 77.78% | 2/12 | 0/12 | 6/12 |
| GPTZero 2026-05-11-base | 35/36 | 97.22% | 0/12 | 0/12 | 1/12 |
| Pangram 3.3.2 | 36/36 | 100% | 0/12 | 0/12 | 0/12 |
| Originality Turbo 3.0.2 | 34/36 | 94.44% | 0/12 | 0/12 | 2/12 |

[Metrics, sample identities, and hashes](benchmark-results.json) support reproduction. There are only 12 samples per condition, linked by author, so the table is insufficient for population-accuracy estimates or a definitive ranking. The local model produced high-confidence false positives on human writing and is therefore limited to experimental auxiliary use. It detected basic AI samples better than style-imitation samples. Raising the threshold removed one human false positive but added three imitation-AI misses; this was not described as an improvement.

**The pilot did not show an advantage over GPTZero.** Better explanation, coordinates, and source review are separate from better classification accuracy. Arbitrary stylistic weights must not be added to reverse the measured result. The separate Korean evaluation below is not comparable to this English pilot.

## Improvements and validation boundaries

Verified v2 improvements included blocking additional detector charges, complete paragraph review, exact evidence anchoring, rejection of invented quotations, separate language scopes, explicit unreviewed passages, and separation of measured sensitivity from analyst interpretation. Code and actual artifacts support those claims. Accuracy improvement requires a separate matched-sample measurement.

Further Korean or humanizer-related training requires usable provenance-labeled data, author/topic/source-group separation, untouched test data, and genre/language-specific false-positive, false-negative, and calibration evaluation. Arbitrary ensembles, weights, or confidence numbers without new evidence are not validated improvements.

## Trained Korean model introduced in v3

The [Korean model card](korean-model.md) reports 97.51% accuracy and 0.90% human FPR on a 1,846-document topic-disjoint holdout. It contains 1,714 essays; accuracy on 37 abstracts and 95 poems is 91.89% and 87.37%. Calibration used a separate 1,907 documents. ECE changed from 0.03648 to 0.01704, while accuracy changed from 97.72% to 97.51%. This does not establish perfect probabilities or increased accuracy.

No matched Korean GPTZero execution or archived verdicts were obtained, so **relative Korean performance against GPTZero is unmeasured**. The historical English GPTZero 97.22% and Korean 97.51% belong to different evaluations and cannot establish a ranking. Commercial API calls: zero. General prose and current humanizers require new evaluation.
