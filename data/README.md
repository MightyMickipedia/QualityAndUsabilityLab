# Summaries from the annotated news summaries dataset that annotators rated as "perfect" on Faithfulness (`d7`) or Content Coverage (`d6`).


## How to run

From the repository root:

```bash
python scripts/select_perfect.py                       # option A (strict, default)
python scripts/select_perfect.py --criterion B         # mean >= 6.5
python scripts/select_perfect.py --criterion B --mean-threshold 7
python scripts/select_perfect.py --criterion C         # at least one 7
```

Only the Python standard library is needed (Python 3.8+).
Further options: `--input`, `--outdir`, `--sample-size` (default 5), `--seed` (default 42).

Input: `annotated_news_summaries/data_files/annotations_exactly_3_annotators.jsonl`

## Definition of "perfect"

| Option | Definition |
|---|---|
| A | Every annotator gave 7 (strict, fewest summaries). Default. |
| B | Mean rating >= threshold. Default threshold is 6.5; with `--mean-threshold 7` the mean must be exactly 7. |
| C | At least one annotator gave 7 (loose, most summaries). |

The criterion is applied separately to Faithfulness (`d7`) and Content Coverage (`d6`).
Missing ratings are ignored; a summary without any rating is never selected.

## Files

- `perfect_faithfulness.jsonl` - summaries with Faithfulness (`d7`) judged perfect
- `perfect_coverage.jsonl` - summaries with Content Coverage (`d6`) judged perfect
- `sample_faithfulness.md`, `sample_coverage.md` - randomly drawn, readable summaries
  including the article (5 by default, see `--sample-size`; fixed by `--seed`)

One line = one summary (`item_id` + `model`), not one annotator row. Fields: `item_id`, `model`,
`title`, `article`, `summary`, `ratings_d6_coverage`, `ratings_d7_faithfulness`, `n_annotators`.

Texts (`title`, `article`, `summary`) are repaired on load if they contain double-encoded UTF-8
(e.g. `zerstÃ¶rt` -> `zerstört`).

## Counts per option

<!-- COUNTS:START -->
Input: `annotations_exactly_3_annotators.jsonl` - 2340 annotator rows, 780 unique summaries (item_id + model).

| Option | Definition | Faithfulness (d7) | Coverage (d6) |
|---|---|---|---|
| A | every annotator gave 7 (strict) | 100 | 66 |
| B | mean >= 6.5 | 167 | 131 |
| C | at least one annotator gave 7 (loose) | 433 | 407 |

Currently written files use option **A**.
<!-- COUNTS:END -->