"""The review workspace page (REQ-U1, REQ-U2, REQ-A3): a queue of items, each shown as question | answer |
passages, with the reviewer's actions underneath.

State is read from disk on every rerun and saved after every action, so a reload never loses work. Only
selections and filters live in `st.session_state`. Run with `uv run streamlit run src/qa/ui.py`.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import streamlit as st

from qa.dataset import ROOT, Dataset
from qa.export import export_markdown
from qa.llm import make_client
from qa.review import add_note, approve, process_request, save_edit, set_change, workspace_dataset
from qa.staleness import refresh_stale_marks, stale_mark
from qa.store import EXTENDED_ADDITIONS, EXTENDED_WORKSPACE, load_state, save_state, state_path
from qa.views import STATUSES, counts, history, item_view, reasons_text

CHANGES_DIR = ROOT / "data" / "changes"
MODE_BADGES = {
    "replay": ("Replay — saved real responses, no API key", "blue"),
    "record": ("Record — new calls are made and saved", "orange"),
}
STATUS_COLOURS = {
    "answered": "green",
    "unresolved": "orange",
    "approved": "blue",
    "needs_review": "violet",
    "error": "red",
}
SUPERSEDED_LABEL = "Superseded text — replaced via the supersedes field; not used as evidence"
QUESTIONNAIRES = {
    "Seed questionnaire (Q1–Q8)": ("workspace", None),
    "Extended questionnaire (X1–X35, added data)": (EXTENDED_WORKSPACE, EXTENDED_ADDITIONS),
}


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def workspace() -> tuple[Path, str | None]:
    """The chosen questionnaire's state file and additions; each questionnaire keeps its own workspace."""
    name, additions = QUESTIONNAIRES[st.session_state.get("questionnaire", next(iter(QUESTIONNAIRES)))]
    return state_path(name), additions


def load_workspace(path: Path, additions: str | None) -> tuple[dict, Dataset]:
    """Fresh from disk each rerun; a version change found here is saved at once, so it shows needs_review."""
    state = load_state(path, additions)
    dataset = workspace_dataset(state)
    seq = state["seq"]
    refresh_stale_marks(state, dataset, now())
    if state["seq"] != seq:
        save_state(path, state)
    return state, dataset


def new_request() -> None:
    """A callback, so it can select the new request before the selector is drawn."""
    path, additions = workspace()
    state = load_state(path, additions)
    st.session_state["request"] = process_request(state, workspace_dataset(state), make_client(), now())
    save_state(path, state)


def sidebar(state: dict, dataset: Dataset, path: Path) -> tuple[str | None, list[str]]:
    """Mode, state file, request and filter choice, counts, change files and data issues."""
    with st.sidebar:
        text, colour = MODE_BADGES.get(os.environ.get("QA_MODE") or "replay", ("Unknown mode", "red"))
        st.badge(text, color=colour)
        st.radio("Questionnaire", list(QUESTIONNAIRES), key="questionnaire", on_change=forget_request)
        st.caption(f"State file: `{path}`")
        request_ids = [r["id"] for r in state["requests"]]
        if st.session_state.get("request") not in request_ids:
            st.session_state["request"] = request_ids[-1] if request_ids else None
        request_id = st.selectbox("Request", request_ids, key="request")
        statuses = st.multiselect("Show statuses", STATUSES, default=list(STATUSES), key="statuses")
        if request_id:
            for name, number in counts(state, dataset, request_id).items():
                st.metric(name.replace("_", " ").capitalize(), number)
        st.subheader("Change files")
        for change in sorted(CHANGES_DIR.glob("*.json")):
            if applies_to(change, dataset):
                change_checkbox(state, path, change)
        st.subheader("Data issues")
        for issue in dataset.issues:
            st.caption(f"{issue.severity.upper()} {issue.code} {issue.item_id}: {issue.detail}")
        if not dataset.issues:
            st.caption("None")
    return request_id, statuses


def forget_request() -> None:
    """Request IDs restart in each questionnaire, so a switch must not keep the old selection."""
    st.session_state.pop("request", None)


def applies_to(change: Path, dataset: Dataset) -> bool:
    """Only offer change files whose documents are loaded in this questionnaire's workspace."""
    documents = json.loads(change.read_text()).get("documents", [])
    return all(d["id"] in dataset.documents for d in documents)


def change_checkbox(state: dict, path: Path, change: Path) -> None:
    """No widget key: the box is redrawn from the saved state, so the file on disk stays the truth."""
    relative = change.relative_to(ROOT).as_posix()
    applied = relative in state["applied_changes"]
    label = json.loads(change.read_text()).get("label", "CHANGE")
    if st.checkbox(f"{label}: {change.name}", value=applied) != applied:
        set_change(state, relative, not applied, now())
        save_state(path, state)
        st.rerun()


