# 009 · The model decides contradictions; code verifies only the quotes and the passage

- Status: accepted
- Requirements: the assignment brief's "Flag unsupported claims and conflicting versions. Use a current document when
  explicit metadata resolves the conflict; otherwise leave the question for review." and "Check that references and
  excerpts exist and that the cited content supports the answer."; its description of the model's role: "Synthesize
  answers across documents, recognize missing or conflicting evidence, and reuse corrections that a person has
  reviewed." Ambiguity AMB-34.

## Context

Whether two current passages disagree about the same fact is a judgement about meaning, so the model makes it
(decision 035). The draft is asked to list conflicting pairs, but it can miss one, for example by citing only one side.
The second model call, the support check, receives the question, the answer, the cited passages and the other
authoritative passages (`other_passages`), and it can name a passage that contradicts the answer. That is a useful
second chance. But if every named passage were accepted as given, a slip, such as an invented quote or a passage about
another subject, could turn a correct answer into a conflict.

Examples from the supplied documents:

- In the seed, EXPORT-v1 is replaced, so EXPORT-v1:p1 is never in `other_passages`, and a contradiction naming it
  cannot be accepted for Q1.
- In test fixture FX-1 (decision 023) both EXPORT documents are authoritative. A Q1 draft "No, free-plan users cannot
  export CSV." citing EXPORT-v2:p1 can be contradicted by EXPORT-v1:p1 "CSV exports are available on every plan.",
  with both quotes copied exactly.
- ACCESS-v1:p1 ("Users can sign in with email and password. Account owners can invite team members.") is among the
  other passages for Q7, but it is about another subject; a contradiction naming it against Q7's billing answer would
  be spurious.

## Options considered

1. **Ignore contradictions from the support check.** Only the draft can detect conflicts.
2. **Accept any passage the support check names.** Any naming or copying slip flips a correct answer.
3. **Code decides whether two passages conflict, for example by comparing keywords or numbers.** String rules would
   judge meaning (decision 035). Rejected.
4. **The model decides that a contradiction exists; code verifies only mechanical facts:** the named passage is loaded,
   authoritative, not cited by the answer, and was sent in `other_passages`; the contradicted words from the answer and
   the contradicting sentence from the passage are both verbatim (whitespace collapse only).

## Decision

Option 4. The support check returns each contradiction as a passage ID, the answer claim and the passage quote. Code
checks only the facts listed above. A contradiction that fails any of them is stored under `contradictions_rejected`
and changes nothing. One that passes gives `unresolved` / `conflict` with `conflict_source: support_check`, and the
reviewer sees both passages. The prompt asks the model to list a passage only if it gives a different answer to this
same question. Code does not second-guess that judgement, because whether a verbatim passage is about the same fact is
meaning, not a mechanical fact.

## Consequences

- Residual risk, stated in the README: a spurious but verbatim contradiction would pass code's checks. It would show as
  a failed row, because the answer key requires Q1 and Q3–Q8 on the seed not to have reason `conflict`: no two
  authoritative seed passages disagree. It is fixed by a prompt change and re-recording, never by editing the key.
- Tests with SIMULATED verdicts: P10, a correct Q7 draft whose verdict names ACCESS-v1:p1 with a passage quote that is
  not in that passage, is rejected and Q7 stays answered; P11, the same but with the verbatim quote "Account owners can
  invite team members." and an answer claim that is not in the answer, is rejected; in FX-1, a Q1 draft citing
  EXPORT-v2:p1 with a verdict naming EXPORT-v1:p1, both quotes verbatim, is accepted as `conflict` with
  `conflict_source: support_check`.
- Unit tests also reject a named passage that is unknown, replaced, cited by the answer, or not in `other_passages`.

## Evidence

- `data/seed/domain.md:6` (authority by supersedes only, so unlinked disagreements cannot be settled by metadata).
- `data/seed/seed.json:12`, `:25` (the EXPORT pair used in FX-1); `:51` (ACCESS-v1:p1); `:64` (BILLING-v1:p1, Q7's
  passage, which must stay answered).
