# To-do suggestions and issues

Things we noticed in each other's work. Suggestions, not tasks. Grouped by the person who could pick them up.

## Giuseppe

- **Model chatter at the start of 15 summaries in data v2.** They begin with a line that isn't part of the summary, e.g. *"Hier ist eine Zusammenfassung des Artikels:"* or *"Hier ist ein prägnanter Erstsatz…"*. 10 in `data/perfect_faithfulness_v2.jsonl`, 5 in `data/perfect_coverage_v2.jsonl`, all from llama-1b / llama-3b.
  - Why it matters: an injection model may edit or drop that line, which counts as a second change.
  - Idea: `scripts/select_perfect.py` strips a first line that starts with "Hier ist …:" (last semester's `perturb.py` does this with `_split_boilerplate`). The alternative is to drop those 15 summaries.
  - Items: faithfulness 1077, 1318, 1336, 137, 143, 5184, 5757 (llama-3b), 1112, 1262, 1328 (llama-1b); coverage 117, 1279, 1349, 137 (llama-3b), 1262 (llama-1b).

## Anton

- **The prompt files in the repo have different names than the ones the outputs point to.**
  - What happened: you ran the injection with four prompt files. Each output line in `data/injected/discourse_test.jsonl` notes the name of the prompt file that produced it (field `prompt`). The prompt files were then uploaded under other names.

    | Name in the outputs | File in `scripts/injection/prompts/` |
    |---|---|
    | `discourse_corefe.md` | `faithfulness_corefe.md` |
    | `discourse_linke.md` | `faithfulness_linke.md` |
    | `verifiability_oute.md` | `faithfulness_oute.md` |
    | `verifiability_grame.md` | `faithfulness_grame.md` |

  - Why it matters: the outputs point to files that don't exist in the repo. We can guess which file is meant, but we can't be sure the text is the same as in the run.
  - Idea: rename the four files in the repo to the names in the outputs. 
- **Fallback rule missing in the four prompts.** Malte's and Mick's prompts have it: if no fitting change exists for the type and severity, the model returns the summary unchanged and starts `change` with `KEINE_PASSENDE_AENDERUNG:` plus a short reason, and it must not produce a different error type instead.
  - Why it matters: without it the model forces an error even when none fits, e.g. a CorefE in a summary without pronouns. The test set includes item 109, a one-sentence summary.
  - Idea: copy the paragraph from `semantic_frame_ente.md` (section "Kontrolle und Ausgabe"). The runner then marks such outputs with the warning `no fitting change`.

## Mick

- **The coverage README links to a file that isn't in the repo.** `scripts/injection/coverage/README.md` says the finished delivery with links to the results and prompts is in `data/injected/coverage_README.md` ("Coverage-Übersicht"). That file was never committed, so the link is broken.
  - Idea: commit `data/injected/coverage_README.md`, or remove the sentence if the overview isn't needed.
