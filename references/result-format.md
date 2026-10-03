# Results and percentage semantics

## Numeric contract

| Available evidence | Permitted numbers | Invalid conversion |
| --- | --- | --- |
| Stylistic observations only | Actual character, sentence, or repetition counts | Turning intuition into percentages such as AI 83%, Human 17% |
| Binary classifier probabilities | AI/Human outputs with their definitions and conditions | Certifying the person's actual writing history |
| Human/AI/Mixed probabilities | All three original classes | Discarding Mixed, merging it into Human, or silently renormalizing |
| Fraction of flagged text | Flagged share of the eligible prose | Subtracting it from 100 and calling the remainder a human-authorship probability |
| Predicted class plus confidence | Confidence in the named predicted class | Inventing the opposite class probability without a supporting schema |
| Logit, perplexity, curvature, ratio, or risk score | Raw score with its name, direction, and units | Calling a rescaled 0–100 score a probability |
| Applicable validation and calibration | Estimates and metrics limited to that validation distribution | Generalizing them to arbitrary users, languages, or new generators |

Accuracy, AUROC, precision at a threshold, individual class probability, and the proportion of AI-like text are different quantities. Display precision is not evidence precision. Preserve raw values in records; whole percentages or one decimal place are usually sufficient in a user-facing table.

Explain totals of 99.9 or 100.1 caused by rounding. If internal values are out of range or do not sum correctly, report a schema error instead of calculating a result. `null` does not mean 0%.

## Default Korean result

Run `korean_model.py` and fill **Estimated Human class probability: X%; estimated AI class probability: Y%** with the actual returned values. X/Y are placeholders, not permission to invent numbers. Include the model version, exact input hash, calibration reference (50% AI; equal essay/abstract/poetry weight), and applicability warnings. Do not turn evaluation accuracy into this document's confidence. See the [Korean model card](korean-model.md).

Passing `--model-result work/korean-result.json` to the HTML report command checks the input hash and two-class probability sum before displaying the values. Distinguish these values from stylistic observations, feature logit contributions, and paragraph-removal deltas. Deltas are measured in percentage points, not paragraph-level authorship probability.

## No completed applicable measurement

> This text alone does not establish whether AI was involved. [Main observation] is present, but [plausible human explanation] also fits.
>
> AI-authorship probability: **unavailable**. Human-authorship probability: **unavailable**.
> Method: review of the original text and local surface measurements. No external detector model was run.

Follow with as much evidence as the text supports. Do not manufacture flags to fill a table. If a score is needed, run an applicable free local model; try the bundled model first for Korean. State actual failures such as damaged weights, unsupported input, or encoding errors. A measured out-of-domain estimate should be labeled as such, not hidden as if no measurement occurred. Do not require a commercial API or paid key. Missing percentages do not prevent a full evidence review.

## A supplied three-class result

The following numbers are a **fictional formatting example**, not analysis results:

| Document | Detector-reported AI | Human | Mixed | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Korean document A | 65% | 20% | 15% | The detector assigned its highest probability to the AI class |

An additional display of AI involvement (AI + Mixed) 80% versus Human-only 20% is appropriate only if the class definitions permit that aggregation. It does not mean that AI wrote 80% of the words. Retain the original three values.

Below the table, record the detector/model version, measurement time, original input/hash or submitted scope, language/genre conditions, and independent calibration status. Mark unknown versions as unknown. When reports disagree, preserve each definition and explain possible reasons for the conflict.

Example measured-result wording: “Provider-reported class probabilities: AI …%, Human …%, Mixed …%. These are the named detector's classifications for the submitted version, not proof of its writing history.” Supply model, date, coverage, and known validation limits. Use the user's language in the actual response.

## Requirements for calibration

Calibration is not an arbitrary conservative reduction of a score. Fit an appropriate Platt, temperature, or isotonic transformation on separate calibration data with raw scores and genuine labels, then evaluate Brier score, log loss, and reliability on untouched test data. [Guo et al.](https://proceedings.mlr.press/v70/guo17a.html)

Posterior probabilities may change when AI prevalence differs between the validation data and deployment population. Mixed, translated, and edited labels also need consistent definitions. Do not label an output calibrated when no calibration procedure was run. `evaluate.py` **evaluates only; it does not fit a calibrator**. The Korean `train_korean.py` actually fits a sigmoid on separate calibration groups and exports it with the model. This calibration does not apply to the English checkpoint.

## Detailed report format

1. Overall assessment for each document and the meaning of any measured scores. Otherwise mark both AI and Human probabilities unavailable.
2. Whole-document analysis: structure, reasoning/specificity, voice, rhythm/repetition, language features, and sources/history.
3. Paragraph review: P1… location, exact excerpt, observation, AI-like interpretation, plausible human alternative, strength, and evidence basis. Use a neutral assessment when there is no signal.
4. Detailed key evidence and counterevidence. Claims of repetition across the document require multiple actual locations.
5. Reviewed paragraph counts and any excluded or unreviewed scope.

For long documents, explain the main findings in chat and provide full-text highlighted HTML. Highlight colors and review coverage are not probabilities. Follow the exact ledger contract in the [evidence protocol](evidence-protocol.md). Report a deletion experiment as, for example, “score change: +12 percentage points,” separate from analyst interpretation. Do not reuse illustrative values as real results.

The English local model retains Human, AI, AI-edited, and Humanized classes. If AI involvement is aggregated, also display all four original values. For multiple windows, explain window scores and do not label an uncalibrated window average as a document-authorship probability.
