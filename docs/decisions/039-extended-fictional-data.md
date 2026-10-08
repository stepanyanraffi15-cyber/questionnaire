# 039 · Add a second, labelled fictional dataset and questionnaire beside the unchanged seed

- Status: accepted (replaces the "add nothing" part of decision 033)
- Requirements: `data/seed/domain.md:16` "Keep the seeded policies and their authority metadata. Add questions and
  short passages consistent with those rules. Include supported, unsupported, conflicting-source, approved-reuse, and
  changed-source scenarios."; `:18` "Keep seed cases and their expected results so the reviewer can run the same
  checks."; the starter pack's `generate-assignment-data` skill.

## Context

Decision 033 added no documents or questions. The seed has five documents and eight questions, so it could not show
a conflict that `supersedes` does not settle, and retrieval had nothing to choose from: every current passage fit in
the prompt. Adding retrieval (decision 040) needs on-topic passages that do not answer, or recall@k means nothing. The
author asked for more data, generated with the starter pack's skill, with several cases of every scenario kind, and
without changing the seed or its counts.

## Options considered

1. **Add the new documents and questions to the seed questionnaire.** Every seed count, the key's totals and the
   recorded Q1–Q8 answers would change, and new passages could quietly answer or contradict a seed question. Rejected.
2. **A separate additions file with its own questionnaire, loaded beside the seed documents.** The seed scenario,
   its key and its counts stay exactly as they were. Chosen.
3. **A separate dataset with no seed documents.** Simpler, but loses the seed passages as realistic distractors.

## Decision

Option 2.

- `data/additions/extended.json` (label `ADDED FICTIONAL DATA`): 30 documents, 31 passages and questions X1–X26, in
  the seed's four topics, so the seed's topic-to-owner map routes them. Loaded with `load_dataset(additions_path=…)`;
  its documents join the seed's, and its questions replace the seed questions for that workspace.
- Coverage, several cases each: supported (X1, X7, X12, X13, X19, X21); undocumented (X3, X6, X9, X22); documented
  "No" (X8, X17, X23); conflict settled by `supersedes` (X4, X10, X16, X20); conflict `supersedes` does not settle,
  with the newer-dated document second each time (X5, X11, X18, X24); "can" vs "only" traps (X2, X3, X9, X14, X22);
  partial answers (X15, X25, X26); multi-sentence passages where the answer is not the first sentence (X2, X8, X13,
  X17); on-topic distractors that answer nothing (EXPORT-AUDIT, SUPPORT-TRAINING, ACCESS-INVITE,
  BILLING-DISCOUNT, BILLING-TERMS:p2, and the seed passages); approved reuse and a changed source version in the
  extended scenario (`data/scenario/extended-demo.json`, change file `data/changes/access-2fa-version-2.json`).
- No added passage changes or contradicts a seed fact. One bears on a seed question: BILLING-TERMS-v1 (annual
  billing not offered, monthly renewal) touches Q7; see the note under Consequences. The seed scenario still loads
  the seed only.
- Each workspace has its own state file (`state/workspace.json`, `state/workspace-extended.json`), and the UI has a
  questionnaire switch, so the seed counts never change by accident.

## Consequences

- Two scenarios are graded, each against its own key and observed file (decision 042).
- The data is invented and easy: synthetic test sets are easier than real queries (Rahmani et al., SIGIR 2024). The
  results show the rules work on this data, not that the system is accurate in general.
- One note from the blind re-derivation: on this corpus, BILLING-TERMS-v1 documents that annual billing is not
  offered. Seed Q7's key forbids claiming that, which is right for the seed corpus. If Q1–Q8 were ever run on the
  extended corpus, that forbidden claim would need review. They are not.

## Evidence

- `tests/test_extended_data.py` (loads with no issues, same owners, seed unchanged, conflict pairs have no link).
- `data/GENERATION.md` (method and file list).
- Rahmani et al., *Synthetic Test Collections for Retrieval Evaluation*, SIGIR 2024,
  https://arxiv.org/abs/2405.07767; Cuconasu et al., *The Power of Noise*, SIGIR 2024,
  https://arxiv.org/abs/2401.14887 (on-topic distractors hurt more than random ones, so the distractors are on-topic).

## Update (decision 043)

Nine harder questions (X27–X35) and twelve documents were added later; the file now has 42 documents, 43 passages and
questions X1–X35.
