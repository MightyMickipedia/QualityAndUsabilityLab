# Error taxonomy - Faithfulness and Content Coverage

Week 1 deliverable (due 04.11.). For each error type: name, definition from the paper, German explanation, 2 examples from our dataset.

- Faithfulness: FRANK, Pagnoni et al. 2021, Table 1 - https://arxiv.org/pdf/2104.13346
- Content Coverage: APPLS, Guo et al. 2024 (EMNLP), Table 2, informativeness - https://aclanthology.org/2024.emnlp-main.519.pdf
- Examples come only from summaries all annotators rated 7 (`data/perfect_faithfulness.jsonl`, `data/perfect_coverage.jsonl`, option A).
- Each example changes one thing. Full summaries are in `data/examples/examples.csv` (column `example_id`).

## At a glance

All 11 error types with one example change each. Details per type are further down.

| Dimension | Type | German name | Example change | Examples |
|---|---|---|---|---|
| Faithfulness | PredE | Prädikatfehler | „abschaffen“ → „beibehalten“ | 2 ✓ |
| Faithfulness | EntE | Entitätsfehler | „Die CDU“ → „Die SPD“ | 2 ✓ |
| Faithfulness | CircE | Umstandsfehler | „in Greifswald“ → „in Rostock“ | 2 ✓ |
| Faithfulness | CorefE | Koreferenzfehler | „Sie“ (Esken) → „Er“ (Zuckerberg) | 2 ✓ |
| Faithfulness | LinkE | Verknüpfungsfehler | „nachdem“ → „bevor“ | 2 ✓ |
| Faithfulness | OutE | Information nicht im Artikel | + „Grönland hat rund 56.000 Einwohner.“ | 2 ✓ |
| Faithfulness | GramE | Grammatikfehler | „wird von der SEC verklagt“ → „wird die SEC verklagt“ | 2 ✓ |
| Coverage | Delete sentences | Sätze löschen | sentence on genetic differences and aggression deleted (ants) | 2 ✓ (+2 in examples.csv) |
| Coverage | Add out-of-domain | Themenfremden Satz hinzufügen | + battery sentence in a Panama Canal summary | 2 ✓ (+2 in examples.csv) |
| Coverage | Add in-domain | Themennahen Satz hinzufügen | + invented phone call between Frederiksen and Trump | 2 ✓ (+2 in examples.csv) |
| Coverage | Add definitions | Definition hinzufügen | + definition of „Abholzung“ | 2 ✓ (+2 in examples.csv) |

**Done:** all 11 types have the paper definition, a German explanation and 2 examples (30 examples in total in `data/examples/examples.csv`).

