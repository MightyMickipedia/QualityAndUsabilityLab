# Task 3 - Inject discourse and verifiability errors (CorefE, LinkE, OutE, GramE)

**Goal:** get CorefE, LinkE, OutE and GramE into "perfect" summaries automatically, one error per output.

Input: `data/perfect_faithfulness.jsonl` (the current file: 100 summaries, 3 annotators, all gave 7). Some texts still contain `<br/>` / `<strong>` tags, which you can just remove. Few-shot examples: `data/examples/examples.csv` (F-CorefE, F-LinkE, F-OutE, F-GramE).

## How
Up to you. Some thoughts:
- **LLM prompts (1-2):** probably the easiest way. CorefE and LinkE are both about how sentences connect (pronouns, "nachdem/bevor/weil"), and OutE and GramE are different, so two prompts could make sense. Give the prompt the article, the summary, the error type and the severity, plus 1-2 examples from `examples.csv`. Ask for the modified summary and a one-line description of the change.
- **Python:** not a must. Last semester's `scripts/legacy/perturb.py` swaps articles and prepositions and breaks word order, which might help for GramE.
- **OutE:** the added fact should really be missing from the article. Worth a quick check, e.g. whether the new words appear in the article.
- **GramE:** one broken construction is probably enough. FRANK (p. 3) says minor grammar mistakes don't count.
- Severity high / medium / low: see the table in `documentation/Taxonomy.md` (section Severity)

## Test
Pick 10 summaries (mix short and long ones) and make one output per type for each: **4 types × 10 = 40 outputs**. Check them by hand: right type? only one error? still fluent German?

Severities: a mix is probably more useful than only one level, e.g. per type 4 × high, 3 × medium, 3 × low. With the runner that's three runs per type (one per severity), each with its part of your 10 summaries via `--items`.

## Deliverables (by Tue 10.11.)
- prompt files in `scripts/injection/prompts/` (and scripts in `scripts/injection/`, if you write any)
- `data/injected/discourse_test.jsonl` (40 outputs, format from task 5) (with the runner: add `--out data/injected/discourse_test.jsonl`, every run appends to that file)

