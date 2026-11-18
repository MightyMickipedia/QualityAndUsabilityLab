"""Convert data/APPLS_errors/human_labeled.csv to the shared output format.

Writes one .jsonl per error type into data/injected/ (delete_sentence, add_in_domain_sentence).
The few rows of other types in the CSV are examples and are skipped.
Usage: python scripts/annotation/convert_coverage_csv.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "APPLS_errors" / "human_labeled.csv"
TYPES = ["delete_sentence", "add_in_domain_sentence"]

rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
for error_type in TYPES:
    out = ROOT / "data" / "injected" / f"{error_type}.jsonl"
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            if r["error_type"] != error_type:
                continue
            rec = {
                "id": f"inj-{error_type}-{r['severity']}-{r['item_id']}-{r['model']}-{r['example_id']}",
                "item_id": r["item_id"],
                "model": r["model"],
                "dimension": "coverage",
                "error_type": error_type,
                "severity": r["severity"],
                # the CSV has no method column, only an author ("Mick" or "Codex draft")
                "method": "manual" if r["author"] == "Mick" else "llm:codex",
                "prompt": "",
                "original_summary": r["original_summary"],
                "modified_summary": r["modified_summary"],
                "change": r["change"],
                "warnings": [],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print(f"{out.relative_to(ROOT)}: {n} outputs")
