# Review of existing detector skills and humanizers

Reviewed on 2026-10-03. We read the original repositories/instructions of these six public skills. We did not install them or execute their commands. This comparison is independently written rather than copied from their instructions. Popularity, stars, and unsupported numeric claims are not evidence of detection performance.

| Public skill | Actual role | Useful design element | Inference not adopted |
| --- | --- | --- | --- |
| [Valpep/wiki-ai-detector](https://github.com/Valpep/wiki-ai-detector/blob/main/SKILL.md) | Style checklist covering vocabulary density, inflated meaning, and formulaic structure | Context and repeated structure matter more than isolated words | Treating fixed vocabulary counts or structures as strong authorship evidence |
| [hannsxpeter/authenticity-check](https://github.com/hannsxpeter/authenticity-check/blob/main/SKILL.md) | A 0–100 naturalness assessment with passage reasons and separate Unicode observations | Exact locations, alternatives, character-code checks, and separation of analysis from editing | Converting naturalness to authorship probability or style density to an established AI-first/Mixed history |
| [mattc95/ai-detector-skill](https://github.com/mattc95/ai-detector-skill/blob/main/SKILL.md) | Multi-class classification through the GPTHumanizer API | Distinguishing returned probabilities, errors, and incomplete execution | Assuming the skill bundles a trained model or can produce the same probabilities without its API |
| [lynote-ai/ai-text-detector](https://github.com/lynote-ai/ai-text-detector/blob/main/SKILL.md) | Local CLI execution followed by score, confidence, signals, and caveats | Reproducible execution and evidence-oriented reporting | Assuming its returned score is a calibrated Korean-authorship probability |
| [aragossa/ai-tell-detector](https://github.com/aragossa/ai-tell-detector/blob/main/en/ai-tell-detector/SKILL.md) | English/Russian style-pattern review | Observations anchored to original lines and limits of a single score | Extending English/Russian rules to validated Korean performance |
| [resemble-ai/detect-skill](https://github.com/resemble-ai/detect-skill/blob/master/SKILL.md) | Media analysis and a separate text-detection API workflow | Interpreting completed responses and separating predicted-class confidence from AI probability | Applying media scores to text or citing vendor metrics as independent validation |

Resemble's text confidence is described as confidence in the predicted class. Avoid reversing `human, confidence=0.97` into AI 97%. Do not automatically manufacture the opposite class probability without checking the API definition. Korean applicability also needs separate confirmation.

## Lessons from local humanizer skills

Relevant portions of `bilingual-humanizer`, `humanizer`, `humanizer-ko`, `humanizer-kr`, and `korean-humanizer` were reviewed in the development environment. They provide editorial guidance about natural phrasing, translation-like syntax, repetition, and formulaic structure. Research citations inside editing instructions do not validate those instructions as detectors.

- Preserve the distinction among writing history, detector score, and naturalness in `bilingual-humanizer`. Original sources were rechecked; its prior examples were not reused as this skill's benchmark.
- Use Korean endings, particles, nominalization, and spacing as genre-sensitive review questions. Expressions such as “다양한” and “해당,” commas, or particular endings are not banned words or authorship proof.
- Describing KatFishNet's 94.88 as accuracy across all Korean documents conflicts with Table 3 of the paper. The actual metric and genre are recorded in the [research review](research-methods.md).
- Naturalizing text does not erase its generation history. The style patterns a humanizer edits and the authorship process a detector estimates are different targets.

## Design conclusions

Style checklists, trained classifiers, external APIs, and process evidence are not interchangeable. Do not alter percentages to praise an edit or intensify suspicion. The skill's contribution is a consistent workflow for **language-specific observations, actual measurement, score interpretation, and error checks**. Its prompt does not itself train a new high-performance detector.
