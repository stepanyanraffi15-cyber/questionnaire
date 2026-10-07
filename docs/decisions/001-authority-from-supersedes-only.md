# 001 · Authority comes only from the supersedes field

- Status: accepted
- Requirements: Rule 2 of `data/seed/domain.md` ("A document may replace another only through its explicit supersedes
  field."); the assignment brief's "Use a current document when explicit metadata resolves the conflict; otherwise
  leave the question for review." and its minimum demonstration "The outdated policy’s conflict is visible, and the
  answer uses the document that explicitly supersedes it." Ambiguities AMB-1 (status vs supersedes) and AMB-24 (what
  "explicit metadata" and "current" mean).

## Context

Each seed document carries two signals that could look like authority: its own `status` field (`current` or
`superseded`) and, on the replacing document, a `supersedes` field naming the document it replaces. In the seed they
agree: EXPORT-v1 has `"status": "superseded"` and EXPORT-v2 has `"supersedes": "EXPORT-v1"`
(`data/seed/seed.json:7`, `:21`). Rule 2 names only the supersedes field and says "only". The brief's wording, "Use a
current document when explicit metadata resolves the conflict", is broader: a reader could map "current" onto the
`status` value. `domain.md` calls its rules "the source of truth for this assignment", so the narrower rule governs.

Because the two signals agree everywhere in the seed, logic that reads only `status` would also pass the seed's Q1
case, so the seed alone cannot tell the two readings apart. No documents are added to the main dataset (decision 033).
Test fixture FX-1b, made from the supplied EXPORT pair, makes the signals disagree instead: it removes EXPORT-v2's
supersedes edge but leaves EXPORT-v1 marked superseded (decisions 023 and 034). Status-only logic would then treat
EXPORT-v1 as replaced; supersedes-only logic keeps it authoritative.

## Options considered

1. **Supersedes only; status is a cross-check that warns on disagreement.** Literal reading of Rule 2. A document
   marked `superseded` that nothing replaces stays authoritative, with a visible warning.
2. **Both must agree, otherwise the document's passages become "authority uncertain" and dependent questions go to
   review.** Conservative, but makes `status` an authority input, which "only through its explicit supersedes field"
   rules out.
3. **Either signal removes authority.** Breaks Rule 2 when status says superseded and no edge exists. Rejected.
4. **Status alone.** Contradicts Rule 2. Rejected.

## Decision

Option 1. A loaded document `b` is **replaced** when some loaded document `a` has `a.supersedes == b.id`; every other
document is **authoritative**. "Current" in the brief's wording means "not replaced through any supersedes edge",
computed from the edges, not read from `status`. Authority is computed in code, so the Q1 outcome never depends on the
model obeying metadata; reading an edge is a mechanical fact in the sense of decision 035. A status/supersedes
disagreement produces the visible warning `status_mismatch` and changes nothing else; decision 034 covers the case of a
document marked superseded that no edge replaces. Treating an explicit edge as sufficient for replacement (not only
necessary) follows the worked example: "EXPORT-v2 explicitly replaces it".

## Consequences

- Q1 is answered from EXPORT-v2:p1 and EXPORT-v1:p1 is shown as replaced text, whatever the dates or statuses say.
- Unit tests cover: replaced via an edge; a status mismatch in both directions (warning only); an edge to an unknown
  document (ignored, error); a self-edge and cycles (error).
- Fixture FX-1b and the deliberate invalid fixture for a status/supersedes mismatch must produce the warning and leave
  authority unchanged.
- Revisit if the rules gain a second authority signal.

## Evidence

- `data/seed/domain.md:6` "A document may replace another only through its explicit supersedes field. A newer date
  alone does not establish authority. Keep replaced text available to reviewers."
- `data/seed/domain.md:3` "These fictional rules are the source of truth for this assignment."
- `data/seed/domain.md:12` "EXPORT-v2 explicitly replaces it and limits CSV export to paid plans."
- `data/seed/seed.json:4-8`, `:17-21` (EXPORT-v1 and EXPORT-v2 metadata).
