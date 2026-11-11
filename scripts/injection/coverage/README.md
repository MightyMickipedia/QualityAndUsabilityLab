# Coverage-Prompts

Die fertige Abgabe mit direkten Links zu Ergebnis und Prompts steht in der [Coverage-Übersicht](../../../data/injected/coverage_README.md). Dieser Ordner enthält das wiederverwendbare Codegerüst und Hilfsdaten.

- `coverage_selection.json`: Auswahl der zehn Ausgangstexte und Zuordnung der Schweregrade; keine generierten Ausgaben.
- `../prompts/coverage_delete.md`, `../prompts/coverage_add.md`: gemeinsame Promptstruktur und Texterhaltung.
- `descriptions.json`: Fehlertypen und Schweregrade für Löschen, themennahe Ergänzungen sowie themenfremde Ergänzungen/Definitionen.
- `prompt_helper.py`: setzt nur die gewählte Typ- und Schweregradbeschreibung ein und lädt den unveränderten `../run.py` als Modul. Auswahl, Datenformat und Prüfungen bleiben beim Runner; nur dessen HTTP-Funktion wird für diesen lokalen Modulaufruf durch einen eigenen Adapter ersetzt.
- `generated/<error_type>_<severity>.md`: erzeugtes Template; bleibt lokal erhalten und wird bei gleicher Auswahl überschrieben. Die fünf Runner-Platzhalter werden erst vom Runner gefüllt. Der Dateiname erscheint im Ausgabefeld `prompt` des Runners.

Vom Repository-Hauptordner, nur Standardbibliothek erforderlich:

```powershell
python scripts/injection/coverage/prompt_helper.py --error_type add_in_domain_sentence --severity medium --timeout 600 --no_thinking --n 1 --dry_run
```

`--error_type` akzeptiert `delete_sentence`, `add_out_of_domain_sentence`, `add_in_domain_sentence` und `add_definition`; `--severity` akzeptiert `high`, `medium` und `low`. Nur die gewählten Beschreibungen gelangen in den LLM-Prompt. Typregeln bleiben auch bei hoher Severity verbindlich; ist die Kombination ungeeignet, gilt der Fallback des Prompts.

Weitere Runner-Argumente wie `--items`, `--input`, `--out`, `--n` und `--dry_run` werden weitergereicht. `--prompt` wird automatisch gesetzt und darf nicht übergeben werden. Auswahl und erzeugter Dateiname stimmen mit den maßgeblichen Runner-Parametern überein. Ohne `--dry_run` gelten API-Konfiguration und Ausgabe-/Append-Verhalten aus `../README.md`.

`--timeout` setzt eine positive Anzahl Sekunden pro HTTP-Anfrage: Standard 120 Sekunden, `--timeout 600` für zehn Minuten. Der eigene Adapter führt genau einen Versuch aus, ohne die vier Transportversuche des ursprünglichen Runners zu übernehmen. HTTP-, Verbindungs- und Timeoutfehler werden gemeldet; es erfolgt keine automatische Neugenerierung oder Reparatur. `--dry_run` sendet keine API-Anfrage. Die Runnerdatei und globale Netzwerkfunktionen bleiben unverändert. `--no_thinking` sendet zusätzlich `reasoning_effort: "none"` an den OpenAI-kompatiblen Endpunkt und deaktiviert bei unterstützten Ollama-Modellen das Thinking. Ohne dieses Flag fehlt das Feld und das bisherige Modellverhalten bleibt erhalten. Der urllib-Timeout ist ein Netzwerkwartezeitlimit, keine harte Gesamtzeitgrenze für eine dauerhaft Daten liefernde Verbindung.

Die aktuelle Severity-Kalibrierung ist eine neu vereinbarte Projektregel und nicht durch das Paper validiert. Beim Löschen fehlt für high ein zentraler Befund oder entscheidender Ereignisaspekt, für medium eine relevante Nebeninformation und für low ein kleines sachliches Randdetail. Bei erfundenen themennahen Ergänzungen bedeutet high einen neuen zentralen Deutungsaspekt, medium einen relevanten Nebenprozess und low ein nebensächliches Detail.

Bei themenfremden Sätzen und entbehrlichen korrekten Definitionen zählt der Wortanteil des Zusatzes relativ zur bereinigten Originalzusammenfassung: low höchstens 15 %, medium mehr als 15 % bis einschließlich 35 %, high mehr als 35 %. Wörter werden wie `run.clean(summary).split()` gezählt. Genau ein natürlicher Satz ohne Füllwörter bleibt Pflicht. High-Zusätze sind bei kurzen Originaltexten leichter erreichbar; Textlänge und Severity können dadurch zusammenhängen und sollten bei der Auswertung gemeinsam berücksichtigt werden.
