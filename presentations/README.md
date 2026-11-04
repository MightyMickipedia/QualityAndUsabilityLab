# Weekly update slides

Neha asked for 2-3 update slides every week (meeting 28.10.2026). This folder has a reusable template: plain black, a dark "LLM judge" picture (scales of justice) in the background, the week number and date at the top, and slide numbers at the bottom.

## Folders

- `build/` - the generator (`deck.js`), the style (`styles.js`), the background picture (`backgrounds.js` -> `assets/bg-scales.png`)
- `week-01/` - `content.js` (this week's text) and `week-01.pptx`

## New week

```bash
mkdir presentations/week-02
cp presentations/week-01/content.js presentations/week-02/
# edit presentations/week-02/content.js (week, date, slide text)
cd presentations/build
npm install                # once
./build.sh week-02         # -> presentations/week-02/week-02.pptx
```

Slide types in `content.js`: `done` (project manager, headline, who did what), `table` (header + rows), `questions` (numbered list + a box on the right). Add more types in `deck.js` if a week needs them.

`build.sh` uses LibreOffice and `pdftoppm` to make a PDF and preview images in `build/preview/` (not committed). If the local pptx skill is installed, it also validates the file; set `PY=/path/to/python` to a Python with `defusedxml` and `lxml`.
