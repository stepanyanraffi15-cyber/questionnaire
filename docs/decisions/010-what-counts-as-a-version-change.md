# 010 · What counts as "a referenced document version changes"

- Status: accepted
- Requirements: Rule 3 of `data/seed/domain.md` ("Mark an approved answer for review if a referenced document version
  changes."); the assignment brief's "If an approved answer’s source version changes, mark it for review before reuse;
  a simple version comparison is enough." and "Reloading preserves approval and evidence. Changing a referenced source
  version makes its approved answer require review." Ambiguities AMB-2 (version change) and AMB-19 (which references
  count).

## Context

Each document has an integer `version`, and the seed's IDs embed it (`EXPORT-v1` version 1, `EXPORT-v2` version 2).
In the seed, a new version of a policy arrives as a **new document ID that supersedes the old one**. If staleness
compared only the cited document's own version field, a new document superseding EXPORT-v2 would leave an approved Q1
answer citing EXPORT-v2 version 2 "fresh", and it would be reused from a replaced source. That conflicts with Rule 2
and with the minimum demonstration "the answer uses the document that explicitly supersedes it".

An approved Q1 answer also displays EXPORT-v1:p1 as replaced context. It is not support.

## Options considered

1. **Same document ID, different version field.** Minimal and literal; misses a new superseding document and silent
   text edits.
2. **Option 1, plus "the cited document is now replaced" through another loaded document's supersedes, plus "the cited
   document or passage is no longer loaded".** Still a simple metadata comparison; matches the seed's convention.
3. **Option 2 plus a text hash.** Catches silent edits; goes beyond "a simple version comparison".
4. **Lineage by ID prefix ("EXPORT-*").** Invents a naming rule. Rejected.

Which references: (a) support citations only; (b) support plus replaced or conflict context.

## Decision

Option 2 with references (a). At approval, the record snapshots `(passage_id, doc_id, version, excerpt)` for every
support source. An approval is stale when, for any snapshot entry, the document's version differs (higher or lower),
the document is now replaced, or the document or passage is no longer loaded. All three are mechanical comparisons
(decision 035). Each stale reason is stored as fields (the document, its version at approval and its current version,
or what replaced it, or that it is missing) and shown to people as one line, for example "EXPORT-v2: version 2 at
approval, 3 now". Tests and the answer key compare the fields, not the sentence. Replaced context is displayed but
does not drive staleness. Checks run at load and again before every reuse.

## Consequences

- A text edit with no version change is not detected; stated as a limitation.
- Document-level granularity: a SUPPORT-v1 change marks both Q3 and Q4 approvals. Safe over-flagging.
- Tests: a version bump (stale); a new superseding document (stale), using a test-fixture copy of EXPORT-v2 under the
  ID EXPORT-v3 that supersedes EXPORT-v2 with the text unchanged; a removal (stale); a bump of an unrelated document
  (fresh). The reference scenario uses the version bump (decision 024).

## Evidence

- `data/seed/domain.md:7`.
- `data/seed/seed.json:17-21` (EXPORT-v2 version 2, supersedes EXPORT-v1).
- `data/seed/expected-seed-results.json:25` (row `source-change`): "Change the version of an approved answer’s source.
  Mark the answer for review before reuse."
