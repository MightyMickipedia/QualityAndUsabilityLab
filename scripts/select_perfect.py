"""Select "perfect" (rated 7) summaries from the annotation data."""

import argparse
import json
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "annotated_news_summaries" / "data_files" / "annotations_exactly_3_annotators.jsonl"
DEFAULT_OUTDIR = ROOT / "data"
DIMENSIONS = {"faithfulness": "d7", "coverage": "d6"}
START, END = "<!-- COUNTS:START -->", "<!-- COUNTS:END -->"


def is_perfect(ratings, criterion, threshold):
    if not ratings:
        return False
    if criterion == "A":
        return all(r == 7 for r in ratings)
    if criterion == "B":
        return statistics.mean(ratings) >= threshold
    return any(r == 7 for r in ratings)  # C


# Repair double-encoded UTF-8 (Example: "zerstÃ¶rt" -> "zerstört")
MOJIBAKE = re.compile(r"Ã.|Â.|â€.")


def _redecode(s):
    try:
        return s.encode("cp1252").decode("utf-8")
    except UnicodeError:
        return None


def fix_text(text):
    if not isinstance(text, str):
        return text
    return _redecode(text) or MOJIBAKE.sub(lambda m: _redecode(m.group()) or m.group(), text)


def load_grouped(path):
    """One record per (item_id, model), collecting the ratings of all annotators."""
    groups, n_rows = {}, 0
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"WARNING: line {line_no} skipped ({e})", file=sys.stderr)
                continue
            n_rows += 1
            key = (row["item_id"], row["model"])
            g = groups.setdefault(key, {
                "item_id": key[0], "model": key[1],
                "title": fix_text(row.get("title")),
                "article": fix_text(row.get("article")),
                "summary": fix_text(row.get("summary")),
                "ratings_d6_coverage": [], "ratings_d7_faithfulness": [],
                "n_annotators": 0,
            })
            g["n_annotators"] += 1
            for field, name in (("d6", "ratings_d6_coverage"), ("d7", "ratings_d7_faithfulness")):
                value = row.get(field)
                if value not in (None, ""):
                    v = float(value)
                    g[name].append(int(v) if v.is_integer() else v)
    return groups, n_rows


def write_sample(path, dim, field, records, k, seed):
    sample = random.Random(seed).sample(records, min(k, len(records)))
    lines = [f"# Sample: perfect {dim} summaries ({field} = 7)", "",
             f"{len(sample)} randomly drawn summaries (seed={seed}) out of {len(records)}.", ""]
    for i, r in enumerate(sample, 1):
        summary = str(r["summary"]).strip().replace("\n", "\n> ")
        lines += ["---", "", f"## {i}. item_id `{r['item_id']}` - model `{r['model']}`", "",
                  f"**Title:** {r['title']}", "",
                  f"**Ratings d7 (Faithfulness):** {r['ratings_d7_faithfulness']}  ",
                  f"**Ratings d6 (Coverage):** {r['ratings_d6_coverage']}  ",
                  f"**Annotators:** {r['n_annotators']}", "",
                  "**Summary:**", "", f"> {summary}", "",
                  "**Article:**", "", str(r["article"]).strip(), ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def update_readme(path, block):
    """Replace only the block between the markers; the rest of the README stays untouched."""
    text = path.read_text(encoding="utf-8") if path.exists() else "# data/\n"
    if START not in text:
        text += f"\n## Counts per option\n\n{START}\n{END}\n"
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    path.write_text(f"{head}{START}\n{block}\n{END}{tail}", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    ap.add_argument("--criterion", choices=["A", "B", "C"], default="A",
                    help="A: all 7 | B: mean >= threshold | C: at least one 7 (default: A)")
    ap.add_argument("--mean-threshold", type=float, default=6.5,
                    help="threshold for option B (default 6.5; 7 = mean exactly 7)")
    ap.add_argument("--sample-size", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: input file not found: {args.input}")
    groups, n_rows = load_grouped(args.input)
    if not groups:
        sys.exit("ERROR: no data read from the input file.")
    args.outdir.mkdir(parents=True, exist_ok=True)

    def ratings(g, field):
        return g["ratings_d7_faithfulness" if field == "d7" else "ratings_d6_coverage"]

    # counts for all options
    counts = {opt: {f: sum(is_perfect(ratings(g, f), opt, args.mean_threshold) for g in groups.values())
                    for f in ("d7", "d6")} for opt in "ABC"}

    # files for the chosen option
    for dim, field in DIMENSIONS.items():
        selected = [g for g in groups.values()
                    if is_perfect(ratings(g, field), args.criterion, args.mean_threshold)]
        out = args.outdir / f"perfect_{dim}.jsonl"
        with open(out, "w", encoding="utf-8") as f:
            for rec in selected:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        write_sample(args.outdir / f"sample_{dim}.md", dim, field, selected, args.sample_size, args.seed)
        print(f"[option {args.criterion}] {out.name}: {len(selected)} summaries")

    block = "\n".join([
        f"Input: `{args.input.name}` - {n_rows} annotator rows, {len(groups)} unique summaries (item_id + model).",
        "",
        "| Option | Definition | Faithfulness (d7) | Coverage (d6) |",
        "|---|---|---|---|",
        f"| A | every annotator gave 7 (strict) | {counts['A']['d7']} | {counts['A']['d6']} |",
        f"| B | mean >= {args.mean_threshold:g} | {counts['B']['d7']} | {counts['B']['d6']} |",
        f"| C | at least one annotator gave 7 (loose) | {counts['C']['d7']} | {counts['C']['d6']} |",
        "",
        f"Currently written files use option **{args.criterion}**"
        + (f" (threshold {args.mean_threshold:g})" if args.criterion == "B" else "") + ".",
    ])
    update_readme(args.outdir / "README.md", block)

    print("\nCounts per option (unique summaries):")
    for opt in "ABC":
        print(f"  {opt}: d7 faithfulness={counts[opt]['d7']}, d6 coverage={counts[opt]['d6']}")
    print(f"\nTotal: {n_rows} rows, {len(groups)} unique summaries. README updated.")


if __name__ == "__main__":
    main()