# 015 · "Asked again" means a new request of the same questionnaire; reuse is decided when the item is processed

- Status: accepted
- Requirements: Rule 3 of `data/seed/domain.md` ("Only an approved answer can be reused. An unapproved edit is a
  draft."); the assignment brief's "Let a reviewer edit and approve a supported answer, or leave it unresolved with a
  note. Show the correction and its reuse on a subsequent request; preserve this state after a reload." and "When a
  question is repeated, reuse its approved answer and show its approval and sources."; its minimum demonstration "A
  reviewer’s approved correction appears when the same question is asked again; an unapproved edit is not reused as
  approved knowledge." Ambiguity AMB-15.

## Context

The supplied scenario says "Approve a corrected Q1 answer, then ask Q1 again. Reuse only the approved wording with
approval and source records." The seed does not define how a question is asked again, and it holds one questionnaire:
the flat list Q1–Q8. Two things need deciding: what asking again is, and when reuse is decided. If reuse were
evaluated on every load, an item drafted before the approval would flip to "approved" afterwards, and the saved
evidence could not show that reuse skipped the model.

## Options considered

How a question is asked again:
1. **A new request (run) of the same Q1–Q8 questionnaire, with the same question IDs and texts.** Uses only the
   supplied questions.
2. **A separate follow-up questionnaire whose single question has a new ID and Q1's text.** Would show that matching
   uses text rather than ID, but adds a question that is not in the supplied data (decision 033). Rejected.
3. **A free-text "ask a question" box.** Not required; the scripted checks would need a separate path.

When reuse is decided:
1. **Dynamically:** any item whose text matches a fresh approval shows it whenever the workspace loads. Earlier items
   change retroactively.
2. **At processing time:** when a request processes an item, it looks up the approval; if one is served, a `Reuse`
   record is appended and no model call is made. Earlier items never change.

## Decision

A question is asked again when a new request runs the same Q1–Q8 questionnaire (decision 022). Items are keyed
`request/question`, so R3/Q1 is Q1 in the third request. Reuse is decided at processing time: take the **newest**
approval for the item's match key (decision 014) and serve it only if it is fresh (no stale mark, no stale reasons).
Otherwise serve nothing and draft normally. An older approval is never served after a newer one replaced it.

## Consequences

- The reference scenario (decision 026): S2 saves the corrected wording W on R1/Q1 and the edit E3 on R1/Q3, neither
  approved; at S3 the new request R2 drafts Q1 and Q3 afresh, so R2/Q1 is not W and R2/Q3 is not E3. S4 approves W on
  R1/Q1. At S5 the request R3 serves W on R3/Q1, with the approver, the sources and their versions, and no model call,
  while R3/Q3 is still a fresh draft. After the version change and the re-approval, R5/Q1 at S11 reuses the new
  approval.
- Every request has eight items, so the counts of different requests are comparable (decision 020).
- An item drafted before an approval keeps its draft: R2/Q1 stays answered after S4. The reviewer can approve it
  separately.

## Evidence

- `data/seed/domain.md:7`.
- `data/seed/expected-seed-results.json:21` (row `approval-reuse`).
- `data/seed/seed.json:69-110` (the one questionnaire, Q1–Q8).
