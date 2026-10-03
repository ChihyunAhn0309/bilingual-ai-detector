# Korean probability model and validation scope

Version 3 introduced a **trained Korean classifier** that computes estimated Human/AI probabilities without additional detector-service fees, an API key, GPU, or model download. Inference uses the Python standard library. The approximately 2 MB `models/korean-linear-v1.json` contains its weights. Supply a local file preserving the original text.

```text
python scripts/korean_model.py manuscript.txt --genre unknown --out work/korean-result.json
```

`--genre essay|abstract|poetry|unknown` labels applicability; it does not change the score. Use `unknown` for business reports, fiction, chat, and other unevaluated genres. The Korean-dominant input filter requires at least 10 Hangul characters and at least 50% Hangul among alphabetic characters. This is an input screen, not a validated minimum length.

The middle 90% of training lengths spans **210–907 Unicode codepoints**; other lengths receive a warning. Inputs above 200,000 characters are explicitly rejected rather than silently truncated. Acceptance below that limit does not establish long-document accuracy.

## Outputs and explanations

- `class_probabilities.human` and `.ai`: calibrated estimates for two mutually exclusive training labels, summing to 1. Mixed authorship and AI-only editing were not trained as separate classes.
- `calibration`: a sigmoid fitted on separate data containing 1,907 documents and 52 groups. Its reference gives AI/Human equal 50% priors and equal weight to essays, abstracts, and poetry. It does not measure the user's actual AI prevalence; distribution changes can affect calibration.
- `feature_explanation.lexical`: the 30 strongest character 2–5-grams and up to five exact original locations for each. Positive values raise this model's AI logit; negative values lower it. These are **computational contributions in this model**, not universal evidence of AI authorship. Overlapping features are not independent votes.
- `intercept_contribution + all_feature_contributions_sum`: reconstructs the calibrated logit, whose sigmoid gives the AI estimate. The displayed top 30 features alone cannot reconstruct the full score.
- `paragraph_sensitivity`: the original score minus the score after deleting a paragraph, in percentage points. Context, length, and normalization all change, so this is neither paragraph-authorship probability nor causal sentence attribution. The default limit is 60 paragraph deletions; skipped counts are disclosed. Classification itself uses the full document.
- `applicability_cautions`: length, genre, and learned-pattern coverage warnings. Retain them in the final report.
- `text_sha256`, `model_sha256`, and `measured_at_utc`: input, weights, and measurement records. Hashes do not authenticate generation history.

The agent reviews the whole document to write observations, interpretations, and plausible human alternatives. Do not invent semantic significance for small character fragments. A positive contribution from a fragment such as “새 ” does not make that expression AI-only vocabulary. Specificity, argument quality, and changes in endings belong in a separate stylistic analysis.

## Training method and data

`korean-char-style-logistic-v1` uses character TF-IDF and logistic regression. It is neither a copy of KatFishNet nor a fine-tuned Korean LLM. It uses 40,000 vocabulary features, character 2–5-grams, sublinear TF, L2 document normalization, and `min_df=3`. Vocabulary, IDF, and scaler fitting use training data only.

Six predefined candidates combine C={0.5,2,8} and surface-feature weight={0,0.25}. Genre/class-balanced log loss on selection data chose **C=8 and surface-feature weight=0**. The 16 surface features remain available as observations but make no direct contribution to the selected classifier. After selection, a regularized sigmoid was fitted on separate groups. Weights and thresholds were not changed in response to final-test results.

Sources:

