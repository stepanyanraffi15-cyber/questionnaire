"""Grade the workspace's observed results against the hand-made answer key and write docs/RESULTS.md.

Independent of the application on purpose: standard library only, nothing imported from `src/`. It re-reads
the passages from `data/` itself, so even the excerpt check is repeated here rather than trusted.

- Mechanical checks (IDs, verbatim excerpts, statuses, owners, versions, counts) are graded by this code.
- Meaning checks (expected facts, forbidden claims) use the judge's saved verdict
  (`runs/judge/verdicts.json`, recorded by `reference/judge.py`) and the author's sign-off
  (`reference/signoff.json`). Only a sign-off makes a meaning check PASS: unsigned, a judge PASS (or no
  verdict) is PENDING and a judge FAIL is FAIL.
- Retrieval recall@k is reported per row next to the row's result, as a measurement, not a check: was each
  gold passage among the top k for the question, and was it shown to the model by the end of its searches.

Two scenarios are graded: the seed one (top level of the key) and the extended one (the key's
`extended` block), each against its own observed file.

Exit code: 0 everything passes, 1 any FAIL, 3 no FAIL but something PENDING, 2 the grader itself crashed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "reference" / "expected.json"
OBSERVED = ROOT / "runs" / "report" / "observed.json"
EXTENDED_OBSERVED = ROOT / "runs" / "report" / "observed-extended.json"
METHODS = ("bm25", "dense", "hybrid", "shown")
VERDICTS = ROOT / "runs" / "judge" / "verdicts.json"
SIGNOFF = ROOT / "reference" / "signoff.json"
RESULTS = ROOT / "docs" / "RESULTS.md"


def collapse(text: str) -> str:
    return " ".join(text.split())


def load_passages() -> dict[str, str]:
    """Passage texts straight from the seed, the additions and the change files (a change file may replace a
    document; it never changes passage text here).
    """
    docs = json.loads((ROOT / "data" / "seed" / "seed.json").read_text())["documents"]
    for path in sorted((ROOT / "data" / "additions").glob("*.json")):
        docs += json.loads(path.read_text()).get("documents", [])
    for path in sorted((ROOT / "data" / "changes").glob("*.json")):
        docs += json.loads(path.read_text()).get("documents", [])
    return {p["id"]: p["text"] for d in docs for p in d["passages"]}


def field_value(view: dict, field: str):
    value = view
    for part in field.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    return value


def check_mechanical(check: dict, steps: dict, texts: dict, passages: dict) -> tuple[str, str]:
    """Return (PASS|FAIL, observed summary) for one mechanical check."""
    if "same_as" in check:
        same = steps[check["step"]]["items"] == steps[check["same_as"]]["items"]
        same = same and steps[check["step"]]["counts"] == steps[check["same_as"]]["counts"]
        return (
            "PASS" if same else "FAIL"
        ), f"items and counts {'equal' if same else 'differ from'} {check['same_as']}"
    view = steps[check["step"]]["items"].get(check["item"])
    if view is None:
        return "FAIL", "item missing from the observed results"
    value = field_value(view, check["field"])
    ok = _operator_holds(check, value, texts, passages)
    return ("PASS" if ok else "FAIL"), json.dumps(value, ensure_ascii=False)[:160]


def _operator_holds(check: dict, value, texts: dict, passages: dict) -> bool:
    if "equals" in check:
        return value == check["equals"]
    if "not_equals" in check:
        return value != check["not_equals"]
    if "equals_text" in check:
        return value == texts[check["equals_text"]]
    if "not_equals_text" in check:
        return value != texts[check["not_equals_text"]]
    if "ids_subset_of" in check:
        ids = _ids(value)
        return set(ids) <= set(check["ids_subset_of"]) and (bool(ids) or not check.get("non_empty"))
    if "ids_include" in check:
        return set(check["ids_include"]) <= set(_ids(value))
    if "excerpts_verbatim" in check:
        return bool(value) and all(
            collapse(c["excerpt"]) and collapse(c["excerpt"]) in collapse(passages.get(c["passage_id"], ""))
            for c in value
        )
    if "versions" in check:
        found = {c["passage_id"]: c["version"] for c in value or []}
        return found == check["versions"]
    if "non_empty" in check:
        return bool(value)
    raise ValueError(f"unknown check operator in {check}")


def _ids(value) -> list[str]:
    """Passage IDs from a citation list, or the list itself when it already holds IDs."""
    return [v["passage_id"] if isinstance(v, dict) else v for v in value or []]


def meaning_key(question: str, answer: str, facts: list[str], forbidden: list[str]) -> str:
    """The judge's verdict is tied to this exact answer; a different answer needs a new verdict."""
    payload = {"question": question, "answer": answer, "expected_facts": facts, "forbidden_claims": forbidden}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def check_meaning(check: dict, steps: dict, verdicts: dict, signoffs: dict) -> tuple[str, str, str]:
    """Return (PASS|FAIL|PENDING, judge summary, sign-off summary)."""
    view = steps[check["step"]]["items"][check["item"]]
    answer = field_value(view, check["field"]) or ""
    if not answer.strip() and not check["expected_facts"]:
        return "PASS", "empty text states nothing, so no forbidden claim is made", "not needed"
    key = meaning_key(view["question_text"], answer, check["expected_facts"], check["forbidden_claims"])
    verdict = verdicts.get(key)
    judged = judge_result(verdict, answer) if verdict else ("PENDING", "no saved judge verdict")
    signoff = signoffs.get(key)
    if signoff is None:
        return ("FAIL" if judged[0] == "FAIL" else "PENDING"), judged[1], "awaiting the author's sign-off"
    result = "PASS" if signoff["result"] == "pass" else "FAIL"
    return result, judged[1], f"{signoff['result']} by {signoff['by']} on {signoff['date']}"


