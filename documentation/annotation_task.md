# Annotation task

Everybody rates 12 summaries per batch. One batch takes about 1 hour (up to 5 minutes per summary). Why we do it is in `annotation_proposal.md`.

## Who rates what

Batch 2 works exactly like batch 1, with 12 new summaries each. None of them was in batch 1.

**Batch 2**

| Person | Page | Answers file |
|---|---|---|
| Giuseppe | `data/annotation/batch2/pages/Giuseppe.html` | `data/annotation/batch2/answers/Giuseppe.json` |
| Malte | `data/annotation/batch2/pages/Malte.html` | `data/annotation/batch2/answers/Malte.json` |
| Anton | `data/annotation/batch2/pages/Anton.html` | `data/annotation/batch2/answers/Anton.json` |
| Mick | `data/annotation/batch2/pages/Mick.html` | `data/annotation/batch2/answers/Mick.json` |
| Ivan | `data/annotation/batch2/pages/Ivan.html` | `data/annotation/batch2/answers/Ivan.json` |

**Batch 1** (done)

| Person | Page | Answers file |
|---|---|---|
| Giuseppe | `data/annotation/pages/Giuseppe.html` | `data/annotation/answers/Giuseppe.json` |
| Malte | `data/annotation/pages/Malte.html` | `data/annotation/answers/Malte.json` |
| Anton | `data/annotation/pages/Anton.html` | `data/annotation/answers/Anton.json` |
| Mick | `data/annotation/pages/Mick.html` | `data/annotation/answers/Mick.json` |
| Ivan | `data/annotation/pages/Ivan.html` | `data/annotation/answers/Ivan.json` |

Your 12 summaries are drawn at random and in random order. You don't get the error types you generated or wrote the prompt for. Every summary is also rated by one other person (in parallel), but you don't know by whom.

## Steps

1. Open your page in a browser.
2. For every summary:
   1. Read the article.
   2. Then read the summary. Green words were added. Red struck-through words were in the original and have been removed: rate the summary without them. The original summary is folded below it; you don't need it, but you can open it.
   3. Rate **faithfulness** from 1 to 7: is everything in the summary correct according to the article?
   4. Rate **coverage** from 1 to 7: does the summary contain the key information of the article?
   5. Press **Next**.
3. When all 12 are done, press **Save answers file**. Put the downloaded `<name>.json` into the answers folder of the batch (see the table; the page also shows the path), then commit and push it.

## How to rate

- Rate the **whole summary** against the article, as a news reader would. The marks only help you find the change; don't rate the change alone.
- Give **both ratings for every summary**, whatever was changed.
- The anchors are on the page: **7** excellent, **4** mixed, **1** poor. Use 2, 3, 5 and 6 for everything in between.

## Good to know

- **Back** lets you change a rating. The counter at the top shows how many are done.
- On a wide screen the article is next to the summary. **One below the other** at the top puts it above the summary instead; on a narrow screen it is always above.
- If "Save answers file" doesn't work, press **Copy answers** and paste the text into your answers file.

## After everybody is done

One person runs `python scripts/annotation/agreement.py`. It reads all batches together, prints how much we agree and the mean rating per severity, and writes `data/annotation/ratings.csv`.
