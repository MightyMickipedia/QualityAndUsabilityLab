"""Select coverage prompt descriptions and delegate generation to ../run.py."""
import argparse
from functools import partial
import http.client
import importlib.util
import json
import math
from pathlib import Path
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
ERROR_TYPES = ("delete_sentence", "add_out_of_domain_sentence", "add_in_domain_sentence", "add_definition")
SEVERITIES = ("high", "medium", "low")


def positive_seconds(value):
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive finite number of seconds")
    return seconds


def call_llm(prompt, model, base_url, api_key, temperature, retries=1, *, timeout=120, no_thinking=False):
    """Single HTTP attempt; timeout applies to this request. No automatic retries."""
    payload = {"model": model, "temperature": temperature,
               "messages": [{"role": "user", "content": prompt}]}
    if no_thinking:
        payload["reasoning_effort"] = "none"
    body = json.dumps(payload).encode()
    request = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=body,
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
        if "error" in data:
            raise RuntimeError(f"API error: {data['error']}")
        content = data["choices"][0]["message"].get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(part.get("text", "") for part in content if isinstance(part, dict))
        return ""
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"HTTP {error.code} from the API: {detail}") from error
    except (urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError,
            KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"API request failed (timeout={timeout:g}s; no retry): {error}") from error


def run_coverage(arguments, timeout, no_thinking=False):
    spec = importlib.util.spec_from_file_location("coverage_runner", ROOT.parent / "run.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.call_llm = partial(call_llm, timeout=timeout, no_thinking=no_thinking)
    previous_argv = sys.argv
    try:
        sys.argv = [str(ROOT.parent / "run.py"), *arguments]
        runner.main()
    finally:
        sys.argv = previous_argv
    return 0


def generate_prompt(error_type, severity, output_dir=None):
    descriptions = json.loads((ROOT / "descriptions.json").read_text(encoding="utf-8"))
    group = {"delete_sentence": "delete", "add_in_domain_sentence": "add_in_domain"}.get(error_type, "add_irrelevant")
    template_name = "delete" if error_type == "delete_sentence" else "add"
    template = (ROOT.parent / "prompts" / f"coverage_{template_name}.md").read_text(encoding="utf-8")
    template = template.replace("{type_description}", descriptions["error_types"][error_type])
    template = template.replace("{severity_description}", descriptions["severities"][group][severity])
    output_dir = Path(output_dir) if output_dir is not None else ROOT / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{error_type}_{severity}.md"
    output.write_text(template, encoding="utf-8")
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--error_type", required=True, choices=ERROR_TYPES)
    parser.add_argument("--severity", required=True, choices=SEVERITIES)
    parser.add_argument("--timeout", type=positive_seconds, default=120,
                        help="HTTP timeout per request in seconds (default: 120); no retries")
    parser.add_argument("--no_thinking", action="store_true",
                        help="send reasoning_effort=none to disable supported model thinking")
    args, forwarded = parser.parse_known_args(argv)
    if any(arg.startswith("--") and "--prompt".startswith(arg.split("=", 1)[0])
           for arg in forwarded):
        parser.error("--prompt is selected by this helper and cannot be overridden")
    prompt = generate_prompt(args.error_type, args.severity)
    arguments = [*forwarded, "--prompt", str(prompt),
                 "--error_type", args.error_type, "--severity", args.severity]
    return run_coverage(arguments, args.timeout, args.no_thinking)


if __name__ == "__main__":
    sys.exit(main())
