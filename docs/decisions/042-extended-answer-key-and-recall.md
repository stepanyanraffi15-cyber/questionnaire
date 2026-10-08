# 042 · Answer key for the extended questionnaire, re-derived blind, with gold passages and recall@k

- Status: accepted
- Requirements: the starter pack's skill: "Keep expected results in a separate file, with each result linked to its
  input and the rule that determines it" and "verify expected results independently of the application being
  assessed. Do not accept the application's output as the answer key."

## Context

The extended data (decision 039) needs expected results, and retrieval (decision 040) needs a way to tell a retrieval
miss from a drafting mistake.

## Decision

- The key for X1–X26 is the `extended` block of `reference/expected.json`, written from the passages and metadata
  before the application was run on this data. Each row has its passage quotes and authority metadata
  (`derived_from`), `gold_passages`, mechanical checks and, for answered rows, meaning checks (expected facts and
  forbidden claims). The step counts for S1–S5 are hand-computed.
- A separate AI agent re-derived every row blind: it was given the data, `domain.md` and the decision records, and
  was told not to open `src/`, `runs/`, `tests/` or `reference/`. It agreed on every status, reason, owner, gold
  passage, replaced passage and step count. Its output is saved unedited in
  `docs/research/extended-key-blind-rederivation.md`. It proposed extra forbidden claims (for example "within 24
  hours" for X7, "Only administrators" for X14, and "14 days after they are opened" for X12), which were added. Its doubts are
  recorded here: X9 ("English or German are answered") is the most arguable undocumented row, and X2 relies on
  decision 006's reading that a "can" fact answers a "where can" question. Both were kept.
- `gold_passages` are the current passages that answer a question: both sides of a conflict, the documented part of a
  partial question, and none for an undocumented question. The seed rows got the same field, read from their
  `derived_from`; no seed expectation changed.
- The grader reports **recall@k** for each row next to the row's result: the share of gold passages in the first
  retrieval for the question, and the share shown to the model by the end of its searches. It is a measurement, not a
  check, and rows with no gold passage show n/a, not 0 or 1. Retrieval and answers are reported separately because
  relevance labels only loosely predict answer quality (Salemi and Zamani, eRAG, SIGIR 2024; Es et al., RAGAS, EACL
  2024).
- The key is never changed to make a check pass.

## Consequences

- A FAIL can now be read in two parts: was the gold passage retrieved, and was the answer right.
- Test `reference/test_grade.py` checks the extended counts against the rows' statuses, every quote and authority
  entry against the data, gold passages against current passages, and the recall arithmetic.

## Evidence

- `docs/RESULTS.md` (extended summary and the recall table).
- Salemi and Zamani, https://arxiv.org/abs/2404.13781.
