"""RULE-3, REQ-A3, REQ-D2, REQ-U2: only approvals are reused, exactly; version changes force review; state
reloads.
"""

import pytest

from conftest import SimulatedClient, W
from qa.dataset import ROOT
from qa.review import ApprovalBlocked, add_note, approve, match_key, process_request, save_edit, set_change
from qa.review import workspace_dataset as dataset_of
from qa.staleness import stale_reasons
from qa.store import load_state, new_state, save_state
from qa.views import counts, history, item_view

CHANGE = "data/changes/export-v2-version-3.json"


@pytest.fixture
def workspace():
    state = new_state()
    client = SimulatedClient()
    process_request(state, dataset_of(state), client, "t1")
    return state, client


def test_an_unapproved_edit_is_never_reused(workspace):
    state, client = workspace
    save_edit(state, "R1/Q1", W, "Product reviewer", "t2")
    process_request(state, dataset_of(state), client, "t3")
    view = item_view(state, dataset_of(state), "R2/Q1")
    assert (view["status"], view["reused"]) == ("answered", False)
    assert view["answer"] != W


def test_an_approved_answer_is_reused_exactly_with_no_model_call(workspace):
    state, client = workspace
    approve(state, dataset_of(state), client, "R1/Q1", W, ["EXPORT-v2:p1"], "Product reviewer", "", "t2")
    before = len(client.calls)
    process_request(state, dataset_of(state), client, "t3")
    view = item_view(state, dataset_of(state), "R2/Q1")
    assert (view["status"], view["reused"], view["answer"]) == ("approved", True, W)
    assert view["approval"]["sources"][0]["version"] == 2 and view["replaced_shown"] == ["EXPORT-v1:p1"]
    assert (
        client.calls[before:].count("draft") == 7
    )  # Q1 was served from the approval; the other seven drafted
    assert counts(state, dataset_of(state), "R2")["approved"] == 1


def test_matching_is_exact_apart_from_whitespace():
    assert match_key("Can free-plan  users export CSV? ") == match_key("Can free-plan users export CSV?")
    assert match_key("can free-plan users export csv?") != match_key("Can free-plan users export CSV?")


def test_a_version_change_marks_the_approval_for_review_and_the_mark_is_sticky(workspace):
    state, client = workspace
    approve(state, dataset_of(state), client, "R1/Q1", W, ["EXPORT-v2:p1"], "Product reviewer", "", "t2")
    set_change(state, CHANGE, True, "t3")
    view = item_view(state, dataset_of(state), "R1/Q1")
    assert view["status"] == "needs_review"
    assert view["approval"]["stale_reasons"] == [
        {"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}
    ]
    process_request(state, dataset_of(state), client, "t4")
    assert item_view(state, dataset_of(state), "R2/Q1")["reused"] is False
    set_change(state, CHANGE, False, "t5")  # back to version 2: the mark stays until someone re-approves
    assert item_view(state, dataset_of(state), "R1/Q1")["status"] == "needs_review"
    approve(
        state, dataset_of(state), client, "R1/Q1", W, ["EXPORT-v2:p1"], "Product reviewer", "re-checked", "t6"
    )
    assert item_view(state, dataset_of(state), "R1/Q1")["status"] == "approved"


def test_a_removed_source_passage_also_needs_review():
    approval = {"sources": [{"passage_id": "EXPORT-v2:p9", "doc_id": "EXPORT-v2", "version": 2}]}
    reasons = stale_reasons(approval, dataset_of(new_state()))
    assert reasons == [
        {"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 2, "change": "passage_removed"}
    ]


def test_the_guard_blocks_mechanical_problems_and_needs_a_note_when_support_fails(workspace):
    state, client = workspace
    dataset = dataset_of(state)
    with pytest.raises(ApprovalBlocked):
        approve(state, dataset, client, "R1/Q2", "Yes.", [], "Product reviewer", "", "t2")
    with pytest.raises(ApprovalBlocked):
        approve(state, dataset, client, "R1/Q1", W, ["EXPORT-v1:p1"], "Product reviewer", "", "t2")
    client.unsupported = {"Free plans can export."}
    with pytest.raises(ApprovalBlocked):
        approve(state, dataset, client, "R1/Q1", "Free plans can export.", ["EXPORT-v2:p1"], "P", "", "t2")
    override = approve(
        state, dataset, client, "R1/Q1", "Free plans can export.", ["EXPORT-v2:p1"], "P", "why", "t2"
    )
    assert override["support_basis"] == "override"


def test_state_survives_a_reload_and_keeps_a_revision_history(workspace, tmp_path):
    state, client = workspace
    add_note(
        state, "R1/Q2", "Needs Product reviewer: JSON export is not documented.", "Product reviewer", "t2"
    )
    approve(state, dataset_of(state), client, "R1/Q1", W, ["EXPORT-v2:p1"], "Product reviewer", "ok", "t3")
    path = tmp_path / "workspace.json"
    save_state(path, state)
    reloaded = load_state(path)
    for item in ("R1/Q1", "R1/Q2"):
        assert item_view(reloaded, dataset_of(reloaded), item) == item_view(state, dataset_of(state), item)
    assert [e["event"] for e in history(reloaded, "R1/Q1")] == ["drafted", "approved (A1)"]
    assert (ROOT / CHANGE).exists()
