# Annotation proposal

How we rate a part of the injected summaries by hand. Updated after the meeting with Neha on 18.11. What each of us has to do is in `annotation_task.md`.

## Why we need it

We asked the model for an error of a certain type and severity, but we don't know how bad the summary really is for a reader. So we rate a sample ourselves, like news readers: how faithful is the summary, and how much of the article does it cover. These human ratings are what we later compare the LLM judges with. Neha asked for at least two people per summary, so we can report how much we agree.

## How others did it

| Paper | What they rated | Who | Agreement |
|---|---|---|---|
| SummEval (Fabbri et al., 2021), sent by Neha | 100 news articles, 16 systems; consistency, relevance, fluency, coherence on a 1-5 scale | 5 crowd workers and 3 experts per summary | Krippendorff's α = 0.49 (crowd), 0.41 (experts, first round), 0.71 (experts, second round) |
| FRANK (Pagnoni et al., 2021) | every sentence: factual or not, then the error type | 3 crowd workers per summary | κ = 0.58 for factual or not |
| APPLS (Guo et al., 2024) | 100 sampled pairs on 5-point scales | 2 annotators | κ = 0.48 |

What we take from them:

- **A scale, not yes or no.** FRANK asks yes or no because it only wants to know whether there is an error. We already know there is one. We want to know how much it hurts the summary, and a scale shows that. SummEval rates news summaries on a scale, like we do.
- **The article is shown, and the summaries are mixed.** In SummEval the annotators first read the article, then rate the summaries. The order was random for every annotator.
- **A sample is enough.** SummEval rated 100 articles, APPLS checked 100 pairs.
- **Disagreement is normal.** SummEval's first round reached α = 0.41 to 0.49. We report our agreement as it is.

## The two ratings

Every summary gets two ratings from 1 to 7, one for each dimension, separately. The anchors are Neha's (`documentation/rubrics/`), the same ones the LLM judges get. 2, 3, 5 and 6 are in between.

**Faithfulness (Faktentreue).** Die Zusammenfassung sollte inhaltlich korrekt und sprachlich verständlich sein. Sie darf keine erfundenen Details enthalten, die nicht in der Quelle vorkommen.

| Score | Anchor |
|---|---|
| 7 | Ausgezeichnet: Alle Aussagen sind sachlich korrekt. |
| 4 | Durchwachsen: Enthält sachliche Fehler, die Gesamtzusammenfassung gibt jedoch die wichtigsten Fakten korrekt wieder. |
| 1 | Mangelhaft: Faktisch unzuverlässig; die meisten Aussagen sind falsch. |

How: read each sentence of the summary and check it against the article. Count how many statements are wrong and how severe they are.

**Coverage (Inhaltsabdeckung).** Die Zusammenfassung sollte die wesentlichen Informationen des Originalartikels aus der Perspektive eines Nachrichtenlesers erfassen, sodass der Originalartikel selbst nicht mehr benötigt werden sollte.

| Score | Anchor |
|---|---|
| 7 | Ausgezeichnet: Alle Schlüsselinformationen sind enthalten. |
| 4 | Gemischt: Ein oder zwei wichtige Details fehlen. |
| 1 | Mangelhaft: Es fehlen viele wichtige Punkte. |

How: find the key information of the article, then check whether the summary contains it. Missing key points lower the score; missing minor details don't.

Both ratings are given for every summary, whatever kind of error was injected. An added sentence can also lower faithfulness, a wrong fact can also lower coverage.

**No separate severity rating.** The two ratings are our judgment of how severe the error is: a light error barely lowers them, a heavy one lowers them a lot. A separate low/medium/high would mean rating the change alone, which Neha asked us not to do, and the judges give no such rating to compare with. The asked severity stays hidden and is compared with our ratings afterwards.

