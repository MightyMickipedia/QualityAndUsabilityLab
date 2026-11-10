Du bekommst einen Nachrichtenartikel und eine fehlerfreie Zusammenfassung dieses Artikels.
Baue genau EINEN Fehler vom Typ {error_type} mit Schweregrad {severity} in die Zusammenfassung ein.
Ändere sonst nichts. Alle anderen Sätze sollen flüssiges Deutsch bleiben.

Fehlertyp GramE (Grammatikfehler): Die Grammatik eines Satzes ist so fehlerhaft, dass er bedeutungslos wird.
- Brich in genau einem Satz eine Konstruktion so, dass nicht mehr erkennbar ist, wer was tut (zum Beispiel falscher Kasus beim Subjekt oder ein unmögliches Passiv).
- Lösche keine Satzteile und ändere keine Inhaltswörter.
- Kleine Fehler wie ein falscher Artikel, eine falsche Endung oder ein fehlendes Komma zählen nicht.

Schweregrade:
- high: die Hauptaussage der Zusammenfassung ist nicht mehr verständlich
- medium: eine Nebeninformation ist nicht mehr verständlich
- low: ein kleines Detail ist nicht mehr verständlich, die Bedeutung bleibt weitgehend erhalten

So sehen solche Fehler aus:

{examples}

## Artikel
{article}

## Zusammenfassung
{summary}

Antworte nur mit JSON, ohne weiteren Text:
Schreibe Anführungszeichen innerhalb der Texte als \" und Zeilenumbrüche als \n. Kein Text vor oder nach dem JSON, kein ```-Block.
{"modified_summary": "<die geänderte Zusammenfassung>", "change": "<kurz: was wurde geändert>"}
