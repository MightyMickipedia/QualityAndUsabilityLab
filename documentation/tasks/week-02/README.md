# Week 2 tasks (04.11. - 11.11.2026)

**Goal of the week:** automatic error injection. Scripts and prompts that take a "perfect" summary and return the same summary with one error of a given type and severity.

| # | Task | File |
|---|---|---|
| 1 | Data v2: summaries with 2 or 3 annotators, clean text, sentence count | `task1_data.md` |
| 2 | Injection: semantic frame errors (PredE, EntE, CircE) | `task2_semantic_frame.md` |
| 3 | Injection: discourse and verifiability errors (CorefE, LinkE, OutE, GramE) | `task3_discourse.md` |
| 4 | Injection: coverage errors (all 4 APPLS types) | `task4_coverage.md` |
| 5 | Shared format and runner, severity guide, last semester's scripts, slides | `task5_pipeline.md` |

## Rules for everyone
- One error per output, of the requested type and severity.
- Python scripts are not a must for tasks 2-4. LLM prompts are probably easier for most types, see for yourself.
- Save outputs in the shared format from task 5 (one JSON line per modified summary). The format and the runner are ready in `scripts/injection/` (README there). The runner is optional: it saves you writing your own API code. Until Friday, you can test prompts by hand in any chat model.
- Prompts go in `scripts/injection/prompts/`, scripts (if any) in `scripts/injection/`, outputs in `data/injected/`.
- Test: in your task, take the same 10 summaries (mix short and long) and make one output per error type for each, so 10 per type (task 2: 30, tasks 3 and 4: 40 each).
- Use the few-shot examples from `data/examples/examples.csv` for your types.
- Post in the chat which task you take and when it's ready. Results are due by Tue 10.11. evening, so the slides are ready for Wed.
- Research questions: Ivan writes a draft by Mon 09.11. and posts it in the chat. Give feedback if you don't agree.

## Dependencies
- Tasks 2-4 use the current `data/perfect_faithfulness.jsonl` / `data/perfect_coverage.jsonl` (3 annotators). Task 1's new files (`*_v2.jsonl`) are for the next steps, not this week's injection.
- The output format and the runner are ready (`scripts/injection/README.md`). The severity scale is in `documentation/Taxonomy.md` (section Severity).
- Last semester's scripts are in `scripts/legacy/`. The README there maps their operations to our error types.

## Meeting with Neha, 04.11.2026

- **Feedback:** the presentation is good, and so is the taxonomy file.
- **Material:** from her side there is only one presentation, the kickoff slides. They contain everything we need to know.
- **Direction:** we follow the outline in the kickoff slides, but it's not set in stone. We can partly choose our own direction.
- **This week's task: an automatic error-injection pipeline.** We develop Python scripts that inject errors. That matches the kickoff timeline for 4–11 Nov: *"Inject errors – factual errors by types (use [FRANK]) and coverage errors like deletion of content"*.
- **Prompts:** write 2–3 prompts, each for a group of error types, and make them work for long summaries too, not only short ones.
- **Last semester's scripts:** she shared two in the meeting chat. One uses an LLM, the other is pure Python and swaps cities, organisations and countries. We should map them to our error types.
- **Severity:** high / medium / low.
- **Data fixes:** repair the umlaut encoding and remove the HTML tags (`<br/>`, `<strong>`). Data with 2 or 3 annotators may be combined.
- **Next week:** finalise the research questions.
- **Mick** missed a mandatory meeting, and Neha will contact him.

Kickoff slides: `documentation/intro_kickoff.pdf`. Error types and examples: `documentation/Taxonomy.md`, `data/examples/examples.csv`.
