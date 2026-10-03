# Bilingual AI Detector v3.1.0 — public independent-review summary

Review date: 2026-10-03. **Software defects R1/R3/R4/R7/R8 reproduced during review were fixed and retested on the final frozen snapshot. No reproducible release-blocking software defect remained on the examined paths.**

This is the English translation published with documentation version 3.1.1. The findings and measurements are unchanged. The [original review](https://github.com/ChihyunAhn0309/bilingual-ai-detector/blob/54b50bb4c5c08f570c61b9b504b86bc7bc2ad609/references/review-public.md) remains available in the 3.1.0 commit. Translation is not a new independent execution of the review.

The root cause of intermittent Windows/PyTorch native crashes, R6, remains unknown. Failure handling and worker-owned locking were verified; this does not establish that the underlying crash was fixed or that every environment is stable. The review is neither legal rights clearance nor a guarantee of universal accuracy.

## Frozen snapshot and public manifests

`reviewed-files-public.json` records SHA256 hashes and sizes for **44 repository-relative paths**, excluding three pyc/cache files. Its file-list digest is `e689e65855307706ae900feeab299d606186e022515d760d849f5c8a141a18e5`.

Korean model SHA256: `f3048088269f293b5f54b131a26571eefcdb9ffd57d86acfd41b4d8d71d41e1f`.

The live package matched that snapshot at the last review check. Later review artifacts, manifests, README links, and verification-history additions were outside the source manifest. The English documentation update also changes document/skill-metadata hashes while leaving executable code, model weights, and evaluation data unchanged. The source manifest remains a historical record; it has not been rewritten to imply a fresh review of translated files.

`review-artifacts-public.json` records the current English review-document hashes and identifies the original review commit. Do not automatically apply this review to later code changes.

## Software checks and findings

| Check or finding | Final reviewed result |
| --- | --- |
| Existing unit tests | 56 passed; this is not an accuracy measurement |
| Independent subprocess checks | 16 matched their expected outcomes |
| Independent result-schema checks | 20 matched their expected outcomes |
| Real checkpoint through the supervisor | Succeeded; maximum change in the four class scores was 0; three paragraph deletions measured |
| R1: English report lost uncalibrated/experimental/false-positive warnings | Warning retention verified |
| R3: missing UTC measurement time | Preserved in the original and attached results |
| R4: clearly non-English or empty input | Rejected before inference; script proportions are not language identification |
| R7: incomplete or invalid probability results | Rejected before final output; null error and no final result |
| R8: worker survives supervisor termination | Worker retained its lock and rejected a new CLI job |
| R6: native crash | Root cause unresolved; only failure handling and serialized execution were verified |

General worker errors, missing results, JSON/hash errors, changed input, and results left before an error exit were rejected. Existing outputs, source text, and an output created during execution were not overwritten. Normal lock contention and reacquisition after release also passed.

A controlled Windows worker terminated through `ExitProcess(0xC0000005)` produced worker exit 3221225477; the supervisor returned exit 2 with null probabilities and no final result. This was an injected status-code test, not a new reproduction or root-cause repair of PyTorch's crash.

Lifecycle/failure checks ran the frozen `local_model.main` and `runtime_guard` in real subprocesses, replacing only the expensive `LocalDetector` in memory. Actual model inference was tested separately and succeeded. Result checks covered model/revision/hash metadata, UTC, class names, finite values and sums, original-text coordinates and token coverage, single/multi-window probability rules, and paragraph-removal deltas. These checks are not a signature authenticating arbitrary edited output or its semantic correctness.

Inference with network audit guards in both parent and worker attempted no socket calls. No commercial detector API, paid service, or cloud GPU was used. CLI workers sharing the same temporary directory participate in locking; direct `LocalDetector` library calls do not. The review did not test every allowed dependency combination or every operating system.

## Performance reproduction and interpretation

These are independent reruns of existing public evaluation data, not a newly collected provenance-confirmed population. Synthetic functionality fixtures were excluded from accuracy denominators.

| Korean evaluation | Documents | Accuracy | Human false positives |
| --- | ---: | ---: | ---: |
| Full topic holdout | 1,846 | 97.5081% | 8/885 |
| Essays | 1,714 | 98.1914% | 6/856 |
| Abstracts | 37 | 91.8919% | 1/10 |
| Poetry | 95 | 87.3684% | 1/19 |
| Transfer with shared topics | 752 | 97.2074% | 1/376 |

Rescoring all 2,598 documents differed from saved scores by less than 1.45e-15. Holdout AUROC was 0.9983468256, Brier 0.0184938276, and ECE10 0.0170381651. Checks covered six source-file hashes, all retained 12,844 text hashes and labels, and absence of group/normalized-exact-text overlap across the primary splits. They do not prove complete separation of hidden authors or semantically similar documents.

Repeating Korean candidate training, selection, separate calibration, and evaluation reproduced the weights, split manifest, and test predictions byte for byte. The calibration's 50% class prior and genre balancing are not estimates of deployment prevalence. Essays dominate the evaluation, while human abstract/poetry subsets are small.

Rerunning the 36-document English pilot produced exactly the saved scores. Default-threshold accuracy was 30/36 (83.33%), with 3/12 human false positives. The model-card threshold yielded 28/36 and 2/12 human false positives. Archived GPTZero verdicts on the same samples scored 35/36; no commercial service was called again.

The final implementation corrections affected CLI validation and locking. AST comparison found `LocalDetector`, `windows`, and `validate_english_input` unchanged from the performance-reproduction snapshot; only `main` changed. Korean weights also remained identical. Consequently, later checks targeted changed execution paths and a real input rather than rerunning Korean training and the full English pilot after every patch.

These numbers do not certify an individual's writing history. The English checkpoint remains an independently uncalibrated experimental scorer. Paragraph-removal deltas are not paragraph-authorship probabilities. General performance on new genres, generators, or humanizers, a Korean advantage over GPTZero, and perfect detection were not established. The agent using the skill supplies the full natural-language interpretation and counterexplanations.

## Publication scope and privacy

The license scope of upstream datasets was not independently cleared. Absence of a license file alone does not establish an automatic prohibition on publishing independently trained parameters, and no specific mandatory-removal violation was identified. Preserve the notices that raw data are not redistributed and no project-wide open-source license is granted. This review does not grant rights; public access and unrestricted reuse are different.

This summary, `review-public.json`, `reviewed-files-public.json`, and `review-artifacts-public.json` contain no private local filesystem paths, original test passages, or private logs. Public source-repository links identify the published project. Detailed local audit records, raw-data caches, and native-crash logs are excluded from the public package.
