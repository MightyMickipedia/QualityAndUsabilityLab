Du bekommst einen Nachrichtenartikel und eine fehlerfreie Zusammenfassung dieses Artikels.
Baue genau EINEN Fehler vom Typ {error_type} mit Schweregrad {severity} in die Zusammenfassung ein.
Ändere sonst nichts. Die Zusammenfassung soll flüssiges Deutsch bleiben.

Schweregrade:
- high: der Fehler verändert die Hauptaussage der Zusammenfassung
- medium: eine Nebeninformation ist falsch
- low: ein kleines Detail ist falsch, die Bedeutung bleibt weitgehend erhalten

So sehen solche Fehler aus:

{examples}

## Artikel
{article}

## Zusammenfassung
{summary}

Antworte nur mit JSON, ohne weiteren Text:
{"modified_summary": "<die geänderte Zusammenfassung>", "change": "<kurz: was wurde geändert>"}
