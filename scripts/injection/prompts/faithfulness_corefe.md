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
