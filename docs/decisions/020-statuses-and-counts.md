# 020 · Item statuses are disjoint; counts are per request

- Status: accepted
- Requirements: the assignment brief's "Create a questionnaire queue with status filters" and "Show answered,
  unresolved, and approved counts."; its note "The supplied expected values apply to the original seeds; recalculate
  them if added data changes a total." Ambiguity AMB-13.

## Context

The seed defines one status value, `unresolved` (row Q2 of `expected-seed-results.json`). The brief names three counts
but does not define them, and an approved answer whose source changed needs a "needs review" state. If the expected
counts and the observed counts use different definitions, count checks fail for the wrong reason.

## Options considered

1. **Disjoint statuses:** pending, answered (checked draft, not approved), unresolved, approved (with a `reused`
   flag), needs_review, error. Counts are per request; the three required ones come first.
2. **Nested:** approved is a subset of answered.

## Decision

Option 1. Status is computed from records, first match wins: (1) the item has a deciding approval (its newest linked
approval) → approved if fresh, otherwise needs_review; (2) its latest processing failed → error; (3) a note is newer
than its latest suggestion or edit → unresolved; (4) the latest suggestion's status (answered or unresolved);
(5) pending. Counts are shown per request as answered, unresolved, approved, then needs review, error, pending. Status
and reason values and the counts are mechanical facts (decision 035).

### As built (2026-10-08)

There is no fifth status `pending`. An item with neither a suggestion nor an approval cannot arise from a processed request; if it ever did, it shows as `error` with reason `not_processed`. Counts are answered, unresolved, approved, needs_review and error.

## Consequences

- The first run on the seed (R1 at step S1): answered 7, unresolved 1, approved 0. No data is added (decision 033), so
  the supplied seed totals apply unchanged.
- After W is approved on R1/Q1 (S4), R1 reads answered 6, unresolved 1, approved 1; after the version change (S7),
  answered 6, unresolved 1, approved 0, needs review 1.
- A reused item counts as approved in its own request (R3/Q1 at S5).
- Every request has eight items, and its counts sum to eight; the answer key checks this in code.
- Test fixture FX-1 (never part of the demonstration): answered 6, unresolved 2.

## Evidence

- `data/seed/expected-seed-results.json:10` Q2 `"status": "unresolved"` (the only status value supplied).
- `data/seed/seed.json:69-110` (eight questions).