- [KatFishNet repository](https://github.com/Shinwoo-Park/katfishnet), revision `5e3dc89cc31a029be38fb2d871476b0aff7b793c`: Korean essays, abstracts, poetry, and generated counterparts. The [ACL 2025 paper](https://aclanthology.org/2025.acl-long.1030/) describes the original research; the metrics below belong to this separate model.
- [Detect_AI_Generated_Korean_Text](https://github.com/gygUnig/Detect_AI_Generated_Korean_Text), revision `b822d8e807298797d45003cc4171f554811cb01c`: train/validation files and test-v2 outputs from several generators. Upstream performance claims are not inherited by this model.
- [scikit-learn calibration documentation](https://scikit-learn.org/stable/modules/calibration.html): calibration methods and evaluation. Calibration does not necessarily increase accuracy.

Of 12,894 source rows, 50 normalized exact duplicates were removed, leaving 12,844. Each document remains intact. Grouping connects essay topics, abstract titles, source-poem groups, and identical text across datasets. Splits contain 6,621 training, 1,718 selection, 1,907 calibration, 1,846 topic-disjoint final-test, and 752 transfer-test documents. The four primary splits have disjoint groups. Incomplete author identifiers prevent a guarantee of full author separation or removal of semantically similar documents.

Ko-Detect's original test-v2 was never used for training, selection, or calibration. Samples sharing topics with fitting stages are reported separately as `transfer_test`; they are not a wholly new-topic test.

## Measured results — 2026-10-03

The classification threshold is estimated AI probability ≥ 0.5. **Accuracy is the proportion of correct labels on this public evaluation data, not a user's document probability.**

| Final-test subset | Documents | Accuracy | Human false-positive rate | AI recall |
| --- | ---: | ---: | ---: | ---: |
| Overall; 92.85% essays | 1,846 | 97.51% (1,800/1,846) | 0.90% (8/885) | 96.05% |
| Essays | 1,714 | 98.19% | 0.70% (6/856) | 97.09% |
| Abstracts | 37 | 91.89% | 10.00% (1/10) | 92.59% |
| Poetry | 95 | 87.37% | 5.26% (1/19) | 85.53% |

Overall AUROC=0.99835, Brier=0.01849, and ECE (10 bins)=0.01704. A 300-replicate bootstrap over 34 topic/source groups gives a 95% percentile accuracy interval of **95.75–98.64%** and an FPR interval of **0.54–2.32%**. These are not performance intervals for new genres. The human abstract and poetry subsets contain only 10 and 19 documents, so their FPRs are unstable.

Calibration changed overall Brier from 0.01864 to 0.01849, genre/class-balanced Brier from 0.05500 to 0.05065, and ECE from 0.03648 to 0.01704. **Accuracy decreased slightly from 97.72% to 97.51%.** Do not claim calibration improved accuracy. One ECE value does not prove adequate calibration across all probability ranges and genres.

The separate 752-document transfer test achieved 97.21% accuracy, 0.27% FPR (1/376), and 94.68% AI recall. All samples are essays and share topics with fitting stages. Standard-library inference differed from the training pipeline by at most 4.45e-16 on the first 25 documents of each evaluation set.

**No matched Korean GPTZero comparison was performed.** Comparing this 97.51% with the English pilot's GPTZero 97.22% would confound languages, samples, and targets. These are public-data holdout results for this implementation, not external institutional product certification.

## Reproduction and artifacts

Inference needs no additional packages. Retraining requires numpy, scipy, scikit-learn, and threadpoolctl; the original run used Python 3.13 and scikit-learn 1.9.0. Download and training are separate commands. The downloader retrieves pinned public revisions without sending user text.

```text
python scripts/prepare_korean_data.py work/korean-data
python scripts/train_korean.py --data-root work/korean-data --output-dir work/korean-retrained
```

Raw datasets are not redistributed. Public access does not establish unrestricted redistribution or commercial-use rights. Follow applicable source terms; this project does not grant new third-party permissions.

- [Full run results](korean-validation.json): source hashes, candidate selection, calibration, and genre/generator metrics.
- [Per-document predictions](korean-test-predictions.jsonl): labels, scores, and hashes without original text.
- [Split manifest](korean-split-manifest.jsonl): training/selection/calibration/evaluation groups and document hashes.
- [Source URLs, revisions, and hashes](korean-source-manifest.json).

General current performance, human–AI collaboration, humanizers, translation, adversarial editing, and new generators remain insufficiently validated. Stronger deployment claims require new provenance-confirmed samples, separate recalibration, and evaluation in the intended environment. This model supplies documented **Korean class-probability estimates**.
