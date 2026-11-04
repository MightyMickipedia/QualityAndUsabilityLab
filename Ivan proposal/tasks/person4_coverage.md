# Person 4 - Coverage (informativeness) errors

Name: Mick (MickiPedia)
Source: APPLS, EMNLP 2024, Table 2 (informativeness), https://aclanthology.org/2024.emnlp-main.519.pdf
Use summaries with Content Coverage (`d6`) = 7.

## Task
For each of the 4 types below: check the definition against the paper, then make **2 examples** from real summaries (one error each).
Paper definitions and examples are already in `documentation/Taxonomy.md`, Part 2. The German explanations are done by Ivan (Person 5).

## Delete sentences / Sätze löschen
- Definition (paper): Remove an IMPORTANT sentence (key fact), not a trivial one. (check against Table 2)

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why it is important / off-topic: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why: ______
- Severity guess (low / medium / high): ______

## Add out-of-domain sentence / Themenfremden Satz hinzufügen
- Definition (paper): Add a sentence from a completely different topic (hallucination). (check against Table 2)

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why it is important / off-topic: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why: ______
- Severity guess (low / medium / high): ______

## Add in-domain sentence / Themennahen Satz hinzufügen
- Definition (paper): Add a plausible sentence on the same topic that is not in the article. (check against Table 2)

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why it is important / off-topic: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why: ______
- Severity guess (low / medium / high): ______

## Add definition / Definition hinzufügen
- Definition (paper): Add unnecessary background/definition of a term. (check against Table 2)

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why it is important / off-topic: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- Deleted/added sentence and why: ______
- Severity guess (low / medium / high): ______

## Done when
- [x] 4 types x 2 examples (`APPLS_errors/human_labeled.csv`)
- [ ] all examples added to `examples/examples.csv`
