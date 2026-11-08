# data/

Summaries from the annotated news summaries dataset that annotators rated as "perfect" on Faithfulness (`d7`) or Content Coverage (`d6`).

## How to run

From the repository root:

```bash
python scripts/select_perfect.py                       # option A (strict, default)
python scripts/select_perfect.py --criterion B         # mean >= 6.5
python scripts/select_perfect.py --criterion B --mean-threshold 7
python scripts/select_perfect.py --criterion C         # at least one 7
```

Only the Python standard library is needed (Python 3.8+).
Further options: `--input`, `--outdir`, `--suffix` (default `_v2`), `--sample-size` (default 5), `--seed` (default 42).

The script writes the v2 files (`*_v2.*`). The v1 files below were created with an earlier version of the script and are not overwritten.

## Inputs

- **v2 (current default):** `data/annotated_news_summaries/data_files/annotations_at_least_2_annotators.jsonl` - every summary rated by 2 or 3 annotators.
- **v1 (existing files):** `data/annotated_news_summaries/data_files/annotations_exactly_3_annotators.jsonl` - only summaries rated by exactly 3 annotators.

## Definition of "perfect"

| Option | Definition |
|---|---|
| A | Every annotator gave 7 (strict, fewest summaries). Default. With 2 annotators both gave 7, with 3 annotators all three. |
| B | Mean rating >= threshold. Default threshold is 6.5; with `--mean-threshold 7` the mean must be exactly 7. |
| C | At least one annotator gave 7 (loose, most summaries). |

The criterion is applied separately to Faithfulness (`d7`) and Content Coverage (`d6`).
Missing ratings are ignored; a summary without any rating is never selected.

## Files

**v1** (exactly 3 annotators, texts as in the source data apart from the UTF-8 repair)

- `perfect_faithfulness.jsonl` - summaries with Faithfulness (`d7`) judged perfect
- `perfect_coverage.jsonl` - summaries with Content Coverage (`d6`) judged perfect
- `sample_faithfulness.md`, `sample_coverage.md` - randomly drawn, readable summaries
  including the article (5 by default, see `--sample-size`; fixed by `--seed`)

**v2** (2 or 3 annotators, cleaned texts)

- `perfect_faithfulness_v2.jsonl`, `perfect_coverage_v2.jsonl` - same selection logic as v1, larger and cleaner
- `sample_faithfulness_v2.md`, `sample_coverage_v2.md` - samples for v2, now with the sentence count

One line = one summary (`item_id` + `model`), not one annotator row. Fields: `item_id`, `model`,
`title`, `article`, `summary`, `ratings_d6_coverage`, `ratings_d7_faithfulness`, `n_annotators`.
v2 files additionally contain `n_sentences`.

`n_annotators` is kept so v2 can still be filtered to summaries with 3 annotators.
`n_sentences` is an approximate, regex-based sentence count (common abbreviations and ordinals like "3." are not counted as sentence ends).

## Text cleaning

v1: double-encoded UTF-8 is repaired on load (e.g. `zerstÃ¶rt` -> `zerstört`).

v2 additionally:

- web-interface tags are removed from `title`, `article` and `summary`: `<br/>` becomes a line break, all other tags (e.g. `<strong>`, `</strong>`) are dropped and the text between them is kept
- a pair of quotation marks around a whole summary is removed (only if no other quotation marks are inside)
- leftover broken characters are removed (e.g. a stray `Ã` in `GesprÃ¤chs`, 2 `llama-1b` summaries)
- checked: 0 HTML tags and 0 `Ã`, `Â`, `â€` left in the v2 files

## Counts per option (v1)

<!-- COUNTS:START -->
Input: `annotations_exactly_3_annotators.jsonl` - 2340 annotator rows, 780 unique summaries (item_id + model).

| Option | Definition | Faithfulness (d7) | Coverage (d6) |
|---|---|---|---|
| A | every annotator gave 7 (strict) | 100 | 66 |
| B | mean >= 6.5 | 167 | 131 |
| C | at least one annotator gave 7 (loose) | 433 | 407 |

Currently written files use option **A**.
<!-- COUNTS:END -->

## Counts per option (v2)

<!-- COUNTS_V2:START -->
Input: `annotations_at_least_2_annotators.jsonl` - 3720 annotator rows, 1470 unique summaries (item_id + model). Texts cleaned (HTML tags, umlauts, outer quotes); `n_sentences` added.

| Option | Definition | Faithfulness (d7) | Coverage (d6) |
|---|---|---|---|
| A | every annotator gave 7 (strict) | 226 | 144 |
| B | mean >= 6.5 | 355 | 279 |
| C | at least one annotator gave 7 (loose) | 760 | 670 |

Currently written files use option **A**.
<!-- COUNTS_V2:END -->