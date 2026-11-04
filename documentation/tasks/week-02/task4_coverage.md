# Task 4 - Inject coverage errors (all 4 APPLS types)

**Goal:** get the four coverage errors into "perfect" summaries automatically, one error per output.

Input: `data/perfect_coverage.jsonl` (the current file: 66 summaries, 3 annotators, all gave 7). Some texts still contain `<br/>` / `<strong>` tags, which you can just remove. Few-shot examples: `data/examples/examples.csv` (C-DEL, C-OUT, C-IN, C-DEF) and `data/APPLS_errors/human_labeled.csv`.

## How
Up to you. Some thoughts:
- **Delete sentences:** easy in Python, just split the summary into sentences and remove one. The harder part is picking an important one (Neha: delete important sentences, not unimportant ones). An LLM could pick it.
- **Add out-of-domain:** also easy in Python, e.g. a sentence from a summary on a completely different topic.
- **Add in-domain:** a sentence on the same topic that isn't in the article. Doing both ways would be interesting: (a) a real sentence from another article on the same event, as APPLS does, (b) one invented by an LLM, like C-IN-1/2. It's still an open question for Neha which way we go.
- **Add definitions:** probably easiest with an LLM: explain a term from the summary that doesn't need explaining.
- **LLM prompts (1-2)** for the parts where you use an LLM. Python isn't a must either.
- Severity high / medium / low: see the table in `documentation/Taxonomy.md` (section Severity)

## Test
Pick 10 summaries (mix short and long ones) and make one output per type for each: **4 types × 10 = 40 outputs**. Check them by hand: right type? only one error? still fluent German?

Severities: a mix is probably more useful than only one level, e.g. per type 4 × high, 3 × medium, 3 × low. With the runner that's three runs per type (one per severity), each with its part of your 10 summaries via `--items`.

## Deliverables (by Tue 10.11.)
- prompt files in `scripts/injection/prompts/` (and scripts in `scripts/injection/`, if you write any)
- `data/injected/coverage_test.jsonl` (40 outputs, format from task 5) (with the runner: add `--out data/injected/coverage_test.jsonl`, every run appends to that file)

