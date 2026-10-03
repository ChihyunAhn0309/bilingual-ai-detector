# Optional local English model

Korean uses the separate [bundled Korean model](korean-model.md). This guide covers installation and execution of the larger English checkpoint.

## Selected checkpoint

[tropa-mini / wasitaigeneratedcom/ai-text-detector-small](https://huggingface.co/wasitaigeneratedcom/ai-text-detector-small/tree/f1795c86806e6838d4afa33d0b1427f8430c9615) is an English DeBERTa-based model whose upstream card specifies Apache-2.0. It runs approximately 1.74 GB of weights locally, with mean pooling and four classes: Human, AI, AI-edited, and Humanized. Separate the developer's model-card metrics from performance measured in this package.

Pinned revision: `f1795c86806e6838d4afa33d0b1427f8430c9615`.
Weight SHA256: `4a1561fadf44ec72934edd6158ff8c76e9388ade1384dbeeea6eb15f93251087`.

No API key, inference server, or paid account is needed. Requirements are Python 3.10+, torch, transformers, safetensors, and tokenizers. Windows requires safetensors 0.8+ for its non-mmap loader. Development used packages already installed under Python 3.13. The scripts do not install packages automatically or fall back to cloud execution. If memory is insufficient, mark model scoring unavailable and continue the evidence review.

```text
python scripts/prepare_local_model.py models/tropa-mini
python -B -X utf8 scripts/run_english.py manuscript.txt --language en --explain --out work/local-result.json
```

The downloader retrieves pinned public model files without sending the manuscript. A `.part` file is an incomplete download, not usable weights. Loading uses `local_files_only=True`, `trust_remote_code=False`, and offline settings. Downloaded Python code is not executed. Safetensors are loaded with strict key/shape checks, and initialization on the meta device reduces duplicate weight allocations.

## Runtime protection and supported inputs

The recommended `run_english.py` entry point launches `local_model.py` as a local child process. The actual model worker owns an operating-system file lock, so the lock remains held if only the supervisor dies. Concurrent CLI workers sharing the same temporary directory are rejected. A leftover lock file does not prevent execution when no process holds its lock.

The lower-level `local_model.py` CLI also uses the lock, but `run_english.py` provides abnormal-exit detection and final-result validation. Direct `LocalDetector` library calls do not receive this execution protection.

Independent Windows review observed intermittent native access violations in PyTorch's `torch_cpu.dll`. A later sequential reproduction traced the failure to `safetensors.torch.load_file` and `torch.storage.UntypedStorage.__getitem__` during memory-mapped weight loading, before inference. Version 3.1.2 selects the official `pread` backend on Windows, bypassing that path. Older Windows loaders receive an explicit dependency error rather than a retry through mmap. Other operating systems keep the existing mmap backend.

This is a verified application workaround for the reproduced loading failure, not an upstream library repair or a guarantee of stability in every environment. Low available memory was observed, but its causal role was not established. `pread` allocates tensor storage in process memory, so adequate RAM/pagefile capacity remains necessary. See the [official loading API](https://huggingface.co/docs/safetensors/en/api/torch), [related upstream report](https://github.com/safetensors/safetensors/issues/693), and [release verification](verification.md). The [tested environment](tested-environment.json) records actual package versions; not every allowed combination has been tested.

The supervisor enables Python's fault handler in the worker and validates the exit code, model/input metadata, finite probabilities and their sum, coordinates and token coverage of all windows, and consistency of paragraph-removal measurements. On failure, it writes no final result and returns an error with `authorship_probabilities: null`. It neither overwrites nor reuses an older result. Successful results add `weight_loading_backend` (`pread` on Windows, `mmap` elsewhere); the schema version, four classes, original model hashes, coverage fields, and `execution_guard` remain intact.

Verify that input is actually English. Blank or numeric-only text, Hangul, and predominantly non-Latin text are rejected before inference. The script screen does not distinguish English from French, German, or other Latin-script languages.

## Observed performance limits

Treat this model as an **experimental auxiliary scorer**. In this package's 36-document English pilot, the default threshold achieved 30/36 correct predictions and falsely flagged 3/12 human texts. Two human samples received AI-involvement scores above 0.998 despite being false positives. A high score is therefore not an established probability of authorship. Do not transfer the model card's low-FPR claim to this environment. See the [full comparison and raw results](performance-comparison.md).

## Reading the output

- Single-window input: display all four original model probabilities. If two values are needed, additionally show AI involvement = AI + AI-edited + Humanized, versus Human-only = Human. These are not independently calibrated personal-authorship probabilities.
- Long input: overlapping windows within the 768-token limit cover every token. Show each window's original range, length, and score. Do not provide a whole-document probability. A mean may serve as an evaluation statistic, not a calibrated document probability.
- `--explain`: for a single-window document, delete each original paragraph in turn and measure the score change. The original file remains unchanged. The default limit is 40 paragraphs, and unmeasured counts are reported. Deleting a one-paragraph document leaves empty text, so that measurement is skipped.
- A positive delta means deletion lowered the AI-involvement score. It does not prove AI wrote the paragraph; explain the confounding effects of changed length and context.

## Korean limits and reviewed alternatives

Do not apply this checkpoint to Korean or substantially Korean-mixed documents. A multilingual label alone is not evidence of Korean performance. Korean has language-specific evidence review, supplied-report interpretation, and a separate [bundled classifier](korean-model.md) with calibrated Human/AI estimates. It does not use this English checkpoint.

- [Desklib v1.01](https://huggingface.co/desklib/ai-text-detector-v1.01): its card specifies English; it was not selected as a Korean alternative.
- [Oculus multilingual](https://huggingface.co/danibor/oculus-v2.0-multilingual): Korean is absent from the reviewed support list. The card describes distillation from GPTZero soft labels, which does not establish equal accuracy.
- [Munche](https://huggingface.co/Baragi-AI/Munche-768-AI-Detector): targets Korean genre fiction and has a gated base model and input-length constraints. Its results were not generalized to arbitrary Korean prose.
- [KatFishNet](https://github.com/Shinwoo-Park/katfishnet): Korean linguistic features and public experiments/data are valuable research foundations, not an automatically deployable universal probability model with validation on every new generator and genre. Its paper AUROC is not this skill's accuracy.

Further Korean development requires label provenance, licensing review, author/topic/generation-group splits, and independent tests across modern generators, genres, translation, editing, and humanizers. Translating Korean into English or assigning arbitrary weights to a few features does not establish an improvement.
