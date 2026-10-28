# Annotated German News Summaries

This repository releases a human-annotated dataset for evaluating German news
summaries of articles from Zeit Online. It contains dimension-level quality ratings, pairwise preferences,
source articles, generated summaries, model identifiers, and anonymized
annotator identifiers.

Paper published in Konvens 2026.

The dataset is intended for research on:

- multidimensional summary evaluation;
- preference modelling;
- inter-annotator agreement;
- automatic evaluation metrics;
- system-level comparisons;
- relationships among summary-quality dimensions.

## Dataset overview

| Quantity | Count |
|---|---:|
| Individual annotation records | 4,506 |
| Unique source articles | 422 |
| Pairwise comparison tasks | 1,128 |
| Rated item--model summaries | 2,256 |
| Item--model summaries with at least 2 annotators | 1,470 |
| Item--model summaries with exactly 3 annotators | 780 |
| Summarization systems | 6 |
| Evaluation dimensions | 8 |

Each pairwise task contains two summaries of the same source article. Each
summary receives eight ratings on a 1--7 Likert scale, and the annotator also
selects the preferred summary.

The six systems represented in the data are:

- `gpt3.5`
- `llama-1b`
- `llama-3b`
- `mistral-nemo` (reported as German-Leo in the paper)
- `sauerkraut`
- `wiedervereinigung`

## Main data files

| File | Description |
|---|---|
| `annotations_clean.jsonl` | Complete release containing 4,506 individual annotation records |
| `annotations_at_least_2_annotators.jsonl` | Records belonging to the 1,470 item--model units rated by at least two annotators |
| `annotations_exactly_3_annotators.jsonl` | Records belonging to the 780 item--model units rated by exactly three annotators |
| `preference_data.jsonl` | 735 summary pairs with preference vote counts and train/validation/test split labels |
| `data_summary.json` | Compact dataset summary |

The subset counts refer to unique item--model units. Because a unit contributes
one JSONL record per annotator, the corresponding files contain more lines:

- `annotations_at_least_2_annotators.jsonl`: 3,720 records;
- `annotations_exactly_3_annotators.jsonl`: 2,340 records.

## Evaluation dimensions

The JSONL columns map to the annotation-interface dimensions as follows:

| Column | Dimension |
|---|---|
| `d1` | Grammaticality |
| `d2` | Non-redundancy |
| `d3` | Referential Clarity |
| `d4` | Focus |
| `d5` | Structure & Coherence |
| `d6` | Content Coverage |
| `d7` | Faithfulness |
| `d8` | Complexity |

All dimensions use a 1--7 scale, with higher values indicating better
performance according to the annotation guidelines.

## Record structure

Each line in `annotations_clean.jsonl` is one JSON object containing one
annotator's evaluation of one summary.

| Field | Description |
|---|---|
| `annotation_id` | Annotation identifier |
| `annotator` | Anonymized annotator identifier |
| `row_idx` | Pairwise-task identifier |
| `item_id` | Source-article identifier |
| `sr_no` | Human-readable task number |
| `model` | System that generated the rated summary |
| `d1`--`d8` | Dimension ratings on the 1--7 scale |
| `preferred` | `1` if this summary was selected within its pair, otherwise `0` |
| `created_at` | Annotation creation timestamp |
| `updated_at` | Annotation update timestamp |
| `title` | Source-article title |
| `article` | Source article |
| `summary` | Generated summary |

### Units and grouping keys

Use the following keys for the main analysis units:

| Analysis unit | Grouping columns |
|---|---|
| Individual annotation | `annotation_id` |
| Rated summary | `item_id`, `model` |
| Preference judgment | `row_idx`, `annotator` |
| Source article | `item_id` |

For a valid preference judgment, the two records sharing
`(row_idx, annotator)` contain one `preferred = 1` and one `preferred = 0`.

## Loading the dataset

### pandas

```python
import pandas as pd

df = pd.read_json("annotations_clean.jsonl", lines=True)

dimensions = [f"d{i}" for i in range(1, 9)]
print(df.shape)
print(df[dimensions].describe())
```

### Python standard library

