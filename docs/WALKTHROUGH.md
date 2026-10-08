# Walkthrough

## The problem

A sales team answers buyer questionnaires from company documents. Answers must cite the documents, unknowns must be
routed to the right reviewer instead of guessed, an outdated document must not win over the one that replaced it,
and a reviewer's approved correction must be reused next time, but only while its sources are unchanged.

## The approach in one paragraph

Code applies the four rules; the model writes and checks wording. For each question, Gemini drafts an answer from
the current passages only, with passage IDs and verbatim excerpts. Code checks the IDs, the excerpts and that each
cited passage is current. A second recorded Gemini call checks that the cited passages support every claim. Anything
that fails, or that the passages do not answer, stays unresolved with the owner from the topic map. Reviewers edit,
approve or leave a note; approvals record the source versions, and a version change marks them for review.

## Demo path (replay mode, no API key)

```bash
uv sync --locked
uv run streamlit run src/qa/ui.py
```

1. Click **New request**. Q3 is answered from SUPPORT-v1:p1, with the cited excerpt quoted beside it (MIN-1).
2. Q2 ("Is JSON export available?") is unresolved, routed to the Product reviewer, with a missing-evidence warning;
   Approve is refused until a supporting passage is chosen (MIN-2).
3. Q1 cites EXPORT-v2:p1 and shows EXPORT-v1:p1 in a "Superseded text" box (MIN-3).
4. Edit Q1 to "No. CSV export is for paid plans only; free-plan users cannot export CSV." and save without
   approving. Click **New request**: Q1 is a fresh draft, not the edit. Approve the edit with source EXPORT-v2:p1, then
   **New request** again: Q1 shows **REUSED APPROVAL** with the approver and sources (MIN-4).
5. Refresh the browser or restart the server: everything is still there. Tick **SOURCE CHANGE** in the sidebar
   (EXPORT-v2 goes to version 3): the approved Q1 items turn to **needs review**, "EXPORT-v2: version 2 at approval,
   3 now". A new request drafts Q1 afresh instead of reusing the stale approval (MIN-5).
6. Open **Revision history** on Q1 to see every draft, edit, approval and mark; use **Download** to export the
   request with evidence references and unresolved items.

In replay mode an approval of new wording has no saved support check, so it needs a note and is stored as an
override; the scripted wording above was checked live and replays.

## The extended questionnaire

Switch the sidebar to "Extended questionnaire (X1–X26, added data)" and press New request. This workspace has its own
state file, so the seed counts above do not change. Look at:

- X5: two current documents disagree (7 vs 30 days) and the newer one supersedes nothing, so it stays unresolved
  with both passages shown.
- X4: EXPORT-LIMITS-v2 replaces v1; the old 10,000-row text is shown as replaced. This is also the one FAIL: the
  answer adds a true but unasked sentence about paid plans.
- X9: open "Checks and raw draft". Step 1 is the hybrid retrieval for the question; steps 2 and 3 are the model's own
  `search_passages` calls; it still leaves the question open, because French is never mentioned.

## What the checks show

`uv run qa report && uv run python reference/grade.py` replays both scripted scenarios (seed S1–S11, extended S1–S5)
and grades them against the hand-made key, with retrieval recall@k per row. Code grades the plain checks; the 22
meaning checks (7 seed, 15 extended) count only once the author has compared each answer with its passage and signed
it off in `reference/signoff.json`. The
first real run's Q1 answer failed a meaning check (it said "No" without "paid plans only"); a prompt fix corrected it
(decision 038). See `docs/RESULTS.md` and `docs/LLM_USAGE.md`.

## What I would do next

A cross-family judge, repeated live runs to measure consistency, and a reworded-question suggestion shown for review.
