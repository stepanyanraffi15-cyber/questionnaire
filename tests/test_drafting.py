"""REQ-A1, REQ-A2, RULE-1, RULE-4: drafts are checked mechanically, meaning is the support check's call.

All model replies here are SIMULATED (hand-written from the passages); they test the code's rules, not the
model.
"""

import json

from conftest import DRAFTS, SimulatedClient
from qa.dataset import SEED_PATH, load_dataset
from qa.drafting import draft_item
from qa.review import process_request
from qa.store import new_state
from qa.views import item_view

Q1, Q2, Q3, Q6 = (
    "Can free-plan users export CSV?",
    "Is JSON export available?",
    "When is email support available?",
    "Who can invite team members?",
)


def _question(dataset, text):
    return next(q for q in dataset.questions if q.text == text)


def _with_draft(question_text, **changes) -> SimulatedClient:
    draft = json.loads(json.dumps(DRAFTS[question_text]))
    draft.update(changes)
    return SimulatedClient(drafts={**DRAFTS, question_text: draft})


def test_a_supported_draft_is_answered_with_its_citation_and_version():
    dataset = load_dataset()
    suggestion = draft_item(_question(dataset, Q3), dataset, SimulatedClient())
    assert (suggestion["status"], suggestion["reason"]) == ("answered", None)
    assert suggestion["citations"][0] | {"version": 1} == suggestion["citations"][0]
    assert [c["call_type"] for c in suggestion["calls"]] == ["draft", "support"]


def test_an_undocumented_feature_stays_unresolved_and_routes_to_the_mapped_owner():
    dataset = load_dataset()
    state = new_state()
    process_request(state, dataset, SimulatedClient(), "t")
    view = item_view(state, dataset, "R1/Q2")
    assert (view["status"], view["reason"], view["answer"]) == ("unresolved", "undocumented", "")
    assert view["owner"] == "Product reviewer"


def test_citation_problems_are_caught_by_code():
    dataset = load_dataset()
    q1 = _question(dataset, Q1)
    old = [{"passage_id": "EXPORT-v1:p1", "excerpt": "CSV exports are available on every plan."}]
    assert draft_item(q1, dataset, _with_draft(Q1, citations=old))["reason"] == "superseded_source"
    dashed = [{"passage_id": "SUPPORT-v1:p1", "excerpt": "Monday to Friday, 09:00–17:00 UTC"}]
    q3 = _question(dataset, Q3)
    assert draft_item(q3, dataset, _with_draft(Q3, citations=dashed))["reason"] == "invalid_excerpt"
    unknown = [{"passage_id": "SUPPORT-v1:p2", "excerpt": "Live chat is not offered."}]
    assert draft_item(q3, dataset, _with_draft(Q3, citations=unknown))["reason"] == "invalid_citation"
    assert draft_item(q3, dataset, _with_draft(Q3, citations=[]))["reason"] == "no_citation"


def test_meaning_is_decided_by_the_support_check_and_word_lists_are_only_hints():
    dataset = load_dataset()
    q6 = _question(dataset, Q6)
    overclaim = "Only account owners can invite team members."
    client = _with_draft(Q6, answer=overclaim)
    client.unsupported = {overclaim}
    suggestion = draft_item(q6, dataset, client)
    assert (suggestion["status"], suggestion["reason"]) == ("unresolved", "unsupported_claim")
    assert suggestion["hints"] == ["only"]
    hinted_but_supported = draft_item(q6, dataset, _with_draft(Q6, answer=overclaim))
    assert hinted_but_supported["status"] == "answered"


def test_a_conflict_that_metadata_does_not_resolve_is_left_for_review(tmp_path):
    data = json.loads(SEED_PATH.read_text())
    data["documents"][1]["supersedes"] = None  # EXPORT-v2 is newer, but no longer replaces EXPORT-v1
    seed = tmp_path / "seed.json"
    seed.write_text(json.dumps(data))
    dataset = load_dataset(seed)
    pair = [{"passage_ids": ["EXPORT-v1:p1", "EXPORT-v2:p1"], "basis": "every plan vs paid plans only"}]
    client = _with_draft(Q1, status="unresolved", answer="", citations=[], conflicts=pair)
    suggestion = draft_item(_question(dataset, Q1), dataset, client)
    assert (suggestion["status"], suggestion["reason"]) == ("unresolved", "conflict")
    assert suggestion["conflicts"] == ["EXPORT-v1:p1", "EXPORT-v2:p1"]


def test_failures_are_visible_and_the_batch_continues():
    dataset = load_dataset()
    state = new_state()
    process_request(state, dataset, SimulatedClient(fail={Q2}), "t")
    assert item_view(state, dataset, "R1/Q2")["status"] == "error"
    assert item_view(state, dataset, "R1/Q2")["reason"] == "api_failure"
    assert item_view(state, dataset, "R1/Q3")["status"] == "answered"
    broken = SimulatedClient(drafts={**DRAFTS, Q3: "not json"})
    assert draft_item(_question(dataset, Q3), dataset, broken)["reason"] == "invalid_model_output"
