# How the data was prepared

There are two datasets. The **seed** (`data/seed/`) is exactly as supplied: five documents, Q1–Q8 and the
topic-to-owner map. A test checks that it is byte-identical to `starter-pack/tasks/evidence/`. The **additions**
(`data/additions/extended.json`) are a second, labelled fictional dataset with its own questionnaire, X1–X26
(decision 039). Decision 033 first added nothing; the author later asked for more data to test retrieval and every
scenario kind several times, and 039 replaced that part of 033.

## The seed and its scenario

The seed covers the five scenario kinds in `domain.md` once each:

| Scenario kind | Where |
|---|---|
| Supported | Q3 (and Q4–Q8) |
| Unsupported | Q2: no passage mentions JSON |
| Conflicting source, resolved by metadata | Q1: EXPORT-v2 supersedes EXPORT-v1 |
| Approved reuse | Q1 asked again in a later request (R3, R5) |
| Changed source | EXPORT-v2 version 2 → 3 (below) |

The seed has no conflict that metadata does not resolve. A test covers it (`tests/test_drafting.py`, the seed with
EXPORT-v2's `supersedes` link removed; decision 023), and the extended data now has four such cases.

## The added data (extended questionnaire)

`data/additions/extended.json` (label `ADDED FICTIONAL DATA`): 30 documents with 31 short passages, and questions
X1–X26, in the seed's four topics (exports, support, access, billing). The seed's owner map routes them. It is loaded
beside the seed documents, which stay in the corpus as extra on-topic passages. Its questions replace Q1–Q8 for that
workspace only, so the seed scenario and its counts do not change.

| Scenario kind | Cases |
|---|---|
| Supported | X1, X7, X12, X13, X19, X21 |
| Undocumented (must stay unresolved) | X3, X6, X9, X22 |
| Documented "No" | X8, X17, X23 |
| Conflict settled by `supersedes` | X4, X10, X16, X20 (EXPORT-LIMITS, SUPPORT-STATUS, ACCESS-SESSION, BILLING-REFUND v1 → v2) |
| Conflict `supersedes` does not settle (newer date second, no link) | X5, X11, X18, X24 |
| "can" vs "only" traps | X2, X14 (answered without "only"); X3, X9, X22 (unknown, not No) |
| Partial answers (unresolved, decision 007) | X15, X25, X26 |
| Multi-sentence passages, answer not in sentence 1 | X2, X8, X13, X17 |
| On-topic distractors that answer nothing | EXPORT-AUDIT-v1, SUPPORT-TRAINING-v1, ACCESS-INVITE-v1, BILLING-DISCOUNT-v1, BILLING-TERMS-v1:p2, the seed passages |
| Approved reuse, unapproved edit, note | Extended scenario S2–S3 (X1, X13 approved; X12 edited; X5 note) |
| Changed source version | `data/changes/access-2fa-version-2.json` at S4 (ACCESS-2FA-v1 version 1 → 2) |

Checks made while writing it: every supersedes pair has the old document marked superseded; no conflicting pair is
linked; no added passage changes or contradicts a seed fact (BILLING-TERMS-v1 bears on Q7, which never runs on this corpus); IDs are unique
(`tests/test_extended_data.py`, `uv run qa check-data --additions data/additions/extended.json` reports 0 issues).

## Scenario and change files

| File | What | Check it serves |
|---|---|---|
| `data/scenario/min-demo.json` | Scripted reviewer input for steps S1–S11: which requests to run, the edits, the note, the approvals and fixed times (decisions 025, 026, 036) | MIN-4, MIN-5 |
| `data/changes/export-v2-version-3.json` | The full EXPORT-v2 record with `version` 3; text, date, status and `supersedes` unchanged (decision 024) | MIN-5, RULE-3 |
| `data/scenario/extended-demo.json` | Scripted input for the extended scenario S1–S5: two approvals, an edit, a note, the version change, fixed times | RULE-3, RULE-4 |
| `data/changes/access-2fa-version-2.json` | ACCESS-2FA-v1 at `version` 2, everything else unchanged | RULE-3 |

The reviewer texts only restate passages. Seed scenario:
- W, the corrected Q1 answer: "No. CSV export is for paid plans only; free-plan users cannot export CSV." (EXPORT-v2:p1)
- E3, an edit on Q3 that is never approved: "Email support hours are 09:00 to 17:00 UTC, Monday to Friday."
  (SUPPORT-v1:p1, first sentence)
- N, the note on Q2: "Needs Product reviewer: JSON export is not documented."

Extended scenario: A1 "Scheduled exports run once a day at 02:00 UTC." (EXPORT-SCHEDULE-v1:p1); A13 "Yes. Account
owners can require two-factor authentication for the whole team." (ACCESS-2FA-v1:p1); E12, never approved, "Tickets
close after 14 days without a customer reply." (SUPPORT-TICKETS-v1:p1); N5, the note on the X5 conflict.

**Change-file format:** `{"_purpose", "label", "documents"?: [full records that replace loaded documents by ID],
"owners"?: {topic: owner}}`. A target that is not already loaded is reported as `unknown_change_target` and the file
is not applied. Document IDs are treated as opaque labels, so "EXPORT-v2 at version 3" raises no warning.

**Questionnaire mapping:** each dataset's flat question list is one questionnaire (Q1–Q8, or X1–X26, in file order).
A request is one run of it; items are named request/question, such as R1/Q1 or R1/X5 (decision 022).

## Method

- Hand-written with AI assistance (Claude Code), following the checklist of the starter pack's
  `generate-assignment-data` skill: inputs saved as fixed files, expected results kept separately in `reference/`,
  each result linked to its input and rule, arithmetic checked with code (`reference/test_grade.py`).
- The added data was written by hand with AI assistance for this exercise; every passage is invented and states no
  real product's policy. Its answer key was written from the passages before the application ran on them, then
  re-derived blind by a separate AI agent that never saw the application's code or output (decision 042).
- No random generation, so there is no random seed.
- The skill's `tasks/<task>/` folder is `data/seed/` in this repository.
- Test inputs (variants of the seed for invalid references, the unresolved conflict and an instruction-like passage)
  are built inline in `tests/` and labelled there; none is loaded with the main data.
