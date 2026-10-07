# 017 · The reviewer chooses support sources from authoritative passages

- Status: accepted
- Requirements: the assignment brief's "Let a reviewer edit and approve a supported answer, or leave it unresolved
  with a note."; Rule 2 of `data/seed/domain.md` ("A document may replace another only through its explicit
  supersedes field. A newer date alone does not establish authority. Keep replaced text available to reviewers.").
  Ambiguity AMB-33.

## Context

If approval could only reuse the model's citations, a wrong "not documented" (for example on Q4) or a missing citation
could never be corrected and approved. Letting the reviewer type citations or excerpts freely would let unverifiable
evidence into an approval.

## Options considered

1. **Model citations only; state the limitation.**
2. **Free-typed citations and excerpts.** Hard to verify; allows invented excerpts.
3. **A source selector over the authoritative passages.** Replaced passages are never offered.

## Decision

Option 3. When approving, the reviewer picks support sources from a multiselect over the authoritative passages. The
default is the draft's citations, or the stale approval's sources on re-approval. A chosen passage's excerpt is the
draft's excerpt when the draft cited it, otherwise the full passage text. The approval guard (decision 016) runs on the
chosen sources. This splits the work as decision 035 asks: the person chooses the evidence, code checks that the
chosen passages are authoritative and the excerpts verbatim, and the recorded support check judges whether they
support the text.

## Consequences

- A replaced passage cannot be chosen (tested).
- On re-approval of R1/Q1 at step S10, the selector starts from the stale approval's source, EXPORT-v2:p1.
- In replay mode a new text-and-sources combination has no recorded support check, so it needs an override note
  (decision 016).

## Evidence

- `data/seed/domain.md:6`.
- `data/seed/seed.json:38` "Live chat is not offered." (an example of evidence a reviewer may need to select).
