# 003 · Supersession replaces whole documents; forks and replaced documents never block answers

- Status: proposed
- Requirements: Rule 2 of `data/seed/domain.md` ("A document may replace another only through its explicit supersedes
  field. A newer date alone does not establish authority. Keep replaced text available to reviewers."); Rule 1 ("Use
  only the supplied fictional product documents as evidence. An undocumented feature is unknown, not automatically
  supported or unsupported."). Ambiguities AMB-20 (scope of supersession) and AMB-21 (forks and replaced documents that
  conflict with unrelated documents).

## Context

`supersedes` is a field on a whole document, and Rule 2 says "A document may replace another". Three situations are not
covered by the seed but follow from the rule's shape:

- A replaced document states a fact that its replacement does not restate.
- Two documents both supersede the same document (a fork).
- A replaced document contradicts a third, unrelated authoritative document.

The seed is unaffected: EXPORT-v1 has one passage, and EXPORT-v2:p1 addresses the same CSV-by-plan fact.

## Options considered

Scope:
1. **Whole-document replacement.** A fact found only in a replaced document is no longer evidence, so the question is
   unknown under Rule 1. Deterministic and literal.
2. **Claim-level replacement.** Only facts the replacement restates are replaced. Needs a meaning judgement and
   reinterprets "replace another".

Forks:
1. **Both replacers are authoritative; if they disagree, the question is an unresolved conflict.**
2. **Pick the replacer by date.** Forbidden by Rule 2.
3. **Reject forks as invalid data.** No rule forbids two documents superseding one.

Replaced document vs unrelated document:
1. **The replaced document has no authority, so only the unrelated one counts; the replaced text is shown.**
2. **Unresolved, because the unrelated document does not supersede it.** Lets a replaced document block answers.

## Decision

Whole-document replacement. Replaced passages are never evidence and are always shown as "Superseded text". In a fork
both replacers are authoritative, and a disagreement between them is an unresolved conflict (whether they disagree is
decided by the model, decision 009). A replaced document never blocks an answer.

## Consequences

- Unit tests cover a chain (C replaced by B, B replaced by A: only A is authoritative), a fork, and a replaced document
  against an unrelated one. Their corpora are variants of the supplied documents (copies with new IDs or changed
  supersedes fields, texts unchanged), so they add no product facts (decision 033).
- A fact that exists only in a replaced document becomes "undocumented"; this is visible because the replaced text is
  still shown to the reviewer.

## Evidence

- `data/seed/domain.md:5`, `:6`.
- `data/seed/domain.md:12` "EXPORT-v2 explicitly replaces it and limits CSV export to paid plans."
- `data/seed/seed.json:12`, `:25` (the one replaced passage and its replacement).
