"""Draw the annotation sample and build one HTML page per annotator.

Reads the week-3 outputs in data/injected/ (shared format), draws N_SAMPLE outputs at random
(2 or 3 per error type, the same number per asked severity, only short to medium texts), gives each output to two annotators
at random and writes
  data/annotation/sample.json          which sample is which output, and who annotates it
  data/annotation/pages/<name>.html    the page for one annotator, nothing to install
Nobody gets an error type they generated or wrote the prompt for. Everybody gets the same number
of outputs, in random order, so error types and severities are mixed.
An existing sample.json is kept, so the pages stay the same when outputs are regenerated later.
Further batches go to data/annotation/batch<N>/ and only use outputs that no earlier batch has.
Usage: python scripts/annotation/build_pages.py                       build batch 1 from sample.json (draw it if missing)
       python scripts/annotation/build_pages.py --batch 2             the same for batch 2
       python scripts/annotation/build_pages.py [--batch N] --redraw  draw a new sample for that batch
"""
import difflib
import hashlib
import html
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INJECTED = ROOT / "data" / "injected"
OUT = ROOT / "data" / "annotation"
SEED = 2026
N_SAMPLE = 30  # 2 annotators each -> 12 per person
PER_OUTPUT = 2
PEOPLE = ["Giuseppe", "Malte", "Anton", "Mick", "Ivan"]

# who generated the week-3 outputs or wrote the prompt, per error type: they don't annotate it
INVOLVED = {
    "PredE": {"Ivan", "Malte"},
    "EntE": {"Malte"},
    "CircE": {"Malte"},
    "CorefE": {"Anton"},
    "LinkE": {"Anton"},
    "OutE": {"Giuseppe", "Anton"},
    "GramE": {"Giuseppe", "Anton"},
    "delete_sentence": {"Mick"},
    "add_in_domain_sentence": {"Mick"},
    "add_out_of_domain_sentence": {"Ivan", "Mick"},
    "add_definition": {"Ivan", "Mick"},
}

# only short to medium texts, so one summary takes a few minutes (about the shortest 40% of the outputs)
MAX_ARTICLE_WORDS = 450
MAX_SUMMARY_WORDS = 120

# outputs that can't be annotated: (item_id, model) -> reason
EXCLUDE = {("1408", "mistral-nemo"): "the original summary is in English"}


def load_outputs():
    """All changed week-3 outputs, by error type."""
    by_type = {}
    for path in sorted(INJECTED.glob("*.jsonl")):
        if path.name.endswith("_test.jsonl") or path.name.startswith("example_"):
            continue
        for line in open(path, encoding="utf-8"):
            rec = json.loads(line)
            if rec["original_summary"].strip() == rec["modified_summary"].strip():
                continue  # the model made no change
            if (str(rec["item_id"]), rec["model"]) in EXCLUDE:
                continue
            rec["file"] = path.name
            by_type.setdefault(rec["error_type"], []).append(rec)
    return by_type


def load_articles():
    articles = {}
    for dim in ("faithfulness", "coverage"):
        for line in open(ROOT / "data" / f"perfect_{dim}_v2.jsonl", encoding="utf-8"):
            r = json.loads(line)
            title = r.get("title", "")
            if title == "Title Not Found":  # placeholder in the source data
                title = ""
            articles[str(r["item_id"])] = (title, r["article"])
    return articles


def mark_changes(original, modified, exact=False):
    """The modified summary as HTML: removed words struck through in <del>, new words in <ins>.
    exact=True (batch 2 on) keeps every space inside the tags, so dropping the <del> parts gives exactly
    the modified summary and dropping the <ins> parts exactly the original. Batch 1 keeps the old marks."""
    a, b = re.split(r"(\s+)", original), re.split(r"(\s+)", modified)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        old, new = "".join(a[i1:i2]), "".join(b[j1:j2])
        if exact:
            out.append(html.escape(new) if op == "equal" else
                       (f'<del title="removed">{html.escape(old)}</del>' if old else "") +
                       (f"<ins>{html.escape(new)}</ins>" if new else ""))
            continue
        if op == "equal" or not (old.strip() or new.strip()):
            out.append(html.escape(new))
            continue
        side = new if new.strip() else old  # keep the spaces around the change
        lead, trail = re.match(r"\s*", side).group(), re.search(r"\s*$", side).group()
        parts = []
        if old.strip():
            parts.append(f'<del title="removed">{html.escape(old.strip())}</del>')
        if new.strip():
            parts.append(f"<ins>{html.escape(new.strip())}</ins>")
        out.append(lead + " ".join(parts) + trail)
    return "".join(out)


