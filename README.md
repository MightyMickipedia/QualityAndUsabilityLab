# Quality and Usability Lab: LLM judges on German news summaries

Goal: test whether LLM judges notice deliberately injected errors in German news summaries.

## Repository layout

| Folder | What's in it |
|---|---|
| `data/` | all data: the original dataset (`annotated_news_summaries/`), the "perfect" summaries (`perfect_*.jsonl`, `sample_*.md`), the error examples (`examples/examples.csv`, `APPLS_errors/`) |
| `scripts/` | code, e.g. `select_perfect.py` (see `data/README.md`) |
| `documentation/` | everything else: the error taxonomy (`Taxonomy.md`), weekly slides (`presentations/`), task files and templates (`Ivan proposal/`), the to-do list (`Todo.txt`) |

Start with `documentation/Taxonomy.md`.
