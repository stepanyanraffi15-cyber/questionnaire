# 026 · The supplied seed cases are checked on the first run of the unmodified seed

- Status: accepted
- Requirements: `data/seed/domain.md:18` "Keep seed cases and their expected results so the reviewer can run the same
  checks."; the assignment brief's "Keep the provided seed cases and their expected results." and "The supplied
  expected values apply to the original seeds; recalculate them if added data changes a total."

## Context

`starter-pack/README.md:7` says "The supplied expected results apply to the original seeds. Check new expected results
separately before comparing your application with them." An earlier draft of this design added documents and
questions, so it needed a separate baseline step (S0) on the seed alone before the scenario ran on the seed plus the
additions. No documents or questions are added any more (decision 033): the scenario's first run loads exactly the
supplied seed, and the only change file is applied later, at S7.

## Options considered

1. **Keep a separate baseline step S0 on the seed, then start the scenario with an identical first run.** Two runs of
   the same input; the second adds steps and counts to explain but no new check.
2. **Merge the baseline into the scenario's first run: S1 runs Q1–Q8 on the unmodified seed as request R1, and the
   supplied cases are checked there.**

## Decision

Option 2. The scenario has steps S1 to S11:

- S1: first run, request R1 (Q1–Q8 on the seed only).
- S2: save W on R1/Q1 and E3 on R1/Q3, neither approved, and leave note N on R1/Q2 (decision 025).
- S3: re-run as R2.
- S4: approve R1/Q1 with W, sources [EXPORT-v2:p1].
- S5: re-run as R3.
- S6: reload.
- S7: apply the EXPORT-v2 version change (decision 024).
- S8: re-run as R4.
- S9: reload.
- S10: re-approve R1/Q1 with W.
- S11: re-run as R5.

The three supplied cases (Q1, Q2, Q3) are checked on R1 at S1. Expected S1 counts: answered 7, unresolved 1,
approved 0. Every request has eight items; the items that reuse an approval are R3/Q1 and R5/Q1.

## Consequences

- The supplied expectations apply unchanged, because R1 runs on exactly the data they were written for.
- One fewer run to record and explain.

## Evidence

- `data/seed/domain.md:18`.
- `starter-pack/README.md:7`.
- `data/seed/expected-seed-results.json:2-18` (the supplied Q1, Q2 and Q3 cases).
