"""Run a scripted scenario from a clean state and record what the workspace shows.

Two scenarios exist: the reference scenario on the seed (S1-S11) and the extended one on the added data
(S1-S5). The outputs under `runs/report/` are application output. The expected results live separately
in `reference/` and are never derived from them (REF-2).
"""

from __future__ import annotations

import dataclasses
import json
import tempfile
from pathlib import Path

from qa.dataset import ROOT, Dataset
from qa.drafting import draft_item
from qa.llm import load_settings
from qa.retrieval import load_retrieval_settings
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


def build_report(client, scenario_path: Path, mode: str) -> dict:
    """The whole observed file: run the scenario from a clean state, then the search ablation."""
    settings = load_settings()
    with tempfile.TemporaryDirectory() as tmp:
        observed = run_scenario(client, Path(tmp) / "workspace.json", scenario_path)
    model = {
        "provider": settings.provider,
        "model": settings.model,
        "embedding_model": settings.embedding_model,
    }
    ablation = search_ablation(client, scenario_path, observed["steps"]["S1"]["items"])
    return {"mode": mode, "model": model, **observed, "search_ablation": ablation}


def search_ablation(client, scenario_path: Path, items: dict) -> dict:
    """Did the search tool change an outcome? Every first-request item where the model searched is drafted
    again with no searches allowed, and both outcomes are kept side by side (measured, not graded).
    """
    scenario = json.loads(scenario_path.read_text())
    dataset = workspace_dataset(new_state(scenario.get("additions")))
    no_search = dataclasses.replace(load_retrieval_settings(), max_searches=0)
    result = {}
    for item, view in items.items():
        suggestion = view["suggestion"] or {}
        if not any(step["action"] == "search_passages" for step in suggestion.get("steps") or []):
            continue
        question = next(q for q in dataset.questions if q.id == view["question_id"])
        without = draft_item(question, dataset, client, no_search)
        result[item] = {
            "with_search": {"status": suggestion["status"], "reason": suggestion["reason"]},
            "without_search": {
                "status": without["status"],
                "reason": without["reason"],
                "answer": without["answer"],
            },
        }
    return result


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