```python
import json

with open("annotations_clean.jsonl", encoding="utf-8") as source:
    records = [json.loads(line) for line in source if line.strip()]

print(len(records))
```

## Common dataset operations

### Average repeated annotations per rated summary

This gives equal weight to every item--model summary rather than giving
multiply annotated summaries more weight:

```python
import pandas as pd

df = pd.read_json("annotations_clean.jsonl", lines=True)
dimensions = [f"d{i}" for i in range(1, 9)]

summary_ratings = (
    df.groupby(["item_id", "model"], as_index=False)[dimensions]
      .mean()
)

print(len(summary_ratings))  # 2,256
```

### Select summaries with at least two annotators

```python
counts = (
    df.groupby(["item_id", "model"])["annotator"]
      .nunique()
)
eligible = counts[counts >= 2].index

multi_annotator = (
    df.set_index(["item_id", "model"])
      .loc[eligible]
      .reset_index()
)

print(len(eligible))          # 1,470 item--model units
print(len(multi_annotator))   # 3,720 annotation records
```

### Reconstruct pairwise preferences

```python
pairs = []

for (row_idx, annotator), group in df.groupby(["row_idx", "annotator"]):
    if len(group) != 2 or group["preferred"].sum() != 1:
        continue

    winner = group.loc[group["preferred"] == 1].iloc[0]
    loser = group.loc[group["preferred"] == 0].iloc[0]

    pairs.append({
        "row_idx": row_idx,
        "annotator": annotator,
        "chosen_model": winner["model"],
        "rejected_model": loser["model"],
    })

preferences = pd.DataFrame(pairs)
print(len(preferences))
```

## Reproducing the analyses

Run commands from the repository root.

### Inter-annotator agreement

```bash
python compute_iaa.py
```

This creates dimension-level Krippendorff's alpha results, preference
agreement results, and descriptive statistics.

### Preference modelling

```bash
python logreg_preferences.py
```

This estimates how chosen-minus-rejected differences in the eight ratings
relate to pairwise preference.

### Dimension correlations, PCA, and length analysis

```bash
MPLCONFIGDIR=/tmp/mplconfig python analyze_dimension_correlations.py
```

Outputs are saved under `dimension_correlation_results/`.

### Rating distributions

```bash
MPLCONFIGDIR=/tmp/mplconfig python analyze_rating_distributions.py
```

By default, this uses the 1,470 item--model units with at least two
annotators. Outputs are saved under `rating_distribution_results/`.

### Descriptive ratings by topic

The topic analysis additionally requires an item-level metadata CSV containing
`item_id` and `topic` columns.

```bash
python analyze_ratings_by_topic.py \
  --metadata item_metadata.csv \
  --min-topic-articles 1 \
  --descriptive-only
```

Outputs are saved under `topic_rating_results/`.

## Summary generation

The generation prompt is provided in `summary_generation_prompt.md`, and the
generation workflow is implemented in `generate_summaries.py`. For exact
reproduction, document the model checkpoint, software version, decoding
parameters, and random seed used for each system.

## Repository structure

```text
.
├── annotations_clean.jsonl
├── annotations_at_least_2_annotators.jsonl
├── annotations_exactly_3_annotators.jsonl
├── data_summary.json
├── summary_generation_prompt.md
├── generate_summaries.py
├── compute_iaa.py
├── logreg_preferences.py
├── analyze_dimension_correlations.py
├── analyze_rating_distributions.py
├── analyze_ratings_by_topic.py
├── dimension_correlation_results/
├── rating_distribution_results/
└── topic_rating_results/
```

## Notes on interpretation

- The JSONL rows are individual annotation records, not independent source
  articles.
- Some summaries have one annotation and others have two or three. Average by
  `(item_id, model)` when every rated summary should contribute equally.
- The `preferred` field identifies the selected summary, not whether it was
  displayed as Summary A or Summary B.
- Presentation position is confounded with model identity in the original
  design, so raw A-versus-B selection rates should not be interpreted as
  positional bias.
- Topic labels are suitable for descriptive analysis but should be accompanied
  by documentation of how they were assigned and quality-checked.

## Citation

If you use this dataset, please cite the associated paper. Full citation
information will be added upon publication.
