"""Draw the annotation sample and build one HTML page per annotator.

Reads the outputs in data/injected/ (shared format), draws PER_TYPE outputs per error type,
gives each group of error types to two annotators and an adjudicator (see GROUPS) and writes
  data/annotation/sample.json          which output is which sample, and who annotates it
  data/annotation/pages/<name>.html    the page for one annotator, nothing to install
Usage: python scripts/annotation/build_pages.py
"""
import difflib
import html
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INJECTED = ROOT / "data" / "injected"
OUT = ROOT / "data" / "annotation"
SEED = 2026
PER_TYPE = 5

# groups of error types: two annotators each, and an adjudicator who settles where the two differ.
# See documentation/annotation_proposal.md.
GROUPS = {
    "A": (["PredE", "add_out_of_domain_sentence", "add_definition"], ["Giuseppe", "Anton"], "Malte"),
    "B": (["EntE", "CircE"], ["Anton", "Ivan"], "Mick"),
    "C": (["delete_sentence", "add_in_domain_sentence"], ["Ivan", "Malte"], "Giuseppe"),
    "D": (["OutE", "GramE"], ["Malte", "Mick"], "Anton"),
    "E": (["CorefE", "LinkE"], ["Mick", "Giuseppe"], "Ivan"),
}
ASSIGNMENT = {t: (g, pair, adj) for g, (types, pair, adj) in GROUPS.items() for t in types}

DEFINITIONS = {
    "PredE": "Predicate error: the action or state (usually the verb) contradicts the article. The participants are right, but what they do is wrong.",
    "EntE": "Entity error: a participant of the action (person, organisation, thing) or one of its attributes, such as a number, is wrong.",
    "CircE": "Circumstance error: action and participants are right, but the circumstances are wrong: place, time, manner or condition.",
    "CorefE": "Coreference error: a pronoun or reference points to the wrong antecedent, or to none.",
    "LinkE": "Discourse link error: statements are linked wrongly, for example a wrong order in time or a wrong cause.",
    "OutE": "Out-of-article error: the summary contains information that is not in the article, even if it is true in reality.",
    "GramE": "Grammatical error: the grammar of a sentence is so broken that the sentence loses its meaning.",
    "delete_sentence": "Delete sentence: one sentence with important information was removed from the summary.",
    "add_in_domain_sentence": "Add in-domain sentence: one sentence was added that sounds fitting but does not belong to this article.",
    "add_out_of_domain_sentence": "Add out-of-domain sentence: one sentence from a completely different topic was added.",
    "add_definition": "Add definition: a definition or background explanation of a term was added.",
}

# outputs that can't be annotated: (item_id, model) -> reason
EXCLUDE = {("1408", "mistral-nemo"): "the original summary is in English"}

SKIP_FILES = ("_test.jsonl", "example_")


def load_outputs():
    by_type = {}
    for path in sorted(INJECTED.glob("*.jsonl")):
        if path.name.endswith(SKIP_FILES[0]) or path.name.startswith(SKIP_FILES[1]):
            continue
        for line in open(path, encoding="utf-8"):
            rec = json.loads(line)
            if rec["original_summary"].strip() == rec["modified_summary"].strip():
                continue  # the model made no change, nothing to annotate
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
            articles[str(r["item_id"])] = (r.get("title", ""), r["article"])
    return articles


def mark_changes(original, modified):
    """Word-level diff. Returns (original with removed words marked, modified with new words marked)."""
    a, b = re.split(r"(\s+)", original), re.split(r"(\s+)", modified)
    left, right = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        old, new = html.escape("".join(a[i1:i2])), html.escape("".join(b[j1:j2]))
        if op == "equal":
            left.append(old)
            right.append(new)
        else:
            if old.strip():
                left.append(f"<del>{old}</del>")
            else:
                left.append(old)
            if new.strip():
                right.append(f"<ins>{new}</ins>")
            else:
                right.append(new)
    return "".join(left), "".join(right)


def main():
    rng = random.Random(SEED)
    by_type, articles = load_outputs(), load_articles()
    sample = []
    for error_type, (_, annotators, _) in ASSIGNMENT.items():
        pool = by_type.get(error_type, [])
        if len(pool) < PER_TYPE:
            print(f"warning: only {len(pool)} outputs for {error_type}")
        for rec in rng.sample(pool, min(PER_TYPE, len(pool))):
            sample.append((rec, annotators))
    # sample ids in random order, so the id says nothing about the output
    order = list(range(len(sample)))
    rng.shuffle(order)
    entries = []
    for number, idx in enumerate(order, 1):
        rec, annotators = sample[idx]
        group, _, adjudicator = ASSIGNMENT[rec["error_type"]]
        entries.append({"sample_id": f"s{number:03d}", "output_id": rec["id"], "file": rec["file"],
                        "error_type": rec["error_type"], "group": group, "annotators": annotators,
                        "adjudicator": adjudicator, "_rec": rec})

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pages").mkdir(exist_ok=True)
    (OUT / "answers").mkdir(exist_ok=True)
    with open(OUT / "sample.json", "w", encoding="utf-8") as f:
        json.dump({"seed": SEED, "per_type": PER_TYPE,
                   "samples": [{k: v for k, v in e.items() if k != "_rec"} for e in entries]},
                  f, ensure_ascii=False, indent=1)

    template = open(Path(__file__).with_name("page_template.html"), encoding="utf-8").read()
    names = sorted({n for _, pair, _ in GROUPS.values() for n in pair})
    for name in names:
        items = []
        # grouped by error type, so the annotator works on one type at a time
        for error_type in ASSIGNMENT:
            for e in entries:
                if e["error_type"] != error_type or name not in e["annotators"]:
                    continue
                rec = e["_rec"]
                original, modified = mark_changes(rec["original_summary"], rec["modified_summary"])
                title, article = articles[str(rec["item_id"])]
                items.append({"id": e["sample_id"], "type": error_type, "definition": DEFINITIONS[error_type],
                              "original": original, "modified": modified,
                              "title": html.escape(title), "article": html.escape(article)})
        page = template.replace("__NAME__", name).replace(
            "__DATA__", json.dumps(items, ensure_ascii=False).replace("</", "<\\/"))
        (OUT / "pages" / f"{name}.html").write_text(page, encoding="utf-8")
        groups = ", ".join(g for g, (_, pair, _) in GROUPS.items() if name in pair)
        print(f"{name}: {len(items)} outputs (groups {groups})")
    print(f"{len(entries)} outputs in the sample -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
