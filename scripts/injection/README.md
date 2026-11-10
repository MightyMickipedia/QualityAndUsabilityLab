# Error injection

Scripts and prompts that put one error into a "perfect" summary. Week 2 tasks: `documentation/tasks/week-02/`.

```
scripts/injection/
  run.py            runner for LLM-based injection (optional to use)
  prompts/          prompt templates (.md), one or more per task
  *.py              rule-based scripts, if you write any
data/injected/      outputs, one .jsonl per run
```

## Output format

Every injection, by LLM or by a script, writes **one JSON line per modified summary** with these fields:

| Field | Meaning | Example |
|---|---|---|
| `id` | unique id: `inj-<error_type>-<severity>-<item_id>-<model>-<run>` | `inj-EntE-high-1008-mistral-nemo-20261105-101500-3e33` |
| `item_id` | article id from the dataset | `"1008"` |
| `model` | system that wrote the **original** summary (from the dataset) | `"mistral-nemo"` |
| `dimension` | `faithfulness` or `coverage` | `"faithfulness"` |
| `error_type` | name as in `Taxonomy.md` / `examples.csv` | `"EntE"`, `"delete_sentence"` |
| `severity` | `high`, `medium` or `low` | `"high"` |
| `method` | how the error was injected: `rule` or `llm:<model name>` | `"llm:<model>"` |
| `prompt` | prompt file name, or the script name for rule-based | `"example.md"` |
| `original_summary` | the perfect summary, tags removed | |
| `modified_summary` | the summary with the error | |
| `change` | one line: what changed | `"„Die CDU“ → „Die SPD“"` |
| `warnings` | optional, list of automatic warnings (see below) | `["unchanged"]` |

Error type names: `PredE`, `EntE`, `CircE`, `CorefE`, `LinkE`, `OutE`, `GramE`, `delete_sentence`, `add_out_of_domain_sentence`, `add_in_domain_sentence`, `add_definition`.

```json
{"id": "inj-EntE-high-1008-mistral-nemo-20261105-101500-3e33", "item_id": "1008", "model": "mistral-nemo", "dimension": "faithfulness", "error_type": "EntE", "severity": "high", "method": "llm:<model>", "prompt": "example.md", "original_summary": "Die CDU präsentiert …", "modified_summary": "Die SPD präsentiert …", "change": "„Die CDU“ → „Die SPD“", "warnings": []}
```

Writing your own script? Pls preferably use the same fields, and the rest of the pipeline can read your outputs.

## Runner (`run.py`)

Optional. It does the part every LLM-based injection needs anyway:

1. loads summaries from `data/perfect_faithfulness.jsonl` or `data/perfect_coverage.jsonl` (picked by error type) and removes the `<br/>` / `<strong>` tags
2. fills your prompt template: `{article}`, `{summary}`, `{error_type}`, `{severity}`, `{examples}` (few-shot examples of that type from `data/examples/examples.csv`)
3. calls the LLM
4. writes the output format above to `data/injected/`

Only the Python standard library is needed. It works with any OpenAI-compatible API (OpenRouter, OpenAI, most providers, a local server). Tested on 04.11. with the free `nvidia/nemotron-3.5-super-vl:free` through OpenRouter, which works (see `data/injected/README.md`):

```bash
export LLM_API_KEY="..."
export LLM_MODEL="..."                              # model name at your provider
export LLM_BASE_URL="https://openrouter.ai/api/v1"  # default, change for other providers

# see the filled prompt first, no API call, no key needed
python scripts/injection/run.py --prompt scripts/injection/prompts/example.md --error_type EntE --severity high --n 1 --dry_run

# 10 random summaries
python scripts/injection/run.py --prompt scripts/injection/prompts/example.md --error_type EntE --severity high --n 10

# the same 10 summaries for every type: pass them explicitly
python scripts/injection/run.py ... --items 1008/gpt3.5,1032/sauerkraut,...
```

Your prompt should ask for JSON `{"modified_summary": "...", "change": "..."}` (see `prompts/example.md`). If the model answers with plain text instead, the whole answer is saved as `modified_summary`.

Automatic warnings (`warnings` field). They only catch obvious failures, so check the outputs by hand anyway:
- `unchanged`, `empty answer`, `answer was not the requested JSON`
- `no fitting change`: the model returned the summary unchanged on purpose and `change` starts with `KEINE_PASSENDE_AENDERUNG:` (some prompts allow this when no error of that type and severity fits). `unchanged` without that marker means the model just failed to change anything
- `length changed`: for types that swap a word or phrase (PredE, EntE, CircE, CorefE, LinkE, GramE), if the length is outside 0.8-1.25×
- OutE and `add_*` should get longer, `delete_sentence` shorter. If not, there's a warning
- `maybe not German`

Errors: a wrong key or model name stops the run with the provider's message. Rate limits and server errors are retried. If one summary still fails, it's skipped and the run continues.
