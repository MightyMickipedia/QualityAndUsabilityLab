Du bekommst einen Nachrichtenartikel und eine fehlerfreie Zusammenfassung dieses Artikels.
Baue genau EINEN Fehler vom Typ {error_type} mit Schweregrad {severity} in die Zusammenfassung ein.
Ändere sonst nichts. Die Zusammenfassung soll flüssiges Deutsch bleiben.

Fehlertyp CorefE (Koreferenzfehler): Ein Pronomen oder eine Referenz hat ein falsches oder gar kein Bezugswort.
- Ersetze ein Pronomen durch ein anderes (er → sie, dessen → ihre) oder einen Namen durch ein Pronomen, das sich dann auf eine andere Person oder Sache bezieht.
- Ersetze keinen Namen durch einen anderen Namen. Das wäre ein Entitätsfehler.
- Passe nur die Verbform an, wenn die Grammatik es verlangt.
- Setze ein Pronomen nur dort ein, wo es grammatisch passt, nicht als Einschub (z. B. nicht „Kanzlerkandidatin, er, gewählt“).

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
