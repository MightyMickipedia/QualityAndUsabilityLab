# perturb_ai.py
# AI-based version of perturb.py — same CLI, same output format, but uses the
# Anthropic API to rewrite summaries instead of applying rules.
#
# needs:
#   pip install anthropic pandas
#   export ANTHROPIC_API_KEY="sk-ant-..."
#
# then just run it like perturb.py:
#   python perturb_ai.py --input_faith adv_proj_faithfulness.jsonl \
#                        --input_nrd   adv_proj_nrd.jsonl \
#                        --input_gram  adv_proj_grammaticality.jsonl
#
# pass --test 3 to try just 3 items per dataset first

import json, random, argparse, os, time, sys

import anthropic
import pandas as pd


# config — same defaults as perturb.py

SCORE_DISTRIBUTION = {
    5: 0.20,
    4: 0.20,
    3: 0.20,
    2: 0.20,
    1: 0.20,
}
RANDOM_SEED = 42
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 800
DELAY_BETWEEN_CALLS = 0.4   # small pause between calls to stay within rate limits
MAX_RETRIES = 3


# the rubrics get pasted verbatim into each prompt so the model knows what each score means

RUBRIC_FAITHFULNESS = """Die Zusammenfassung sollte inhaltlich korrekt und sprachlich verständlich sein.
Sie darf keine erfundenen Details enthalten, die nicht in der Quelle vorkommen.
7 – Ausgezeichnet: Alle Aussagen sind sachlich korrekt.
6 – Sehr gut: Alle Aussagen sind sachlich korrekt, bis auf eine geringfügige Ungenauigkeit.
5 – Gut: Enthält einige inhaltliche Ungenauigkeiten, der Rest ist jedoch korrekt.
4 – Durchwachsen: Enthält sachliche Fehler, die Gesamtzusammenfassung gibt jedoch die wichtigsten Fakten korrekt wieder.
3 – Schwach: Enthält mehrere sachliche Fehler, die die Genauigkeit erheblich beeinträchtigen.
2 – Sehr mangelhaft: Enthält viele sachliche Fehler; wichtige Informationen sind ungenau oder irreführend.
1 – Mangelhaft: Faktisch unzuverlässig; die meisten Aussagen sind falsch."""

RUBRIC_NRD = """Die Zusammenfassung vermeidet unnötige Wiederholungen (z. B. wiederholte Fakten,
Wiederverwendung von Nominalphrasen anstelle von Pronomen).
7 – Ausgezeichnet: Keine Wortwiederholungen oder inhaltliche Wiederholungen.
6 – Sehr gut: Eine Wort- oder inhaltliche Wiederholung, die aber nicht auffällt.
5 – Gut: Einige Wort- oder inhaltliche Wiederholungen, die den Lesefluss aber nicht sonderlich stören.
4 – Durchwachsen: Einige Wort- oder inhaltliche Wiederholungen, die den Lesefluss beeinträchtigen.
3 – Schwach: Viele Wiederholungen, die den Lesefluss stark beeinträchtigen.
2 – Sehr mangelhaft: Viele Wiederholungen, die das Verständnis des Textes stark beeinträchtigen.
1 – Mangelhaft: Viele Wiederholungen, die die Zusammenfassung unbrauchbar/unlesbar machen."""

RUBRIC_GRAMMATICALITY = """Die Zusammenfassung sollte keine Datelines, systeminterne Formatierung,
Gross- und Kleinschreibungsfehler, unidiomatischen Formulierungen oder
ungrammatischen Saetze enthalten, die das Lesen erschweren.
1 – Mangelhaft: Viele Fehler; schwer zu lesen.
2 – Sehr mangelhaft: Viele grammatische Fehler, die das Verstaendnis stark beeintraechtigen.
3 – Schwach: Mehrere grammatische Fehler, die den Lesefluss deutlich stoeren.
4 – Durchwachsen: Ein paar kleinere Fehler, aber verstaendlich.
5 – Gut: Wenige kleinere grammatische oder idiomatische Fehler; insgesamt gut lesbar.
6 – Sehr gut: Fast keine Fehler; nur geringfuegige sprachliche Unsauberkeiten.
7 – Ausgezeichnet: Keine grammatischen Fehler."""


# seed upfront

random.seed(RANDOM_SEED)


def fix_encoding(text: str) -> str:
    sample = text[:200]
    if not any(0xC0 <= ord(c) <= 0xFF for c in sample):
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


# one prompt builder per dimension — the rubric goes in, the model does the rest

def _prompt_faithfulness(summary: str, article: str, target_score: int) -> str:
    return f"""Du bist ein Experte für deutsche Texte. Deine Aufgabe ist es, eine Zusammenfassung so umzuschreiben, dass sie genau Score {target_score} auf der folgenden Skala erhält.

Bewertungsskala (Faithfulness):
{RUBRIC_FAITHFULNESS}

Originalzusammenfassung:
{summary}

Quellartikel (zur Orientierung):
{article[:2000]}

Schreibe die Zusammenfassung so um, dass sie Score {target_score} entspricht. Verändere nur den Inhalt (Faktentreue), nicht die Grammatik oder den Satzbau. Gib NUR die umgeschriebene Zusammenfassung zurück, ohne Erklärung oder Kommentar."""


