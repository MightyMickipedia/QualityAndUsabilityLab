#!/usr/bin/env python3
"""Runner for LLM-based error injection.

Takes "perfect" summaries, fills a prompt template, asks an LLM to inject one error,
and saves the results in the shared output format (see README.md in this folder).

Only the Python standard library is needed. Any OpenAI-compatible chat API works
(OpenRouter, OpenAI, most other providers, a local server). Set:

    export LLM_API_KEY="..."
    export LLM_MODEL="..."                                   # e.g. a model name from OpenRouter
    export LLM_BASE_URL="https://openrouter.ai/api/v1"       # default

Examples:

    # look at the filled prompt for one summary, no API call
    python scripts/injection/run.py --prompt scripts/injection/prompts/example.md \
        --error_type EntE --severity high --n 1 --dry_run

    # 10 summaries, EntE, high
    python scripts/injection/run.py --prompt scripts/injection/prompts/example.md \
        --error_type EntE --severity high --n 10
"""
import argparse
import csv
import http.client
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "data" / "examples" / "examples.csv"

FAITHFULNESS = {"PredE", "EntE", "CircE", "CorefE", "LinkE", "OutE", "GramE"}
COVERAGE = {"delete_sentence", "add_out_of_domain_sentence", "add_in_domain_sentence", "add_definition"}
SEVERITIES = {"high", "medium", "low"}
NO_CHANGE_MARKER = "KEINE_PASSENDE_AENDERUNG:"  # start of "change" when the model finds no fitting error


