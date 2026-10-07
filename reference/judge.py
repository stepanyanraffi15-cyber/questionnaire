"""Record the Gemini judge's verdict for every meaning check in the answer key (live calls; needs an API key).

Kept apart from the application: its own prompt (`reference/judge_prompt.md`), its own Gemini call, and
nothing imported from `src/`. Verdicts are saved in `runs/judge/verdicts.json` so `grade.py` can replay
them with no key. Each verdict is tied to the exact observed answer; a new answer needs a new verdict.

Usage:
    uv run python reference/judge.py --list   # each meaning check, its key and the observed answer
    uv run python reference/judge.py          # record the missing verdicts (live calls)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime

from grade import EXPECTED, OBSERVED, ROOT, VERDICTS, field_value, load_passages, meaning_key

JUDGE_MODEL = "gemini-3.8-flash"
THINKING_LEVEL = "medium"
PROMPT = ROOT / "reference" / "judge_prompt.md"
SCHEMA = {
    "type": "object",
    "properties": {
        "basis": {"type": "string"},
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string"},
                    "stated": {"type": "boolean"},
                    "quote": {"type": "string"},
                },
                "required": ["fact", "stated", "quote"],
            },
        },
        "forbidden": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "made": {"type": "boolean"},
                    "quote": {"type": "string"},
                },
                "required": ["claim", "made", "quote"],
            },
        },
    },
    "required": ["basis", "facts", "forbidden"],
}


def meaning_checks(expected: dict, observed: dict) -> list[dict]:
    """Every meaning check with the observed answer it grades; empty answers need no judge."""
    passages = load_passages()
    found = []
    for case in expected["cases"] + expected["extra_rows"]:
        for check in case["meaning"]:
            view = observed["steps"][check["step"]]["items"][check["item"]]
            answer = field_value(view, check["field"]) or ""
            if not answer.strip() and not check["expected_facts"]:
                continue
            sources = [
                {"id": d["passage_id"], "text": passages[d["passage_id"]]} for d in case["derived_from"]
            ]
            request = {
                "question": view["question_text"],
                "passages": sources,
                "expected_facts": check["expected_facts"],
                "forbidden_claims": check["forbidden_claims"],
                "answer": answer,
            }
            key = meaning_key(
                view["question_text"], answer, check["expected_facts"], check["forbidden_claims"]
            )
            found.append({"case": case["id"], "key": key, "request": request})
    return found


def record(check: dict, client) -> dict:
    from google.genai import types

    config = types.GenerateContentConfig(
        system_instruction=PROMPT.read_text(),
        response_mime_type="application/json",
        response_json_schema=SCHEMA,
        thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL),
    )
    user = json.dumps(check["request"], ensure_ascii=False, indent=1)
    response = client.models.generate_content(model=JUDGE_MODEL, contents=user, config=config)
    usage = response.usage_metadata
    return {
        "case": check["case"],
        "model": JUDGE_MODEL,
        "thinking_level": THINKING_LEVEL,
        "prompt_file": "reference/judge_prompt.md",
        "request": check["request"],
        "response": json.loads(response.text),
        "response_id": response.response_id,
        "usage": {
            "prompt_token_count": usage.prompt_token_count,
            "candidates_token_count": usage.candidates_token_count,
            "thoughts_token_count": usage.thoughts_token_count,
        },
        "recorded_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Record judge verdicts for the answer key's meaning checks")
    parser.add_argument(
        "--list", action="store_true", help="only list the checks and whether a verdict exists"
    )
    args = parser.parse_args()
    expected, observed = json.loads(EXPECTED.read_text()), json.loads(OBSERVED.read_text())
    verdicts = json.loads(VERDICTS.read_text()) if VERDICTS.exists() else {}
    checks = meaning_checks(expected, observed)
    if args.list:
        for check in checks:
            state = "verdict saved" if check["key"] in verdicts else "no verdict"
            print(f"{check['case']}  {check['key']}  [{state}]  {check['request']['answer']!r}")
        return 0
    missing = [c for c in checks if c["key"] not in verdicts]
    if missing:
        client = _client()
        for check in missing:
            verdicts[check["key"]] = record(check, client)
            _save(verdicts)
            print(f"LIVE judge verdict recorded for {check['case']}")
    print(f"{len(checks)} meaning checks, {len(missing)} new verdicts -> {VERDICTS.relative_to(ROOT)}")
    return 0


def _save(verdicts: dict) -> None:
    VERDICTS.parent.mkdir(parents=True, exist_ok=True)
    VERDICTS.write_text(json.dumps(verdicts, indent=1, ensure_ascii=False, sort_keys=True) + "\n")


def _client():
    from dotenv import load_dotenv
    from google import genai

    load_dotenv(ROOT / ".env")
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        sys.exit("judge.py needs GOOGLE_API_KEY (or GEMINI_API_KEY) in the environment or the local env file")
    return genai.Client()


if __name__ == "__main__":
    sys.exit(main())
