# Task 1 - Data v2

**Goal:** bigger and cleaner sets of "perfect" summaries for the next steps. Due **Fri 06.11.** This week's injection tasks (2-4) keep using the current files, so write the new ones next to them, don't overwrite.

## 1. Use summaries with 2 or 3 annotators
Right now `scripts/select_perfect.py` only reads `annotations_exactly_3_annotators.jsonl`, so only summaries rated by exactly 3 people count. Neha said on 04.11. that summaries rated by **2 or 3** annotators can be used together, because inter-annotator agreement was computed for both.

- [ ] Switch the input to `data/annotated_news_summaries/data_files/annotations_at_least_2_annotators.jsonl`. It contains every summary with 2 or 3 annotators.
- [ ] Keep option A as the default: a summary is "perfect" if **every** annotator gave it 7. For a summary with 2 annotators that means both gave 7, and with 3 annotators all three.
- [ ] Expected result with option A: about **226** faithfulness and **144** coverage summaries (now 100 / 66).
- [ ] Keep `n_annotators` in each row, so we can still filter to 3 annotators later if needed.

## 2. Clean the texts
- [ ] Remove the web-interface tags from `title`, `article` and `summary`: turn `<br/>` into a line break, and drop `<strong>`, `</strong>` (and any other tags you find) but keep the text between them. Right now they appear in 61 of 100 faithfulness rows and 39 of 66 coverage rows.
- [ ] Check the new files afterwards: no `<br`, `<strong>`, `</strong>` or other `<…>` tag should be left in any row (the count should be 0). Worth a quick look at `data/injected/` too, since injected summaries should be tag-free as well.
- [ ] Keep the umlaut repair that is already in the script (`zerstÃ¶rt` → `zerstört`), and check that no `Ã`, `Â` or `â€` is left in the output.
- [ ] A few summaries (3 of 100 faithfulness) start and end with a stray quotation mark (e.g. `"Elektroautos …gedacht."`). Probably worth removing. In a first test the injection model removed them by itself, which counts as a second change.

## 3. Sentence count (extra, nice to have)
For each summary, count its sentences. Save the number as `n_sentences` in that summary's line.

```json
{"item_id": "1008", "model": "mistral-nemo", "...": "...", "n_sentences": 4}
```

Why: so we can test short and long summaries. Deleting a sentence (task 4) also needs at least 2.

## Done when
- [ ] new files `data/perfect_faithfulness_v2.jsonl` and `data/perfect_coverage_v2.jsonl` from 2 + 3 annotators, without tags (the current `perfect_*.jsonl` stay as they are)
- [ ] checked: 0 HTML tags and 0 broken umlauts left in the new files
- [ ] new counts in `data/README.md`
- [ ] (extra) `n_sentences` in every row
