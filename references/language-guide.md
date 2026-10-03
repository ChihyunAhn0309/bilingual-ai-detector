# Korean and English analysis guide

These review procedures are design principles for the skill. Do not turn group differences observed in research into an individual document's probability or an arbitrary fixed threshold.

## Korean

Analyze the Korean original. Testing an English translation does not establish the original's authorship. Distinguish Hangul syllables, whitespace-delimited units, morphemes, and model tokens. Do not convert an English 300-word requirement into a Korean 300-character requirement.

| Observation | What to examine | Plausible human explanation |
| --- | --- | --- |
| Spacing and punctuation | Spacing choices in comparable constructions, comma placement and function, commas after connective endings | Copyediting, institutional style, translation from English, lists, or quotations |
| Part-of-speech combinations | Measure POS n-gram diversity only after actually running a morphological analyzer | Specialist vocabulary, analyzer errors, or length differences |
| Endings and subjects | Whether honorifics, tense, subjects, and endings fit the purpose | Consistent formal register is normal in official and academic prose |
| Nominalization and translation-like phrasing | Whether constructions such as “~에 대해” or “~을 통해” and chains of abstract nouns obscure content | Legal/academic conventions, translation, or editorial style |
| Repeated structure | Openings, enumerations, or conclusions repeated without a content-based reason | Assignment format, report templates, or taught essay structure |

KatFishNet is an actual classification approach using Korean spacing, POS combinations, and punctuation. Counting commas is not a reproduction. Its Table 3 value of 94.88 is mean AUROC × 100 for the essay punctuation model, distinct from poetry 73.10 and abstracts 75.62. These are not this skill's accuracy figures. [Paper, Table 3](https://aclanthology.org/2025.acl-long.1030.pdf)

The local profiler does not perform morphological analysis. `surface_type_token_ratio` measures diversity of whitespace-delimited surface forms, not POS diversity or information entropy. It does not count spacing errors or calculate a supposedly normal comma rate.

## English

Assess the original language, genre, and intended audience. Repeated transitions, vague attribution, inflated significance, uniform structure, and redundant restatement can justify editorial observations. They cannot by themselves identify the authoring process.

Do not treat simple vocabulary, low sentence-length variation, formulaic exam answers, or careful grammar as proof of AI. Consider language learning, professional editing, accessibility choices, and institutional templates without guessing which applies to the author. A 2023 study documented false-positive bias on its non-native English samples; those rates do not describe every current product. [Liang et al.](https://arxiv.org/abs/2304.02819)

Treat familiar “AI words” and punctuation as weak, context-dependent observations. Examine clusters in relation to the passage's purpose. A specific example, emotional anecdote, typo, or fragmented sentence can also be generated. Do not ask an LLM whether it remembers generating a passage; conversational recognition is not provenance.

## Mixed languages, short texts, and transformations

- English product names inside Korean sentences do not make a separate English document. Review substantial independent English passages separately while preserving context and boundaries.
- Hangul/Latin proportions describe character composition. Latin script does not establish English; verify the language.
- Short texts provide limited information. Apply the actual tool's requirements rather than inventing a universal minimum. Length alone does not guarantee reliability.
- Quotations, code, lists, tables, poetry, and OCR errors may fall outside a prose model's scope. Paragraph-level probabilities also require validation.
- AI correction of a human draft, human editing of an AI draft, translation, and collaborative writing are different hypotheses. Text alone does not establish the direction.
- Humanizing can reduce surface signals without changing writing history. Conversely, formal human prose can contain many such signals without being AI-generated.
- Zero-width characters, BOMs, combining marks, and directional controls can have legitimate purposes. Report observed codepoints and locations, not an “AI watermark.” Statistical watermark verification requires the relevant generation scheme, detector, keys/tokenizer, and other conditions.

## Evidence tables

Use: `Location | Exact excerpt | Observation | Plausible human explanation | Limit on the inference`.

Specify 1-based line numbers or 0-based Python Unicode codepoint offsets. Do not confuse them with UTF-16 positions. Put known writing history in a separate table: supplied record, verified scope, and what remains unverified. A hash computed after receipt establishes input identity, not the author or creation time.

## Separate the Korean model from language observations

The Korean classifier learns character patterns described in its [model card](korean-model.md). It does not turn comma counts or formal endings into probabilities through a hand-written rule sum. Run it on the Korean original and retain plausible human alternatives. Separate learned feature contributions, paragraph-removal sensitivity, and the analyst's stylistic observations.
