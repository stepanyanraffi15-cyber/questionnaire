# 011 · Stale marks are sticky until re-approval

- Status: accepted
- Requirements: Rule 3 of `data/seed/domain.md` ("Mark an approved answer for review if a referenced document version
  changes."); the assignment brief's "Reloading preserves approval and evidence. Changing a referenced source version
  makes its approved answer require review." Ambiguity AMB-18.

## Context

Once a source version changes, the approved answer needs review. If the version is later changed back, should the
approval silently become reusable again? A computed check would say yes; a recorded mark would say no until a person
looks at it.

## Options considered

1. **Computed:** recompute staleness on every load; a revert clears it. Simplest, but a change and its revert can bring
   an answer back into reuse without anyone reviewing it.
2. **Sticky:** the first time an approval's stale reasons are non-empty, append a `StaleMark` record. The approval
   stays stale, even after a revert, until a reviewer re-approves. Auditable; matches "Mark … for review".

## Decision

Option 2. A `StaleMark` (approval id, reasons, time) is appended once and never modified. The approval stays "needs
review" until a person re-approves, even if the source changes back. Re-approval appends a **new** approval with a new
version snapshot and a `replaces` link to the previous one; the old approval keeps its mark. Re-approval is a built and
tested path.

## Consequences

- In the reference scenario, S7 applies the EXPORT-v2 version change: R1/Q1 (where W was approved) and R3/Q1 (which
  was served that approval) become needs review. S10 re-approves R1/Q1 with W at EXPORT-v2 version 3; the new approval
  replaces the S4 one, which keeps its mark. R3/Q1 stays needs review, because earlier items never change (decision
  015). The next request, R5 at S11, reuses the new approval.
- A unit test changes EXPORT-v2 to version 3 and back to 2: the approval stays needs review.
- Interview or demo drills that toggle a version run in a separate state directory (`QA_STATE_DIR`), so the
  demonstration's state is not left in needs review.

## Evidence

- `data/seed/domain.md:7`.
- `data/seed/expected-seed-results.json:25` (row `source-change`).
