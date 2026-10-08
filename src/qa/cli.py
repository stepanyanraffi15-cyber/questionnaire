"""Command line: `qa report`, `qa check-data`, `qa export`, `qa inspect`."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from qa.dataset import ROOT, load_dataset
from qa.export import export_markdown
from qa.llm import RECORDINGS_DIR, make_client
from qa.review import workspace_dataset
from qa.scenario import EXTENDED_SCENARIO_PATH, SCENARIO_PATH, build_report
from qa.store import EXTENDED_ADDITIONS, EXTENDED_WORKSPACE, load_state, state_path

OBSERVED_PATH = ROOT / "runs" / "report" / "observed.json"
EXTENDED_OBSERVED_PATH = ROOT / "runs" / "report" / "observed-extended.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qa")
    commands = parser.add_subparsers(dest="command", required=True)
    report = commands.add_parser("report", help="run both scenarios from a clean state")
    report.add_argument("--out", type=Path, default=OBSERVED_PATH)
    report.add_argument("--extended-out", type=Path, default=EXTENDED_OBSERVED_PATH)
    check = commands.add_parser("check-data", help="load the data and list any problems")
    check.add_argument("--change", type=Path, action="append", default=[])
    check.add_argument("--additions", type=Path, help="also load an added-data file")
    export = commands.add_parser("export", help="print a request as a completed questionnaire")
    export.add_argument("request")
    export.add_argument("--extended", action="store_true", help="use the extended questionnaire's workspace")
    inspect = commands.add_parser("inspect", help="show one item of the report with its saved model calls")
    inspect.add_argument("step")
    inspect.add_argument("item")
    inspect.add_argument("--extended", action="store_true", help="look in the extended scenario's report")
    args = parser.parse_args(argv)
    handlers = {"report": _report, "check-data": _check_data, "export": _export, "inspect": _inspect}
    return handlers[args.command](args)


def _report(args) -> int:
    """One client for both scenarios, so record mode makes each distinct call once."""
    mode = os.environ.get("QA_MODE") or "replay"
    client = make_client(mode)
    for scenario, out in ((SCENARIO_PATH, args.out), (EXTENDED_SCENARIO_PATH, args.extended_out)):
        _run_one(client, mode, scenario, out)
    return 0


def _run_one(client, mode: str, scenario: Path, out: Path) -> None:
    observed = build_report(client, scenario, mode)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(observed, indent=1, ensure_ascii=False) + "\n")
    print(observed["scenario"])
    for step_id, step in observed["steps"].items():
        tallies = "  ".join(f"{r}: {_short(c)}" for r, c in step["counts"].items())
        print(
            f"{step_id}  {tallies}"
            + (f"  PROBLEMS: {step['action_problems']}" if step["action_problems"] else "")
        )
    print(f"wrote {out}")


def _check_data(args) -> int:
    dataset = load_dataset(change_paths=args.change, additions_path=args.additions)
    errors = [i for i in dataset.issues if i.severity == "error"]
    for issue in dataset.issues:
        print(f"{issue.severity.upper()} {issue.code} {issue.item_id}: {issue.detail}")
    warnings = len(dataset.issues) - len(errors)
    print(f"{len(dataset.documents)} documents, {len(dataset.questions)} questions loaded")
    print(f"{len(errors)} errors, {warnings} warnings")
    for topic, owner in dataset.owners.items():
        print(f"  {topic:<10} -> {owner}")
    return 1 if errors else 0


def _export(args) -> int:
    path = state_path(EXTENDED_WORKSPACE if args.extended else "workspace")
    state = load_state(path, EXTENDED_ADDITIONS if args.extended else None)
    if args.request not in {r["id"] for r in state["requests"]}:
        print(f"No request {args.request} in {path}; create one in the workspace (New request) first.")
        return 1
    print(export_markdown(state, workspace_dataset(state), args.request), end="")
    return 0


def _inspect(args) -> int:
    """Print one observed item, then the saved request and raw response behind each of its model calls."""
    observed = json.loads((EXTENDED_OBSERVED_PATH if args.extended else OBSERVED_PATH).read_text())
    view = observed["steps"][args.step]["items"][args.item]
    print(json.dumps({k: v for k, v in view.items() if k != "calls"}, indent=1, ensure_ascii=False))
    suggestion = view.get("suggestion") or {}
    for step in suggestion.get("steps") or []:
        if step["action"] == "search_passages":
            print(f"\nsearch_passages({step['query']!r}) found {step['found']}, new {step['new']}")
    for call in view["calls"]:
        path = RECORDINGS_DIR / f"{call['call_type']}-{call['fingerprint'][:16]}.json"
        record = json.loads(path.read_text())
        print(f"\n--- {call['call_type']} call ({call['label']}), {path.relative_to(ROOT)}")
        print("request (data message):", record["request"]["user"])
        print("response:", record["response"]["text"])
    return 0


def _short(tally: dict) -> str:
    return "/".join(str(tally[k]) for k in ("answered", "unresolved", "approved", "needs_review", "error"))


if __name__ == "__main__":
    sys.exit(main())
