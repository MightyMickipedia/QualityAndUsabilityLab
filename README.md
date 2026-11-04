# Quality and Usability Lab: LLM judges on German news summaries

Goal: test whether LLM judges notice deliberately injected errors in German news summaries.

## Repository layout

| Folder | What's in it |
|---|---|
| `data/` | all data: the original dataset (`annotated_news_summaries/`), the "perfect" summaries (`perfect_*.jsonl`, `sample_*.md`), the error examples (`examples/examples.csv`, `APPLS_errors/`), injected summaries (`injected/`) |
| `scripts/` | code: `select_perfect.py` (see `data/README.md`), `injection/` (runner and prompts for error injection), `legacy/` (last semester's scripts, mapped to our error types) |
| `documentation/` | everything else: the error taxonomy (`Taxonomy.md`), the kickoff slides (`intro_kickoff.pdf`), weekly tasks (`tasks/`), weekly slides (`presentations/`), week 1 task files and templates (`Ivan proposal/`), the to-do list (`Todo.txt`) |

Start with `documentation/Taxonomy.md`.
