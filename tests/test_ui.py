"""The review page, driven through Streamlit's AppTest. State is prepared on disk with simulated drafts
(labelled SIMULATED), because the page reads its state from disk; the page itself uses the replay client.
"""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from conftest import SimulatedClient
from qa.dataset import ROOT
from qa.review import process_request, workspace_dataset
from qa.store import load_state, save_state, state_path

APP = str(ROOT / "src" / "qa" / "ui.py")
AT = "2026-10-08T00:00:00Z"


def seed_request() -> None:
    """Request R1 drafted by the simulated client: Q2 unresolved, the other seven answered."""
    state = load_state(state_path())
    process_request(state, workspace_dataset(state), SimulatedClient(), AT)
    save_state(state_path(), state)


def open_page() -> AppTest:
    """A new AppTest is a new browser session: nothing carries over except the state file."""
    page = AppTest.from_file(APP, default_timeout=30).run()
    assert not page.exception
    return page


def shown_counts(page: AppTest) -> dict[str, str]:
    return {metric.label: metric.value for metric in page.metric}


def test_page_shows_counts_and_the_queue():
    seed_request()
    page = open_page()
    assert shown_counts(page) == {
        "Answered": "7",
        "Unresolved": "1",
        "Approved": "0",
        "Needs review": "0",
        "Error": "0",
    }
    questions = [m.value for m in page.markdown if m.value.startswith("**Q")]
    assert len(questions) == 8
    assert any("Missing evidence (undocumented)" in w.value for w in page.warning)


def test_approval_survives_a_reload_and_is_reused_by_a_new_request():
    seed_request()
    page = open_page()
    page.text_input(key="note-R1/Q1").input("Checked against EXPORT-v2:p1 by hand")
    page.button(key="approve-R1/Q1").click().run()
    assert not page.exception

    reloaded = open_page()
    assert shown_counts(reloaded)["Approved"] == "1"
    assert load_state(state_path())["approvals"][0]["support_basis"] == "override"

    reloaded.button(key="new-request").click().run()
    assert reloaded.selectbox(key="request").value == "R2"
    assert shown_counts(reloaded)["Approved"] == "1"
    assert any("**REUSED APPROVAL**" in m.value for m in reloaded.markdown)


def test_unresolved_item_without_sources_cannot_be_approved():
    seed_request()
    page = open_page()
    page.text_area(key="text-R1/Q2").input("Yes, JSON export is available.")
    page.button(key="approve-R1/Q2").click().run()
    assert [e.value for e in page.error] == ["Choose at least one supporting passage"]
    assert load_state(state_path())["approvals"] == []


def test_the_extended_questionnaire_has_its_own_workspace_and_shows_the_search_steps():
    seed_request()
    extended = load_state(state_path("workspace-extended"), "data/additions/extended.json")
    process_request(extended, workspace_dataset(extended), SimulatedClient(), AT)
    save_state(state_path("workspace-extended"), extended)
    page = open_page()
    page.radio(key="questionnaire").set_value("Extended questionnaire (X1–X26, added data)").run()
    assert not page.exception
    assert shown_counts(page)["Answered"] == "15" and shown_counts(page)["Unresolved"] == "11"
    assert len([m for m in page.markdown if m.value.startswith("**X")]) == 26
    assert any(text.value.startswith("Step 1 · retrieval for the question") for text in page.markdown)
    assert len(load_state(state_path())["requests"]) == 1
