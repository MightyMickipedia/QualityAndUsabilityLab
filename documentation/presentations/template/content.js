// Template for the weekly update slides.
// Copy this folder to week-NN, replace the placeholder text, then run: cd ../build && ./build.sh week-NN
// Delete the slides you don't need. Neha asked for 2-3 slides, the first and the last two are the core.
module.exports = {
  week: 3,                 // week number
  date: "DD.MM.2026",      // date of the meeting
  project: "LLM judges on German news summaries",

  slides: [
    // 1. Who did what. One line per person, keep the order.
    {
      type: "done",
      title: "Done this week",
      pm: "Project manager: name",
      headline: "One sentence with the main result of the week",
      headlineNote: "folder/or/file where the result is",
      rows: [
        ["Giuseppe", "What he did. Numbers if there are any."],
        ["Malte", "What he did."],
        ["Anton", "What he did."],
        ["Mick", "What he did."],
        ["Ivan", "What he did."],
      ],
    },
    // 2. One screenshot with two short points next to it.
    {
      type: "image",
      title: "Topic (name)",
      image: "placeholder.png",
      alt: "What the screenshot shows",
      heading: "path/of/the/file.md",
      points: [
        "First point.",
        "Second point.",
      ],
    },
    // 3. Two or three screenshots side by side, each with a caption.
    {
      type: "images",
      title: "Topic (names)",
      images: [
        { image: "placeholder_small.png", caption: "Name · file", alt: "What the screenshot shows" },
        { image: "placeholder_small.png", caption: "Name · file", alt: "What the screenshot shows" },
      ],
    },
    // 4. Plan for the coming week.
    {
      type: "plain",
      title: "Next steps",
      heading: "Kickoff timeline, dd.-dd.mm.: what the timeline says",
      paragraphs: [
        "First step.",
        "Second step.",
        "Who does what.",
      ],
    },
    // 5. Questions. Remove the slide if there are none.
    {
      type: "plain",
      title: "Questions for Neha",
      heading: "Topics in three words",
      paragraphs: [
        "First question.",
        "Second question.",
      ],
    },
  ],
};
