"""Select "perfect" (rated 7) summaries from the annotation data."""

import argparse
import json
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "annotated_news_summaries" / "data_files" / "annotations_at_least_2_annotators.jsonl"
DEFAULT_OUTDIR = ROOT / "data"
DIMENSIONS = {"faithfulness": "d7", "coverage": "d6"}

def is_perfect(ratings, criterion, threshold):
    if not ratings:
        return False
    if criterion == "A":
        return all(r == 7 for r in ratings)
    if criterion == "B":
        return statistics.mean(ratings) >= threshold
    return any(r == 7 for r in ratings)  # C


#text cleaning 

MOJIBAKE = re.compile(r"Ã.|Â.|â€.")
BR_TAG = re.compile(r"<br\s*/?>", re.I)
ANY_TAG = re.compile(r"</?[A-Za-z][^>]*>")
QUOTE_PAIRS = {'"': '"', "„": "“", "“": "”", "”": "”", "«": "»", "»": "«"}
ALL_QUOTES = set(QUOTE_PAIRS) | set(QUOTE_PAIRS.values())


def _redecode(s):
    """Re-decode mojibake; bytes undefined in cp1252 (0x81, 0x8d, 0x8f, 0x90, 0x9d) pass through."""
    out = bytearray()
    for ch in s:
        try:
            out += ch.encode("cp1252")
        except UnicodeEncodeError:
            if ord(ch) > 255:
                return None
            out.append(ord(ch))
    try:
        return out.decode("utf-8")
    except UnicodeDecodeError:
        return None


STRAY = re.compile(r"[ÃÂ](?=[äöüßÄÖÜ])")

def fix_encoding(text):
    """Repair double-encoded UTF-8 ("zerstÃ¶rt" -> "zerstört")."""
    text = _redecode(text) or MOJIBAKE.sub(lambda m: _redecode(m.group()) or m.group(), text)
    return STRAY.sub("", text)

def strip_tags(text):
    """<br/> -> line break; all other tags are dropped, the text between them stays."""
    return ANY_TAG.sub("", BR_TAG.sub("\n", text))


def strip_outer_quotes(text):
    """Remove one pair of quotes around the whole text (only if no other quotes inside)."""
    if len(text) > 2 and QUOTE_PAIRS.get(text[0]) == text[-1]:
        inner = text[1:-1]
        if not any(c in ALL_QUOTES for c in inner):
            return inner.strip()
    return text


def clean(text, quotes=False):
    if not isinstance(text, str):
        return text
    text = strip_tags(fix_encoding(text)).strip()
    return strip_outer_quotes(text) if quotes else text


#sentence count

SENT_SPLIT = re.compile(r'(?:(?<=[.!?])|(?<=[.!?]["“”«]))\s+(?=["„“«]?[A-ZÄÖÜ0-9])')
ABBR = ("dr.", "prof.", "nr.", "bzw.", "ca.", "usw.", "vs.", "z. b.", "u. a.", "d. h.", "st.")


def count_sentences(text):
    """Approximate sentence count (regex; merges after common abbreviations and ordinals like '3.')."""
    parts = []
    for p in SENT_SPLIT.split(text.strip()):
        if parts and (parts[-1].lower().endswith(ABBR) or re.search(r"\b\d{1,2}\.$", parts[-1])):
            parts[-1] += " " + p
        elif p.strip():
            parts.append(p)
    return len(parts)


#loading

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
            g = groups.get(key)
            if g is None:
                summary = clean(row.get("summary"), quotes=True)
                g = groups[key] = {
                    "item_id": key[0], "model": key[1],
                    "title": clean(row.get("title")),
                    "article": clean(row.get("article")),
                    "summary": summary,
                    "ratings_d6_coverage": [], "ratings_d7_faithfulness": [],
                    "n_annotators": 0,
                    "n_sentences": count_sentences(summary) if isinstance(summary, str) else 0,
                }
            g["n_annotators"] += 1
            for field, name in (("d6", "ratings_d6_coverage"), ("d7", "ratings_d7_faithfulness")):
                value = row.get(field)
                if value not in (None, ""):
                    v = float(value)
                    g[name].append(int(v) if v.is_integer() else v)
    return groups, n_rows


#output

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
                  f"**Annotators:** {r['n_annotators']}  ",
                  f"**Sentences:** {r['n_sentences']}", "",
                  "**Summary:**", "", f"> {summary}", "",
                  "**Article:**", "", str(r["article"]).strip(), ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def update_readme(path, block, suffix):
    """Replace only the block between the markers (own markers per suffix)."""
    tag = f"COUNTS{suffix.upper()}"
    start, end = f"<!-- {tag}:START -->", f"<!-- {tag}:END -->"
    title = "Counts per option" + (f" ({suffix.strip('_')})" if suffix else "")
    text = path.read_text(encoding="utf-8") if path.exists() else "# data/\n"
    if start not in text:
        text += f"\n## {title}\n\n{start}\n{end}\n"
    head, rest = text.split(start, 1)
    tail = rest.split(end, 1)[1]
    path.write_text(f"{head}{start}\n{block}\n{end}{tail}", encoding="utf-8")


LEFTOVER = re.compile(r"</?[A-Za-z][^>]*>|Ã|Â|â€")


def count_leftovers(records):
    """Number of rows with HTML tags or broken umlauts in title/article/summary."""
    return sum(any(LEFTOVER.search(str(r[k] or "")) for k in ("title", "article", "summary"))
               for r in records)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    ap.add_argument("--suffix", default="_v2", help="suffix for output files (default _v2)")
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

    counts = {opt: {f: sum(is_perfect(ratings(g, f), opt, args.mean_threshold) for g in groups.values())
                    for f in ("d7", "d6")} for opt in "ABC"}

    for dim, field in DIMENSIONS.items():
        selected = [g for g in groups.values()
                    if is_perfect(ratings(g, field), args.criterion, args.mean_threshold)]
        out = args.outdir / f"perfect_{dim}{args.suffix}.jsonl"
        with open(out, "w", encoding="utf-8") as f:
            for rec in selected:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        write_sample(args.outdir / f"sample_{dim}{args.suffix}.md", dim, field,
                     selected, args.sample_size, args.seed)
        n3 = sum(r["n_annotators"] == 3 for r in selected)
        print(f"[option {args.criterion}] {out.name}: {len(selected)} summaries "
              f"({n3} with 3 annotators), rows with tags/broken umlauts: {count_leftovers(selected)}")

    block = "\n".join([
        f"Input: `{args.input.name}` - {n_rows} annotator rows, {len(groups)} unique summaries (item_id + model). "
        "Texts cleaned (HTML tags, umlauts, outer quotes); `n_sentences` added.",
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
    update_readme(args.outdir / "README.md", block, args.suffix)

    print("\nCounts per option (unique summaries):")
    for opt in "ABC":
        print(f"  {opt}: d7 faithfulness={counts[opt]['d7']}, d6 coverage={counts[opt]['d6']}")
    print(f"\nTotal: {n_rows} rows, {len(groups)} unique summaries. README updated.")


if __name__ == "__main__":
    main()