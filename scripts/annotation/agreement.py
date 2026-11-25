"""Agreement between annotators and first results.

Reads every batch: data/annotation/sample.json with data/annotation/answers/<name>.json, and
data/annotation/batch<N>/ the same way. Prints, over all batches together, per dimension
(faithfulness, coverage): Krippendorff's alpha (interval, as in SummEval), how often the two ratings
are equal or at most 1 apart, and alpha again after normalizing each annotator (own mean subtracted,
or z-score), as a check of how much comes from different use of the scale. Then mean ± SD of the single
ratings per annotator, per asked severity, per kind of injected error and per error type.
Writes data/annotation/ratings.csv: one row per output with its batch, both ratings and their mean.
Usage: python scripts/annotation/agreement.py
"""
import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "data" / "annotation"
DIMS = ["faithfulness", "coverage"]


def krippendorff_interval(units):
    """units: list of lists of ratings (one list per output, any number of raters, >= 2 used)."""
    units = [u for u in units if len(u) >= 2]
    values = [v for u in units for v in u]
    n = len(values)
    if n < 2:
        return float("nan")
    d_o = sum(sum((a - b) ** 2 for a, b in combinations(u, 2)) * 2 / (len(u) - 1) for u in units) / n
    d_e = sum((a - b) ** 2 for a, b in combinations(values, 2)) * 2 / (n * (n - 1))
    return 1.0 if d_e == 0 else 1 - d_o / d_e


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def sd(xs):
    """Sample standard deviation (n - 1)."""
    if len(xs) < 2:
        return float("nan")
    m = mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def fmt(xs):
    return f"{mean(xs):.2f} ± {sd(xs):.2f} (n={len(xs)})" if xs else "-"


def table(title, groups, keys):
    """groups[dim][key] = list of single ratings."""
    print(f"\n{title}")
    width = max(len(str(k)) for k in keys) + 2
    print(f"  {'':<{width}}" + "".join(f"{d:<24}" for d in DIMS))
    for k in keys:
        print(f"  {str(k):<{width}}" + "".join(f"{fmt(groups[d][k]):<24}" for d in DIMS))


def normalized_alpha(pairs, scale):
    """pairs: [((name, rating), (name, rating))]. Each rating is replaced by (rating - own mean) / own SD
    (scale=True) or rating - own mean (scale=False), with mean and SD over all ratings of that annotator."""
    own = defaultdict(list)
    for pair in pairs:
        for name, r in pair:
            own[name].append(r)
    norm = lambda name, r: (r - mean(own[name])) / (sd(own[name]) if scale and sd(own[name]) > 0 else 1)
    return krippendorff_interval([[norm(n, r) for n, r in pair] for pair in pairs])


def load_batch(folder):
    """The samples of one batch, each with the answers of its annotators (None if missing)."""
    sample = json.load(open(folder / "sample.json", encoding="utf-8"))
    answers = {}
    for path in sorted((folder / "answers").glob("*.json")):
        data = json.load(open(path, encoding="utf-8"))
        if data.get("sample") != sample["tag"]:
            print(f"skipped {path.relative_to(ROOT)}: made for another sample ({data.get('sample')}, now {sample['tag']})")
            continue
        answers[data["annotator"]] = data["answers"]
    batch = sample.get("batch", 1)
    print(f"batch {batch}: answers from", ", ".join(answers) or "nobody yet")
    return [dict(s, batch=batch, given=[answers.get(n, {}).get(s["sample_id"]) for n in s["annotators"]])
            for s in sample["samples"]]


def main():
    folders = [DIR] + sorted((f for f in DIR.glob("batch*/") if f.name[5:].isdigit()), key=lambda f: int(f.name[5:]))
    samples = [s for f in folders if (f / "sample.json").exists() for s in load_batch(f)]

    rows, units, named, missing = [], {d: [] for d in DIMS}, {d: [] for d in DIMS}, 0
    by_sev, by_dim, by_type, by_person = ({d: defaultdict(list) for d in DIMS} for _ in range(4))
    for s in samples:
        given = [g if g and all(d in g for d in DIMS) else None for g in s["given"]]  # only complete answers count
        if any(g is None for g in given):
            missing += 1
        row = {"batch": s["batch"], "sample_id": s["sample_id"], "output_id": s["output_id"], "error_type": s["error_type"],
               "error_dimension": s["dimension"], "asked_severity": s["asked_severity"]}
        for k, name in enumerate(s["annotators"], 1):
            g = given[k - 1] or {}
            row[f"annotator_{k}"] = name
            for d in DIMS:
                row[f"{d}_{k}"] = g.get(d, "")
        for d in DIMS:
            vals = [g[d] for g in given if g]
            row[f"{d}_mean"] = round(mean(vals), 2) if vals else ""
            units[d].append(vals)
            if len(vals) == 2:
                named[d].append(tuple((n, g[d]) for n, g in zip(s["annotators"], given)))
            for n, g in zip(s["annotators"], given):
                if g:
                    by_person[d][n].append(g[d])
            by_sev[d][s["asked_severity"]] += vals
            by_dim[d][s["dimension"]] += vals
            by_type[d][s["error_type"]] += vals
        rows.append(row)
    if missing:
        print(f"{missing} of {len(samples)} outputs don't have both ratings yet")

    print(f"\n{'rating':<14}{'pairs':>6}{'alpha':>8}{'equal':>8}{'±1':>8}{'alpha centered':>16}{'alpha z':>9}")
    for d in DIMS:
        pairs = [u for u in units[d] if len(u) == 2]
        if not pairs:
            print(f"{d:<14}{0:>6}")
            continue
        equal = mean([u[0] == u[1] for u in pairs])
        near = mean([abs(u[0] - u[1]) <= 1 for u in pairs])
        print(f"{d:<14}{len(pairs):>6}{krippendorff_interval(pairs):>8.2f}{equal:>8.0%}{near:>8.0%}"
              f"{normalized_alpha(named[d], False):>16.2f}{normalized_alpha(named[d], True):>9.2f}")

    print("\nmean ± SD of the single ratings (n = number of ratings)")
    table("by annotator", by_person, sorted({n for d in DIMS for n in by_person[d]}))
    table("by asked severity", by_sev, ["low", "medium", "high"])
    table("by kind of injected error", by_dim, ["faithfulness", "coverage"])
    table("by error type", by_type, sorted({t for d in DIMS for t in by_type[d]}))

    with open(DIR / "ratings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\n-> data/annotation/ratings.csv")


if __name__ == "__main__":
    main()