def judge_result(verdict: dict, answer: str) -> tuple[str, str]:
    """The judge decides meaning; code checks only that every quote it gives is really in the answer."""
    reply = verdict["response"]
    quotes = [e["quote"] for e in reply["facts"] if e["stated"]] + [
        e["quote"] for e in reply["forbidden"] if e["made"]
    ]
    if any(collapse(q) not in collapse(answer) for q in quotes):
        return "FAIL", "judge quoted words that are not in the answer (verdict rejected)"
    missing = [e["fact"] for e in reply["facts"] if not e["stated"]]
    made = [e["claim"] for e in reply["forbidden"] if e["made"]]
    if missing or made:
        return "FAIL", f"judge: missing {missing}, forbidden made {made}"
    return "PASS", f"judge ({verdict['model']}): all facts stated, no forbidden claim"


def suites(expected: dict) -> list[tuple[str, dict]]:
    """The seed scenario's key is the top level; the extended scenario's key is its `extended` block."""
    seed = {k: v for k, v in expected.items() if k != "extended"}
    return [("seed", seed), ("extended", expected["extended"])]


def grade(expected: dict, observed: dict, verdicts: dict, signoffs: dict, suite: str = "seed") -> list[dict]:
    """One row per check; every row is kept, failing or not."""
    passages, steps, rows = load_passages(), observed["steps"], []
    for case in expected["cases"] + expected["extra_rows"]:
        for check in case["checks"]:
            result, seen = check_mechanical(check, steps, expected["texts"], passages)
            rows.append(_row(case, check, "mechanical", result, seen, ""))
        for check in case["meaning"]:
            result, judged, signed = check_meaning(check, steps, verdicts, signoffs)
            rows.append(_row(case, check, "meaning", result, judged, signed))
    rows += _count_rows(expected, steps)
    return [{"suite": suite, **row} for row in rows]


def _count_rows(expected: dict, steps: dict) -> list[dict]:
    rows = []
    for step, requests in expected["counts"].items():
        for request, numbers in requests.items():
            found = steps[step]["counts"].get(request, {})
            seen = [found.get(name) for name in expected["counts_order"]]
            result = "PASS" if seen == numbers else "FAIL"
            rows.append(
                {
                    "case": "counts",
                    "covers": "REQ-A3",
                    "kind": "mechanical",
                    "where": f"{step} {request}",
                    "expected": numbers,
                    "observed": seen,
                    "result": result,
                    "signoff": "",
                }
            )
    return rows


