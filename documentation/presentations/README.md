# Weekly update slides

Neha asked for 2-3 update slides every week (meeting 28.10.2026). This folder has a reusable template: plain black, a dark "LLM judge" picture (scales of justice) in the background, the week number and date at the top, and slide numbers at the bottom.

## Folders

- `build/` - the generator (`deck.js`), the style (`styles.js`), the background picture (`backgrounds.js` -> `assets/bg-scales.png`)
- `week-01/` - `content.js` (this week's text), `taxonomy.png` (screenshot for slide 2) and `week-01.pptx`

## New week

```bash
mkdir documentation/presentations/week-02
cp documentation/presentations/week-01/content.js documentation/presentations/week-02/
# edit documentation/presentations/week-02/content.js (week, date, slide text)
cd documentation/presentations/build
npm install                # once
./build.sh week-02         # -> documentation/presentations/week-02/week-02.pptx
```

Slide types in `content.js`: `done` (project manager, headline, who did what), `image` (a picture such as a screenshot, with a short list next to it), `images` (two or three pictures side by side with captions), `table` (header + rows), `plain` (heading + paragraphs), `questions` (numbered list + a box on the right).

To screenshot part of a markdown file for an `image` slide: `node build/screenshot.js ../Taxonomy.md "# Part 1" "¹ Table 1" week-01/taxonomy.png` (start line, end line; an optional page width in px as fifth argument makes the screenshot narrower). Add more types in `deck.js` if a week needs them.

`build.sh` uses LibreOffice and `pdftoppm` to make a PDF and preview images in `build/preview/` (not committed). If the local pptx skill is installed, it also validates the file; set `PY=/path/to/python` to a Python with `defusedxml` and `lxml`.