SEVERITIES = ["low", "medium", "high"]


def draw_sample(rng, by_type):
    """2 or 3 outputs per error type, different severities within a type where possible,
    and the same number of low, medium and high overall. Only existing outputs, nothing new."""
    types = sorted(by_type)
    target = N_SAMPLE // len(SEVERITIES)
    for _ in range(10000):
        per_type = {t: N_SAMPLE // len(types) for t in types}
        for t in rng.sample(types, N_SAMPLE - sum(per_type.values())):
            per_type[t] += 1
        slots = {}
        for t in types:
            have = [s for s in SEVERITIES if any(r["severity"] == s for r in by_type[t])]
            sev = rng.sample(have, min(per_type[t], len(have)))
            sev += [rng.choice(have) for _ in range(per_type[t] - len(sev))]
            slots[t] = sev
        counts = [sum(sev.count(s) for sev in slots.values()) for s in SEVERITIES]
        if all(c == target for c in counts):
            break
    else:
        return draw_sample_loose(rng, by_type)
    picked = []
    for t in types:
        for s in SEVERITIES:
            if s not in slots[t]:
                continue
            pool = [r for r in by_type[t] if r["severity"] == s]
            picked += rng.sample(pool, slots[t].count(s))
    rng.shuffle(picked)
    return picked


def assign(rng, picked):
    """Two annotators per output, at random among those allowed, with equal load. Retries until it fits."""
    target = len(picked) * PER_OUTPUT // len(PEOPLE)
    for _ in range(1000):
        load = {p: 0 for p in PEOPLE}
        result = []
        # hardest outputs first: those with the fewest allowed annotators
        order = sorted(range(len(picked)), key=lambda i: (len(INVOLVED[picked[i]["error_type"]]), rng.random()), reverse=True)
        ok = True
        chosen = {}
        for i in order:
            allowed = [p for p in PEOPLE if p not in INVOLVED[picked[i]["error_type"]] and load[p] < target]
            if len(allowed) < PER_OUTPUT:
                ok = False
                break
            rng.shuffle(allowed)
            allowed.sort(key=lambda p: load[p])
            pair = allowed[:PER_OUTPUT]
            for p in pair:
                load[p] += 1
            chosen[i] = sorted(pair, key=PEOPLE.index)
        if ok:
            return [chosen[i] for i in range(len(picked))]
    raise SystemExit("could not assign the outputs evenly, try another seed")


def clean(text):
    """Doubled quotes ("" for ") come from the source dataset, not from the injection."""
    return text.replace('""', '"')


def sample_tag(entries):
    """Short fingerprint of the sample; pages and answers files carry it, so answers can't land on another sample."""
    return hashlib.sha1(json.dumps(entries, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:8]


def draw_sample_loose(rng, by_type):
    """Fallback when the outputs left don't have every severity per type (later batches):
    a type may repeat a severity, but still gets at least two different ones, and the totals stay equal."""
    types = sorted(by_type)
    target = N_SAMPLE // len(SEVERITIES)
    for _ in range(200000):
        per_type = {t: N_SAMPLE // len(types) for t in types}
        for t in rng.sample(types, N_SAMPLE - sum(per_type.values())):
            per_type[t] += 1
        picked = [r for t in types for r in rng.sample(by_type[t], per_type[t])]
        if all(len({r["severity"] for r in picked if r["error_type"] == t}) >= 2 for t in types) and \
                all(sum(r["severity"] == s for r in picked) == target for s in SEVERITIES):
            rng.shuffle(picked)
            return picked
    raise SystemExit("could not balance the severities, try another seed")


def batch_dir(n):
    return OUT if n == 1 else OUT / f"batch{n}"


def main():
    batch = int(sys.argv[sys.argv.index("--batch") + 1]) if "--batch" in sys.argv else 1
    seed = SEED if batch == 1 else f"{SEED}-batch{batch}"
    rng = random.Random(seed)
    earlier = [json.load(open(batch_dir(k) / "sample.json", encoding="utf-8"))["samples"] for k in range(1, batch)]
    used = {e["output_id"] for s in earlier for e in s}
    first_id = sum(len(s) for s in earlier) + 1  # sample ids go on across batches: s031, s032, ...
    out = batch_dir(batch)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pages").mkdir(exist_ok=True)
    (out / "answers").mkdir(exist_ok=True)
    sample_file = out / "sample.json"

    if sample_file.exists() and "--redraw" not in sys.argv:
        # keep the drawn sample; the texts are stored in it, so later reruns of outputs don't change the pages
        entries = json.load(open(sample_file, encoding="utf-8"))["samples"]
        print(f"kept the sample in {sample_file.relative_to(ROOT)} (use --redraw for a new one)")
    else:
        articles = load_articles()
        by_type = {t: [r for r in recs if r["id"] not in used and len(articles[str(r["item_id"])][1].split()) <= MAX_ARTICLE_WORDS
                       and len(r["modified_summary"].split()) <= MAX_SUMMARY_WORDS]
                   for t, recs in load_outputs().items()}
        picked = draw_sample(rng, by_type)
        pairs = assign(rng, picked)
        entries = [{"sample_id": f"s{n:03d}", "output_id": rec["id"], "file": rec["file"], "error_type": rec["error_type"],
                    "dimension": rec["dimension"], "asked_severity": rec["severity"], "annotators": pair,
                    "item_id": str(rec["item_id"]), "title": articles[str(rec["item_id"])][0],
                    "article": articles[str(rec["item_id"])][1], "original_summary": clean(rec["original_summary"]),
                    "modified_summary": clean(rec["modified_summary"])}
                   for n, (rec, pair) in enumerate(zip(picked, pairs), first_id)]
        with open(sample_file, "w", encoding="utf-8") as f:
            json.dump({**({"batch": batch} if batch > 1 else {}), "seed": seed, "n_sample": N_SAMPLE, "tag": sample_tag(entries), "samples": entries}, f, ensure_ascii=False, indent=1)

    template = open(Path(__file__).with_name("page_template.html"), encoding="utf-8").read()
    for name in PEOPLE:
        mine = [e for e in entries if name in e["annotators"]]
        random.Random(f"{SEED}-{name}" if batch == 1 else f"{seed}-{name}").shuffle(mine)  # own random order per annotator, the same on every build
        items = []
        for e in mine:
            title, article = e["title"], e["article"]
            # the page gets no error type, severity or model: the article, the summary with the marks,
            # and the original summary folded away
            items.append({"id": e["sample_id"], "summary": mark_changes(e["original_summary"], e["modified_summary"], exact=batch > 1),
                          "original": html.escape(e["original_summary"]),
                          "title": html.escape(title), "article": html.escape(article)})
        answers_path = (out / "answers" / f"{name}.json").relative_to(ROOT).as_posix()
        page = template.replace("__BATCH__", "" if batch == 1 else f" · batch {batch}").replace(
            "__ANSWERS__", answers_path).replace("__NAME__", name).replace("__SAMPLE__", sample_tag(entries)).replace(
            "__DATA__", json.dumps(items, ensure_ascii=False).replace("</", "<\\/"))
        (out / "pages" / f"{name}.html").write_text(page, encoding="utf-8")
        print(f"{name}: {len(items)} outputs")
    print(f"{len(entries)} outputs in the sample, {PER_OUTPUT} annotators each -> {out.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
