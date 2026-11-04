# Weekly update - week 1 (meeting Wed 04.11.2026)

Slides: `presentations/week-01/` (built from `presentations/week-01/content.js`).

## Slide 1 - Done this week
Project manager: Ivan (we may rotate later)

Taxonomy complete: 7 faithfulness types (FRANK) + 4 coverage types (APPLS), 2 examples each, 22 in total -> `documentation/Taxonomy.md`

- Giuseppe: `select_perfect.py` picks the "perfect" summaries. Option A (all 3 annotators gave 7): 100 faithfulness, 66 coverage.
- Malte: PredE, EntE, CircE, 2 examples each.
- op380: CorefE, LinkE, OutE, GramE, German explanations and 1 example each.
- Mick: delete sentences, add out-of-domain, add in-domain, add definitions, 2 examples each (`APPLS_errors/human_labeled.csv`).
- Ivan: merged everything into Taxonomy.md with the definitions from the papers, the second example for op380's 4 types, 8 more coverage examples, and all 30 examples with full summaries in `examples/examples.csv`.

## Slide 2 - Taxonomy (excerpt from documentation/Taxonomy.md)
| Dimension | Type | German name | Example change |
|---|---|---|---|
| Faithfulness | PredE | Prädikatfehler | „abschaffen“ → „beibehalten“ |
| Faithfulness | EntE | Entitätsfehler | „Die CDU“ → „Die SPD“ |
| Faithfulness | CircE | Umstandsfehler | „in Greifswald“ → „in Rostock“ |
| Faithfulness | CorefE | Koreferenzfehler | „Sie“ (Esken) → „Er“ (Zuckerberg) |
| Faithfulness | LinkE | Verknüpfungsfehler | „nachdem“ → „bevor“ |
| Faithfulness | OutE | Information nicht im Artikel | + „Grönland hat rund 56.000 Einwohner.“ |
| Faithfulness | GramE | Grammatikfehler | „wird von der SEC verklagt“ → „wird die SEC verklagt“ |
| Coverage | Delete sentences | Sätze löschen | sentence on genetic differences and aggression deleted (ants) |
| Coverage | Add out-of-domain | Themenfremden Satz hinzufügen | + battery sentence in a Panama Canal summary |
| Coverage | Add in-domain | Themennahen Satz hinzufügen | + invented phone call between Frederiksen and Trump |
| Coverage | Add definitions | Definition hinzufügen | + definition of „Abholzung“ |

## Slide 3 - Questions for Neha
About our work
1. Is a summary "perfect" only if all 3 annotators gave 7? (A: 100/66, B: 167/131, C: 433/407)
2. Do we need severity levels? If yes, what's the scale? Right now each of us picks low/medium/high.
3. In-domain sentences: a real sentence from another article (as APPLS does), or an invented one? An invented one overlaps with OutE.
4. Are added definitions a coverage error in news summaries?
5. OutE: real-world facts that aren't in the article, or invented facts?
6. We weren't sure how to build the taxonomy, so we did it our way: paper definition, German explanation, 2 examples per type. Is this format fine?

Requests
- Could you send us the most recent presentation? We don't think we have access to it.
- Could you share last semester's error-injection scripts?
- What exactly should be ready by next week?
