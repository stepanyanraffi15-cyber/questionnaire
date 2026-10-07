# 034 · A status of "superseded" without a supersedes link does not replace a document

- Status: accepted
- Requirements: Rule 2 of `data/seed/domain.md` ("A document may replace another only through its explicit supersedes
  field. A newer date alone does not establish authority. Keep replaced text available to reviewers."); the assignment
  brief's "Use a current document when explicit metadata resolves the conflict; otherwise leave the question for
  review." and "Load the documents and questionnaire, preserve their IDs, and check for missing or duplicate
  references." Ambiguity AMB-1 (status vs supersedes).

## Context

In the seed, EXPORT-v1 says `"status": "superseded"` and EXPORT-v2 says `"supersedes": "EXPORT-v1"`, so the two
signals agree. Decision 001 makes the supersedes field the only authority signal. This record settles the case where a
document's own status says "superseded" but no loaded document's `supersedes` field names it. Test fixture FX-1b
(decision 023) is exactly this case: the seed with EXPORT-v2's `supersedes` set to null and EXPORT-v1 left at status
"superseded", texts, dates and versions unchanged.

## Options considered

1. **Not replaced; a `status_mismatch` warning names the document; nothing else changes.** Follows "only through its
   explicit supersedes field".
2. **Replaced, because the document itself says so.** Makes `status` an authority signal, against "only". Rejected.
3. **"Authority uncertain": send every question that depends on the document to review.** Makes `status` an authority
   input in another way, and routes questions for a reason the rules do not name. Rejected.

## Decision

Option 1. In FX-1b, EXPORT-v1 and EXPORT-v2 are both authoritative, and the loader reports one `status_mismatch`
warning, for EXPORT-v1. Both passages reach the model as current evidence (decision 004). Whether they conflict for Q1
is decided by the model and confirmed by a person, as in FX-1 (decisions 009 and 035); from the passages, Q1 is
expected to be unresolved with reason `conflict`, as in FX-1. The opposite mismatch, a document whose status says
"current" while an edge replaces it, is handled the same way: the edge decides and the warning is shown (decision 001).

## Consequences

- Tests: FX-1b loads with one `status_mismatch` warning naming EXPORT-v1, no document is replaced, and EXPORT-v1:p1
  appears in the draft request for Q1.
- The warning is visible to the reviewer among the data issues and in `qa check-data`; it never changes an outcome.
- Revisit if the rules gain a second authority signal.

## Evidence

- `data/seed/domain.md:6`.
- `data/seed/seed.json:7`, `:21` (EXPORT-v1's status and EXPORT-v2's supersedes field).
