# Week 1 tasks (due Wed 04.11.)

Goal of the project: test whether LLM judges notice deliberately injected errors in German news summaries.
This week we do NOT inject errors automatically. We (a) select perfect summaries and (b) build the error lists with hand-made examples.

Dataset: `annotated_news_summaries/data_files/annotations_clean.jsonl`
- one line = one annotator's rating of one summary (`item_id` + `model`)
- `d6` = Content Coverage, `d7` = Faithfulness (scale 1-7)

| Who | Open this file |
|---|---|
| Person 1 | `tasks/person1_data_selection.md` |
| Person 2 | `tasks/person2_faithfulness_semantic_frame.md` |
| Person 3 | `tasks/person3_faithfulness_discourse.md` |
| Person 4 | `tasks/person4_coverage.md` |
| Person 5 | `tasks/person5_reference_and_slides.md` |

Rules for everyone
- Examples go into your own file AND as rows in `examples/examples.csv` (format: `templates/example_format.md`).
- Take examples only from the sub-datasets of Person 1 (until they exist: any summary with d7 = 7 or d6 = 7).
- Change as little as possible: one error per example.
- Write questions for Neha into `templates/weekly_update.md`, section 3.