def _prompt_nrd(summary: str, target_score: int) -> str:
    return f"""Du bist ein Experte für deutsche Texte. Deine Aufgabe ist es, eine Zusammenfassung so umzuschreiben, dass sie genau Score {target_score} auf der folgenden Skala erhält.

Bewertungsskala (Non-Redundancy):
{RUBRIC_NRD}

Originalzusammenfassung:
{summary}

Schreibe die Zusammenfassung so um, dass sie Score {target_score} entspricht. Verändere nur die Redundanz (Wiederholungen), nicht den Inhalt oder die Grammatik. Gib NUR die umgeschriebene Zusammenfassung zurück, ohne Erklärung oder Kommentar."""


def _prompt_grammaticality(summary: str, target_score: int) -> str:
    return f"""Du bist ein Experte für deutsche Texte. Deine Aufgabe ist es, eine Zusammenfassung so umzuschreiben, dass sie genau Score {target_score} auf der folgenden Skala erhält.

Bewertungsskala (Grammaticality):
{RUBRIC_GRAMMATICALITY}

Originalzusammenfassung:
{summary}

Schreibe die Zusammenfassung so um, dass sie Score {target_score} entspricht. Verändere nur die Grammatik und Formulierungen, nicht den Inhalt oder die Redundanz. Gib NUR die umgeschriebene Zusammenfassung zurück, ohne Erklärung oder Kommentar."""


# wraps the API call with retries in case of rate limits or transient errors

def call_api(client: anthropic.Anthropic, prompt: str) -> str:
    for attempt in range(MAX_RETRIES):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...", flush=True)
            time.sleep(wait)
        except anthropic.APIError as e:
            print(f"  API error: {e}", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"  Unexpected error: {e}", flush=True)
            time.sleep(5)
    return None


# same assign_scores logic as in perturb.py

def assign_scores(n: int, dist: dict) -> list:
    # note: round() can be off by 1 for small datasets, remainder goes to top bucket
    assert abs(sum(dist.values()) - 1.0) < 1e-6, "Distribution must sum to 1.0"
    scores = sorted(dist.keys())
    counts, assigned = {}, 0
    for sc in scores[:-1]:
        cnt = round(dist[sc] * n)
        counts[sc] = cnt
        assigned += cnt
    counts[scores[-1]] = n - assigned
    result = []
    for sc, cnt in counts.items():
        result.extend([sc] * cnt)
    random.shuffle(result)
    return result


# I/O helpers

