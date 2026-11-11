// Week 2 content.
module.exports = {
  week: 2,
  date: "11.11.2026",
  project: "LLM judges on German news summaries",

  slides: [
    {
      type: "done",
      title: "Done this week",
      pm: "Project manager: Ivan",
      headline: "Error injection works for all 11 error types: 9 prompts, 94 test outputs in one shared format",
      headlineNote: "scripts/injection/ · data/injected/",
      rows: [
        ["Giuseppe", "Data v2: summaries with 2 or 3 annotators, 226 faithfulness / 144 coverage. HTML tags and umlauts cleaned, sentence count added."],
        ["Malte", "Prompts for PredE, EntE, CircE. 30 test outputs, all checked by hand: 26 OK, 4 with a problem. Model: nemotron-3.5-super-vl (free)."],
        ["Anton", "Prompts for CorefE, LinkE, OutE, GramE. 24 test outputs. Model: nemotron-3-ultra (free)."],
        ["Mick", "Prompts and a helper script for the 4 coverage types. 40 test outputs. Model: gpt-6-luna."],
        ["Ivan", "Shared output format and runner, severity scale, last semester's scripts mapped to our error types, research questions. Runner tested with nemotron-3.5-super-vl (free)."],
      ],
    },
    {
      type: "image",
      title: "Research questions",
      image: "research_questions.png",
      alt: "Screenshot of documentation/research_questions.md: RQ1 error sensitivity, RQ2 faithfulness vs coverage, RQ3 prompt design, and how we measure them",
      heading: "documentation/research_questions.md",
      points: [
        "Three questions, close to the kickoff slides.",
        "We count how often the judge picks the original summary.",
      ],
    },
    {
      type: "images",
      title: "Data v2 (Giuseppe)",
      images: [
        { image: "data_cleaning.png", caption: "data/README.md · text cleaning", alt: "Screenshot of data/README.md, section Text cleaning: tags removed, umlauts repaired, outer quotes removed" },
        { image: "data_counts.png", caption: "data/README.md · counts", alt: "Screenshot of data/README.md, counts for data v2: option A gives 226 faithfulness and 144 coverage summaries" },
      ],
    },
    {
      type: "image",
      title: "Shared output format (Ivan)",
      image: "format.png",
      alt: "Screenshot of scripts/injection/README.md: the table of output fields, one JSON line per modified summary",
      heading: "scripts/injection/README.md",
      points: [
        "One JSON line per modified summary, the same fields for every error type.",
        "The runner fills the prompt, calls the model and writes this format.",
      ],
    },
    {
      type: "images",
      title: "Prompts (Malte, Anton, Mick)",
      images: [
        { image: "prompt_malte.png", caption: "Malte · semantic_frame_ente.md", alt: "Screenshot of Malte's German prompt for the entity error (EntE) with rules for what may be changed" },
        { image: "prompt_anton.png", caption: "Anton · faithfulness_corefe.md", alt: "Screenshot of Anton's German prompt for the coreference error (CorefE) with rules and severity levels" },
        { image: "prompt_mick.png", caption: "Mick · coverage_add.md", alt: "Screenshot of Mick's German prompt for adding one sentence to a summary (coverage errors)" },
      ],
    },
    {
      type: "image",
      title: "Checking the outputs",
      image: "review.png",
      alt: "Screenshot of data/injected/semantic_frame_review.md: Malte's review table of the PredE test outputs with two flagged rows",
      heading: "data/injected/semantic_frame_review.md",
      points: [
        "Example: Malte's written review of his 30 outputs.",
        "26 OK, 4 with a problem.",
      ],
    },
    {
      type: "plain",
      title: "Next steps",
      heading: "Kickoff timeline, 11.-25.11.: create the final error-injected data",
      paragraphs: [
        "We keep the 94 outputs we have. All of them use summaries that are also in data v2.",
        "Next week we add 150 to 200 more, so every error type has about 25.",
        "All five of us check the outputs, about 50 each.",
        "Before that: small fixes to the prompts and the data from this week's review.",
      ],
    },
    {
      type: "plain",
      title: "Questions for Neha",
      heading: "Rubric, compute, severity",
      paragraphs: [
        "Rubric: the timeline says \"rubric for rating to be provided\". Which rubric is meant? We found the 7-point faithfulness scale in last semester's script. Is it this one?",
        "Compute: free models limit the number of calls per day, and running an open model on our own PCs is slow (about 10 minutes for a long prompt). So we are limited in how much data we can create. Which models may we use, is a closed one like gpt-6-luna fine, and can the university provide access?",
        "Severity: the models set low / medium / high unreliably. We would label the severity by hand when we check the outputs. Is that fine?",
      ],
    },
    {
      type: "images",
      title: "Reference: kickoff timeline, phase 2",
      images: [
        { image: "kickoff_phase2.png", caption: "documentation/intro_kickoff.pdf", alt: "Kickoff timeline, phase 2: 28 Oct - 4 Nov error taxonomy, 4-11 Nov inject errors, 11-25 Nov rate the summaries and create the final error-injected data, 25 Nov - 9 Dec prepare the midterm presentation, 10 Dec midterm" },
      ],
    },
  ],
};
