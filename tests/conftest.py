"""Shared test setup. Tests never call a live model: keys are removed and network connections fail.

`SimulatedClient` returns hand-written replies, taken from the seed passages and labelled SIMULATED. It
stands in for the model so the rules can be tested offline; it is not evidence of how the real model
behaves. Its embeddings are word-count vectors, so retrieval runs offline too.
"""

from __future__ import annotations

import hashlib
import json
import re
import socket

import pytest

from qa.llm import Embedding, ModelCallError, ModelReply

KEY_VARIABLES = ("GOOGLE_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI")

W = "No. CSV export is for paid plans only; free-plan users cannot export CSV."


def _answered(answer: str, passage_id: str, excerpt: str) -> dict:
    citation = {"passage_id": passage_id, "excerpt": excerpt}
    return {
        "basis": "simulated",
        "action": "answer",
        "query": "",
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
        "action": "answer",
        "query": "",
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


def _unresolved(*conflict: str) -> dict:
    pairs = [{"passage_ids": list(conflict), "basis": "simulated"}] if conflict else []
    return {
        "basis": "simulated",
        "action": "answer",
        "query": "",
        "status": "unresolved",
        "answer": "",
        "citations": [],
        "conflicts": pairs,
    }


# The extended questionnaire (X1-X26), hand-written from data/additions/extended.json.
EXTENDED_DRAFTS = {
    "When do scheduled exports run?": _answered(
        "Once a day at 02:00 UTC.", "EXPORT-SCHEDULE-v1:p1", "Scheduled exports run once a day at 02:00 UTC."
    ),
    "Where can scheduled exports be sent?": _answered(
        "They can be sent to an SFTP server.",
        "EXPORT-SCHEDULE-v1:p1",
        "Scheduled exports can be sent to an SFTP server.",
    ),
    "Can scheduled exports be sent to Amazon S3?": _unresolved(),
    "How many rows can a single CSV export contain?": _answered(
        "Up to 50,000 rows.", "EXPORT-LIMITS-v2:p1", "A single CSV export can contain up to 50,000 rows."
    ),
    "How long can export files be downloaded after they are created?": _unresolved(
        "EXPORT-FILES-v1:p1", "EXPORT-HELP-v1:p1"
    ),
    "Is XLSX export available?": _unresolved(),
    "How quickly do paid-plan customers get a first reply to email support?": _answered(
        "Within one business day.",
        "SUPPORT-REPLY-v1:p1",
        "Paid-plan customers receive a first reply to email support within one business day.",
    ),
    "Is phone support offered?": _answered(
        "No, phone support is not offered.", "SUPPORT-CHANNELS-v1:p1", "Phone support is not offered."
    ),
    "Are support requests written in French answered?": _unresolved(),
    "How often are status updates posted during an incident?": _answered(
        "Every 30 minutes.",
        "SUPPORT-STATUS-v2:p1",
        "During an incident, status updates are posted every 30 minutes.",
    ),
    "In which languages is the help centre available?": _unresolved(
        "SUPPORT-HELPCENTRE-v1:p1", "SUPPORT-FAQ-v1:p1"
    ),
    "When are support tickets closed automatically?": _answered(
        "After 14 days without a customer reply.",
        "SUPPORT-TICKETS-v1:p1",
        "Support tickets are closed automatically after 14 days without a customer reply.",
    ),
    "Can account owners require two-factor authentication for the whole team?": _answered(
        "Yes, account owners can require it for the whole team.",
        "ACCESS-2FA-v1:p1",
        "Account owners can require two-factor authentication for the whole team.",
    ),
    "Who can turn on two-factor authentication for their own account?": _answered(
        "Each user can turn it on in their profile settings.",
        "ACCESS-2FA-v1:p1",
        "Each user can turn on two-factor authentication in their profile settings.",
    ),
    "Can account owners remove team members and change their roles?": _unresolved(),
    "After how long are inactive sessions signed out?": _answered(
        "After 8 hours.", "ACCESS-SESSION-v2:p1", "Inactive sessions are signed out after 8 hours."
    ),
    "Do passwords expire?": _answered(
        "No, passwords do not expire.", "ACCESS-PASSWORD-v1:p1", "Passwords do not expire."
    ),
    "Can guest users view shared reports?": _unresolved("ACCESS-GUEST-v1:p1", "ACCESS-GUEST-NOTE-v1:p1"),
    "How long are sign-in attempts kept in the audit log?": _answered(
        "For 90 days.", "ACCESS-AUDIT-v1:p1", "Sign-in attempts are kept in the audit log for 90 days."
    ),
    "Within how many days of a payment can a refund be requested?": _answered(
        "Within 30 days of a payment.",
        "BILLING-REFUND-v2:p1",
        "Refunds can be requested within 30 days of a payment.",
    ),
    "Can payments be made by credit card?": _answered(
        "Yes, payments can be made by credit card.",
        "BILLING-PAYMENT-v1:p1",
        "Payments can be made by credit card.",
    ),
    "Is credit card the only accepted payment method?": _unresolved(),
    "Is annual billing offered?": _answered(
        "No, annual billing is not offered.", "BILLING-TERMS-v1:p1", "Annual billing is not offered."
    ),
    "Do prices on the pricing page include sales tax?": _unresolved(
        "BILLING-TAX-v1:p1", "BILLING-PRICING-v1:p1"
    ),
    (
        "Are refunds paid back to the original payment method, and how long do they take to arrive?"
    ): _unresolved(),
    "Do passwords expire, and how many failed sign-in attempts lock an account?": _unresolved(),
}


def search_step(query: str) -> dict:
    """A simulated draft step that calls the search_passages tool."""
    return {
        "basis": "simulated",
        "action": "search_passages",
        "query": query,
        "status": "unresolved",
        "answer": "",
        "citations": [],
        "conflicts": [],
    }


def simulated_vector(text: str) -> list[float]:
    """64 buckets of word counts: texts sharing words point the same way, with no model involved."""
    vector = [0.0] * 64
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        vector[hashlib.sha256(word.encode()).digest()[0] % 64] += 1.0
    return vector if any(vector) else [1.0] + [0.0] * 63


class SimulatedClient:
    """Replies keyed by question text (drafts) or by answer text (support checks). Counts every call.

    A draft entry may be a list of steps: the client plays them in order, one per draft call for that
    question, which is how the search loop is tested.
    """

    def __init__(
        self, drafts: dict | None = None, unsupported: set[str] | None = None, fail: set[str] | None = None
    ):
        self.drafts = {**DRAFTS, **EXTENDED_DRAFTS} if drafts is None else drafts
        self.unsupported = unsupported or set()
        self.fail = fail or set()
        self.calls: list[str] = []
        self.steps: dict[str, int] = {}
        self.requests: list[dict] = []

    def embed(self, texts: list[str], task_type: str) -> list[Embedding]:
        return [Embedding(simulated_vector(text), "SIMULATED") for text in texts]

    def call(self, request) -> ModelReply:
        data = json.loads(request.user)
        self.calls.append(request.call_type)
        self.requests.append(data)
        if data["question"] in self.fail:
            raise ModelCallError("api_failure", "SIMULATED provider error 503")
        if request.call_type == "draft":
            body = self.drafts[data["question"]]
            if isinstance(body, list):
                step = self.steps.get(data["question"], 0)
                self.steps[data["question"]] = step + 1
                body = body[min(step, len(body) - 1)]
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
