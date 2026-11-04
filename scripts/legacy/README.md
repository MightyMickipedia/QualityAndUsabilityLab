# Last semester's perturbation scripts

Shared by Neha in the meeting on 04.11.2026. From last semester's advanced project, on the same dataset. Copied here unchanged.

| Script | How it works | Dimensions |
|---|---|---|
| `perturb.py` | Rule-based (spaCy sentencizer, regex, word lists): changes numbers and years, swaps cities / organisations / countries, adds contradictions, deletes or duplicates sentences, swaps articles and prepositions, drops auxiliaries, breaks word order | faithfulness, non-redundancy, grammaticality |
| `perturb_ai.py` | Same CLI and output format, but an LLM rewrites the summary (Anthropic API, `claude-sonnet-4-20250514`), with the 7-point rubric pasted into the prompt | faithfulness, non-redundancy, grammaticality |

Both aim at a **target score** (1-5 on the 1-7 rubric, 20 % each) rather than at one error type, and can put several errors into one summary. Input files are `adv_proj_*.jsonl` from last semester; they are not in this repo.
