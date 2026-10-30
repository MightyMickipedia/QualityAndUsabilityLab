# Person 2 - Faithfulness errors: semantic frame errors

Name: ______
Source: FRANK, Pagnoni et al. 2021, https://arxiv.org/pdf/2104.13346 (Section 2 / Table 1)

## Task
For each type below: check the definition against the paper, write a German explanation, then make 2 examples from real summaries (one error each).

## Predicate Error (PredE) / Prädikatfehler
- Definition (paper): The main verb/predicate is inconsistent with the article (wrong action or state).
- Erklärung (DE): ______
- Illustration hint (not a real example): Die Stadt *kürzt* das Budget -> Die Stadt *verdoppelt* das Budget

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

## Entity Error (EntE) / Entitätsfehler
- Definition (paper): A subject/object of the predicate is wrong (person, place, organisation, number, attribute).
- Erklärung (DE): ______
- Illustration hint (not a real example): Mitte, Friedrichshain-Kreuzberg und *Neukölln* -> ... *Charlottenburg*; 50 km -> 150 km

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

## Circumstance Error (CircE) / Umstandsfehler
- Definition (paper): Wrong time, place, manner or condition around the event.
- Erklärung (DE): ______
- Illustration hint (not a real example): Bauarbeiten beginnen *im Frühjahr 2027* -> *im Herbst 2026*

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
