// Renders a chunk of a markdown file the way GitHub shows it and saves it as a PNG for the slides.
// Usage: node screenshot.js <markdown file> "<start line>" "<end line (exclusive)>" <out.png>
// Example: node screenshot.js ../../Taxonomy.md "# Part 1" "¹ Table 1" ../week-01/taxonomy.png
// Needs Chrome/Chromium; set CHROME=/path/to/chrome if it is not found.
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const { marked } = require("marked");
const sharp = require("sharp");

const [mdFile, startMark, endMark, out] = process.argv.slice(2);
if (!out) { console.error('usage: node screenshot.js <file.md> "<start>" "<end>" <out.png>'); process.exit(1); }

const md = fs.readFileSync(mdFile, "utf8");
const a = md.indexOf(startMark), b = md.indexOf(endMark, a + 1);
if (a < 0 || b < 0) throw new Error("start or end marker not found");
const chunk = md.slice(a, b);

const css = `
body{margin:0;background:#fff;color:#1f2328;font:15px/1.5 -apple-system,"Segoe UI","Liberation Sans",Arial,sans-serif}
.page{width:1180px;padding:28px 36px}
.bar{font:13px "Liberation Mono",monospace;color:#59636e;border:1px solid #d1d9e0;border-bottom:0;border-radius:6px 6px 0 0;background:#f6f8fa;padding:8px 14px}
.md{border:1px solid #d1d9e0;border-radius:0 0 6px 6px;padding:20px 28px}
h1{font-size:26px;border-bottom:1px solid #d1d9e0;padding-bottom:6px;margin:0 0 12px}
h2{font-size:20px;border-bottom:1px solid #d1d9e0;padding-bottom:4px;margin:18px 0 10px}
blockquote{margin:0 0 12px;padding:0 14px;color:#59636e;border-left:4px solid #d1d9e0}
table{border-collapse:collapse;font-size:13px}
th,td{border:1px solid #d1d9e0;padding:5px 10px;vertical-align:top}
th{background:#f6f8fa} tr:nth-child(2n) td{background:#f6f8fa}
p{margin:0 0 10px}`;
const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><div class="page">
<div class="bar">documentation/Taxonomy.md</div><div class="md">${marked.parse(chunk)}</div></div>`;

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "mdshot-"));
fs.writeFileSync(path.join(tmp, "page.html"), html);
const chrome = process.env.CHROME || (() => {
  const base = path.join(os.homedir(), ".t3/tools/chrome-headless-shell");
  for (const p of [base]) if (fs.existsSync(p)) {
    const found = execFileSync("find", [p, "-name", "chrome-headless-shell", "-type", "f"]).toString().trim().split("\n")[0];
    if (found) return found;
  }
  return "chromium";
})();
const raw = path.join(tmp, "raw.png");
execFileSync(chrome, ["--headless", "--hide-scrollbars", "--force-device-scale-factor=2",
  "--window-size=1252,2400", `--screenshot=${raw}`, `file://${path.join(tmp, "page.html")}`], { stdio: "ignore" });
// Cut the empty white space below the content.
sharp(raw).trim({ background: "#ffffff", threshold: 2 }).extend({ top: 24, bottom: 24, left: 24, right: 24, background: "#ffffff" })
  .png().toFile(out).then((i) => console.log(out, `${i.width}x${i.height}`));
