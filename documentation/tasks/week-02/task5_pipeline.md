# Task 5 - Shared format and runner, severity guide, last semester's scripts, slides

**Goal:** the common pieces that tasks 2-4 build on, so we end up with one set of results instead of four incompatible ones. A-D are done. The slides (E) follow when everyone's results are in.

## A. Shared output format - done
In `scripts/injection/README.md`: one JSON line per modified summary, same fields for everyone (`id`, `item_id`, `model`, `dimension`, `error_type`, `severity`, `method`, `prompt`, `original_summary`, `modified_summary`, `change`, optional `warnings`).

## B. Runner - done
`scripts/injection/run.py`, optional for tasks 2-4. It loads the summaries and removes the tags, fills a prompt template (`{article}`, `{summary}`, `{error_type}`, `{severity}`, `{examples}`), calls the LLM and saves in the format above. Standard library only, and it works with any OpenAI-compatible API (OpenRouter by default). `--dry_run` shows the filled prompt without an API call. Example prompt: `scripts/injection/prompts/example.md`.

- [ ] Still open: which model we use for injection. Ask Neha whether paid/closed models are fine. Last semester's `perturb_ai.py` used Claude Sonnet 4.

## C. Last semester's scripts - done
The mapping is in `scripts/legacy/README.md` ("What we can reuse"). In short:
- reusable: number and year changes (EntE / CircE), city / country / organisation swaps (CircE / EntE, organisation list needs same-group swaps), word shuffling (GramE)
- partly: random sentence deletion (delete_sentence, but not an important sentence), preposition swaps (often flip the meaning, so PredE / LinkE rather than grammar)
- not covered: PredE, CorefE, LinkE, OutE and three of the four coverage types
- they aim at a score level and mix several errors. We want one error of one type.

## D. Severity guide - done
The table (high / medium / low, one example each) is in `documentation/Taxonomy.md`, section Severity. The same three definitions are in `scripts/injection/prompts/example.md`, so the model knows what the level means.

## E. Weekly slides (Tue 10.11. evening)
`documentation/presentations/week-02/content.js`: done this week, example outputs, Ivan's research-question draft, questions for Neha.

## Done when
- [x] format (A) and runner (B)
- [x] mapping table (C) in `scripts/legacy/README.md`
- [x] severity guide (D) in Taxonomy.md (section Severity), also in `scripts/injection/prompts/example.md`
- [ ] week 2 slides ready for Wed