def recall(case: dict, steps: dict) -> dict | None:
    """Recall of the row's gold passages at the row's first checked item; None for rows with no gold field.

    `bm25`, `dense` and `hybrid` are the shares of gold passages in each method's top k for the question;
    `shown` adds what the model's own searches found. All are None when the row has no gold passage (an
    undocumented question) or the item was not drafted.
    """
    if "gold_passages" not in case:
        return None
    first = case["checks"][0]
    view = steps[first["step"]]["items"].get(first["item"]) or {}
    retrieval = (view.get("suggestion") or {}).get("retrieval")
    gold = set(case["gold_passages"])
    found = {"item": f"{first['step']} {first['item']}", "gold": sorted(gold)}
    if not gold or not retrieval:
        return {**found, "bm25": None, "dense": None, "hybrid": None, "shown": None, "missed": []}
    hybrid = [hit["passage_id"] for hit in retrieval["hits"]]
    searched = [pid for step in view["suggestion"].get("steps") or [] for pid in step.get("new", [])]
    return {
        **found,
        "bm25": _share_of(gold, retrieval.get("bm25_top", [])),
        "dense": _share_of(gold, retrieval.get("dense_top", [])),
        "hybrid": _share_of(gold, hybrid),
        "shown": _share_of(gold, hybrid + searched),
        "missed": sorted(gold - set(hybrid + searched)),
    }


def _share_of(gold: set[str], found: list[str]) -> float:
    return len(gold & set(found)) / len(gold)


def _row(case: dict, check: dict, kind: str, result: str, seen: str, signed: str) -> dict:
    where = f"{check['step']} {check.get('item', '')} {check.get('field', '')}".strip()
    expected = {k: v for k, v in check.items() if k not in ("step", "item", "field")}
    return {
        "case": case["id"],
        "covers": ", ".join(case.get("covers", [])),
        "kind": kind,
        "where": where,
        "expected": expected,
        "observed": seen,
        "result": result,
        "signoff": signed,
    }


def overall(rows: list[dict]) -> str:
    results = {r["result"] for r in rows}
    return "FAIL" if "FAIL" in results else "PENDING" if "PENDING" in results else "PASS"


