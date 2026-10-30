# Person 1 - Select the 7-rated summaries

Name: ______

## Task
Write `scripts/select_perfect.py` that reads `annotated_news_summaries/data_files/annotations_clean.jsonl` and writes:
- `data/perfect_faithfulness.jsonl` - summaries with Faithfulness (`d7`) = 7
- `data/perfect_coverage.jsonl` - summaries with Content Coverage (`d6`) = 7

Each output line: `item_id`, `model`, `title`, `article`, `summary`, ratings of all annotators, number of annotators.
One line per summary (`item_id` + `model`), not per annotator.

## Decision needed (bring to the team meeting)
A summary is "perfect" if:
- [ ] A: every annotator gave 7 (strict, fewer summaries)
- [ ] B: the mean rating is 7 or >= 6.5
- [ ] C: at least one annotator gave 7 (loose)
Implement it as a command-line option so we can switch. Report the counts for each option.

## Done when
- [ ] script runs with one command, documented in `data/README.md`
- [ ] counts per file written into `data/README.md`
- [ ] a readable sample (`data/sample_*.md`: 5 summaries with article) for the others to pick examples from
