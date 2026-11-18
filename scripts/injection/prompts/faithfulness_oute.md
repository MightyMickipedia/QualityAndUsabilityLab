Du bekommst einen Nachrichtenartikel und eine fehlerfreie Zusammenfassung dieses Artikels.
Baue genau EINEN Fehler vom Typ {error_type} mit Schweregrad {severity} in die Zusammenfassung ein.
Ändere sonst nichts. Die Zusammenfassung soll flüssiges Deutsch bleiben.

Fehlertyp OutE (Information nicht im Artikel): Die Zusammenfassung enthält eine Information, die im Artikel nicht vorkommt, auch wenn sie in der Realität stimmt.
- Füge eine passende Information hinzu, als Satz, Nebensatz oder Einschub.
- Prüfe am Artikel, dass sie dort weder wörtlich noch sinngemäß steht. Wenn der Artikel „Anfang Januar“ nennt, ist „im Januar“ keine neue Information.
- Die Information darf dem Artikel nicht widersprechen. Vorhandene Aussagen bleiben unverändert.

Schweregrade:
- high: die neue Information betrifft die Hauptaussage der Zusammenfassung
- medium: die neue Information betrifft eine Nebeninformation
- low: die neue Information ist ein kleines Hintergrunddetail, die Bedeutung bleibt weitgehend erhalten

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
