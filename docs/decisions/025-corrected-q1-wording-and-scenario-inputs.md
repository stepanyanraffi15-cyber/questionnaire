# 025 · Fixed reviewer inputs for the reference scenario, including the corrected Q1 wording

- Status: accepted
- Requirements: the assignment brief's "Let a reviewer edit and approve a supported answer, or leave it unresolved with
  a note. Show the correction and its reuse on a subsequent request; preserve this state after a reload."; its overview
  "preserves the reviewer’s approved wording for the next identical question"; its minimum demonstration "A reviewer’s
  approved correction appears when the same question is asked again; an unapproved edit is not reused as approved
  knowledge." Ambiguity AMB-26.

## Context

The supplied step says "Approve a corrected Q1 answer, then ask Q1 again" but never gives the correction. Reuse can
only be told apart from a fresh draft if the approved text differs from the model's suggestion. The minimum
demonstration also needs an unapproved edit, and "leave it unresolved with a note" needs a note. The reference check
needs fixed reviewer text, notes, an approver and times so the report is reproducible. These inputs must add no product
facts (decision 033): each one restates a supplied passage or records a review action.

## Options considered

The approved text:
1. **The model's suggestion unchanged.** Reuse and re-drafting would look identical. Rejected.
2. **A fixed corrected wording that only restates EXPORT-v2:p1, which the scenario asserts differs from the recorded
   suggestion.**

Wording of the correction:
1. "No. CSV export is only for paid plans, so free-plan users cannot export CSV." The word "so" states a cause that the
   passage does not state; the passage gives two separate sentences. Rejected.
2. **"No. CSV export is for paid plans only; free-plan users cannot export CSV."**

Wording of the note on Q2:
1. "JSON export is not in the documents; asked the Product reviewer to confirm." It records an action that never
   happens in the app. Rejected.
2. **"Needs Product reviewer: JSON export is not documented."**

## Decision

Option 2 with the second wordings, stored in `data/scenario/min-demo.json` and labelled as scripted reviewer input:

- **W**, the corrected Q1 wording, saved on R1/Q1 at step S2 without approval, approved at S4 and re-approved at S10:
  "No. CSV export is for paid plans only; free-plan users cannot export CSV." Its source: EXPORT-v2:p1.
- **E3**, an edit on R1/Q3, saved at S2 and never approved: "Email support hours are 09:00 to 17:00 UTC, Monday to
  Friday." It only restates the first sentence of SUPPORT-v1:p1, and it shows that an unapproved edit is not reused
  even when other approvals exist.
- **N**, the note left on R1/Q2 at S2: "Needs Product reviewer: JSON export is not documented."
- Approver: "Product reviewer".
- Approval note: "Corrected wording checked against EXPORT-v2:p1."
- Re-approval note: "Re-checked against EXPORT-v2 version 3."
- Times: fixed, one minute apart in step order, starting at 2026-10-08T09:00:00Z.

W's support rests on a person reading it against EXPORT-v2:p1, where each of its three statements ("No", "for paid
plans only", "free-plan users cannot export CSV") is found, and on the recorded support check that runs when it is
approved. That "only" also appears in EXPORT-v2:p1 is at most a hint; it is not why W is accepted (decision 035).

## Consequences

- If the recorded suggestion for Q1 ever equals W, the scenario reports it instead of passing silently.
- R2/Q1 (S3) must differ from W; R2/Q3 (S3) and R3/Q3 (S5) must differ from E3 and are not approved; R1/Q2 stays
  unresolved with N.
- Changing W in the scenario file makes the reuse check fail until the answer key is updated by hand; a useful drill.

## Evidence

- `data/seed/expected-seed-results.json:21` (row `approval-reuse`): "Approve a corrected Q1 answer, then ask Q1 again.
  Reuse only the approved wording with approval and source records."
- `data/seed/seed.json:25` (EXPORT-v2:p1), `:38` (SUPPORT-v1:p1).
