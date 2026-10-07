"""Shared test setup. Tests never call a live model: keys are removed and network connections fail.

`SimulatedClient` returns hand-written replies, taken from the seed passages and labelled SIMULATED. It
stands in for the model so the rules can be tested offline; it is not evidence of how the real model
behaves.
"""

from __future__ import annotations

import json
import socket

import pytest

from qa.llm import ModelCallError, ModelReply

KEY_VARIABLES = ("GOOGLE_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI")

W = "No. CSV export is for paid plans only; free-plan users cannot export CSV."


def _answered(answer: str, passage_id: str, excerpt: str) -> dict:
    citation = {"passage_id": passage_id, "excerpt": excerpt}
    return {
        "basis": "simulated",
        "status": "answered",
        "answer": answer,
        "citations": [citation],
        "conflicts": [],
    }


DRAFTS = {
    "Can free-plan users export CSV?": _answered(
        "No, CSV export is available on paid plans only.",
        "EXPORT-v2:p1",
        "Free-plan users cannot export CSV.",
    ),
    "Is JSON export available?": {
        "basis": "simulated",
        "status": "unresolved",
        "answer": "",
        "citations": [],
        "conflicts": [],
    },
    "When is email support available?": _answered(
        "Monday to Friday, 09:00 to 17:00 UTC.",
        "SUPPORT-v1:p1",
        "Email support is available Monday to Friday, 09:00 to 17:00 UTC.",
    ),
    "Is live chat offered?": _answered(
        "No, live chat is not offered.", "SUPPORT-v1:p1", "Live chat is not offered."
    ),
    "How do users sign in?": _answered(
        "With email and password.", "ACCESS-v1:p1", "Users can sign in with email and password."
    ),
    "Who can invite team members?": _answered(
        "Account owners can invite team members.", "ACCESS-v1:p1", "Account owners can invite team members."
    ),
    "How often are subscriptions billed?": _answered(
        "Monthly.", "BILLING-v1:p1", "Paid subscriptions are billed monthly in USD."
    ),
    "Who can download billing invoices?": _answered(
        "Account owners can download billing invoices.",
        "BILLING-v1:p1",
        "Account owners can download billing invoices.",
    ),
}


class SimulatedClient:
    """Replies keyed by question text (drafts) or by answer text (support checks). Counts every call."""

    def __init__(
        self, drafts: dict | None = None, unsupported: set[str] | None = None, fail: set[str] | None = None
    ):
        self.drafts = DRAFTS if drafts is None else drafts
        self.unsupported = unsupported or set()
        self.fail = fail or set()
        self.calls: list[str] = []

    def call(self, request) -> ModelReply:
        data = json.loads(request.user)
        self.calls.append(request.call_type)
        if data["question"] in self.fail:
            raise ModelCallError("api_failure", "SIMULATED provider error 503")
        if request.call_type == "draft":
            body = self.drafts[data["question"]]
        else:
            supported = data["answer"] not in self.unsupported
            body = {
                "basis": "simulated",
                "supported": supported,
                "unsupported_claims": [],
                "contradicted_by": [],
            }
        text = body if isinstance(body, str) else json.dumps(body)
        return ModelReply(text, "SIMULATED", "simulated", "simulated", "2026-10-08T00:00:00Z")


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    """No keys, replay mode, state in a temporary folder, and any network connection raises."""
    for name in KEY_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("QA_MODE", "replay")
    monkeypatch.setenv("QA_STATE_DIR", str(tmp_path / "state"))

    def refuse(*args, **kwargs):
        raise OSError("network access is disabled in tests")

    monkeypatch.setattr(socket.socket, "connect", refuse)


@pytest.fixture
def client() -> SimulatedClient:
    return SimulatedClient()
