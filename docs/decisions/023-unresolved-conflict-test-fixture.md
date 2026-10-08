# 023 · Test fixture FX-1: an unresolved conflict built from the supplied EXPORT pair

- Status: accepted
- Requirements: the assignment brief's "Use a current document when explicit metadata resolves the conflict; otherwise
  leave the question for review." and "Add questions or short passages only if needed for the checks."; Rule 2 of
  `data/seed/domain.md` ("A document may replace another only through its explicit supersedes field. A newer date alone
  does not establish authority."); `data/seed/domain.md:16` "Include supported, unsupported, conflicting-source,
  approved-reuse, and changed-source scenarios." Ambiguity AMB-25.

## Context

The seed's only conflict (EXPORT-v1 against EXPORT-v2) is resolved by the supersedes field, so the brief's "otherwise
leave the question for review" branch has no input in the supplied data. The seed also cannot tell supersedes-based
authority apart from date- or version-based authority, because for EXPORT all signals agree. The main dataset stays
the supplied seed (decision 033), so this branch needs a test input that adds no product facts.

## Options considered

1. **Add a refund-policy pair (two documents giving different day counts, the newer one with a higher version and no
   supersedes) and a refund question to the main data.** Would show the branch in the demonstration, but invents a
   refund policy and a question that the supplied documents never mention. Rejected.
2. **Add a newer-dated billing document stating another currency, plus a currency question.** Invents a fact and
   contests the passage that answers Q7 ("Paid subscriptions are billed monthly in USD."). Rejected.
3. **Leave the branch untested.** The requirement would have no check. Rejected.
4. **Test fixture FX-1: a copy of the seed with EXPORT-v2's `supersedes` set to null and EXPORT-v1's `status` set to
   "current"; texts, dates and versions unchanged.** Uses only supplied text.

## Decision

Option 4, plus one variant:

- **FX-1** (under `tests/fixtures/`, with a `_purpose` field and the label TEST FIXTURE): the seed with
  EXPORT-v2.supersedes = null and EXPORT-v1.status = "current". Expected: Q1 unresolved, reason `conflict`, owner
  Product reviewer, EXPORT-v1:p1 and EXPORT-v2:p1 both shown as conflicting, no presented answer; Q2–Q8 as in the run
  on the seed; counts answered 6, unresolved 2. Code decides that both documents are authoritative, because no edge
  links them. The model decides that the two passages conflict, through a conflict pair in its draft or a
  support-check contradiction (decision 009), and a person confirms it (decision 035).
- **FX-1b**: the same, except that EXPORT-v1 keeps `status: "superseded"`. Only a supersedes link replaces a document,
  so EXPORT-v1 is still authoritative, and the loader shows a `status_mismatch` warning (decision 034).
- Neither fixture is ever part of the main data or the demonstration.

## Consequences

- FX-1 tests Rule 2's "A newer date alone does not establish authority": EXPORT-v2 is newer (2026-08-01 against
  2026-01-01), has the higher version and the "-v2" suffix, and still does not win (decision 002).
- Limitation of the supplied data, stated in the README: the "otherwise leave the question for review" branch is shown
  by a test fixture, not in the demonstration.
- The seed runs keep their supplied expectations, because FX-1 changes no seed file and no passage text.

## Evidence

- `data/seed/domain.md:6`, `:16`.
- `data/seed/seed.json:3-28` (the EXPORT pair: texts, dates, versions, statuses and the one supersedes edge).

## Update (decision 037)

The lean build did not create `tests/fixtures/`. The same unresolved conflict (EXPORT-v2 without its `supersedes` link) is tested with a small inline variant of the seed in
`tests/`.
