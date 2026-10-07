# 013 · What a repeated question shows when its approval is stale

- Status: proposed
- Requirements: Rule 3 of `data/seed/domain.md` ("Only an approved answer can be reused. An unapproved edit is a draft.
  Mark an approved answer for review if a referenced document version changes."); the assignment brief's "If an
  approved answer’s source version changes, mark it for review before reuse; a simple version comparison is enough."
  Ambiguity AMB-11.

## Context

After a source version changes, the approved Q1 answer needs review. When the same question arrives again in a new
request, the system must not serve the stale wording as approved, but the reviewer's earlier wording is useful for
re-approval.

## Options considered

1. **A fresh draft only; hide the stale approval.** The reviewer's wording is lost from view.
2. **A fresh draft, with the stale approval shown beside it and labelled.** Helps re-approval; nothing stale is
   presented as approved.
3. **Nothing until review.** Blocks the user; the item sits in "needs review".

## Decision

Option 2. A stale approval is never served or counted as approved. Items linked to it show `needs_review` with their
stale reasons. A new request gets a fresh model draft (with its own status) and the stale approval shown next to it,
labelled "approved earlier — source changed (EXPORT-v2 v2→v3) — not reused". Re-approval creates a new snapshot
(decision 011).

## Consequences

- The reference scenario checks R4/Q1 at S8, the first request after the version change: it is not reused, a model
  call is recorded, the stale approval is shown, and R4's approved count is 0.

## Evidence

- `data/seed/domain.md:7`.
- `data/seed/expected-seed-results.json:25` (row `source-change`): "Mark the answer for review before reuse."