def render(rows: list[dict], expected: dict, observed: dict, extended: dict) -> str:
    key_sha = hashlib.sha256(EXPECTED.read_bytes()).hexdigest()[:16]
    seed_rows = [r for r in rows if r["suite"] == "seed"]
    lines = [
        "# Check results",
        "",
        "Written by `reference/grade.py` from `runs/report/observed.json` (seed scenario) and",
        "`runs/report/observed-extended.json` (extended scenario). Do not edit by hand.",
        "",
        f"- Seed: {_run_line(observed)}",
        f"- Extended: {_run_line(extended)}",
        f"- Answer key sha256: {key_sha}",
        "- Mechanical rows are graded by code. Meaning rows use a recorded Gemini judge (same model family",
        "  as the application, a stated limitation) plus the author's sign-off. Only a sign-off makes a",
        "  meaning row PASS; unsigned, a judge PASS is PENDING and a judge FAIL is FAIL.",
        "",
        "## Minimum demonstration",
        "",
        "| Check | Case | Result |",
        "|---|---|---|",
    ]
    for case in expected["cases"]:
        case_rows = [r for r in seed_rows if r["case"] == case["id"]]
        lines.append(
            f"| {', '.join(case['covers'])} | {case['id']}: {case['title']} | {overall(case_rows)} |"
        )
    count_rows = [r for r in seed_rows if r["case"] == "counts"]
    lines += [
        f"| REQ-A3 | answered / unresolved / approved counts at every step | {overall(count_rows)} |",
        "",
    ]
    lines += _extended_summary(rows, expected["extended"])
    lines += _recall_table(rows, expected["extended"], extended)
    lines += _ablation_table(extended)
    lines += [
        "## Every check",
        "",
        "| Scenario | Case | Kind | Where | Expected | Observed | Result | Sign-off |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        expected_text = json.dumps(r["expected"], ensure_ascii=False).replace("|", "\\|")
        observed_text = str(r["observed"]).replace("|", "\\|")
        lines.append(
            f"| {r['suite']} | {r['case']} | {r['kind']} | {r['where']} | {expected_text} | "
            f"{observed_text} | {r['result']} | {r['signoff']} |"
        )
    return "\n".join(lines) + "\n"


def _run_line(observed: dict) -> str:
    model = observed.get("model", {})
    embeddings = model.get("embedding_model")
    return f"mode {observed.get('mode')} · model {model.get('model')} · embeddings {embeddings}"


def _extended_summary(rows: list[dict], key: dict) -> list[str]:
    ext_rows = [r for r in rows if r["suite"] == "extended"]
    lines = [
        "## Extended questionnaire (added data)",
        "",
        "| Kind | Case | Result |",
        "|---|---|---|",
    ]
    for case in key["cases"] + key["extra_rows"]:
        case_rows = [r for r in ext_rows if r["case"] == case["id"]]
        lines.append(f"| {case['kind']} | {case['id']}: {case['title']} | {overall(case_rows)} |")
    count_rows = [r for r in ext_rows if r["case"] == "counts"]
    return lines + [f"| counts | counts at every step | {overall(count_rows)} |", ""]


def _recall_table(rows: list[dict], key: dict, extended: dict) -> list[str]:
    """Extended rows only (the seed corpus is smaller than k, so every method finds everything there).
    Recall sits next to each row's own result; rows with no gold passage show n/a, never 0 or 1.
    """
    lines = [
        "## Retrieval recall@k (extended questionnaire)",
        "",
        "Measured, not graded. For each row, the share of its gold passages in the top k of keyword search",
        'alone (BM25), embeddings alone (dense), and the fused list the model was given (hybrid); "shown"',
        "adds what the model's own searches found. n/a: no gold passage (an undocumented question).",
        "",
        "| Case | Gold | BM25 | dense | hybrid | shown | Missed | Row result |",
        "|---|---|---|---|---|---|---|---|",
    ]
    measured = []
    for case in key["cases"] + key["extra_rows"]:
        found = recall(case, extended["steps"])
        if found is None:
            continue
        result = overall([r for r in rows if r["suite"] == "extended" and r["case"] == case["id"]])
        if found["hybrid"] is not None:
            measured.append(found)
        shares = " | ".join(_share(found[m]) for m in METHODS)
        lines.append(
            f"| {case['id']} | {', '.join(found['gold']) or '-'} | {shares} | "
            f"{', '.join(found['missed'])} | {result} |"
        )
    if measured:
        means = " | ".join(f"{sum(f[m] for f in measured) / len(measured):.2f}" for m in METHODS)
        lines.append(f"| **mean, {len(measured)} rows** | | {means} | | |")
    return lines + [""]


def _ablation_table(extended: dict) -> list[str]:
    """Did the search tool change an outcome? Read from the report's re-draft with no searches allowed."""
    ablation = extended.get("search_ablation", {})
    changed = [i for i, a in ablation.items() if _outcome(a["with_search"]) != _outcome(a["without_search"])]
    lines = [
        "## Did the search tool change an outcome? (extended questionnaire, request R1)",
        "",
        f"The model used search_passages on {len(ablation)} items. Each was drafted again with no search",
        f"allowed; the outcome (status and reason) changed on {len(changed)} of them.",
        "",
        "| Item | With searches | Without searches | Changed |",
        "|---|---|---|---|",
    ]
    for item, a in ablation.items():
        mark = "yes" if item in changed else "no"
        lines.append(f"| {item} | {_outcome(a['with_search'])} | {_outcome(a['without_search'])} | {mark} |")
    return lines + [""]


def _outcome(result: dict) -> str:
    return f"{result['status']} ({result['reason']})" if result["reason"] else result["status"]


def _share(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _load_json(path: Path, default: dict) -> dict:
    return json.loads(path.read_text()) if path.exists() else default


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--observed", type=Path, default=OBSERVED)
    parser.add_argument("--extended-observed", type=Path, default=EXTENDED_OBSERVED)
    parser.add_argument("--results", type=Path, default=RESULTS)
    args = parser.parse_args(argv)
    expected = json.loads(EXPECTED.read_text())
    observed = json.loads(args.observed.read_text())
    extended = json.loads(args.extended_observed.read_text())
    verdicts = _load_json(VERDICTS, {})
    signoffs = _load_json(SIGNOFF, {"signoffs": {}})["signoffs"]
    rows = []
    for (suite, key), data in zip(suites(expected), (observed, extended), strict=True):
        rows += grade(key, data, verdicts, signoffs, suite)
    args.results.write_text(render(rows, expected, observed, extended))
    result = overall(rows)
    tally = {name: sum(r["result"] == name for r in rows) for name in ("PASS", "FAIL", "PENDING")}
    print(f"{result}: {tally} -> {args.results}")
    return {"PASS": 0, "FAIL": 1, "PENDING": 3}[result]


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - any crash must exit 2, distinct from a FAIL
        print(f"grader crashed: {exc!r}", file=sys.stderr)
        sys.exit(2)
