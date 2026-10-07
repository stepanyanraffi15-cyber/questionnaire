# 002 · Newer dates and higher versions grant no authority

- Status: accepted
- Requirements: Rule 2 of `data/seed/domain.md` ("A newer date alone does not establish authority."); the assignment
  brief's "Flag unsupported claims and conflicting versions. Use a current document when explicit metadata resolves the
  conflict; otherwise leave the question for review. Suggest an owner from the topic mapping instead of inventing
  one." Ambiguity AMB-7 (a newer-dated document contradicts an older one without supersedes).

## Context

Four of the five seed documents share the date 2026-08-01. The one older date belongs to EXPORT-v1 (2026-01-01), and
the newer EXPORT-v2 is also the document that supersedes it. So "newest date wins" also passes the seed's Q1 case,
even though Rule 2 forbids it. Each document also has an integer `version`, and the IDs carry a suffix such as `-v2`.
None of these is the supersedes field. Two authoritative documents that disagree and are not linked by any supersedes
chain are a conflict that metadata does not resolve.

The seed contains no such unlinked disagreement, and no documents are added to the main dataset (decision 033). The
case is therefore shown by test fixture FX-1 (decision 023): the supplied EXPORT pair with the supersedes edge removed
and EXPORT-v1 marked current. There EXPORT-v2 has the newer date (2026-08-01 against 2026-01-01), the higher version
(2 against 1) and the "-v2" suffix, and it still must not win.

## Options considered

1. **Date, version and ID suffix never give authority; disagreeing unlinked documents make the question unresolved
   with reason `conflict`; both passages are shown neutrally with dates as plain data.**
2. **Use date or version as a tie-breaker when no edge exists.** Contradicts "A newer date alone does not establish
   authority" and the "only" in Rule 2.
3. **Badge or sort the newer passage as "preferred" in the UI or the prompt.** Brings date back as an implicit signal
   for reviewers and for the model.

## Decision

Option 1. Dates, versions and ID suffixes are never authority signals. They are not sent to the model at all
(decision 004); the UI shows dates as plain data next to each conflicting passage with the note "dates do not decide".
When authoritative passages disagree and no supersedes link joins their documents, the question is `unresolved` with
reason `conflict`, the owner comes from the topic mapping, both passages are shown, and no answer is adopted. Which
documents are authoritative is decided by code from the edges alone; whether two passages disagree about the question
is decided by the model and checked by code and a person (decisions 009 and 035). A document that explicitly
supersedes another still wins even if its date is older; that follows from "only through its explicit supersedes
field" and is pinned by a unit test.

## Consequences

- Test fixture FX-1 is the reference case for this rule: Q1 becomes unresolved with reason `conflict`, owner Product
  reviewer, with EXPORT-v1:p1 and EXPORT-v2:p1 both shown, although EXPORT-v2 is newer and has the higher version.
- Unit tests on variants of the supplied documents, with their texts unchanged: a date-only difference, a version-only
  difference, and an older-dated superseder.
- The model could prefer fresher-looking text if it saw dates; keeping dates out of the prompt removes that path.

## Evidence

- `data/seed/domain.md:6` "A newer date alone does not establish authority."
- `data/seed/seed.json:6`, `:19`, `:32`, `:45`, `:58` (dates; four documents dated 2026-08-01).
- `data/seed/seed.json:5`, `:18` (EXPORT-v1 version 1, EXPORT-v2 version 2).
- `data/seed/document.template.json:4` `"date": "2026-08-01"` (the template default ties with the seed).
