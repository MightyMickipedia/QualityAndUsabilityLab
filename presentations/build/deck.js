// Builds one weekly deck in one or more styles.
// Usage: node deck.js <week-folder> [style ...]
//   node deck.js week-01                 -> scales (the team's style)
//   node deck.js week-01 all             -> all four styles
//   node deck.js week-01 gavel terminal  -> only these
// Output: presentations/<week-folder>/<style>/<week-folder>-<style>.pptx
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const STYLES = require("./styles");

// Optional: write theme colours/fonts into the file with the local pptx skill, if present.
// Without it the deck still builds (colours are set on every object anyway).
let applyTheme = async () => {};
try {
  const base = path.join(process.env.HOME, ".claude/skills/synced");
  const skill = fs.readdirSync(base).map((d) => path.join(base, d, "pptx"))
    .find((p) => fs.existsSync(path.join(p, "scripts/apply_theme.js")));
  if (skill) applyTheme = require(path.join(skill, "scripts/apply_theme.js")).applyTheme;
} catch (e) { /* no skill installed */ }

const W = 10, H = 5.625;
const pad2 = (n) => String(n).padStart(2, "0");

// Text box with fixed defaults; every call gets a fresh options object.
function T(slide, text, o) {
  slide.addText(text, Object.assign({ isTextBox: true, margin: 0, valign: "top", fit: "none" }, o));
}

function themeFor(s) {
  return {
    name: `Weekly ${s.label}`, headFontFace: s.head, bodyFontFace: s.body,
    colors: { dk1: s.text, lt1: "000000", dk2: s.muted, lt2: s.cell, accent1: s.accent, accent2: s.muted,
      accent3: s.line, accent4: s.cell, accent5: s.text, accent6: s.accent, hlink: s.accent, folHlink: s.muted },
  };
}

// The reusable frame: background picture, week label, project name, slide number, title.
function defineLayout(pres, s, c) {
  const weekLabel = s.deco === "brackets" ? `[ week ${pad2(c.week)} · ${c.date} ]` : `WEEK ${pad2(c.week)}  ·  ${c.date}`;
  const objects = [
    { image: { x: 0, y: 0, w: W, h: H, path: path.join(__dirname, "assets", s.bg) } },
    { text: { text: weekLabel, options: { x: 0.5, y: 0.22, w: 4.5, h: 0.25, fontFace: s.deco === "brackets" ? s.head : s.body, fontSize: 9, bold: true, color: s.accent, charSpacing: 1.5, margin: 0 } } },
    { text: { text: c.project, options: { x: 5, y: 0.22, w: 4.5, h: 0.25, fontFace: s.body, fontSize: 9, color: s.muted, align: "right", margin: 0 } } },
    { text: { text: "Weekly update", options: { x: 0.5, y: 5.22, w: 4, h: 0.22, fontFace: s.body, fontSize: 8, color: s.muted, margin: 0 } } },
  ];
  if (s.deco === "rule") objects.push({ line: { x: 0.5, y: 0.52, w: 9, h: 0, line: { color: s.line, width: 0.75 } } });
  if (s.deco === "underline") objects.push({ line: { x: 0.5, y: 1.2, w: 0.7, h: 0, line: { color: s.accent, width: 2.5 } } });
  if (s.deco === "margin") objects.push({ line: { x: 0.3, y: 0, w: 0, h: H, line: { color: s.accent, width: 1 } } });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: "000000" },
    objects,
    slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontFace: s.body, fontSize: 9, color: s.accent, align: "right" },
    placeholders: undefined,
  });
}

function title(slide, s, text) {
  T(slide, (s.titlePrefix || "") + text, { x: 0.5, y: 0.58, w: 9, h: 0.55, fontFace: s.head, fontSize: 26, bold: true, color: s.text, objectName: "Title" });
}

function slideDone(pres, s, d) {
  const slide = pres.addSlide({ masterName: "CONTENT" });
  title(slide, s, d.title);
  // Project manager badge
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.36, w: 3.45, h: 0.32, rectRadius: 0.08, fill: { color: s.cell }, line: { color: s.accent, width: 1 }, objectName: "PM badge" });
  T(slide, d.pm, { x: 0.62, y: 1.36, w: 3.25, h: 0.32, valign: "middle", fontFace: s.body, fontSize: 11, color: s.text });
  // Headline
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.88, w: 0.06, h: 0.62, fill: { color: s.accent }, line: { type: "none" }, objectName: "Headline bar" });
  T(slide, [
    { text: d.headline, options: { bold: true, color: s.text, fontSize: s.body === "Arial" ? 11.5 : 12.5, breakLine: true } },
    { text: d.headlineNote, options: { color: s.muted, fontSize: 9.5, fontFace: s.deco === "brackets" ? "Courier New" : s.body } },
  ], { x: 0.7, y: 1.86, w: 8.8, h: 0.68, fontFace: s.body, valign: "top" });
  // Who did what
  let y = 2.8;
  d.rows.forEach(([who, what]) => {
    const lines = Math.ceil(what.length / 100);
    const h = 0.18 + 0.2 * lines;
    T(slide, who, { x: 0.5, y, w: 1.3, h, fontFace: s.body, fontSize: 12, bold: true, color: s.accent });
    T(slide, what, { x: 1.9, y, w: 7.6, h, fontFace: s.body, fontSize: 12, color: s.text });
    y += h;
  });
}

