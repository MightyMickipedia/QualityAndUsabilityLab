# Last semester's perturbation scripts

Shared by Neha in the meeting on 04.11.2026. From last semester's advanced project, on the same dataset. Copied here unchanged.

| Script | How it works | Dimensions |
|---|---|---|
| `perturb.py` | Rule-based (spaCy sentencizer, regex, word lists): changes numbers and years, swaps cities / organisations / countries, adds contradictions, deletes or duplicates sentences, swaps articles and prepositions, drops auxiliaries, breaks word order | faithfulness, non-redundancy, grammaticality |
| `perturb_ai.py` | Same CLI and output format, but an LLM rewrites the summary (Anthropic API, `claude-sonnet-4-20250514`), with the 7-point rubric pasted into the prompt | faithfulness, non-redundancy, grammaticality |

Both aim at a **target score** (1-5 on the 1-7 rubric, 20 % each) rather than at one error type, and can put several errors into one summary. Input files are `adv_proj_*.jsonl` from last semester; they are not in this repo.

## What we can reuse

They aim at a score level and mix several errors per summary. We want one error of one type, so use single functions.

| Function in `perturb.py` | Our type | Reusable? |
|---|---|---|
| `_perturb_year` (years) | CircE | yes |
| `_perturb_integer`, `_perturb_decimal`, `_perturb_percent`, `_perturb_large_num` (numbers) | EntE | yes |
| `_swap_city`, `_swap_country` | CircE (place), sometimes EntE | yes, but only cities/countries on its lists |
| `_swap_org` | EntE | partly: the list mixes parties, companies and media (CDU → Siemens) |
| `_delete_sents` | delete_sentence | partly: deletes a random sentence, not an important one |
| `_shuffle_tokens` | GramE | yes |
| `_wrong_prep` | often PredE / LinkE, not grammar ("mit → ohne", "nach → vor") | partly |
| other grammar functions (articles, small words, "gecheckt") | GramE, but minor | probably not |
| `_contradict_sents`, the redundancy functions | none of ours | no |

`perturb_ai.py`: one prompt per dimension that asks for a target score. Useful for German prompt wording, not for single error types.

Not covered: PredE, CorefE, LinkE, OutE, add_out_of_domain_sentence, add_in_domain_sentence, add_definition.
