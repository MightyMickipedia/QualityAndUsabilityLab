# Injected summaries

Outputs of the error injection, one `.jsonl` per run or per task. Format: `scripts/injection/README.md`.

## example_EntE_high.jsonl - test run (04.11.2026)

- Ivan ran `scripts/injection/run.py` with `nvidia/nemotron-3.5-super-vl:free` through OpenRouter (free model). Everything worked.
- Command: `run.py --prompt scripts/injection/prompts/example.md --error_type EntE --severity high --n 3` (seed 42)
- Results: 3 outputs, each with one content change, and the model refers to the severity definition ("Hauptaussage").
  - „FDP“ → „SPD“: clean EntE
  - „spanische“ → „deutsche“: EntE (attribute of the restaurant)
  - „E-Auto-Batterien“ → „Dieselautos“: EntE. The model also removed stray quotation marks around the summary, a small second change (task 1 removes those quotes from the data)
