# 030 · Review state lives in one append-only JSON file

- Status: accepted
- Requirements: the assignment brief's "Store drafts, cited evidence, review status, edits, and approvals. Keep
  model-generated suggestions separate from approved answers, and retain the source versions behind each approved
  answer." and "Local JSON files or SQLite are sufficient."; its minimum demonstration "Reloading preserves approval
  and evidence."

## Context

State must survive a browser refresh and a restart. In Streamlit, session state resets when the user refreshes the
page, so nothing domain-related can live there. The amount of state is tiny.

## Options considered

1. **One JSON file (`state/workspace.json`, directory set by `QA_STATE_DIR`) with append-only record lists, written
   atomically (temp file plus `os.replace`).**
2. **SQLite.** More machinery for a handful of records.
3. **A JSONL event log.** Needs a replay step to build current state.

## Decision

Option 1. Records: Request, Suggestion, Reuse, Edit, Note, Approval (with version snapshot and `replaces`), StaleMark,
and the list of applied change files. Suggestions, Approvals and StaleMarks are never modified. Model suggestions and
approvals are separate record types, so a suggestion can never be read as an approved answer. Status is computed from
records (decision 020). The UI reads state from disk on every rerun and writes after each action; only selection and
filters live in Streamlit session state. The state directory is gitignored.

### As built (2026-10-08)

Approvals carry no `replaces` field (see decision 018); otherwise as described.

## Consequences

- Two browser tabs writing at once cannot corrupt the file, but the last write wins; documented.
- Tests: atomic write; a reload in a subprocess reproduces the same item views (steps S6 and S9 of the reference
  scenario do the same).

## Evidence

- `data/seed/expected-seed-results.json:25` (row `source-change`; state must persist across a reload).
