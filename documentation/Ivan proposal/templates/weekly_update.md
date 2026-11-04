# Weekly update - week 1 (meeting Wed 04.11.2026)

Slides: `documentation/presentations/week-01/` (built from `documentation/presentations/week-01/content.js`).

## Slide 1 - Done this week
Project manager: Ivan (we may rotate later)

Taxonomy complete: 7 faithfulness types (FRANK) + 4 coverage types (APPLS), 2 examples each, 22 in total -> `documentation/Taxonomy.md`

- Giuseppe: `select_perfect.py` picks the "perfect" summaries. Option A (all 3 annotators gave 7): 100 faithfulness, 66 coverage.
- Malte: PredE, EntE, CircE, 2 examples each.
- Anton: CorefE, LinkE, OutE, GramE, German explanations and 1 example each.
- Mick: delete sentences, add out-of-domain, add in-domain, add definitions, 2 examples each (`data/APPLS_errors/human_labeled.csv`).
- Ivan: merged everything into Taxonomy.md with the definitions from the papers, the second example for Anton's 4 types, 8 more coverage examples, and all 30 examples with full summaries in `data/examples/examples.csv`.

## Slide 2 - The taxonomy file
Screenshot of `documentation/Taxonomy.md` (Part 1, error types), next to a short list: one file for both taxonomies; per type the paper's definition and example, a German explanation, 2 examples; all 30 examples in `data/examples/examples.csv`.

## Slide 3 - Taxonomy overview
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

## Slide 4 - Questions & Requests for Neha
About our work

We weren't sure how to build the taxonomy, so we did it our way: paper definition, German explanation, 2 examples per type. Is this format fine?

Could you send us the most recent presentation? We don't think we have access to it.
