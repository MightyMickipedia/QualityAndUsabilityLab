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

Antworte nur mit JSON, ohne weiteren Text:
Schreibe Anführungszeichen innerhalb der Texte als \" und Zeilenumbrüche als \n. Kein Text vor oder nach dem JSON, kein ```-Block.
{"modified_summary": "<die geänderte Zusammenfassung>", "change": "<kurz: was wurde geändert>"}
