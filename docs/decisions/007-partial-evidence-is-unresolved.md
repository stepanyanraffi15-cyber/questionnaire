# 007 · A question with only partial evidence is unresolved as a whole

- Status: proposed
- Requirements: Rule 1 of `data/seed/domain.md` ("Use only the supplied fictional product documents as evidence. An
  undocumented feature is unknown, not automatically supported or unsupported."); the assignment brief's "Load the
  documents and questionnaire, preserve their IDs, and check for missing or duplicate references." Ambiguity AMB-22.

## Context

A question may ask for several facts where some are documented and some are not, for example a hypothetical "Can
account owners invite team members and export JSON?". No seed question has this shape, but the rule for it decides how
"unknown" applies to any part of a question.

## Options considered

1. **The whole question is unresolved and goes to the owner; the partial draft is visible to the reviewer but not
   presented as an answer.** One status per question.
2. **"Answered", with the undocumented part stated as "not documented".** Mixed status; the counts become ambiguous.
3. **Split into sub-questions.** Changes questionnaire IDs, against "preserve their IDs".

## Decision

Option 1. The draft prompt says "If the passages answer only part of the question, set unresolved." Whether the
passages answer the whole question is a judgement about meaning, so the model makes it and the reviewer sees it; code
does not try to count the parts of a question (decision 035). The reviewer can still write and approve a supported
answer through the normal guard (decision 016).

## Consequences

- No change to the seed outcomes.
- The counts keep one status per item.

## Evidence

- `data/seed/domain.md:5` "An undocumented feature is unknown, not automatically supported or unsupported."