def load_jsonl(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def save_jsonl(records: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  Saved {len(records)} records -> {path}")


def append_high_scores(source_path: str, out_path: str, score_field: str, target_count: int):
    # tack the high-quality originals (6+7) onto the end of the output
    try:
        items = load_jsonl(source_path)
    except FileNotFoundError:
        print(f"  Skipping high-score append: {source_path} not found")
        return
    sixes  = [i for i in items if round(i.get(score_field, 0)) == 6]
    sevens = [i for i in items if round(i.get(score_field, 0)) == 7]
    sixes  = random.sample(sixes,  min(target_count, len(sixes)))
    sevens = random.sample(sevens, min(target_count, len(sevens)))
    with open(out_path, "a", encoding="utf-8") as f:
        for item in sixes + sevens:
            summ = fix_encoding(item.get("summary", ""))
            score = item.get(score_field)
            rec = {
                "id":                item.get("id"),
                "original_score":    score,
                "target_score":      score,
                "original_summary":  summ,
                "perturbed_summary": summ,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"  Appended {len(sixes)} sixes + {len(sevens)} sevens from {source_path}")


# generic pipeline helper, not actually used by the CLI below but kept for importing

def run_pipeline(client, items, scores, build_prompt_fn, original_score_field, out_path,
                 high_score_source, high_score_field, dist, label):
    records = []
    changed = 0
    total = len(items)

    for i, (item, target) in enumerate(zip(items, scores)):
        summ = fix_encoding(item.get("summary", ""))
        art  = fix_encoding(item.get("article", ""))
        prompt = build_prompt_fn(summ, art, target) if original_score_field == "faithfulness_score" \
            else build_prompt_fn(summ, target)
        pert = call_api(client, prompt)
        if pert is None:
            pert = summ
        if pert != summ:
            changed += 1
        records.append({
            "id":                item.get("id"),
            "original_score":    item.get(original_score_field),
            "target_score":      target,
            "original_summary":  summ,
            "perturbed_summary": pert,
        })
        print(f"  [{i+1}/{total}] id={item.get('id')} score={target}", flush=True)
        time.sleep(DELAY_BETWEEN_CALLS)

    if not records:
        print("  No records.")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    print(f"  Changed: {changed}/{len(records)}")
    print(f"  Score distribution:\n{df['target_score'].value_counts().sort_index().to_string()}")
    save_jsonl(records, out_path)
    append_high_scores(high_score_source, out_path, high_score_field, len(records) // len(dist))
    return df


# CLI — mirrors perturb.py exactly so it can be swapped in

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input_faith", default="adv_proj_faithfulness.jsonl")
    p.add_argument("--input_nrd",   default="adv_proj_nrd.jsonl")
    p.add_argument("--input_gram",  default="adv_proj_grammaticality.jsonl")
    p.add_argument("--out_faith",   default="perturbed_ai_faithfulness.jsonl")
    p.add_argument("--out_nrd",     default="perturbed_ai_nrd.jsonl")
    p.add_argument("--out_gram",    default="perturbed_ai_grammaticality.jsonl")
    p.add_argument("--seed",        type=int, default=RANDOM_SEED)
    p.add_argument("--test",        type=int, default=0,
                   help="if > 0, only process this many items per dataset (smoke test)")
    args = p.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY before running.")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    random.seed(args.seed)
    dist = SCORE_DISTRIBUTION

    if args.test:
        print(f"TEST MODE: {args.test} items per dataset\n")

    def get_items(path):
        items = load_jsonl(path)
        return items[:args.test] if args.test else items

    print(f"Model: {MODEL}")
    print(f"Score distribution: {dist}")

    # --- faithfulness ---
    print(f"\n-- Faithfulness (AI): {args.input_faith}")
    items_f = get_items(args.input_faith)
    scores_f = assign_scores(len(items_f), dist)
    records_f, changed_f = [], 0
    for i, (item, target) in enumerate(zip(items_f, scores_f)):
        summ = fix_encoding(item.get("summary", ""))
        art  = fix_encoding(item.get("article", ""))
        pert = call_api(client, _prompt_faithfulness(summ, art, target)) or summ
        if pert != summ: changed_f += 1
        records_f.append({"id": item.get("id"), "original_score": item.get("faithfulness_score"),
                           "target_score": target, "original_summary": summ, "perturbed_summary": pert})
        print(f"  [{i+1}/{len(items_f)}] id={item.get('id')} score={target}", flush=True)
        time.sleep(DELAY_BETWEEN_CALLS)
    df_f = pd.DataFrame(records_f)
    print(f"  Changed: {changed_f}/{len(records_f)}")
    print(f"  Score distribution:\n{df_f['target_score'].value_counts().sort_index().to_string()}")
    save_jsonl(records_f, args.out_faith)
    append_high_scores("faithfulness_rating_6_7.jsonl", args.out_faith, "faithfulness_score",
                       len(records_f) // len(dist))

    # --- nrd ---
    print(f"\n-- NRD (AI): {args.input_nrd}")
    items_n = get_items(args.input_nrd)
    scores_n = assign_scores(len(items_n), dist)
    records_n, changed_n = [], 0
    for i, (item, target) in enumerate(zip(items_n, scores_n)):
        summ = fix_encoding(item.get("summary", ""))
        pert = call_api(client, _prompt_nrd(summ, target)) or summ
        if pert != summ: changed_n += 1
        records_n.append({"id": item.get("id"), "original_score": item.get("non_redundancy_score"),
                           "target_score": target, "original_summary": summ, "perturbed_summary": pert})
        print(f"  [{i+1}/{len(items_n)}] id={item.get('id')} score={target}", flush=True)
        time.sleep(DELAY_BETWEEN_CALLS)
    df_n = pd.DataFrame(records_n)
    print(f"  Changed: {changed_n}/{len(records_n)}")
    print(f"  Score distribution:\n{df_n['target_score'].value_counts().sort_index().to_string()}")
    save_jsonl(records_n, args.out_nrd)
    append_high_scores("nrd_rating_6_7.jsonl", args.out_nrd, "non_redundancy_score",
                       len(records_n) // len(dist))

    # --- grammaticality ---
    print(f"\n-- Grammaticality (AI): {args.input_gram}")
    items_g = get_items(args.input_gram)
    scores_g = assign_scores(len(items_g), dist)
    records_g, changed_g = [], 0
    for i, (item, target) in enumerate(zip(items_g, scores_g)):
        summ = fix_encoding(item.get("summary", ""))
        pert = call_api(client, _prompt_grammaticality(summ, target)) or summ
        if pert != summ: changed_g += 1
        records_g.append({"id": item.get("id"), "original_score": item.get("grammaticality_score"),
                           "target_score": target, "original_summary": summ, "perturbed_summary": pert})
        print(f"  [{i+1}/{len(items_g)}] id={item.get('id')} score={target}", flush=True)
        time.sleep(DELAY_BETWEEN_CALLS)
    df_g = pd.DataFrame(records_g) if records_g else pd.DataFrame()
    if records_g:
        print(f"  Changed: {changed_g}/{len(records_g)}")
        print(f"  Score distribution:\n{df_g['target_score'].value_counts().sort_index().to_string()}")
        save_jsonl(records_g, args.out_gram)
        append_high_scores("grammaticality_rating_6_7.jsonl", args.out_gram, "grammaticality_score",
                           len(records_g) // len(dist))
    else:
        print("  No records to process.")

    print(f"\nDone.  Faith: {len(df_f)} | NRD: {len(df_n)} | Gram: {len(df_g)}")
