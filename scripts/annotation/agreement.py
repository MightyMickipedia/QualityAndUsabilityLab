"""Agreement between the two annotators of each output.

Reads data/annotation/sample.json and data/annotation/answers/<name>.json, prints percent agreement
and Cohen's kappa per question, and writes data/annotation/disagreements.csv.
Usage: python scripts/annotation/agreement.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "data" / "annotation"
QUESTIONS = {"q1": "number of changes", "q2": "asked error type", "q3": "correct German", "q4": "severity"}


def cohen_kappa(pairs):
    n = len(pairs)
    observed = sum(a == b for a, b in pairs) / n
    first, second = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum(first[c] * second[c] for c in first) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def main():
    samples = json.load(open(DIR / "sample.json", encoding="utf-8"))["samples"]
    answers = {}
    for path in sorted((DIR / "answers").glob("*.json")):
        data = json.load(open(path, encoding="utf-8"))
        answers[data["annotator"]] = data["answers"]
    print("answers from:", ", ".join(answers) or "nobody yet")

    pairs = {q: [] for q in QUESTIONS}
    disagreements, missing = [], 0
    for s in samples:
        a, b = s["annotators"]
        ra, rb = answers.get(a, {}).get(s["sample_id"]), answers.get(b, {}).get(s["sample_id"])
        if not ra or not rb:
            missing += 1
            continue
        for q in QUESTIONS:
            if ra.get(q) and rb.get(q):  # a question both answered (q2-q4 are skipped when q1 is "none")
                pairs[q].append((ra[q], rb[q]))
                if ra[q] != rb[q]:
                    disagreements.append([s["sample_id"], s["group"], s["error_type"], q, QUESTIONS[q], a, ra[q], b, rb[q], s["adjudicator"]])
    if missing:
        print(f"{missing} of {len(samples)} outputs don't have both annotations yet")

    print(f"\n{'question':<24}{'outputs':>8}{'agree':>8}{'kappa':>8}")
    for q, label in QUESTIONS.items():
        p = pairs[q]
        if not p:
            print(f"{q + ' ' + label:<24}{0:>8}")
            continue
        agree = sum(x == y for x, y in p) / len(p)
        print(f"{q + ' ' + label:<24}{len(p):>8}{agree:>8.0%}{cohen_kappa(p):>8.2f}")

    with open(DIR / "disagreements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sample_id", "group", "error_type", "question", "question_text", "annotator_1", "answer_1",
                    "annotator_2", "answer_2", "adjudicator", "settled_answer"])
        w.writerows(row + [""] for row in disagreements)
    print(f"\n{len(disagreements)} disagreements -> data/annotation/disagreements.csv")


if __name__ == "__main__":
    main()
