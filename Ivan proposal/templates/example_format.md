# Example format (`examples/examples.csv`)

Columns:
| column | meaning |
|---|---|
| `example_id` | e.g. `F-EntE-1`, `C-DEL-2` |
| `dimension` | `faithfulness` or `coverage` |
| `error_type` | e.g. `EntE`, `LinkE`, `delete_sentence` |
| `item_id` | from the dataset |
| `model` | from the dataset |
| `original_summary` | full original summary |
| `modified_summary` | full summary with the one error |
| `change` | short description of what changed |
| `severity` | `low` / `medium` / `high` (guess for now) |
| `author` | your name |

One row = one example. Full summaries, not single sentences, so the rows can be used as few-shot examples later.
