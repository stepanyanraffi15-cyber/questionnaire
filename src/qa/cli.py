"""Command line: `qa report`, `qa check-data`, `qa export`, `qa inspect`."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from qa.dataset import ROOT, load_dataset
from qa.export import export_markdown
from qa.llm import RECORDINGS_DIR, load_settings, make_client
from qa.review import workspace_dataset
from qa.scenario import run_scenario
from qa.store import load_state, state_path

OBSERVED_PATH = ROOT / "runs" / "report" / "observed.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qa")
    commands = parser.add_subparsers(dest="command", required=True)
    report = commands.add_parser("report", help="run the reference scenario from a clean state")
    report.add_argument("--out", type=Path, default=OBSERVED_PATH)
    check = commands.add_parser("check-data", help="load the data and list any problems")
    check.add_argument("--change", type=Path, action="append", default=[])
    export = commands.add_parser("export", help="print a request as a completed questionnaire")
    export.add_argument("request")
    inspect = commands.add_parser("inspect", help="show one item of the report with its saved model calls")
    inspect.add_argument("step")
    inspect.add_argument("item")
    args = parser.parse_args(argv)
    handlers = {"report": _report, "check-data": _check_data, "export": _export, "inspect": _inspect}
    return handlers[args.command](args)


def _report(args) -> int:
    mode = os.environ.get("QA_MODE") or "replay"
    settings = load_settings()
    with tempfile.TemporaryDirectory() as tmp:
        observed = run_scenario(make_client(mode), Path(tmp) / "workspace.json")
    observed = {"mode": mode, "model": {"provider": settings.provider, "model": settings.model}, **observed}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(observed, indent=1, ensure_ascii=False) + "\n")
    for step_id, step in observed["steps"].items():
        tallies = "  ".join(f"{r}: {_short(c)}" for r, c in step["counts"].items())
        print(
            f"{step_id}  {tallies}"
            + (f"  PROBLEMS: {step['action_problems']}" if step["action_problems"] else "")
        )
    print(f"wrote {args.out}")
    return 0


def _check_data(args) -> int:
    dataset = load_dataset(change_paths=args.change)
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
    path = state_path()
    state = load_state(path)
    if args.request not in {r["id"] for r in state["requests"]}:
        print(f"No request {args.request} in {path}; create one in the workspace (New request) first.")
        return 1
    print(export_markdown(state, workspace_dataset(state), args.request), end="")
    return 0


def _inspect(args) -> int:
    """Print one observed item, then the saved request and raw response behind each of its model calls."""
    observed = json.loads(OBSERVED_PATH.read_text())
    view = observed["steps"][args.step]["items"][args.item]
    print(json.dumps({k: v for k, v in view.items() if k != "calls"}, indent=1, ensure_ascii=False))
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