**Broken data.** The English summary (item 1408) is left out of the sample. The doubled quotes from the source dataset ("" instead of ") are cleaned on the pages. We checked the summaries of both batches; none is broken.

## What the annotator sees

- the article
- the summary with the injected error, with the changes marked: added words green, removed words red and struck through
- the original summary, folded away; open it only if you need it
- the two rating scales

Not shown: the error type, the asked severity and the model that generated it. The marks save us from searching for the change, which Neha agreed to. But we rate the whole summary against the article, not the change alone. How severe the error is, each of us judges alone, through the two ratings.

## What we annotate

30 summaries, drawn at random from the existing week-3 outputs: 2 or 3 per error type, and 10 per asked severity (low, medium, high), so we can compare the severities. Each summary is rated by two people, so 60 ratings, 12 per person.

The two annotators of each summary are drawn at random. The only rule: nobody rates an error type they generated or wrote the prompt for. Everybody gets their 12 summaries in their own random order, so error types and severities are mixed.

**Batch 2** (decided 25.11.): another 30 summaries, 12 more per person, drawn in the same way from the outputs not used in batch 1. In the outputs left, the low severity is missing for some types, so a type may repeat a severity there; it still has at least two different ones, and the totals stay 10 low, 10 medium, 10 high.

Left out: outputs where the model made no change, the week-2 test outputs, and the output with an English summary (item 1408, mistral-nemo).

## Steps

1. **Rating.** Everybody rates their 12 summaries alone, without talking about them.
2. **Agreement.** A script computes the agreement per dimension.
3. **Tricky cases.** If we find cases we read differently, we talk about them in the meeting and note what we decided. We don't change the ratings afterwards.
4. **Results.** The rating of a summary is the mean of the two ratings.

## Agreement and first results

Per dimension, the script reports:

- **Krippendorff's alpha** (interval), as in SummEval. It compares how far apart the two ratings of the same summary are with how far apart ratings are in general. 1 means the two always give the same rating, 0 means no better than chance. Interval means a 6 against a 7 counts as a small disagreement, a 2 against a 7 as a large one. It works when the pairs of annotators differ from summary to summary, which is the case here. SummEval got 0.41 to 0.49 in the first round.
- How often the two ratings are **equal**, and how often they are **at most 1 apart**. Easier to explain on a slide.
- The **mean rating per asked severity** (low, medium, high) and per kind of injected error (faithfulness or coverage). This shows whether the errors are as bad as we asked for, for the midterm.

## Effort

About 2 to 5 minutes per summary, so up to 1 hour per person. Plan with 5 minutes.

## Tools

One HTML page per annotator in `data/annotation/pages/`. It opens in any browser, also on a phone, with nothing to install. The article is on the left, the summary and the ratings on the right. A button at the top puts them below each other instead; on a phone they are always below each other.

1. Open your page, e.g. `data/annotation/pages/Malte.html`.
2. Rate the summaries. The ratings are kept in the browser while you work.
3. Press "Save answers file" and put the file into `data/annotation/answers/`, e.g. `Malte.json`.

Scripts in `scripts/annotation/`:

- `build_pages.py` draws the sample (`data/annotation/sample.json`, with the texts), assigns the annotators and builds the pages. Run again, it keeps the sample; `--redraw` draws a new one. `--batch 2` does the same for batch 2 in `data/annotation/batch2/`.
- `agreement.py` reads the answers files of all batches, prints agreement and first results and writes `data/annotation/ratings.csv`.
- `convert_coverage_csv.py` turned Mick's `data/APPLS_errors/human_labeled.csv` into `data/injected/delete_sentence.jsonl` and `add_in_domain_sentence.jsonl`, so all 11 types are in the shared format.

The pages are ready. Regenerating outputs later (e.g. the unchanged ones) doesn't change them: the sample only has outputs with a change, and their texts are stored in `sample.json`.

## Decided

- 1 to 7, as in the judge rubrics, so we can compare with the judges.
- 30 summaries in batch 1, 30 more in batch 2.
