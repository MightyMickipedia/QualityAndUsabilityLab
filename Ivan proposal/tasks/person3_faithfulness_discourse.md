# Person 3 - Faithfulness errors: discourse and verifiability errors

Name: ______
Source: FRANK, Pagnoni et al. 2021, https://arxiv.org/pdf/2104.13346 (Section 2 / Table 1)

## Task
For each type below: check the definition against the paper, write a German explanation, then make 2 examples from real summaries (one error each).

## Coreference Error (CorefE) / Koreferenzfehler
- Definition (paper): A pronoun or reference points to the wrong or a non-existent entity.
- Erklärung (DE): ______
- Illustration hint (not a real example): *Sie* (= Umweltverbände) begrüßen ... -> pronoun now refers to the Geschäftsleute

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

## Discourse Link Error (LinkE) / Diskursverknüpfungsfehler
- Definition (paper): Wrong relation between statements: cause/effect or temporal order (incl. our temporal errors).
- Erklärung (DE): ______
- Illustration hint (not a real example): *Weil* es weniger Brände gab, sank die Zerstörung -> reversed cause; or swapped order of events

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

## Out of Article Error (OutE) / Nicht-im-Artikel-Fehler
- Definition (paper): The summary contains information that cannot be verified from the article.
- Erklärung (DE): ______
- Illustration hint (not a real example): adding: *Der Senat hat den Plan einstimmig beschlossen.*

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

## Grammatical Error (GramE) / Grammatikfehler
- Definition (paper): The sentence is so ungrammatical that its meaning is unclear or misleading.
- Erklärung (DE): ______
- Illustration hint (not a real example): broken word order/case that changes who does what

### Example 1
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

### Example 2
- item_id / model: ______
- Original: ______
- Modified: ______
- What changed: ______
- Severity guess (low / medium / high): ______

## Done when
- [ ] every type has German explanation + 2 examples
- [ ] all examples added to `examples/examples.csv`
