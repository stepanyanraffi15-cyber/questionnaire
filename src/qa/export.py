"""Export one request as a completed questionnaire, with evidence references and unresolved items (OPT-1)."""

from __future__ import annotations

from qa.dataset import Dataset
from qa.views import counts, item_view


def export_markdown(state: dict, dataset: Dataset, request_id: str) -> str:
    request = next(r for r in state["requests"] if r["id"] == request_id)
    views = [item_view(state, dataset, f"{request_id}/{qid}") for qid in request["questions"]]
    tally = counts(state, dataset, request_id)
    lines = [
        f"# Questionnaire {request_id}",
        "",
        "Counts: " + ", ".join(f"{name} {n}" for name, n in tally.items()),
        "",
        "## Answers",
        "",
    ]
    for view in views:
        if view["answer"]:
            lines += _answer_lines(view)
    lines += ["## Unresolved or needing review", ""]
    for view in views:
        if not view["answer"]:
            lines += _open_lines(view)
    return "\n".join(lines).rstrip() + "\n"


def _answer_lines(view: dict) -> list[str]:
    sources = "; ".join(
        f'{c["passage_id"]} (version {c["version"]}): "{c["excerpt"]}"' for c in view["citations"]
    )
    lines = [
        f"**{view['question_id']}. {view['question_text']}**",
        "",
        view["answer"],
        "",
        f"- Evidence: {sources}",
    ]
    if view["approval"]:
        approval = view["approval"]
        lines.append(
            f"- Approved by {approval['approver']} at {approval['at']} ({approval['support_basis']})"
        )
    else:
        lines.append("- Model draft, not yet approved")
    if view["replaced_shown"]:
        lines.append(f"- Replaced text kept for reviewers: {', '.join(view['replaced_shown'])}")
    return lines + [""]


def _open_lines(view: dict) -> list[str]:
    lines = [
        f"**{view['question_id']}. {view['question_text']}**",
        "",
        f"- Status: {view['status']} ({view['reason'] or 'no reason'}); owner: {view['owner']}",
    ]
    if view["note"]:
        lines.append(f"- Note: {view['note']}")
    if view["conflicts_shown"]:
        lines.append(f"- Conflicting passages: {', '.join(view['conflicts_shown'])}")
    return lines + [""]