function slideTable(pres, s, d) {
  const slide = pres.addSlide({ masterName: "CONTENT" });
  title(slide, s, d.title);
  const border = { type: "solid", pt: 0.5, color: s.line };
  const head = d.header.map((t) => ({ text: t, options: { bold: true, color: s.accent, fill: { color: "000000" }, border } }));
  let prevDim = "";
  const body = d.rows.map((r) => {
    const dim = r[0] === prevDim ? "" : r[0]; prevDim = r[0];
    return r.map((t, i) => ({ text: i === 0 ? dim : t, options: {
      color: i === 0 ? s.muted : s.text, bold: i === 1, fill: { color: s.cell }, border,
      fontFace: i === 1 && s.deco === "brackets" ? "Courier New" : s.body } }));
  });
  slide.addTable([head, ...body], { x: 0.5, y: 1.3, w: 9, colW: [1.1, 1.8, 2.35, 3.75], fontSize: 10, fontFace: s.body,
    rowH: 0.27, margin: [2, 6, 2, 6], valign: "middle", objectName: "Taxonomy excerpt" });
  T(slide, d.note, { x: 0.5, y: 4.82, w: 8.4, h: 0.25, fontFace: s.body, fontSize: 9, italic: true, color: s.muted });
}

function slideQuestions(pres, s, d) {
  const slide = pres.addSlide({ masterName: "CONTENT" });
  title(slide, s, d.title);
  // Numbers are written as text: LibreOffice renders separate numbered paragraphs as "1." each.
  const list = (items, numbered) => items.flatMap((t, i) => [
    { text: numbered ? `${i + 1}  ` : "■  ", options: { bold: true, color: s.accent } },
    { text: t, options: { breakLine: i < items.length - 1, paraSpaceAfter: 5 } }]);
  T(slide, d.left.heading, { x: 0.5, y: 1.3, w: 5.7, h: 0.3, fontFace: s.body, fontSize: 12, bold: true, color: s.accent });
  T(slide, list(d.left.items, true), { x: 0.5, y: 1.62, w: 5.7, h: 3.5, fontFace: s.body, fontSize: 10.5, color: s.text });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 1.3, w: 3.0, h: 2.15, rectRadius: 0.08, fill: { color: s.cell }, line: { color: s.accent, width: 1 }, objectName: "Requests box" });
  T(slide, d.right.heading, { x: 6.7, y: 1.45, w: 2.6, h: 0.3, fontFace: s.body, fontSize: 12, bold: true, color: s.accent });
  T(slide, list(d.right.items, false), { x: 6.7, y: 1.8, w: 2.65, h: 1.55, fontFace: s.body, fontSize: 10.5, color: s.text });
}

async function build(weekDir, styleKey) {
  const c = require(path.join(weekDir, "content.js"));
  const s = STYLES[styleKey];
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = `Weekly update, week ${c.week}`;
  pres.subject = `${c.project}, week ${c.week} (${c.date})`;
  pres.theme = { headFontFace: s.head, bodyFontFace: s.body };
  defineLayout(pres, s, c);
  for (const d of c.slides) ({ done: slideDone, table: slideTable, questions: slideQuestions })[d.type](pres, s, d);
  const name = path.basename(weekDir);
  const outDir = path.join(weekDir, styleKey);
  fs.mkdirSync(outDir, { recursive: true });
  const file = path.join(outDir, `${name}-${styleKey}.pptx`);
  await pres.writeFile({ fileName: file });
  await applyTheme(file, themeFor(s));
  return file;
}

(async () => {
  const [week, ...styles] = process.argv.slice(2);
  if (!week) { console.error("usage: node deck.js <week-folder> [style ...]"); process.exit(1); }
  const weekDir = path.resolve(__dirname, "..", week);
  // Default style is "scales" (chosen for the weekly updates); "all" builds every style.
  const keys = !styles.length ? ["scales"] : styles[0] === "all" ? Object.keys(STYLES) : styles;
  for (const k of keys) console.log(await build(weekDir, k));
})();
