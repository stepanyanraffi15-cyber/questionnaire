# 016 · The approval guard: mechanical problems block; a failed support check needs a recorded note

- Status: accepted
- Requirements: the assignment brief's "Let a reviewer edit and approve a supported answer, or leave it unresolved with
  a note."; Rule 1 of `data/seed/domain.md` ("Use only the supplied fictional product documents as evidence."); Rule 2
  ("A document may replace another only through its explicit supersedes field."). Ambiguities AMB-6 (approvability)
  and AMB-27 (items with no evidence or with a conflict).

## Context

A reviewer can edit wording before approving. The brief pairs "approve a supported answer" with "leave it unresolved
with a note". Two failure modes must be prevented: approving content the documents do not support, and letting a
possibly wrong model verdict permanently block a correct answer. A draft such as "No, only CSV export is offered." for
Q2, citing EXPORT-v2:p1, passes every mechanical check (the citation exists, the excerpt is verbatim); only the
meaning-based support check catches it. Under decision 035, a block must rest on a mechanical fact, and meaning is
judged by the recorded support check and the reviewer.

## Options considered

1. **Block on mechanical checks and on the support check.** Approval depends entirely on a model verdict.
2. **Mechanical problems block; the support check runs on the exact text being approved; a "not supported", failed or
   unavailable check requires a note, stored as an override and shown on every reuse; strengthening words only warn.**
3. **Also block on a strengthening word that none of the source passages contains.** A word list would decide meaning,
   and decision 006 shows it misjudges in both directions. Rejected.
4. **Allow and record.** The reviewer can approve unsupported content without saying why.
5. **Allow silently.** Breaks Rule 1. Rejected.

## Decision

Option 2.

**Hard blocks** (approval impossible; each is a mechanical fact): no support source; a source passage unknown or
replaced; an excerpt not verbatim in its passage; the item's recorded reason is a verified conflict; the item is in
error.

**Warning** (shown, never blocking): strengthening words (only, all, every, always, never, exclusively, solely) that
appear in the text but in none of the chosen source passages.

**Then** the support check runs on the exact text and sources being approved (replayed when that same request was
recorded). If it says not supported, fails, or cannot run, approval requires a note; the approval is stored with
`support_basis: override` and labelled as such on every reuse.

An item with no evidence, such as Q2, cannot be approved until the reviewer selects authoritative sources that pass
the guard (decision 017); otherwise it is left unresolved with a note. An item whose recorded reason is a verified
conflict, such as Q1 in test fixture FX-1, is blocked by that conflict and is left unresolved with a note. No approved
"non-answers".

## Consequences

- In replay mode, new reviewer wording has no recorded support check, so its approval needs an override note. The
  walkthrough uses the scripted corrected wording W, whose check is recorded (decision 025). Stated as a limitation.
- Tests: each hard block; a strengthening word shows a warning and does not block; the override path; Q2 cannot be
  approved with no source.

## Evidence

- `data/seed/domain.md:5`, `:6`.
- `data/seed/seed.json:25` "CSV exports are available on paid plans only. Free-plan users cannot export CSV."
