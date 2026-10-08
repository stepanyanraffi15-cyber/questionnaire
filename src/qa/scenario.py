"""Run a scripted scenario from a clean state and record what the workspace shows.

Two scenarios exist: the reference scenario on the seed (S1-S11) and the extended one on the added data
(S1-S5). The outputs under `runs/report/` are application output. The expected results live separately
in `reference/` and are never derived from them (REF-2).
"""

from __future__ import annotations

import json
from pathlib import Path

from qa.dataset import ROOT, Dataset
from qa.review import add_note, approve, process_request, save_edit, set_change, workspace_dataset
from qa.store import load_state, new_state, save_state
from qa.views import counts, item_view

SCENARIO_PATH = ROOT / "data" / "scenario" / "min-demo.json"
EXTENDED_SCENARIO_PATH = ROOT / "data" / "scenario" / "extended-demo.json"
SUGGESTION_FIELDS = (
    "status",
    "reason",
    "answer",
    "hints",
    "conflict_source",
    "contradictions_rejected",
    "retrieval",
    "steps",
)


def run_scenario(client, state_file: Path, scenario_path: Path = SCENARIO_PATH) -> dict:
    """Play every step; after each one, snapshot the counts and every item view."""
    scenario = json.loads(scenario_path.read_text())
    state = new_state(scenario.get("additions"))
    save_state(state_file, state)
    dataset = workspace_dataset(state)
    steps = {}
    for step in scenario["steps"]:
        problems = []
        for action in step["actions"]:
            try:
                state, dataset = _perform(action, state, dataset, client, step["at"], state_file)
            except (ValueError, LookupError) as exc:
                problems.append(f"{action['type']}: {exc}")
        save_state(state_file, state)
        steps[step["id"]] = {**_snapshot(state, dataset), "action_problems": problems}
    return {"contract_version": 1, "scenario": scenario_path.relative_to(ROOT).as_posix(), "steps": steps}


def _perform(
    action: dict, state: dict, dataset: Dataset, client, at: str, state_file: Path
) -> tuple[dict, Dataset]:
    kind = action["type"]
    if kind == "run_questionnaire":
        request_id = process_request(state, dataset, client, at)
        if request_id != action["request"]:
            raise LookupError(f"expected request {action['request']}, got {request_id}")
    elif kind in ("save_edit", "add_note"):
        by = item_view(state, dataset, action["item"])["owner"]
        (save_edit if kind == "save_edit" else add_note)(state, action["item"], action["text"], by, at)
    elif kind == "approve":
        args = (action["item"], action["text"], action["sources"], action["approver"], action["note"], at)
        approve(state, dataset, client, *args)
    elif kind == "reload":
        save_state(state_file, state)
        state = load_state(state_file)
        dataset = workspace_dataset(state)
    elif kind == "apply_change":
        dataset = set_change(state, action["file"], True, at)
    else:
        raise LookupError(f"unknown scenario action {kind!r}")
    return state, dataset


def _snapshot(state: dict, dataset: Dataset) -> dict:
    items = {}
    for request in state["requests"]:
        for question_id in request["questions"]:
            view = item_view(state, dataset, f"{request['id']}/{question_id}")
            suggestion = view.pop("suggestion")
            view["suggestion"] = {k: suggestion[k] for k in SUGGESTION_FIELDS} if suggestion else None
            if suggestion and suggestion["support"]:
                view["suggestion"]["supported"] = suggestion["support"]["supported"]
            items[view["item"]] = view
    return {"counts": {r["id"]: counts(state, dataset, r["id"]) for r in state["requests"]}, "items": items}
