# Weekly update slides

Neha asked for 2-3 update slides every week (meeting 28.10.2026). This folder has a reusable template. The team uses the **Scales** style: plain black, a dark "LLM judge" picture in the background, the week number and date at the top, and slide numbers at the bottom.

## Styles

| Style | Background picture | Accent | Fonts |
|---|---|---|---|
| `gavel` | robot judge with a gavel | amber | Calibri |
| `scales` | scales of justice with a robot in one pan | teal | Cambria headings, Calibri text |
| `terminal` | dot grid and a large robot | green | Courier New headings, Calibri text |
| `redpen` | document under a magnifying glass, check marks | red | Arial |

## Folders

- `build/` - the generator (`deck.js`), the four styles (`styles.js`), the background pictures (`backgrounds.js` -> `assets/`)
- `week-01/` - `content.js` (this week's text) and `scales/week-01-scales.pptx` + `.pdf`

## New week

```bash
cp -r presentations/week-01 presentations/week-02
rm -r presentations/week-02/*/            # old decks
# edit presentations/week-02/content.js (week, date, slide text)
cd presentations/build
npm install                               # once
./build.sh week-02                        # Scales; ./build.sh week-02 all builds all four
```

Slide types in `content.js`: `done` (project manager, headline, who did what), `table` (header + rows), `questions` (numbered list + a box on the right). Add more types in `deck.js` if a week needs them.

`build.sh` uses LibreOffice for the PDF and `pdftoppm` for the preview images in `build/preview/` (not committed). If the local pptx skill is installed, it also validates the file; set `PY=/path/to/python` to a Python with `defusedxml` and `lxml`.
