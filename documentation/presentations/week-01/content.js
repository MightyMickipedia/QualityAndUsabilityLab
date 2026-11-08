// Week 1 content. Copy this folder for the next week and edit only this file.
// Source of the text: "documentation/Ivan proposal/templates/weekly_update.md".
module.exports = {
  week: 1,
  date: "04.11.2026",
  project: "LLM judges on German news summaries",

  slides: [
    {
      type: "done",
      title: "Done this week",
      pm: "Project manager: Ivan (we may rotate later)",
      headline: "Taxonomy complete: 7 faithfulness types (FRANK) + 4 coverage types (APPLS), 2 examples each, 22 in total",
      headlineNote: "documentation/Taxonomy.md",
      rows: [
        ["Giuseppe", "select_perfect.py picks the \"perfect\" summaries. Option A (all 3 annotators gave 7): 100 faithfulness, 66 coverage."],
        ["Malte", "PredE, EntE, CircE, 2 examples each."],
        ["Anton", "CorefE, LinkE, OutE, GramE, German explanations and 1 example each."],
        ["Mick", "Delete sentences, add out-of-domain, add in-domain, add definitions, 2 examples each."],
        ["Ivan", "Merged everything into Taxonomy.md with the definitions from the papers, the second example for Anton's 4 types, 8 more coverage examples, and all 30 examples with full summaries in examples.csv."],
      ],
    },
    {
      type: "image",
      title: "The taxonomy file",
      image: "taxonomy.png",
      alt: "Screenshot of documentation/Taxonomy.md, Part 1: the 7 FRANK error types with definition, paper example and German explanation",
      heading: "documentation/Taxonomy.md",
      points: [
        "One file for both taxonomies: Part 1 faithfulness (FRANK, 7 types), Part 2 coverage (APPLS, 4 types).",
        "Per type: the paper's definition and example, a German explanation, 2 examples from our dataset.",
        "Each example: original, modified, what changed, severity.",
        "All 30 examples with full summaries: data/examples/examples.csv.",
      ],
    },
    {
      type: "table",
      title: "Taxonomy overview",
      note: "from documentation/Taxonomy.md · full definitions, German explanations and both examples per type are in the file",
      header: ["Dimension", "Type", "German name", "Example change"],
      rows: [
        ["Faithfulness", "PredE", "Prädikatfehler", "„abschaffen“ → „beibehalten“"],
        ["Faithfulness", "EntE", "Entitätsfehler", "„Die CDU“ → „Die SPD“"],
        ["Faithfulness", "CircE", "Umstandsfehler", "„in Greifswald“ → „in Rostock“"],
        ["Faithfulness", "CorefE", "Koreferenzfehler", "„Sie“ (Esken) → „Er“ (Zuckerberg)"],
        ["Faithfulness", "LinkE", "Verknüpfungsfehler", "„nachdem“ → „bevor“"],
        ["Faithfulness", "OutE", "Information nicht im Artikel", "+ „Grönland hat rund 56.000 Einwohner.“"],
        ["Faithfulness", "GramE", "Grammatikfehler", "„wird von der SEC verklagt“ → „wird die SEC verklagt“"],
        ["Coverage", "Delete sentences", "Sätze löschen", "sentence on genetic differences and aggression deleted (ants)"],
        ["Coverage", "Add out-of-domain", "Themenfremden Satz hinzufügen", "+ battery sentence in a Panama Canal summary"],
        ["Coverage", "Add in-domain", "Themennahen Satz hinzufügen", "+ invented phone call between Frederiksen and Trump"],
        ["Coverage", "Add definitions", "Definition hinzufügen", "+ definition of „Abholzung“"],
      ],
    },
    {
      type: "plain",
      title: "Questions & Requests for Neha",
      heading: "About our work",
      paragraphs: [
        "We weren't sure how to build the taxonomy, so we did it our way: paper definition, German explanation, 2 examples per type. Is this format fine?",
        "Could you send us the most recent presentation? We don't think we have access to it.",
      ],
    },
  ],
};