def render_item(state: dict, dataset: Dataset, view: dict) -> None:
    with st.container(border=True):
        question, answer, passages = st.columns(3)
        with question:
            question_column(view)
        with answer:
            answer_column(state, view)
        with passages:
            passages_column(view, dataset)
        if view["suggestion"]:
            checks_expander(view["suggestion"])
        with st.expander("Revision history"):
            st.table(history(state, view["item"]))
        review_actions(state, dataset, view)


def question_column(view: dict) -> None:
    st.markdown(f"**{view['question_id']}. {view['question_text']}**")
    st.badge(view["status"], color=STATUS_COLOURS[view["status"]])
    st.caption(f"Topic: {view['topic']} · Owner: {view['owner']}")
    if view["edited"]:
        st.info(f"edited (unapproved): {view['edit_text']}")
    if view["note"]:
        st.caption(f"Reviewer note: {view['note']}")


def answer_column(state: dict, view: dict) -> None:
    """The presented answer with where it came from, and every warning a reviewer must not miss."""
    status, reason, detail = view["status"], view["reason"], view["detail"]
    if view["answer"]:
        st.write(view["answer"])
    if view["approval"]:
        approval_block(view["approval"], view["reused"])
    elif view["calls"]:
        labels = ", ".join(f"{c['call_type']}: {c['label']}" for c in view["calls"])
        st.caption(f"Model draft ({labels}; model {view['calls'][0]['model']})")
    if status == "error":
        st.error(f"Error ({reason}): {detail}")
    elif reason == "conflict" or (status == "unresolved" and view["conflicts_shown"]):
        st.error(f"Conflicting evidence: {detail}. Passages: {', '.join(view['conflicts_shown'])}")
    elif status == "unresolved":
        st.warning(f"Missing evidence ({reason}): {detail}")
    if status != "error" and not view["citations"] and not view["approval"]:
        st.warning("No citations: no passage is cited for this item")
    if view["stale_approval_shown"]:
        stale_approval_note(state, view["stale_approval_shown"])


def approval_block(approval: dict, reused: bool) -> None:
    title = "STALE APPROVAL" if approval["stale"] else "REUSED APPROVAL" if reused else "APPROVED"
    sources = "; ".join(
        f"{s['passage_id']} ({s['doc_id']} version {s['version']})" for s in approval["sources"]
    )
    st.markdown(
        f"**{title}** {approval['id']} · by {approval['approver']} at {approval['at']}  \n"
        f"Note: {approval['note'] or 'none'} · Support basis: {approval['support_basis']}  \n"
        f"Sources: {sources}"
    )
    if approval["stale"]:
        st.write(f"Approved text: {approval['text']}")
        st.warning(f"Needs review: {reasons_text(approval['stale_reasons'])}")
    for word in approval["warnings"]:
        st.caption(f"Hint only: '{word}' is in the approved text but not in any source")


def stale_approval_note(state: dict, approval_id: str) -> None:
    """A fresh draft replaced an approval that went stale; show which one and why, for comparison."""
    approval = next(a for a in state["approvals"] if a["id"] == approval_id)
    mark = stale_mark(state, approval_id)
    why = reasons_text(mark["reasons"]) if mark else "no stale mark"
    st.warning(f"Earlier approval {approval_id} is stale ({why}). Its text: {approval['text']}")


def passages_column(view: dict, dataset: Dataset) -> None:
    """Cited excerpts with version and date (plain data), then conflicting and replaced passages."""
    for citation in view["citations"]:
        document = dataset.documents.get(citation["doc_id"])
        date = document.date if document else "document not loaded"
        st.markdown(f"**{citation['passage_id']}** · version {citation['version']} · dated {date}")
        st.markdown(f"> {citation['excerpt']}")
    for passage_id in view["conflicts_shown"]:
        st.error(f"Conflicting passage {passage_id}: {passage_text(dataset, passage_id)}")
    for passage_id in view["replaced_shown"]:
        st.warning(f"{SUPERSEDED_LABEL}  \n**{passage_id}**: {passage_text(dataset, passage_id)}")


def passage_text(dataset: Dataset, passage_id: str) -> str:
    passage = dataset.passages.get(passage_id)
    return passage.text if passage else "(passage not loaded)"


def checks_expander(suggestion: dict) -> None:
    """What the code checked and what the model said, so a reviewer can see why the status is what it is."""
    with st.expander("Checks and raw draft"):
        if suggestion.get("retrieval"):
            retrieval_steps(suggestion)
        for citation in suggestion["citations"]:
            st.write(f"✓ {citation['passage_id']}: excerpt found verbatim in a current passage")
        if suggestion["support"]:
            support = suggestion["support"]
            verdict = "supported" if support["supported"] else "not supported"
            st.write(f"Support check: {verdict} — {support['basis']}")
        for word in suggestion["hints"]:
            st.write(f"Hint only: '{word}' is in the answer but not in any cited passage")
        for item in suggestion["contradictions_rejected"]:
            st.write(f"Rejected contradiction (quotes not verbatim or not current): {item}")
        st.json(suggestion["draft"] or {})


