# 024 · The source-change scenario uses an in-place version bump

- Status: accepted
- Requirements: Rule 3 of `data/seed/domain.md` ("Mark an approved answer for review if a referenced document version
  changes."); the assignment brief's "Reloading preserves approval and evidence. Changing a referenced source version
  makes its approved answer require review." and "If an approved answer’s source version changes, mark it for review
  before reuse; a simple version comparison is enough."; Rule 4 ("Use the supplied topic-to-reviewer mapping.").
  Ambiguity AMB-29.

## Context

The supplied step is "Change the version of an approved answer’s source. Mark the answer for review before reuse."
`data/seed/` must not be edited, so the change must be applied at load time. Two shapes are possible: change
EXPORT-v2's `version` field in place, or add a new document that supersedes EXPORT-v2. In the seed, every ID suffix
equals the version field; an in-place bump breaks that pattern, but no rule says IDs encode versions.

The same load-time mechanism can serve a drill: changing the owner map to see questions route to another reviewer
without a code change. The owner it names must come from the supplied mapping, because an invented role would break
Rule 4.

## Options considered

Source change:
1. **A change file that replaces EXPORT-v2 by ID with the same record at version 3 (same text).** Triggers review under
   every reading of "version changes"; versions are not sent to the model, so prompts are unchanged and existing
   recordings still replay.
2. **A new superseding document (EXPORT-v3) in the scenario.** Also triggers review under decision 010, but adds a
   document to the main data, changes the prompt (a new passage ID), needs new recordings, and changes which document
   Q1 cites.
3. **Edit the seed.** Not allowed.

Drill owner:
1. **A new owner name that is not in the mapping (for example "Data reviewer").** Invents an owner. Rejected.
2. **An existing owner from the mapping: exports → "Support reviewer".**

## Decision

Source change option 1: `data/changes/export-v2-version-3.json`, labelled SOURCE CHANGE, holds the full EXPORT-v2
record with version 3 and the text unchanged. Change files have the shape `{"_purpose", "label", "documents"?: [full
records replacing loaded documents by ID], "owners"?: {topic: owner}}`; a target that is not already loaded gives
`unknown_change_target` and the file is not applied. IDs are treated as opaque labels, so "EXPORT-v2 at version 3"
raises no warning.

Drill owner option 2: `data/changes/drill-exports-owner.json`, labelled DRILL, maps exports to "Support reviewer". It
is never used by the reference scenario; it lets a person watch Q1 and Q2 route to another owner from the mapping with
no code change.

The new-superseding-document case is covered by unit tests with a test fixture: a copy of EXPORT-v2 under the ID
EXPORT-v3 that supersedes EXPORT-v2, with the text unchanged.

## Consequences

- `data/GENERATION.md` explains the ID/version note and both change files.
- Neither change file adds a document, passage, topic or fact (decision 033).

## Evidence

- `data/seed/expected-seed-results.json:25` (row `source-change`).
- `data/seed/seed.json:16-28` (EXPORT-v2).
- `data/seed/seed.json:111-116` (owner map: Product reviewer, Support reviewer, Billing reviewer).
