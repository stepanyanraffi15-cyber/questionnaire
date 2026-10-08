"""Decision 041: the model may call one read-only tool, search_passages, a limited number of times.

Every reply here is SIMULATED; these tests check the loop's rules in code, not the model.
"""

import typing

from conftest import SimulatedClient, search_step
from qa.dataset import ROOT, load_dataset
from qa.drafting import draft_item
from qa.prompts import DraftOutput
from qa.retrieval import load_retrieval_settings

EXTENDED = ROOT / "data" / "additions" / "extended.json"
X12 = "When are support tickets closed automatically?"
TICKETS = "Support tickets are closed automatically after 14 days without a customer reply."


def _answer(passage_id: str, excerpt: str) -> dict:
    return {
        "basis": "simulated",
        "action": "answer",
        "query": "",
        "status": "answered",
        "answer": "After 14 days without a customer reply.",
        "citations": [{"passage_id": passage_id, "excerpt": excerpt}],
        "conflicts": [],
    }


def _x12(dataset):
    return next(q for q in dataset.questions if q.text == X12)


def test_a_search_adds_passages_and_every_step_is_recorded():
    dataset = load_dataset(additions_path=EXTENDED)
    client = SimulatedClient(
        drafts={X12: [search_step("tickets closed 14 days"), _answer("SUPPORT-TICKETS-v1:p1", TICKETS)]}
    )
    suggestion = draft_item(_x12(dataset), dataset, client)
    assert (suggestion["status"], suggestion["reason"]) == ("answered", None)
    assert [s["action"] for s in suggestion["steps"]] == ["search_passages", "answer"]
    assert suggestion["steps"][0]["query"] == "tickets closed 14 days"
    assert [c["call_type"] for c in suggestion["calls"]] == ["draft", "draft", "support"]
    second = client.requests[1]
    assert second["searches"][0]["query"] == "tickets closed 14 days" and second["searches_left"] == 1
    assert {p["id"] for p in second["passages"]} >= {p["id"] for p in client.requests[0]["passages"]}


def test_the_model_must_answer_once_its_searches_are_used_up():
    dataset = load_dataset(additions_path=EXTENDED)
    client = SimulatedClient(drafts={X12: [search_step("tickets")]})
    suggestion = draft_item(_x12(dataset), dataset, client)
    settings = load_retrieval_settings()
    assert (suggestion["status"], suggestion["reason"]) == ("error", "step_limit")
    assert client.calls == ["draft"] * (settings.max_searches + 1)
    assert client.requests[-1]["searches_left"] == 0


def test_a_passage_the_model_was_never_shown_cannot_be_cited():
    dataset = load_dataset(additions_path=EXTENDED)
    unseen = "Onboarding webinars are held on the first Tuesday of each month."
    client = SimulatedClient(drafts={X12: _answer("SUPPORT-TRAINING-v1:p1", unseen)})
    suggestion = draft_item(_x12(dataset), dataset, client)
    assert "SUPPORT-TRAINING-v1:p1" not in {p["id"] for p in client.requests[0]["passages"]}
    assert (suggestion["status"], suggestion["reason"]) == ("unresolved", "invalid_citation")


def test_search_passages_is_the_only_tool():
    actions = typing.get_args(DraftOutput.model_fields["action"].annotation)
    assert set(actions) == {"search_passages", "answer"}