def retrieval_steps(suggestion: dict) -> None:
    """What the model was shown: the first search for the question, then each search_passages call it made."""
    retrieval = suggestion["retrieval"]
    labels = ", ".join(retrieval["embedding_labels"])
    st.write(f"Step 1 · retrieval for the question (top {retrieval['top_k']}, embeddings {labels}):")
    st.table([{**hit, "bm25_rank": _rank(hit["bm25_rank"])} for hit in retrieval["hits"]])
    for number, step in enumerate(suggestion.get("steps") or [], start=2):
        if step["action"] == "search_passages":
            new = ", ".join(step["new"]) or "nothing new"
            st.write(f"Step {number} · model called search_passages({step['query']!r}) → found {new}")
        else:
            st.write(f"Step {number} · model answered ({step['status']})")


def _rank(rank: int | None) -> str:
    """A passage with no shared keyword has no BM25 rank; show a dash rather than an empty float column."""
    return "—" if rank is None else str(rank)


def review_actions(state: dict, dataset: Dataset, view: dict) -> None:
    """One text area serves edit and approval; the note serves approval overrides and leaving unresolved."""
    item = view["item"]
    with st.expander("Review: edit, approve or leave unresolved", expanded=view["status"] != "approved"):
        st.text_area("Answer text", value=prefill_text(view), key=f"text-{item}")
        options = [p.id for p in dataset.authoritative_passages()]
        defaults = [pid for pid in default_sources(state, view) if pid in options]
        st.multiselect("Supporting passages", options, default=defaults, key=f"sources-{item}")
        st.text_input("Reviewer", value=view["owner"] or "", key=f"by-{item}")
        st.text_input("Note", key=f"note-{item}")
        edit, accept, leave = st.columns(3)
        if edit.button("Save edit", key=f"edit-{item}"):
            run_action(state, dataset, item, "edit")
        if accept.button("Approve", key=f"approve-{item}", type="primary"):
            run_action(state, dataset, item, "approve")
        if leave.button("Leave unresolved with note", key=f"leave-{item}"):
            run_action(state, dataset, item, "note")


def prefill_text(view: dict) -> str:
    """The newest wording a person or the model gave: an edit, then the approval, then the draft."""
    if view["edited"]:
        return view["edit_text"]
    if view["approval"]:
        return view["approval"]["text"]
    suggestion = view["suggestion"] or {}
    return suggestion.get("answer") or (suggestion.get("draft") or {}).get("answer", "")


def default_sources(state: dict, view: dict) -> list[str]:
    """Passage IDs to preselect, each once (two excerpts can come from the same passage)."""
    if view["approval"]:
        ids = [s["passage_id"] for s in view["approval"]["sources"]]
    elif view["stale_approval_shown"]:
        stale = next(a for a in state["approvals"] if a["id"] == view["stale_approval_shown"])
        ids = [s["passage_id"] for s in stale["sources"]]
    else:
        ids = [c["passage_id"] for c in view["citations"]]
    return list(dict.fromkeys(ids))


def run_action(state: dict, dataset: Dataset, item: str, action: str) -> None:
    """Apply one reviewer action and save it; a refusal (empty text, a blocked approval) is shown as is."""
    values = st.session_state
    text, by, note = values[f"text-{item}"], values[f"by-{item}"], values[f"note-{item}"]
    try:
        if action == "edit":
            save_edit(state, item, text, by, now())
        elif action == "approve":
            sources = values[f"sources-{item}"]
            approve(state, dataset, make_client(), item, text, sources, by, note, now())
        else:
            add_note(state, item, note, by, now())
    except ValueError as exc:
        st.error(str(exc))
        return
    save_state(workspace()[0], state)
    st.rerun()


def main() -> None:
    st.set_page_config(page_title="Questionnaire review", layout="wide")
    path, additions = workspace()
    state, dataset = load_workspace(path, additions)
    request_id, statuses = sidebar(state, dataset, path)
    st.title("Questionnaire review")
    st.button("New request", key="new-request", on_click=new_request)
    if not request_id:
        st.info("No request yet. Press New request to run the questionnaire.")
        return
    st.download_button(
        "Export request as Markdown",
        export_markdown(state, dataset, request_id),
        file_name=f"questionnaire-{request_id}.md",
        mime="text/markdown",
    )
    request = next(r for r in state["requests"] if r["id"] == request_id)
    for question_id in request["questions"]:
        view = item_view(state, dataset, f"{request_id}/{question_id}")
        if view["status"] in statuses:
            render_item(state, dataset, view)


if __name__ == "__main__":
    main()
