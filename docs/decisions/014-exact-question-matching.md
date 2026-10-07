# 014 · Exact question matching: whitespace and Unicode form only; topic ignored

- Status: proposed
- Requirements: the assignment brief's "Exact question matching is sufficient; do not reuse an unreviewed draft as an
  approved answer." and "When a question is repeated, reuse its approved answer and show its approval and sources."
  Ambiguities AMB-3 (how exact) and AMB-10 (topic in the key).

## Context

All eight seed question texts are distinct ASCII strings. A question is repeated when a later request runs the same
questionnaire again (decision 015), so the reference scenario repeats Q1 with byte-identical text. The worked example
in `domain.md` shows Q1 inside curly quotes, which must not become part of a key if copied. Matching on rewording is a
separate, optional feature ("Suggest an approved answer for a differently worded question, while showing the match for
review").

## Options considered

Normalisation:
1. Byte-identical. A trailing space defeats reuse.
2. **NFC, trimmed, whitespace runs collapsed.** Content still identical.
3. Option 2 plus case folding.
4. Option 3 plus stripping trailing punctuation. Options 3 and 4 drift toward "differently worded".

Topic:
1. **Text only.** Matches "exact question matching".
2. Text plus topic. Stricter; goes beyond "question matching".

## Decision

Key = the question text after Unicode NFC, trimming, and collapsing whitespace runs. Case, punctuation and wording
must match. The topic is not part of the key. Exact matching is a mechanical fact, so code decides it (decision 035).
The UI shows the stored text that matched.

## Consequences

- Tests: a whitespace variant matches; "can free-plan users export csv?" does not; "Can free plan users export CSV?"
  (no hyphen) never matches. These unit tests, not an extra question, show that matching uses the text.
- The same text under a different topic would reuse the approval; no such case exists in the data.

## Evidence

- `data/seed/seed.json:73` "Can free-plan users export CSV?"
- `data/seed/domain.md:12` (the question shown inside curly quotes).
