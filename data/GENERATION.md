# How the data was prepared

## What was added: no documents, passages, topics or questions

The main dataset is `data/seed/` exactly as supplied (five documents, Q1–Q8, the topic-to-owner map). A test checks
that it is byte-identical to `starter-pack/tasks/evidence/`.

Nothing was added to it (decision 033). The assignment allows additions "only if needed for the checks", and the
seed already covers all five checks and the five scenario kinds in `domain.md`:

| Scenario kind | Where |
|---|---|
| Supported | Q3 (and Q4–Q8) |
| Unsupported | Q2: no passage mentions JSON |
| Conflicting source, resolved by metadata | Q1: EXPORT-v2 supersedes EXPORT-v1 |
| Approved reuse | Q1 asked again in a later request (R3, R5) |
| Changed source | EXPORT-v2 version 2 → 3 (below) |

`domain.md` also says "Add questions and short passages consistent with those rules". We read the assignment's
narrower wording as deciding, so the honest gap is that **a conflict that metadata does not resolve** has no input in
the seed. It is covered only by a test (`tests/test_drafting.py`): the seed with EXPORT-v2's `supersedes` link
removed, so the newer EXPORT-v2 must not win by date alone (decision 023). It is not part of the demonstration.

## Inputs added beside the seed (no new facts)

| File | What | Check it serves |
|---|---|---|
| `data/scenario/min-demo.json` | Scripted reviewer input for steps S1–S11: which requests to run, the edits, the note, the approvals and fixed times (decisions 025, 026, 036) | MIN-4, MIN-5 |
| `data/changes/export-v2-version-3.json` | The full EXPORT-v2 record with `version` 3; text, date, status and `supersedes` unchanged (decision 024) | MIN-5, RULE-3 |

The reviewer texts only restate seed passages:
- W, the corrected Q1 answer: "No. CSV export is for paid plans only; free-plan users cannot export CSV." (EXPORT-v2:p1)
- E3, an edit on Q3 that is never approved: "Email support hours are 09:00 to 17:00 UTC, Monday to Friday."
  (SUPPORT-v1:p1, first sentence)
- N, the note on Q2: "Needs Product reviewer: JSON export is not documented."

**Change-file format:** `{"_purpose", "label", "documents"?: [full records that replace loaded documents by ID],
"owners"?: {topic: owner}}`. A target that is not already loaded is reported as `unknown_change_target` and the file
is not applied. Document IDs are treated as opaque labels, so "EXPORT-v2 at version 3" raises no warning.

**Questionnaire mapping:** the seed's flat question list is the one questionnaire (Q1–Q8 in file order). A request is
one run of it; items are named request/question, such as R1/Q1 (decision 022).

## Method

- Hand-written with AI assistance (Claude Code), following the checklist of the starter pack's
  `generate-assignment-data` skill: inputs saved as fixed files, expected results kept separately in `reference/`,
  each result linked to its input and rule, arithmetic checked with code (`reference/test_grade.py`).
- No random generation, so there is no random seed.
- The skill's `tasks/<task>/` folder is `data/seed/` in this repository.
- Test inputs (variants of the seed for invalid references, the unresolved conflict and an instruction-like passage)
  are built inline in `tests/` and labelled there; none is loaded with the main data.
