# Task 2 - Inject semantic frame errors (PredE, EntE, CircE)

**Goal:** get PredE, EntE and CircE into "perfect" summaries automatically.

Input: `data/perfect_faithfulness.jsonl` (the current file: 100 summaries, 3 annotators, all gave 7). Some texts still contain `<br/>` / `<strong>` tags, which you can just remove. Few-shot examples: `data/examples/examples.csv` (F-PredE, F-EntE, F-CircE).

## How
Up to you. Some thoughts:
- **LLM prompts (1-2):** probably the easiest way for all three types. One prompt for all three may work, since they're similar (one part of a sentence gets swapped). Give the prompt the article, the summary, the error type and the severity, plus 1-2 examples from `examples.csv`. Ask for the modified summary and a one-line description of the change.
- **Python:** not a must. For EntE (party, person, organisation, number) and CircE (place, date) swaps with word lists can work. Last semester's `scripts/legacy/perturb.py` already swaps cities, organisations and countries. For PredE an LLM is probably the better option. Changing a verb's meaning with rules is hard.
- Severity high / medium / low: see the table in `documentation/Taxonomy.md` (section Severity)
- From test runs (EntE, free Nemotron model on OpenRouter, see `data/injected/README.md`):
  - In one test the model swapped „Barcelona“ → „Madrid“ and called it EntE. By FRANK a place is CircE. It's probably worth saying in the prompt that places and times count as CircE, not EntE.
  - It also tends to remove stray quotation marks around a summary, a small second change. Maybe tell it to change nothing else, punctuation and quotation marks included.

## Test
Pick 10 summaries (mix short and long ones) and make one output per type for each: **3 types × 10 = 30 outputs**. Check them by hand: right type? only one error? still fluent German?

Severities: a mix is probably more useful than only one level, e.g. per type 4 × high, 3 × medium, 3 × low. With the runner that's three runs per type (one per severity), each with its part of your 10 summaries via `--items`.

## Deliverables (by Tue 10.11.)
- prompt files in `scripts/injection/prompts/` (and scripts in `scripts/injection/`, if you write any)
- `data/injected/semantic_frame_test.jsonl` (30 outputs, format from task 5) (with the runner: add `--out data/injected/semantic_frame_test.jsonl`, every run appends to that file)

