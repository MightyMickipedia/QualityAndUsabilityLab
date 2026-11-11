# Kurzreview der Semantic-Frame-Tests

**30 von 30 geprüft.** 26 OK, 4 auffällig.

Geprüft wurden Fehlertyp, genau ein klarer Sachfehler, Erhalt des übrigen Textes und flüssiges Deutsch. Bereits vorhandene Sprachfehler wurden bei der Bewertung der Änderungen ausgeklammert.

| Typ | item_id / Modell | Stufe | Ergebnis |
|---|---|---|---|
| PredE | 1010 / sauerkraut | high | OK |
| PredE | 1179 / mistral-nemo | high | Die Begründung mit der Gefahr durch den Wind passt nicht zur verneinten Einschätzung. |
| PredE | 1180 / llama-1b | high | OK |
| PredE | 1262 / llama-1b | high | OK |
| PredE | 1204 / gpt3.5 | medium | OK |
| PredE | 1242 / mistral-nemo | medium | OK |
| PredE | 1245 / sauerkraut | medium | OK |
| PredE | 1094 / gpt3.5 | low | OK |
| PredE | 1115 / sauerkraut | low | „Teils friedlich“ ist mit „teils aufgeheizt“ vereinbar. Der Sachfehler bleibt unklar. |
| PredE | 1232 / sauerkraut | low | OK |
| EntE | 1010 / sauerkraut | high | OK |
| EntE | 1179 / mistral-nemo | high | OK |
| EntE | 1180 / llama-1b | high | OK |
| EntE | 1262 / llama-1b | high | OK |
| EntE | 1204 / gpt3.5 | medium | „Die Polizei geht vor“ ist zu allgemein für einen eindeutigen Widerspruch zum Artikel. |
| EntE | 1242 / mistral-nemo | medium | OK |
| EntE | 1245 / sauerkraut | medium | OK |
| EntE | 1094 / gpt3.5 | low | OK |
| EntE | 1115 / sauerkraut | low | OK |
| EntE | 1232 / sauerkraut | low | OK |
| CircE | 1010 / sauerkraut | high | OK |
| CircE | 1179 / mistral-nemo | high | OK |
| CircE | 1180 / llama-1b | high | OK |
| CircE | 1262 / llama-1b | high | Zusätzlich wurde der Einleitungssatz „Hier ist ein möglicher Artikel:“ entfernt. |
| CircE | 1204 / gpt3.5 | medium | OK |
| CircE | 1242 / mistral-nemo | medium | OK |
| CircE | 1245 / sauerkraut | medium | OK |
| CircE | 1094 / gpt3.5 | low | OK |
| CircE | 1115 / sauerkraut | low | OK |
| CircE | 1232 / sauerkraut | low | OK |