def clean(text: str) -> str:
    """Remove the web-interface tags from the dataset texts if there are any."""
    text = re.sub(r"<br\s*/?>", "\n", text or "")
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def load_jsonl(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def few_shot(error_type: str, k: int, exclude_item: str) -> str:
    """Up to k examples of this error type from examples.csv, as plain text for the prompt."""
    with open(EXAMPLES, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["error_type"] == error_type and r["item_id"] != exclude_item]
    parts = []
    for i, r in enumerate(rows[:k], 1):
        parts.append(f"Beispiel {i}\nOriginal: {clean(r['original_summary'])}\n"
                     f"Geändert: {clean(r['modified_summary'])}\nÄnderung: {r['change']}")
    return "\n\n".join(parts) if parts else "(keine Beispiele vorhanden)"


def fill(template: str, **values) -> str:
    """Replace {article}, {summary}, {error_type}, {severity}, {examples} in the template.
    Other braces in the template stay as they are."""
    for key, val in values.items():
        template = template.replace("{" + key + "}", val)
    return template


class FatalAPIError(Exception):
    """Wrong key, unknown model, etc. Retrying won't help, so the whole run stops."""


def message_text(content) -> str:
    """Most APIs return a string; some return a list of parts or nothing."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return ""


def call_llm(prompt: str, model: str, base_url: str, api_key: str, temperature: float, retries: int = 4) -> str:
    body = json.dumps({"model": model, "temperature": temperature,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.load(resp)
            if "error" in data:  # some providers answer 200 with an error inside
                raise RuntimeError(f"API error: {data['error']}")
            return message_text(data["choices"][0]["message"].get("content"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:  # rate limit / server trouble: wait, try again
                wait = 5 * attempt
                print(f"  HTTP {e.code}, waiting {wait}s and retrying", file=sys.stderr)
                time.sleep(wait)
                continue
            if e.code in (400, 401, 402, 403, 404):
                raise FatalAPIError(f"HTTP {e.code} from the API: {detail}")
            raise RuntimeError(f"HTTP {e.code} from the API: {detail}")
        except (urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError,
                KeyError, IndexError, json.JSONDecodeError) as e:
            if attempt == retries:
                raise RuntimeError(f"no usable answer after {retries} tries: {e}")
            print(f"  retry {attempt} after error: {e}", file=sys.stderr)
            time.sleep(2 * attempt)


def parse_answer(text: str) -> dict:
    """The prompt asks for JSON {"modified_summary": ..., "change": ...}.
    Finds that object even inside ``` fences or with extra text around it.
    If there is none, the whole answer is kept as the summary and parsed=False."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", text):
        try:
            d, _ = dec.raw_decode(text[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and "modified_summary" in d:
            return {"modified_summary": str(d["modified_summary"]).strip(),
                    "change": str(d.get("change", "")).strip(), "parsed": True}
    return {"modified_summary": text.strip(), "change": "", "parsed": False}


# Error types that should keep the length about the same (a word or a phrase is swapped).
# OutE adds information, so it may get longer.
SAME_LENGTH = {"PredE", "EntE", "CircE", "CorefE", "LinkE", "GramE"}


def checks(original: str, modified: str, error_type: str) -> list:
    """Cheap warnings, not a quality judgement. Always check outputs by hand."""
    warn = []
    if not modified.strip():
        return ["empty answer"]
    if modified.strip() == original.strip():
        warn.append("unchanged")
    ratio = len(modified) / max(len(original), 1)
    if error_type in SAME_LENGTH and not 0.8 <= ratio <= 1.25:
        warn.append(f"length changed ({ratio:.2f}x)")
    if error_type == "OutE" and ratio < 1.0:
        warn.append(f"shorter, but OutE should add something ({ratio:.2f}x)")
    if error_type == "delete_sentence" and ratio >= 1.0:
        warn.append(f"not shorter after deleting ({ratio:.2f}x)")
    if error_type.startswith("add_") and ratio <= 1.0:
        warn.append(f"not longer after adding ({ratio:.2f}x)")
    if not re.search(r"\b(der|die|das|und|ist|nicht|mit)\b", modified, re.I):
        warn.append("maybe not German")
    return warn


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", required=True, type=Path, help="prompt template (.md) with {article} {summary} {error_type} {severity} {examples}")
    ap.add_argument("--error_type", required=True, choices=sorted(FAITHFULNESS | COVERAGE))
    ap.add_argument("--severity", required=True, choices=sorted(SEVERITIES))
    ap.add_argument("--input", type=Path, help="default: data/perfect_faithfulness.jsonl or data/perfect_coverage.jsonl, by error type")
    ap.add_argument("--n", type=int, default=10, help="number of summaries (random, see --seed)")
    ap.add_argument("--items", help="instead of --n: comma-separated item_id/model, e.g. 1008/gpt3.5,1032/sauerkraut")
    ap.add_argument("--k_examples", type=int, default=2, help="few-shot examples from examples.csv")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--out", type=Path, help="default: data/injected/<prompt>_<error_type>_<severity>.jsonl (appends)")
    ap.add_argument("--dry_run", action="store_true", help="print the filled prompt, don't call the LLM")
    a = ap.parse_args()

    dimension = "faithfulness" if a.error_type in FAITHFULNESS else "coverage"
    src = a.input or ROOT / "data" / f"perfect_{dimension}.jsonl"
    rows = load_jsonl(src)
    if a.items:
        wanted = [tuple(x.strip().split("/", 1)) for x in a.items.split(",") if x.strip()]
        rows = [r for r in rows if (r["item_id"], r["model"]) in wanted]
        found = {(r["item_id"], r["model"]) for r in rows}
        missing = ["/".join(w) for w in wanted if w not in found]
        if missing:
            print(f"Not found in {src.name}: {', '.join(missing)}", file=sys.stderr)
    else:
        random.Random(a.seed).shuffle(rows)
        rows = rows[: a.n]
    template = a.prompt.read_text(encoding="utf-8")

    model = os.environ.get("LLM_MODEL", "")
    base_url = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.environ.get("LLM_API_KEY", "")
    if not a.dry_run and not (model and api_key):
        sys.exit("Set LLM_API_KEY and LLM_MODEL (and LLM_BASE_URL if not OpenRouter), or use --dry_run.")

    out = a.out or ROOT / "data" / "injected" / f"{a.prompt.stem}_{a.error_type}_{a.severity}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(2).hex()  # unique even for two runs in the same second
    failed = 0

    for i, r in enumerate(rows, 1):
        summary, article = clean(r["summary"]), clean(r["article"])
        prompt = fill(template, article=article, summary=summary, error_type=a.error_type, severity=a.severity,
                      examples=few_shot(a.error_type, a.k_examples, r["item_id"]))
        if a.dry_run:
            print(f"===== {r['item_id']}/{r['model']} =====\n{prompt}\n")
            continue
        try:
            answer = parse_answer(call_llm(prompt, model, base_url, api_key, a.temperature))
        except FatalAPIError as e:
            sys.exit(f"Stopped: {e}")
        except RuntimeError as e:
            failed += 1
            print(f"[{i}/{len(rows)}] {r['item_id']}/{r['model']} FAILED: {e}", file=sys.stderr)
            continue
        warnings = checks(summary, answer["modified_summary"], a.error_type)
        if answer["change"].startswith(NO_CHANGE_MARKER):
            # The model declined on purpose (prompts may allow this). Not the same as a failed "unchanged".
            declined = answer["modified_summary"].strip() == summary.strip()
            warnings = ["no fitting change"] if declined else ["no fitting change, but the text was changed"] + warnings
        if not answer["parsed"]:
            warnings.insert(0, "answer was not the requested JSON")
        rec = {
            "id": f"inj-{a.error_type}-{a.severity}-{r['item_id']}-{r['model']}-{run_id}",
            "item_id": r["item_id"], "model": r["model"],
            "dimension": dimension, "error_type": a.error_type, "severity": a.severity,
            "method": f"llm:{model}", "prompt": a.prompt.name,
            "original_summary": summary, "modified_summary": answer["modified_summary"], "change": answer["change"],
            "warnings": warnings,
        }
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        flag = f"  ⚠ {', '.join(rec['warnings'])}" if rec["warnings"] else ""
        print(f"[{i}/{len(rows)}] {rec['id']}{flag}")
    if not a.dry_run:
        print(f"-> {out}" + (f"  ({failed} failed, see above)" if failed else ""))


if __name__ == "__main__":
    main()
