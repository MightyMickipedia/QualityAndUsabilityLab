// The four looks. All are plain black with a dark "LLM judge" picture behind the content.
// Fonts are ones PowerPoint has everywhere (Calibri, Cambria, Arial, Courier New).
module.exports = {
  gavel: {
    label: "Gavel",
    bg: "bg-gavel.png",
    head: "Calibri", body: "Calibri",
    accent: "F5B841",          // amber
    text: "F2F2F2", muted: "8C8C8C", line: "2E2E2E", cell: "0E0E0E",
    titlePrefix: "", deco: "underline",
  },
  scales: {
    label: "Scales",
    bg: "bg-scales.png",
    head: "Cambria", body: "Calibri",
    accent: "5EC7BE",          // teal
    text: "EEF4F3", muted: "86A3A0", line: "1F3331", cell: "07100F",
    titlePrefix: "", deco: "rule",
  },
  terminal: {
    label: "Terminal",
    bg: "bg-terminal.png",
    head: "Courier New", body: "Calibri",
    accent: "7EE787",          // green
    text: "E6F2E6", muted: "7E947E", line: "1E2E1E", cell: "070D07",
    titlePrefix: "$ ", deco: "brackets",
  },
  redpen: {
    label: "Red pen",
    bg: "bg-redpen.png",
    head: "Arial", body: "Arial",
    accent: "FF6B6B",          // coral red
    text: "F5EFEF", muted: "9A8A8A", line: "352222", cell: "100909",
    titlePrefix: "", deco: "margin",
  },
};