**Not done yet:**
- Severity: no agreed scale. The low/medium/high values are each author's guess.
- In-domain sentences: open whether to use real sentences from other articles (as APPLS does) or invented ones (Mick's examples). Question for Neha.
- Automatic error injection with an LLM, using these examples as few-shot prompts (next phase).

## Who did what

| Dimension | Paper | Types | Examples | Examples by |
|---|---|---|---|---|
| Faithfulness: semantic frame | FRANK | PredE, EntE, CircE | 6 / 6 | Malte |
| Faithfulness: discourse and verifiability | FRANK | CorefE, LinkE, OutE, GramE | 8 / 8 | Anton, Ivan |
| Content Coverage | APPLS | delete sentences, add out-of-domain, add in-domain, add definitions | 8 / 8 | Mick (8 more by Ivan in examples.csv) |

---

# Part 1 - Faithfulness (FRANK)

A summary is faithful if everything it says is supported by the article. FRANK groups the errors into three levels: semantic frame (PredE, EntE, CircE), discourse (CorefE, LinkE) and content verifiability (OutE, GramE).

FRANK's examples all start from the same original text:

> "The first vaccine for Ebola was approved by the FDA in 2019 in the US, five years after the initial outbreak in 2014. To produce the vaccine, scientists had to sequence the DNA of Ebola, then identify possible vaccines, and finally show successful clinical trials. Scientists say a vaccine for COVID-19 is unlikely to be ready this year, although clinical trials have already started."

## Error types

| Type | Level | Definition (paper) | Paper example | Erklärung (DE) |
|---|---|---|---|---|
| **PredE**<br>Predicate Error / Prädikatfehler | Semantic frame | The predicate in the summary statement is inconsistent with the source article. ¹ | The Ebola vaccine was **rejected** by the FDA in 2019. | Das Prädikat, also die zentrale Handlung oder der Zustand (meist das Verb), widerspricht dem Artikel. Die Beteiligten stimmen, aber was sie tun, ist falsch. |
| **EntE**<br>Entity Error / Entitätsfehler | Semantic frame | The primary arguments (or their attributes) of the predicate are wrong. | The **COVID-19** vaccine was approved by the FDA in 2019. | Wer oder was an der Handlung beteiligt ist, ist falsch: eine Person, Organisation oder Sache wird vertauscht, oder eine ihrer Eigenschaften (z. B. eine Anzahl) stimmt nicht. |
| **CircE**<br>Circumstance Error / Umstandsfehler | Semantic frame | The additional information (like location or time) specifying the circumstance around a predicate is wrong. | The first vaccine for Ebola was approved by the FDA in **2014**. | Handlung und Beteiligte stimmen, aber die näheren Umstände sind falsch: Ort, Zeit, Art und Weise oder Bedingung des Ereignisses. |
| **CorefE**<br>Coreference Error / Koreferenzfehler | Discourse | A pronoun/reference with wrong or non-existing antecedent. | The first vaccine for Ebola was approved in 2019. **They** say a vaccine for COVID-19 is unlikely to be ready this year. | Ein Pronomen oder eine Referenz mit falschem oder nicht existierendem Bezugswort. |
| **LinkE**<br>Discourse Link Error / Verknüpfungsfehler | Discourse | Error in how multiple statements are linked together in the discourse (for example temporal ordering/causal link). | To produce the vaccine, scientists have to show successful human trials, **then** sequence the DNA of the virus. | Fehler darin, wie mehrere Aussagen im Text miteinander verknüpft sind (z. B. zeitliche Abfolge oder kausaler Zusammenhang). |
| **OutE**<br>Out of Article Error / Information nicht im Artikel | Verifiability | The statement contains information not present in the source article. | **China has already started clinical trials** of the COVID-19 vaccine. | Die Aussage enthält Informationen, die im Quellartikel nicht vorkommen. Das gilt auch dann, wenn die Information in der Realität stimmt. |
| **GramE**<br>Grammatical Error / Grammatikfehler | Verifiability | The grammar of the sentence is so wrong that it becomes meaningless. | The Ebola vaccine accepted have already started. | Die Grammatik des Satzes ist so fehlerhaft, dass er bedeutungslos wird (beeinträchtigt die Faithfulness). |

¹ Table 1 calls it "Relation Error", the text calls it "Predicate Error".

## Examples

### PredE - Predicate Error / Prädikatfehler

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | F-PredE-1, item 1008, mistral-nemo | F-PredE-2, item 1032, gpt3.5 |
| **Original** | ... den Solidaritätszuschlag **abschaffen** und das Bürgergeld in eine "Neue Grundsicherung" überführen. | Auch Grünen-Kanzlerkandidat Robert Habeck **kritisiert** den Vorfall. |
| **Modified** | ... den Solidaritätszuschlag **beibehalten** und das Bürgergeld in eine "Neue Grundsicherung" überführen. | Auch Grünen-Kanzlerkandidat Robert Habeck **begrüßt** den Vorfall. |
| **Change** | „abschaffen“ → „beibehalten“. Die vorgesehene Handlung beim Solidaritätszuschlag wird ins Gegenteil verkehrt. | „kritisiert“ → „begrüßt“ im Satz über Robert Habeck. Seine Reaktion auf den Vorfall wird ins Gegenteil verkehrt. |
| **Severity** | high | high |

### EntE - Entity Error / Entitätsfehler

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | F-EntE-1, item 1008, mistral-nemo | F-EntE-2, item 1256, gpt3.5 |
| **Original** | **Die CDU** präsentiert mit "Agenda 2030" ein Wirtschaftsprogramm für die Bundestagswahl, ... | Eine Mutter erklärt, wie sie ihre **vier** Kinder bewusst vernachlässigt, ... |
| **Modified** | **Die SPD** präsentiert mit "Agenda 2030" ein Wirtschaftsprogramm für die Bundestagswahl, ... | Eine Mutter erklärt, wie sie ihre **drei** Kinder bewusst vernachlässigt, ... |
| **Change** | „Die CDU“ → „Die SPD“. Die Partei, der das Wirtschaftsprogramm zugeschrieben wird, wird ausgetauscht. | „vier Kinder“ → „drei Kinder“. Die Anzahl der Kinder als Eigenschaft der beteiligten Gruppe wird verändert. |
| **Severity** | high | low |

### CircE - Circumstance Error / Umstandsfehler

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | F-CircE-1, item 108, sauerkraut | F-CircE-2, item 1032, sauerkraut |
| **Original** | Die Bundesagentur für Arbeit (BA) vermeldet **ein Jahr** nach Einführung des sogenannten Jobturbo Fortschritte ... | Der FDP-Vorsitzende Christian Lindner wurde bei einem Wahlkampfauftritt **in Greifswald** ... beworfen. |
| **Modified** | Die Bundesagentur für Arbeit (BA) vermeldet **drei Jahre** nach Einführung des sogenannten Jobturbo Fortschritte ... | Der FDP-Vorsitzende Christian Lindner wurde bei einem Wahlkampfauftritt **in Rostock** ... beworfen. |
| **Change** | „ein Jahr nach Einführung“ → „drei Jahre nach Einführung“. Nur der zeitliche Abstand zwischen Programmstart und der Fortschrittsmeldung wird verändert. | „in Greifswald“ → „in Rostock“. Der Ort des Schaumtortenangriffs wird verändert. |
| **Severity** | medium | medium |

### CorefE - Coreference Error / Koreferenzfehler

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | F-CorefE-1, item 1236, gpt3.5 | F-CorefE-2, item 1013, mistral-nemo |
| **Original** | ... den suspendierten Präsidenten Yoon Suk Yeol festgenommen, nachdem **er** sich geweigert **hatte**, zur Vernehmung zu erscheinen. | ... nachdem Meta-Geschäftsführer Mark Zuckerberg den Stopp von Faktenchecks angekündigt hat. **Sie** sieht dies als Ablehnung der Regulierung zum Schutz der Demokratie ... |
| **Modified** | ... den suspendierten Präsidenten Yoon Suk Yeol festgenommen, nachdem **sie** sich geweigert **haben**, zur Vernehmung zu erscheinen. | ... nachdem Meta-Geschäftsführer Mark Zuckerberg den Stopp von Faktenchecks angekündigt hat. **Er** sieht dies als Ablehnung der Regulierung zum Schutz der Demokratie ... |
| **Change** | „er“ → „sie“. Jetzt klingt es, als hätten sich Polizei und Behörde geweigert, nicht Yoon. | „Sie“ → „Er“. Die Kritik stammt jetzt von Zuckerberg statt von Esken. |
| **Severity** | medium | medium |

### LinkE - Discourse Link Error / Verknüpfungsfehler

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | F-LinkE-1, item 1236, gpt3.5 | F-LinkE-2, item 101, gpt3.5 |
| **Original** | ... Yoon Suk Yeol festgenommen, **nachdem** er sich geweigert hatte, zur Vernehmung zu erscheinen. | Die Ausweisung der ARD-Mitarbeiter sei eine Reaktion auf die Schließung des Büros des russischen Staatsfernsehens in Deutschland. |
| **Modified** | ... Yoon Suk Yeol festgenommen, **bevor** er sich geweigert hatte, zur Vernehmung zu erscheinen. | Die Schließung des Büros des russischen Staatsfernsehens in Deutschland sei eine Reaktion auf die Ausweisung der ARD-Mitarbeiter. |
| **Change** | „nachdem“ → „bevor“. Die zeitliche Reihenfolge von Weigerung und Festnahme wird umgedreht. | Ursache und Wirkung sind vertauscht. |
| **Severity** | medium | high |

### OutE - Out of Article Error / Information nicht im Artikel

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | F-OutE-1, item 1236, gpt3.5 | F-OutE-2, item 1053, mistral-nemo |
| **Original** | ... nachdem er sich geweigert hatte, zur Vernehmung zu erscheinen. | ... Trump hatte zuvor seine Drohungen bekräftigt und ein militärisches Vorgehen nicht ausgeschlossen. |
| **Modified** | ... nachdem er sich geweigert hatte, zur Vernehmung zu erscheinen. **Die Festnahme ereignete sich im Januar 2025.** | ... Trump hatte zuvor seine Drohungen bekräftigt und ein militärisches Vorgehen nicht ausgeschlossen. **Grönland hat rund 56.000 Einwohner.** |
| **Change** | Ein Satz mit Datum wird angehängt. | Ein Satz wird angehängt. Die Einwohnerzahl stimmt, steht aber nicht im Artikel. |
| **Severity** | low | low |

> **Note (Ivan), item 1236:** the article already says "Anfang Januar". The only new information is the year, so a judge that lets this through isn't really wrong. A fact that is clearly missing from the article would test OutE better.

### GramE - Grammatical Error / Grammatikfehler

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | F-GramE-1, item 1236, gpt3.5 | F-GramE-2, item 1235, mistral-nemo |
| **Original** | Südkoreas Polizei und die Antikorruptionsbehörde haben den suspendierten Präsidenten Yoon Suk Yeol festgenommen, nachdem er sich geweigert hatte, ... | Elon Musk wird **von der** US-Börsenaufsicht SEC verklagt, ... |
| **Modified** | Südkoreas Polizei und die Antikorruptionsbehörde **haben festgenommen**, nachdem **er sich geweigert wurde**. | Elon Musk wird **die** US-Börsenaufsicht SEC verklagt, ... |
| **Change** | Objekt entfernt, falsches Passiv. Wer festgenommen wurde, ist nicht mehr erkennbar. | „von der“ → „die“. Es ist nicht mehr klar, wer wen verklagt. |
| **Severity** | high | high |

> **Note (Ivan), item 1236:** this edit deletes the object, breaks the verb form and cuts the rest of the clause. That's three changes, which breaks our one-error rule. FRANK also says minor grammar mistakes don't count (p. 3), so one broken construction should be enough.

---

# Part 2 - Content Coverage (APPLS, informativeness)

- **Criterion (paper):** "Informativeness measures the extent to which the plain language summary covers essential information from the source text (e.g., methods, main findings) and incorporates relevant background information."
- Coverage errors make the summary miss important content or fill it with content that doesn't belong. Use summaries from `data/perfect_coverage.jsonl`.

APPLS's examples all start from:

> "Worldwide, coronavirus 2 (SARS-CoV-2), a severe acute respiratory syndrome, has infected more than 59 million people and killed more than one of them. The first step is an accurate assessment of the population prevalence of past infections…"

## Error types

| Type | Definition (paper) | Paper example | Erklärung (DE) |
|---|---|---|---|
| **Delete sentences**<br>Sätze löschen | Simulates "salient information missing". "To simulate the loss of relevant information, we delete sentences until a single sentence remains." | The paper marks the deleted sentences in colour, which gets lost when you copy the text. See Table 2 on p. 3. | Ein Satz mit einer wichtigen Information des Artikels wird aus der Zusammenfassung gelöscht. Die Zusammenfassung bleibt korrekt, aber unvollständig. |
| **Add out-of-domain sentence**<br>Themenfremden Satz hinzufügen | Simulates "out-of-domain hallucination". "We add sentences from ACL papers", i.e. text from a completely different field. | **In this paper we address the problem of aggregating the outputs of classifiers solving different nlp tasks.** Worldwide, coronavirus 2 (SARS-CoV-2), ... | Ein Satz aus einem ganz anderen Themenbereich wird eingefügt, etwa aus einem Fachaufsatz. Mit dem Artikel hat er nichts zu tun. |
| **Add in-domain sentence**<br>Themennahen Satz hinzufügen | Simulates "in-domain hallucination". "We add sentences from Cochrane abstracts", i.e. a real sentence from *another document of the same domain*. | ... killed more than one of them. **This review synthesised the latest evidence on the reduction of antipsychotic doses for stable individuals with schizophrenia…** | Ein echter Satz aus einem anderen Nachrichtenartikel wird eingefügt. Er klingt passend, gehört aber nicht zu diesem Artikel. |
| **Add definitions**<br>Definition hinzufügen | Simulates "background explanation". "Background explanations ... involve adding external content like definitions or examples"; the paper adds up to three definitions. | ... killed more than one of them. **Coronaviruses are species in the genera of virus belonging to the subfamily Coronavirinae in the family Coronaviridae. ...** | Eine Begriffserklärung oder Hintergrundinfo wird ergänzt. Sie nimmt Platz weg, gehört aber nicht zum Kern des Artikels. |

Our rule: we delete one sentence that carries a key fact. The paper deletes sentences without choosing, so ours is stricter.

The coverage examples below are Mick's (`data/APPLS_errors/human_labeled.csv`). Ivan made 8 more, one more pair per type: `C-DEL-3/4`, `C-OUT-3/4`, `C-IN-3/4`, `C-DEF-3/4` in `data/examples/examples.csv`.

## Examples

### Delete sentences / Sätze löschen

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | C-DEL-1, item 1004, gpt3.5 | C-DEL-2, item 1095, sauerkraut |
| **Original** | ... nachtragend sein können. **Schwarze Wegameisen reagieren aggressiver auf Mitglieder anderer Völker, je stärker diese genetisch unterschiedlich sind.** Die Studie zeigt, dass Ameisen sich an Kämpfe erinnern ... | ... Apple teilte mit, dass der Vorschlag ein unzulässiger Eingriff ins Tagesgeschäft des Unternehmens sei. **Was die rechtlichen Risiken angehe, habe der Konzern eingespielte Verfahren, um diese zu minimieren.** ... |
| **Modified** | ... nachtragend sein können. Die Studie zeigt, dass Ameisen sich an Kämpfe erinnern ... | ... Apple teilte mit, dass der Vorschlag ein unzulässiger Eingriff ins Tagesgeschäft des Unternehmens sei. ... |
| **Change** | Entfernt: „Schwarze Wegameisen reagieren aggressiver auf Mitglieder anderer Völker, je stärker diese genetisch unterschiedlich sind.“ Damit fehlt der im Artikel beschriebene genetische Einfluss auf Aggression als Ergänzung zur Lernerfahrung. Medium: Ein wichtiger Erklärungsfaktor entfällt, die zentrale Erkenntnis zum Lernen bleibt erhalten. | Entfernt: „Was die rechtlichen Risiken angehe, habe der Konzern eingespielte Verfahren, um diese zu minimieren.“ Damit fehlt Apples konkrete Antwort auf die von den Aktionären angeführten Klagerisiken. Medium: Ein wichtiges Gegenargument entfällt, Apples Ablehnung des Antrags bleibt erkennbar. |
| **Severity** | medium | medium |

### Add out-of-domain sentence / Themenfremden Satz hinzufügen

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | C-OUT-1, item 1011, sauerkraut | C-OUT-2, item 1124, gpt3.5 |
| **Original** | ... der Kanal selbst werde aber von der Panamakanal-Behörde betrieben. | ... Mainz besiegt Bochum 2:0, und Heidenheim schlägt Union Berlin 2:0. |
| **Modified** | ... der Kanal selbst werde aber von der Panamakanal-Behörde betrieben. **Aktuelle Studien zeigen jedoch, dass die meisten Batterien auch nach über 200.000 Kilometern noch über 80 Prozent ihrer Kapazität behalten.** | ... Mainz besiegt Bochum 2:0, und Heidenheim schlägt Union Berlin 2:0. **Der Bericht des World Resources Institutes (WRI) zeigt, dass weltweit rund 3,7 Millionen Hektar tropischer Urwald im vergangenen Jahr zerstört wurden.** |
| **Change** | Hinzugefügt: „Aktuelle Studien zeigen jedoch, dass die meisten Batterien auch nach über 200.000 Kilometern noch über 80 Prozent ihrer Kapazität behalten.“ Satz aus 1090 / gpt3.5. Batterielebensdauer ist themenfremd zum Streit um den Panamakanal. Medium: Ein vollständiger irrelevanter Satz stört den Fokus, ohne die ursprünglichen Informationen zu entfernen. | Hinzugefügt: „Der Bericht des World Resources Institutes (WRI) zeigt, dass weltweit rund 3,7 Millionen Hektar tropischer Urwald im vergangenen Jahr zerstört wurden.“ Satz aus 1 / sauerkraut. Tropischer Waldverlust ist themenfremd zum Bundesligaspieltag. Medium: Der zusätzliche Satz nimmt gegenüber der kurzen Sportzusammenfassung deutlich Raum ein und verwässert ihren Fokus. |
| **Severity** | medium | medium |

### Add in-domain sentence / Themennahen Satz hinzufügen

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | C-IN-1, item 1053, sauerkraut | C-IN-2, item 1207, sauerkraut |
| **Original** | ... Dieser Artikel wird weiter aktualisiert. | ... Trump hat wiederholt alle Vorwürfe zurückgewiesen und Smith als "gestört" bezeichnet sowie dessen Vorgehen als politisch motiviert kritisiert. |
| **Modified** | ... Dieser Artikel wird weiter aktualisiert. **Für die kommende Woche ist ein Telefongespräch zwischen Frederiksen und Trump über den künftigen Status Grönlands vorgesehen.** | ... Trump hat wiederholt alle Vorwürfe zurückgewiesen und Smith als "gestört" bezeichnet sowie dessen Vorgehen als politisch motiviert kritisiert. **Das US-Justizministerium kündigte außerdem an, den Bericht dem Justizausschuss des Kongresses zur Prüfung zuzuleiten.** |
| **Change** | Hinzugefügt: „Für die kommende Woche ist ein Telefongespräch zwischen Frederiksen und Trump über den künftigen Status Grönlands vorgesehen.“ Erfundener themennaher Zusatz. Der Artikel berichtet nur über die Kontaktaufnahme, nicht über einen vereinbarten Gesprächstermin. Medium: Eine plausible, aber unbelegte konkrete Fortsetzung des diplomatischen Vorgangs wird hinzugefügt. | Hinzugefügt: „Das US-Justizministerium kündigte außerdem an, den Bericht dem Justizausschuss des Kongresses zur Prüfung zuzuleiten.“ Erfundener themennaher Zusatz. Der Quellartikel enthält keine solche Ankündigung oder parlamentarische Prüfung. Medium: Ein plausibler zusätzlicher Verfahrensschritt wird als Tatsache dargestellt, ohne die Kernaussage des Berichts zu ersetzen. |
| **Severity** | medium | medium |

### Add definitions / Definition hinzufügen

| | Example 1 | Example 2 |
|---|---|---|
| **Source** | C-DEF-1, item 1, sauerkraut | C-DEF-2, item 1090, gpt3.5 |
| **Original** | ... um den Waldverlust zu stoppen und die bestehenden Wälder zu schützen. | ... sollten E-Auto-Fahrerinnen auf langsames Laden und das Vorwärmen des Akkus achten. |
| **Modified** | ... um den Waldverlust zu stoppen und die bestehenden Wälder zu schützen. **Abholzung bezeichnet das Fällen von Bäumen auf einer Waldfläche.** | ... sollten E-Auto-Fahrerinnen auf langsames Laden und das Vorwärmen des Akkus achten. **Ein Elektroauto ist ein Fahrzeug, das von einem Elektromotor angetrieben wird.** |
| **Change** | Hinzugefügt: „Abholzung bezeichnet das Fällen von Bäumen auf einer Waldfläche.“ Unnötige Begriffsdefinition: Sie erläutert einen bereits verständlichen Begriff, ohne einen weiteren Befund des WRI-Berichts beizutragen. Low: Der kurze Hintergrundsatz verlängert den Text nur geringfügig und verändert keine Kernaussage. | Hinzugefügt: „Ein Elektroauto ist ein Fahrzeug, das von einem Elektromotor angetrieben wird.“ Unnötige Begriffsdefinition: Diese allgemeine Erläuterung liefert keine zusätzliche Information über die untersuchte Batteriehaltbarkeit. Low: Ein kurzer redundanter Hintergrundsatz mindert die Informationsdichte nur geringfügig. |
| **Severity** | low | low |


