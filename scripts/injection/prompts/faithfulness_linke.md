Du bekommst einen Nachrichtenartikel und eine fehlerfreie Zusammenfassung dieses Artikels.
Baue genau EINEN Fehler vom Typ {error_type} mit Schweregrad {severity} in die Zusammenfassung ein.
Ändere sonst nichts. Die Zusammenfassung soll flüssiges Deutsch bleiben.

Fehlertyp LinkE (Verknüpfungsfehler): Die Verbindung zwischen zwei Aussagen ist falsch, etwa die zeitliche Abfolge oder der kausale Zusammenhang.
- Tausche ein Verknüpfungswort (nachdem → bevor, aber → deshalb, obwohl → weil) oder vertausche Ursache und Wirkung.
- Jede Aussage für sich bleibt richtig, nur ihre Verbindung stimmt nicht mehr.
- Ändere keine Namen, Zahlen, Orte oder Zeitangaben.

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
Schreibe Anführungszeichen innerhalb der Texte als \" und Zeilenumbrüche als \n. Kein Text vor oder nach dem JSON, kein ```-Block.
{"modified_summary": "<die geänderte Zusammenfassung>", "change": "<kurz: was wurde geändert>"}
