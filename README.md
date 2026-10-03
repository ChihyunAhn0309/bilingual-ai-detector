# Bilingual AI Detector

An offline Korean and English AI-text analysis skill for Codex. It combines **estimated Human/AI class probabilities, exact passage evidence, and alternative human explanations** with a review of the whole document.

The Korean classifier is bundled and runs with the Python standard library. An optional English checkpoint can be downloaded for local inference. No commercial detection API, paid credits, or hosted inference service is used.

**This tool does not certify authorship or guarantee perfect detection.** Its percentages are model estimates under documented conditions, not verified probabilities of a person's writing history.

Current version: **3.1.2**, with a Windows weight-loading fix and English documentation. Weights, scoring mathematics, and evaluation data are unchanged. See the [original independent review](references/review-public.md), [historical reviewed file hashes](references/reviewed-files-public.json), and [verification history](references/verification.md) for the scope of each release's checks.

## Capabilities

| Capability | Korean | English |
| --- | --- | --- |
| Model | Bundled ~2 MB character TF-IDF/logistic classifier | Optional ~1.74 GB DeBERTa checkpoint |
| Output | Human/AI estimates with separate holdout sigmoid calibration | Human/AI/AI-edited/Humanized outputs without independent calibration |
| Measured evidence | Signed feature contributions at exact source locations and paragraph-removal sensitivity | Paragraph-removal sensitivity |
| Whole-document explanation | The agent reviews every paragraph, explains observations, and supplies plausible human alternatives | Same workflow |
| Long documents | Full input is scored, with warnings outside the training length range | Every token is covered by windows; window averages are not presented as document-authorship probabilities |

The CLI produces model results and validates quotations, coordinates, and review coverage. The agent using the skill writes the detailed natural-language analysis. Running a CLI command alone does not produce a complete editorial review. Codex/ChatGPT session charges are outside this project's control.

Repository documentation is in English. The skill responds in the user's language. Korean examples, learned character patterns, and localized report strings retain their original language.

## Quick start

Python 3.10 or later is required. Development and release checks used Python 3.13 on Windows.

```sh
git clone https://github.com/ChihyunAhn0309/bilingual-ai-detector.git
cd bilingual-ai-detector
python -B -X utf8 scripts/korean_model.py examples/korean.txt --genre unknown --out work/korean-result.json
```

On Windows, `py -3.13` can replace `python`. Korean inference requires no `pip install`, external model download, API key, or GPU. Existing output files are protected: use a new output filename for another run.

### Use as a Codex skill

Place the repository folder at `~/.codex/skills/bilingual-ai-detector`, or under `skills/bilingual-ai-detector` in your custom `CODEX_HOME`. Back up any local changes before replacing an existing installation.

Example request:

> Use $bilingual-ai-detector to calculate the available Human/AI estimates for this text, review every paragraph, and show exact passage evidence with plausible human explanations.

If the new skill is not yet discoverable, start a new conversation. [SKILL.md](SKILL.md) contains the agent instructions. Use the [evidence protocol](references/evidence-protocol.md) to validate quotations and generate a highlighted HTML report.

### Optional English inference

```sh
python -m pip install -r requirements-english.txt
python scripts/prepare_local_model.py models/tropa-mini
python -B -X utf8 scripts/run_english.py examples/english.txt --language en --explain --out work/english-result.json
```

Setup downloads Python packages and a public model. **It does not upload the manuscript.** Inference uses local files only. The English model requires substantial memory and is an experimental auxiliary scorer.

The supervised CLI serializes model workers and produces no probability result after a runtime failure. Windows uses Safetensors 0.8+'s `pread` backend to bypass the reproduced access violation in memory-mapped weight loading. It does not fall back to that crashing path. Memory requirements still apply, and native-runtime stability is not guaranteed. See the [English model guide](references/free-local-model.md) for the checkpoint, hashes, runtime protection, and limitations.

## Measured performance and limits

The Korean topic-disjoint evaluation contained 1,846 documents: accuracy was **97.51%**, with a human false-positive rate of 0.90% (8/885). Essays accounted for 1,714 documents. Accuracy on 37 abstracts and 95 poems was 91.89% and 87.37%, respectively. These results do not establish performance across every genre or current generator. The calibration reference assumes a 50% AI class prior; it does not measure the prevalence in the user's documents. See the [Korean model card and per-document records](references/korean-model.md).

In a 36-document English pilot, the local model achieved 83.33% accuracy, while archived GPTZero verdicts on the same samples achieved 97.22%. **There is no evidence that this skill outperforms GPTZero.** The Korean and English evaluations cannot be ranked against each other. No matched Korean GPTZero comparison was performed. See the [comparison conditions and raw results](references/performance-comparison.md).

Short texts, translation, editing, mixed authorship, new humanizers, and unfamiliar generators may produce errors that these evaluations do not characterize. A paragraph-removal delta is not that paragraph's AI-authorship probability. A common phrase's model contribution does not prove its origin.

## Documentation

| Topic | Guide |
| --- | --- |
| Agent workflow | [Skill instructions](SKILL.md) |
| Language-specific observations | [Korean and English analysis guide](references/language-guide.md) |
| Probability semantics and report structure | [Result format](references/result-format.md) |
| Exact quotations and full-document explanations | [Evidence protocol](references/evidence-protocol.md) |
| Model setup and scope | [Korean model](references/korean-model.md), [English model](references/free-local-model.md) |
| Research and existing detectors | [Research methods](references/research-methods.md), [product comparison](references/product-matrix.md), [skill comparison](references/skill-comparison.md) |
| Evaluation and release evidence | [Validation guide](references/validation.md), [performance comparison](references/performance-comparison.md), [independent review](references/review-public.md) |

## Testing and reproduction

```sh
python -B -X utf8 -m unittest discover -s scripts -p "test_*.py"
```

The 60 unit tests use the standard library and do not download the large English model or call commercial APIs. They cover model hashes, metric recomputation, data splits, Unicode source coordinates, invalid inputs, HTML escaping, guarded execution, and Windows loader selection and failure handling.

The separate review also passed 16 subprocess checks and 20 result-schema checks, ran the real English checkpoint, rescored all 2,598 Korean evaluation documents, and reproduced Korean training. Test counts are not detector-accuracy measurements. See the [verification history](references/verification.md).

Korean retraining is optional:

```sh
python -m pip install -r requirements-training.txt
python scripts/prepare_korean_data.py work/korean-data
python scripts/train_korean.py --data-root work/korean-data --output-dir work/korean-retrained
```

Raw training texts are not included. Source revisions and file hashes are pinned, and download, training, and inference are separate steps. Consult the [source and third-party notices](THIRD_PARTY_NOTICES.md). This public repository has not been granted a project-wide open-source license and does not grant rights to third-party material.
