# 037 · Lean scope: build what the assignment requires, test one behaviour per rule

- Status: accepted
- Requirements: the assignment's "Core scope: one small questionnaire, local text documents, one review workspace,
  and exact-match reuse of approved answers", "Finish the required flow before attempting optional enhancements", and
  the evaluation note "Extra infrastructure or hours do not earn automatic credit".

## Context

The first plan grew well beyond the assignment: batteries of planted drafts and simulated failures stored as fixture
files, a judge calibration set, an owner-map drill, a fixture file per invalid-data case, and several helper
commands. Building it milestone by milestone with multi-agent workflows was slow, and most of those extras check
edge cases the rules do not ask about. The author asked for a lean build: only what the assignment requires, done
simply and correctly, plus the two optional enhancements he chose (export and revision history).

## Options considered

1. **Keep the full plan.** More evidence, but much more code to explain, and slower.
2. **Lean build.** The required flow, the five reference cases, focused tests, and two optional enhancements.

## Decision

Option 2. What is built: loading and validation; authority from `supersedes`; one Gemini draft call with citations
and verbatim excerpts; mechanical checks in code; one recorded Gemini support check for meaning; unresolved items
routed to the mapped owner; edit, approve, and leave-unresolved-with-a-note; exact-match reuse; version change →
needs review (sticky); a JSON state file; record and replay; one Streamlit page; the reference cases graded against
`reference/`; export; revision history.

What earlier records describe but is **not built**, and where the same rule is tested instead:

- Fixture files for invalid data, planted drafts and simulated failures (decisions 008, 009, 021, 023): each rule is
  tested once with a small inline variant of the seed or a hand-written SIMULATED reply in `tests/`. The unresolved
  conflict of decision 023 (EXPORT-v2 without its `supersedes` link) is one such inline test.
- The judge calibration set (decision 027): not built. Meaning checks are graded by the recorded judge plus the
  author's sign-off, which is what decision 027 rests on.
- The owner-map drill file (decision 024): removed. Changing `owners` in a copy of the seed shows the same routing.
- Simulated scenario replies as a data file (decisions 025, 036): the simulated replies live in `tests/conftest.py`.

## Consequences

- Fewer files and tests (about one test per rule or requirement), all offline.
- Edge cases outside the rules (supersedes cycles, forks, a document removed after approval) are handled where the
  code needs it but not separately tested; this is a stated limitation.

## Evidence

- `tests/` (one test per rule or requirement); `reference/test_grade.py`; `docs/RESULTS.md`.
