# 018 · Editing an approved answer creates a pending edit; the approval keeps serving

- Status: accepted
- Requirements: Rule 3 of `data/seed/domain.md` ("Only an approved answer can be reused. An unapproved edit is a
  draft."); the assignment brief's minimum demonstration "A reviewer’s approved correction appears when the same
  question is asked again; an unapproved edit is not reused as approved knowledge." Ambiguity AMB-17.

## Context

A reviewer may want to change wording that is already approved. The rules say an unapproved edit is a draft, so the
edit cannot be reused until approved. What happens to the existing approval meanwhile is not stated.

## Options considered

1. **The approval stays active; the edit is a pending revision, flagged "edited (unapproved)"; approving it appends a
   new approval that replaces the old one for the key.**
2. **Any edit revokes the approval.** An accidental edit destroys a valid approval.
3. **Approved answers cannot be edited.** Corrections need a separate revoke step.

## Decision

Option 1. Approval records are append-only. A new approval for the same match key carries `replaces: <previous id>`,
and only the newest approval for a key can ever be served (decision 015). Revoking approvals is not built.

### As built (2026-10-08)

Approvals carry no `replaces` field. Only the newest approval for a match key is served (`review.newest_approval`), and the revision history lists every approval in order, so what replaced what is still visible.

## Consequences

- Under every option, unapproved edited text is never shown or counted as approved; this is tested. The reference
  scenario shows the same rule on items that were never approved: the edits W (before S4) and E3 are not reused
  (decision 025).
- Tests: after an edit the old approval keeps serving; approving the edit appends a new approval and later requests
  get it.

## Evidence

- `data/seed/domain.md:7`.
