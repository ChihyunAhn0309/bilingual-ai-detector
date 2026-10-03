# Source and third-party notices

This repository distinguishes its analysis code and model artifacts from the datasets, papers, products and optional weights it references. Publication does not grant rights to third-party material. No project-wide open-source license has been selected for this repository.

## Korean training sources

- [KatFishNet](https://github.com/Shinwoo-Park/katfishnet), revision `5e3dc89cc31a029be38fb2d871476b0aff7b793c`, associated with the [ACL 2025 paper](https://aclanthology.org/2025.acl-long.1030/).
- [Detect_AI_Generated_Korean_Text](https://github.com/gygUnig/Detect_AI_Generated_Korean_Text), revision `b822d8e807298797d45003cc4171f554811cb01c`.

Raw source texts are not redistributed here. The Korean JSON model was trained locally using those public research artifacts; it is a separate character classifier, not the KatFishNet implementation. Source URLs, exact revisions and SHA256 hashes are in [korean-source-manifest.json](references/korean-source-manifest.json). Public access is not a blanket reuse license. Consult the upstream data owners and applicable terms before uses that need additional permission. This project does not assert a permissive license for the research data or unrestricted commercial rights for the trained model.

## Optional English weights

[wasitaigeneratedcom/ai-text-detector-small](https://huggingface.co/wasitaigeneratedcom/ai-text-detector-small/tree/f1795c86806e6838d4afa33d0b1427f8430c9615), revision `f1795c86806e6838d4afa33d0b1427f8430c9615`, is described by its upstream model card as Apache-2.0. The large checkpoint is **not included** in this repository. The separate downloader retrieves upstream README and NOTICE alongside the pinned model files. Preserve upstream notices and observe its license when using or redistributing the weights. [Details and limits](references/free-local-model.md)

## English evaluation sources

The saved benchmark uses [jaeholee-brown/ai-text-detectors](https://github.com/jaeholee-brown/ai-text-detectors/tree/3f5ed200e212ef5ca957b6f5675d99ed29ff3c3c), described in the linked Epoch AI study. This repository records aggregate results, sample identities, text hashes and scores, not the original literary passages. No commercial detector service was called to create the saved comparison. Product names are descriptive references; no affiliation or endorsement is claimed.

## Dependencies and examples

Optional Python dependencies retain their upstream licenses. The Korean inference path uses the Python standard library. Texts under `examples/` are synthetic functionality demonstrations and are not used as evidence of accuracy or human authorship.
