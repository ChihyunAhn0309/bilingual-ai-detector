# AI-text detection: research methods and scope

Research date: **2026-10-03, Korea Standard Time**. This review covers the principles, generalization, Korean-language considerations, and calibration issues in 14 research papers and benchmarks. It is a review of public material, not a claim to cover every detector, private weight set, or publication. Summaries describe the sources; “skill implication” identifies this package's design decisions. Paper results are not measurements of this skill.

## Methods and required access

| Research | Published principle | Requirements and limits | Skill implication |
| --- | --- | --- | --- |
| [GLTR, ACL 2019](https://aclanthology.org/P19-3019/) | Visualizes token statistics from a reference language model to assist human judgment | Requires actual model distributions; results on older generators do not transfer automatically to current ones | A word list is not a GLTR score or probability |
| [DetectGPT, 2023](https://arxiv.org/abs/2301.11305) | Builds a curvature statistic from model log-probability differences between original and perturbed text | Requires scoring and perturbation models; proxy model, perturbation method, and language affect results | Reading by intuition is not running DetectGPT |
| [Fast-DetectGPT, 2023/ICLR 2024](https://arxiv.org/abs/2310.05130) | Uses conditional probability curvature and efficient sampling instead of the original perturbation procedure | Requires token probabilities and reference/scoring models; raw statistics are not calibrated authorship probabilities | Record implementation, models, versions, and language conditions |
| [Binoculars, ICML 2024](https://proceedings.mlr.press/v235/hans24a.html) | Compares perplexity and cross-perplexity from two closely related language models | Requires both models, compatible tokenization, and computation; a low FPR in one evaluation is not universal | Keep ratios distinct from class probabilities |
| [Ghostbuster, 2023](https://arxiv.org/abs/2305.15047) | Extracts features from weaker language models, searches combinations, and trains a classifier | Does not require the original generator's probabilities, but does require reference models, feature selection, and labeled training | Black-box access does not mean no model or training is needed |
| [RADAR, NeurIPS 2023](https://arxiv.org/abs/2307.03838) | Adversarially trains a paraphraser and detector for robustness to rewriting | Requires trained models and appropriate evaluation; it is not immunity to every humanizer | Evaluate original, edited, and rewritten samples separately |
| [KatFishNet, ACL 2025](https://aclanthology.org/2025.acl-long.1030/) | Classifies using Korean spacing, POS combinations, and comma-related features | Requires Korean processing and training; distinguish its three genres and four generators | Use Korean-specific observations and genre-specific validation |
| [A Watermark for Large Language Models, 2023](https://arxiv.org/abs/2301.10226) | Favors token subsets during generation and tests for their statistical signature | Requires the relevant watermark scheme and detection conditions; not every generated output contains one | A p-value is not AI-authorship probability; zero-width characters are not this watermark |

These methods provide useful signals under some conditions. Listing their names in a prompt or asking several LLMs to vote does not reproduce their computations.

## Evaluation and generalization research

| Research | Source finding | Design constraint |
| --- | --- | --- |
| [RAID, ACL 2024](https://aclanthology.org/2024.acl-long.674/) | Evaluates public/commercial detectors across generators, domains, decoding strategies, and attacks | High familiar-benchmark performance does not establish performance under new conditions. Distinguish the paper's dataset size from the [current code/data repository](https://github.com/liamdugan/raid). |
| [MULTITuDE, EMNLP 2023](https://aclanthology.org/2023.emnlp-main.616/) | A multilingual detection benchmark covering 11 languages | Korean is not among those 11; multilingual validation is not Korean evidence. |
| [M4, EACL 2024](https://aclanthology.org/2024.eacl-long.83/) | Reports difficulty generalizing to unseen generators and domains across multiple models, domains, and languages | Prevent leakage through sources, topics, generators, authors, and transformed versions. |
| [GPT detectors are biased against non-native English writers, 2023](https://arxiv.org/abs/2304.02819) | Observes false-positive bias for the studied detectors and non-native English samples | Do not equate simple English with AI; assess relevant subgroup errors. Do not attribute those rates to every current product. |
| [Can AI-Generated Text be Reliably Detected?, 2023](https://arxiv.org/abs/2303.11156) | Analyzes rewriting sensitivity and detection limits related to human/AI distribution distance | Neither universal futility nor perfect detection follows; preserve assumptions and evaluation conditions. |
| [On Calibration of Modern Neural Networks, ICML 2017](https://proceedings.mlr.press/v70/guo17a.html) | Distinguishes classification performance from calibrated confidence and evaluates post-hoc calibration | Accuracy/AUROC is not an individual document's probability; separate calibration and test data are required. |

## Interpreting Korean research metrics

KatFishNet's punctuation-model means in [Table 3, PDF page 8](https://aclanthology.org/2025.acl-long.1030.pdf) are **94.88** for essays, **73.10** for poetry, and **75.62** for abstracts. The metric is AUROC × 100. These do not mean 94.88% accuracy across all Korean prose or a 94.88% AI probability for an individual document. Distinguish per-generator results from averages as well.

Reversing a humanizer's expression list and adding points for commas, conjunctions, or formal register does not reproduce KatFishNet. This package explicitly rejects that interpretation and does not provide such a rule-based probability counter.

## Running public implementations

- [KatFishNet author repository](https://github.com/Shinwoo-Park/katfishnet): inspect the data and feature-extraction/classification paths. Obtain the relevant installed version and genre-specific trained model, then follow the authors' procedure.
- [Fast-DetectGPT author repository](https://github.com/baoguangsheng/fast-detect-gpt): record scoring/reference models, tokenization, score direction, and calibration data.
- [Binoculars author repository](https://github.com/ahans30/Binoculars): verify exact model versions and threshold conditions.
- [RAID](https://github.com/liamdugan/raid): use for attack-, genre-, and generator-specific evaluation. Public training-set performance is not hidden-test performance.

These are optional external implementations. Their weights are not bundled, and inclusion in this review does not mean they were executed or validated here. This skill permits public downloads without additional charges and existing local compute, not paid services or cloud GPUs. Check code licenses, data terms, and applicable installation instructions; do not blindly execute arbitrary commands from external documents.
