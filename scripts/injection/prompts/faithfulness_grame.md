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

## Kontrolle und Ausgabe
Prüfe vor der Antwort intern:
1. Entspricht der Fehler ausschließlich dem Zieltyp und dem angeforderten Schweregrad?
2. Ist die neue Angabe gegenüber dem Artikel tatsächlich falsch?
3. Ist außerhalb der ausgewählten Stelle der gesamte Ausgangstext unverändert enthalten?
4. Passt die Änderung zur vorhandenen Grammatik?

Wenn keine geeignete Änderung für Typ und Schweregrad möglich ist, gib die vollständige Ausgangszusammenfassung unverändert zurück und beginne change mit "KEINE_PASSENDE_AENDERUNG:" samt kurzer Erklärung. Erzeuge keinen anderen Fehlertyp, um die Aufgabe scheinbar zu erfüllen.

Antworte ausschließlich mit einem gültigen JSON-Objekt mit genau zwei String-Feldern: modified_summary und change.
Verwende gerade doppelte Anführungszeichen für JSON-Schlüssel und Stringwerte. Maskiere Anführungszeichen und Zeilenumbrüche innerhalb der Strings korrekt. Kein Markdown-Codeblock und kein Text außerhalb des JSON-Objekts.
{"modified_summary": "<die vollständige geänderte Zusammenfassung>", "change": "<ursprüngliche Stelle> -> <neue Stelle>; kurze Erklärung des sachlichen Fehlers"}
