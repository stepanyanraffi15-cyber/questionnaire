# 021 · Load validation: report bad items by ID and continue; no default owner

- Status: accepted
- Requirements: the assignment brief's "Load the documents and questionnaire, preserve their IDs, and check for
  missing or duplicate references.", "Handle invalid model output, missing references, and API failures visibly." and
  "Suggest an owner from the topic mapping instead of inventing one."; Rule 4 of `data/seed/domain.md` ("Use the
  supplied topic-to-reviewer mapping."). Ambiguities AMB-8 (unmapped topic, unknown references) and AMB-14 (what counts
  as a duplicate reference).

## Context

The seed is internally clean: unique document, passage and question IDs; every topic has an owner; the single
supersedes target exists. Deliberate invalid data is needed to show the checks, and it must add no product facts
(decision 033), so each invalid fixture is a variant of the supplied data. One bad record should not hide every other
result.

## Options considered

1. **Exclude and report the bad item or edge with its ID; everything else continues.**
2. **Route unmapped topics to a default owner.** Invents an owner. Rejected.
3. **Reject the whole batch.** One bad fixture hides every other check.

## Decision

Option 1, with these codes:

| Code | Situation | Effect |
|---|---|---|
| `duplicate_document_id` | Two documents share an ID | All copies excluded |
| `duplicate_passage_id` | Two passages share an ID | Error |
| `duplicate_question_id` | Two questions in the loaded list share an ID | All copies excluded |
| `unknown_question_id` | A reference to a question ID that is not loaded | That reference dropped; other items run |
| `unknown_supersedes` | supersedes names an unknown document | Edge ignored |
| `supersedes_cycle` | Self-supersede or cycle | Self-edge ignored; cycle members count as replaced |
| `unmapped_topic` | Topic not in the owner map | Question excluded; no owner invented |
| `unknown_change_target` | A change file names a document or topic that is not loaded | File not applied (decision 024) |
| `status_mismatch` (warning) | status disagrees with supersedes | Authority unchanged (decisions 001, 034) |

Duplicates are judged on IDs. The same question in a later request is not a duplicate, because the item key is
`request/question` (R1/Q1, R3/Q1). Every code is a mechanical fact (decision 035).

### As built (2026-10-08)

Built codes: `duplicate_document_id`, `duplicate_passage_id`, `duplicate_question_id`, `unknown_supersedes`, `unmapped_topic`, `unknown_change_target` and the warning `status_mismatch`. Not built: `unknown_question_id` (there is no questionnaire file, so a question reference cannot be missing; decision 022) and `supersedes_cycle` (members of a cycle count as replaced, but the cycle is not reported; a stated limitation of the lean scope, decision 037).

## Consequences

- Each code is shown by a deliberate invalid fixture under `tests/fixtures/invalid/`, labelled DELIBERATE INVALID and
  never loaded with the main data. The unmapped-topic fixture is a seed question with its topic misspelt, not a new
  subject.
- The questionnaire is the loaded question list itself (decision 022), so it cannot name a missing question;
  `unknown_question_id` can only come from another input that names question items by ID.
- `qa check-data` prints `CODE ID file` lines and exits 1 on any error.

## Evidence

- `data/seed/seed.json:111-116` (owner map).
- `data/seed/seed.json:21` (the only supersedes edge).
