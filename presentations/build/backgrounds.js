// Renders the four "LLM judge" background images (1920x1080 PNG, very dark line art on black).
// Run: node backgrounds.js   -> writes assets/bg-<style>.png
const fs = require("fs");
const path = require("path");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const pi = require("react-icons/pi");

const W = 1920, H = 1080;
const OUT = path.join(__dirname, "assets");
fs.mkdirSync(OUT, { recursive: true });

// One icon as an SVG fragment at (x, y) with the given size, colour and rotation.
function icon(name, x, y, size, color, rotate = 0) {
  const svg = renderToStaticMarkup(React.createElement(pi[name], { size, color }));
  const c = size / 2;
  return `<g transform="translate(${x},${y}) rotate(${rotate},${c},${c})">${svg}</g>`;
}
function dots(color, step = 48, r = 1.6) {
  let s = "";
  for (let x = step / 2; x < W; x += step) for (let y = step / 2; y < H; y += step)
    s += `<circle cx="${x}" cy="${y}" r="${r}" fill="${color}"/>`;
  return s;
}
const svgDoc = (body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="100%" height="100%" fill="#000"/>${body}</svg>`;

const BG = {
  // Robot judge holding a gavel, large on the right.
  gavel: svgDoc(
    icon("PiRobotThin", 900, 80, 1100, "#191919") +
    icon("PiGavelThin", 600, 640, 460, "#221d13", -25)),
  // Scales of justice with a small robot head as the weight on one side.
  scales: svgDoc(
    icon("PiScalesThin", 760, -40, 1200, "#121d1c") +
    icon("PiRobotThin", 1595, 430, 210, "#172423")),
  // Terminal look: faint dot grid and a huge cropped robot bottom right.
  terminal: svgDoc(
    dots("#0c120c") +
    icon("PiRobotThin", 1050, 160, 1150, "#101a10")),
  // Red pen look: a document under a magnifying glass, with check marks.
  redpen: svgDoc(
    icon("PiFileMagnifyingGlassThin", 950, 60, 1000, "#1c1212") +
    icon("PiChecksThin", 760, 700, 380, "#231313", -8)),
};

(async () => {
  for (const [k, svg] of Object.entries(BG)) {
    const f = path.join(OUT, `bg-${k}.png`);
    await sharp(Buffer.from(svg)).png().toFile(f);
    console.log(f);
  }
})();
