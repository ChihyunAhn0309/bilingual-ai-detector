# Development and verification record

Review date: 2026-10-03. Source checking was conducted as a separate pass after document generation. The table groups repeated claims. Agreement with a source verifies attribution, not reproduction of an external model's performance.

## Source checks

| Claim checked | Primary source or location | Finding |
| --- | --- | --- |
| GLTR as statistical detection assistance | [ACL paper](https://aclanthology.org/P19-3019/) | Matches; not generalized to current detection performance. |
| DetectGPT log probabilities, perturbations, and curvature | [Paper](https://arxiv.org/abs/2301.11305) | Matches; actual model computation is required. |
| Fast-DetectGPT conditional curvature and sampling | [Paper](https://arxiv.org/abs/2310.05130), [author implementation](https://github.com/baoguangsheng/fast-detect-gpt) | Matches; implementation example probabilities are not this skill's results. |
| Binoculars comparison of two models | [ICML paper](https://proceedings.mlr.press/v235/hans24a.html), [author implementation](https://github.com/ahans30/Binoculars) | Matches; the implementation also notes non-English limitations. |
| Ghostbuster weak-model features and classifier training | [Paper](https://arxiv.org/abs/2305.15047) | Matches; original-generator probabilities are distinguished from reference-model use. |
| RADAR adversarial detector/paraphraser training | [Paper](https://arxiv.org/abs/2307.03838) | Matches; no guarantee against all rewriting is inferred. |
| KatFishNet features and metrics | [Table 3, PDF page 8](https://aclanthology.org/2025.acl-long.1030.pdf) | 94.88/73.10/75.62 and AUROC confirmed; not described as universal accuracy. |
| Token watermarking during generation | [Paper](https://arxiv.org/abs/2301.10226) | Matches; distinct from Unicode-character inspection. |
| RAID's varied evaluation conditions | [ACL paper](https://aclanthology.org/2024.acl-long.674/) | Matches; paper-era and current repository sizes are not conflated. |
| Korean absent from MULTITuDE's 11 languages | [Language list](https://aclanthology.org/2023.emnlp-main.616/) | Confirmed; not used as Korean-performance evidence. |
| M4 generalization to unseen domains/generators | [EACL paper](https://aclanthology.org/2024.eacl-long.83/) | Matches. |
| False-positive bias on non-native English | [Paper](https://arxiv.org/abs/2304.02819) | Matches within the studied samples/products. |
| Rewriting, distribution distance, and detection limits | [Paper](https://arxiv.org/abs/2303.11156) | Matches; not generalized to unconditional impossibility. |
| Accuracy versus probability calibration | [ICML paper](https://proceedings.mlr.press/v70/guo17a.html) | Matches; initial versions had no fitted calibrator; v3 Korean calibration is documented separately below. |
| GPTZero hierarchical/joint learning, three classes, and undisclosed details | [Technical report §3.2](https://arxiv.org/html/2602.13042v1), [FAQ](https://gptzero.me/faq) | Matches; attributed to the vendor. |
| GPTZero English/Korean support and API request format | [Language list](https://support.gptzero.me/articles/1682612063-what-languages-does-gptzero-support), [developer page](https://gptzero.me/developers) | Documentation contract checked; no live service call. |
| Turnitin prose share, languages, length, and asterisk treatment | [Official guide](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report) | Matches; complement not labeled human-authorship probability. |
| Copyleaks detection/explanation language differences | [Support list](https://docs.copyleaks.com/reference/actions/miscellaneous/ai-detection-supported-languages/), [AI Logic](https://docs.copyleaks.com/concepts/features/ai-logic) | Matches; Korean detection and Korean explanations distinguished. |
| Originality confidence versus allowance | [Score guide](https://originality.ai/blog/score-meaning), [language guide](https://help.originality.ai/en/article/multiple-languages-how-to-use-multi-language-ai-detection-13e5plo/) | Reviewed guidance retained rather than simplified to an older single-score description. |
| Pangram classifier and Korean support | [Method](https://www.pangram.com/knowledge-hub/how-does-pangram-work), [languages](https://www.pangram.com/knowledge-hub/what-languages-does-pangram-work-on) | Matches vendor explanation; detailed weights unverified. |
| Korean absent from Winston AI list | [Language guide](https://help.gowinston.ai/getting-started/which-languages-does-winston-ai-work-with) | Limited to the reviewed AI-text-detection list. |
| ZeroGPT feature families and multilingual claim | [FAQ](https://www.zerogpt.com/faq) | Matches vendor explanation; independent Korean accuracy unverified. |
| Sapling token classification and sentence perplexity | [Official page](https://sapling.ai/ai-content-detector) | Matches; explicit Korean validation scope remains unverified. |
| QuillBot explanation and 80-word requirement | [Official page](https://quillbot.com/ai-content-detector) | Matches; actual version semantics and Korean performance require separate checks. |
| Grammarly passage analysis and text share | [User-guide FAQ](https://support.grammarly.com/hc/en-us/articles/28936304999949-AI-Detector-user-guide) | Matches; not interpreted as document-authorship probability. |
| GPT Killer model families, word-unit aggregation, and combined plagiarism checks | [Official manual](https://manual.muhayu.com/montly-gpt-killer-labs) | Matches; a fixed 400-character specification is not claimed. |
| Six public skills' roles, dependencies, and score meanings | [Comparison with author links](skill-comparison.md) | Original SKILL.md files read; their claims are not promoted to validated performance. |
| Editorial purpose of local humanizer skills | Their local SKILL.md files and relevant detection explanations | Relevant portions checked; existing files and earlier measurements were not repurposed. |

Alternative explanations, the no-additional-detector-fee boundary, abstention, and report format are design decisions, not measured discoveries. No evidence establishing exact personal-authorship probabilities or 100% detection was obtained, and no such claim is made.

## Additional v2 claim checks

| Claim | Evidence | Finding |
| --- | --- | --- |
| Public English results for 1,089 samples and recorded versions | Epoch AI article and pinned `results/all_detectors.csv` | Local reaggregation matched published numbers; not a new current-service run. |
| Present GPTZero cannot be described by perplexity/burstiness alone | Official Support Center notice of the autumn 2023 change | Matches; the benchmark article's older method account was not adopted. |
| Free model's English scope, four classes, license, and mean pooling | Pinned README, config.json, serving_head.json, and NOTICE | Matches; vendor metrics remain separate from local validation. |
| Downloaded weights match the public checkpoint | Hugging Face LFS SHA256 and downloaded-file hash | Matches; no remote Python execution. |
| Raising a threshold is not automatically an improvement | Actual results at two predefined thresholds on the same 36 samples | 30/36 became 28/36; no superiority claim. |
| Insufficient validation for general Korean probabilities in v2 | Actual Desklib/Oculus/Munche/KatFishNet scopes | v2 reported unavailable Korean probabilities; this described the reviewed options, not the nonexistence of every possible Korean model. |
| Detailed explanations prove superiority to GPTZero | No supporting evidence; the pilot favored the opposite conclusion | Claim rejected. |

## v2 software and behavioral checks

- `quick_validate.py` passed skill-format validation.
- **35 unit tests passed**, covering synthetic inputs, numeric operations, coordinates, Unicode/BOM/CRLF, HTML escaping, charge prevention, sample selection, and failed-run denominators. Test pass rates are not detector accuracy.
- The legacy live GPTZero command fails before any external request, even with a key and upload flag. Only supplied results are interpreted.
- Public English weights loaded; actual four-class inference and before/after deletion scores for two paragraphs completed. Initial memory pressure and removal of `prepare_for_model` in Transformers 5 were addressed with meta initialization, bounded threads, and a verified DeBERTa token layout. Execution then succeeded. Synthetic demonstrations were not accuracy samples.
- The public 36-document English pilot completed. Versions, samples, hashes, raw scores, both predefined thresholds, and matched archived verdicts are stored in [benchmark-results.json](benchmark-results.json). See the [performance comparison](performance-comparison.md).
- A separate agent used v2 to analyze a three-paragraph Korean fixture with the actual tools, checking source preservation, quotations, hashes, and coverage without external calls. This was behavioral validation, not ground-truth authorship validation.
- Independent review found internal English keys exposed in the Korean report; localized display labels replaced them. The completed HTML was rendered in a local browser to inspect Korean text, paragraph cards, and highlights.
- The earlier BOM-preservation fix was retained, coordinate/overwrite regressions were checked, and internal links and source syntax were verified.

**Not validated in v2:** general Korean accuracy/FPR, a direct comparison with the latest GPTZero 4o, robustness to every humanizer/genre/new generator, or independent probability calibration. The English pilot is small and public, so training overlap cannot be excluded. Confidence is stronger in execution, coordinates, and metric recomputation than in general authorship discrimination.

## Additional Korean validation in v3

On 2026-10-03, a Korean character classifier was trained and its sigmoid fitted on separate calibration groups. The [model card](korean-model.md), [run results](korean-validation.json), per-document predictions, and split records are distributed together. Earlier statements that Korean probabilities were unavailable describe v2.

- 12,894 source rows became 12,844 after deduplication: training 6,621; selection 1,718; calibration 1,907; final test 1,846; separate shared-topic transfer test 752. The split manifest confirmed no group overlap across the primary splits and no original test-v2 samples in fitting stages.
- Six candidates were predefined. Selection and calibration were fixed before final evaluation; the test did not drive another model adjustment. The selected surface-feature weight is 0, so character features determine predictions.
- Topic-disjoint accuracy was 97.51%, with 8/885 human false positives. The 1,714 essays dominate the overall result. Small abstract/poetry subsets perform worse and are reported separately; this is not universal accuracy.
- Brier/ECE improved after calibration, while accuracy declined slightly from 97.72% to 97.51%. Holdout calibration means separate fitting data, not external institutional certification.
- Standard-library inference matched the sklearn pipeline within 4.45e-16 on the first 25 final-test and 25 transfer samples. Accuracy, FPR, AUROC, Brier, log loss, and ECE were recomputed from all saved evaluation predictions and matched the recorded metrics.
- **45 unit tests passed**, adding Korean offline inference, probability sums, logit reconstruction, exact locations through Unicode/whitespace normalization, deletion deltas, invalid language/input/weights, input-result hashes, leakage checks, and original-test preservation. Test counts are not accuracy.
- Actual Korean CLI inference succeeded with Python `-S`, without loading site-packages, and returned full-input scores and paragraph-removal results. Commercial detector API calls: zero.
- A separate agent analyzed the updated three-paragraph fixture, connecting estimates, full-source review, AI- and human-direction character contributions, and deletion deltas. Records confirmed unchanged source, probability sums, coordinates, contribution reconstruction, 3/3 paragraph coverage, and no external HTML resources. This synthetic demonstration was excluded from accuracy evaluation.

Still unverified: a matched Korean GPTZero comparison and accuracy/calibration for all modern generators, humanizers, mixed authorship, new genres, and actual user populations. No claim of perfect detection or exact personal-history probability is made.

## v3.1 independent release review and corrections

A separate Codex conversation read and executed the sources, weights, and original data. Included artifacts are the [public summary](review-public.md), [machine-readable results](review-public.json), [reviewed source hashes](reviewed-files-public.json), and [review-document hashes](review-artifacts-public.json). This is not external institutional certification or performance testing on a newly collected population.

- Final checks passed: 56 unit tests, 16 independent subprocess tests, and 20 independent result-schema tests.
- English HTML and JSON preserve uncalibrated/experimental/false-positive warnings and UTC measurement time. Clearly non-Latin and empty inputs are rejected before inference; this screen is not an English-language identifier.
- The bundled Korean hash is pinned; malformed roots, numbers, and scales are rejected and were checked with corrupted fixtures.
- The actual English worker owns the lock. Failed, missing, incomplete, or incorrectly bound results are not published. Surviving-worker contention after supervisor termination and injected native exit codes were retested with real subprocesses. Existing results and originals are preserved.
- Real English checkpoint inference through the supervisor reproduced all four earlier class scores with difference 0 and measured three paragraph deletions. The repeated 36-document pilot also matched its saved scores exactly.
- All 2,598 Korean evaluation/transfer documents were rescored within 1.45e-15 of saved predictions. All retained 12,844 hashes/labels and primary-split nonoverlap were checked. Repeated training produced byte-identical weights, splits, and predictions.
- Inference network blocking was verified. No commercial detector API, paid inference, or cloud GPU was used. Raw training text, private audit logs, and the large optional English weights are excluded from the package.

The Windows/PyTorch native-crash root cause remains unknown. Verified runtime protection is not a root-cause repair or a guarantee of stability everywhere. Data/model rights and the public repository's non-OSS scope are distinguished in the [third-party notices](../THIRD_PARTY_NOTICES.md). At the original 3.1 release, only the README and this verification index changed after the reviewed snapshot; executable code and weights retained their reviewed hashes.

## v3.1.1 English documentation edition

README, supporting guides, model cards, comparisons, skill metadata, and the public review text are now in English. Original Korean examples, learned patterns, test fixtures, and localized runtime strings are retained as language data. Executable scripts, weights, and evaluation datasets are byte-identical to the published 3.1.0 commit.

The original independent review is preserved in [commit 54b50bb](https://github.com/ChihyunAhn0309/bilingual-ai-detector/tree/54b50bb4c5c08f570c61b9b504b86bc7bc2ad609). `reviewed-files-public.json` still describes that historical snapshot. The English review translation and updated artifact hashes do not imply that the independent session was rerun. Findings, statuses, benchmark values, and unresolved limitations are unchanged.

Documentation-update checks cover internal links, preserved source URLs, remaining Korean text limited to intentional examples/localization data, unchanged runtime/model/evaluation files, translated-review numeric parity, and the existing 56-test suite. No new detector-accuracy claim is introduced.
