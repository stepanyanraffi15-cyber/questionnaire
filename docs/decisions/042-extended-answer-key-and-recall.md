# 042 · Answer key for the extended questionnaire, re-derived blind, with gold passages and recall@k

- Status: accepted
- Requirements: the starter pack's skill: "Keep expected results in a separate file, with each result linked to its
  input and the rule that determines it" and "verify expected results independently of the application being
  assessed. Do not accept the application's output as the answer key."

## Context

The extended data (decision 039) needs expected results, and retrieval (decision 040) needs a way to tell a retrieval
miss from a drafting mistake.

## Decision

- The key for X1–X35 is the `extended` block of `reference/expected.json`, written from the passages and metadata
  before the application was run on that data (X1–X26 first, X27–X35 later, decision 043). Each row has its passage
  quotes and authority metadata (`derived_from`), `gold_passages`, mechanical checks and, for answered rows, meaning
  checks (expected facts and forbidden claims). The step counts for S1–S5 are hand-computed.
- A separate AI agent re-derived the rows blind, twice: once for X1–X26 and once for X27–X35, with a cross-check
  that the new passages change nothing in X1–X26. Each time it got only the data, `domain.md` and the decision records
  and was told not to open `src/`, `runs/`, `tests/`, `reference/` or `docs/research/`. Both times it agreed on every
  status, reason, owner, gold passage, replaced passage and step count. Its outputs are saved unedited in
  `docs/research/extended-key-blind-rederivation.md` and `…-2.md`.
- `gold_passages` are the current passages that answer a question: both sides of a conflict, the documented part of a
  partial question, and none for an undocumented question. The seed rows got the same field, read from their
  `derived_from`; no seed expectation changed.
- The key never depends on the application's internal numbering: the check that a stale approval is shown for R3/X13
  asks only that one is shown (`not_equals: null`), not for an approval ID such as "A2".
- The key is never changed to make a check pass.

### What the blind derivations suggested, and what was done

| Suggestion | Done | Why |
|---|---|---|
| X2 "Where can scheduled exports be sent?" could be read as asking for every destination (partial) | Rejected; X2 stays answered | Decision 006 treats a "can" fact as answering a "who/where can" question, as for seed Q6 and Q8; the forbidden claims stop "only SFTP" |
| X9 (French) could be read as a closed list, so "No" | Rejected; X9 stays unresolved/undocumented | "English or German are answered" has no "only" (decisions 005, 006); the agent reached the same status |
| X13: forbid "Only account owners can …" | Adopted | The passage says owners can require it, not that only they can |
| X21: forbid saying any other payment method is or is not accepted | Adopted | The passage is silent on other methods |
| X25: show BILLING-REFUND-v1 as replaced "if the draft cites v2" | Rejected; no check added | An unresolved draft keeps no citations, so nothing is shown; the reading is recorded here |
| X14: "each user" may be rephrased "every user" and raise the strengthening hint | Adopted as a reading, no key change | The hint is a warning only (decision 006); the meaning check decides |
| X7 "within 24 hours", X12 "14 days after opening", X14 "Only administrators" | Adopted as forbidden claims | Each states something the passage does not |
| X15: read-only access (ACCESS-READONLY vs ACCESS-OVERVIEW) is arguably a role change, so a checker might call X15 a conflict | Recorded; reason stays "undocumented" | Neither passage says owners can or cannot change roles; the status is unresolved either way |
| X28: BILLING-PAYMENT-v1:p1 may also be cited, since it makes the confirmation email a receipt | Adopted as an allowed citation; the gold passage stays BILLING-RECEIPTS-v1:p1 | It supports the bridge from "confirmation email" to "receipt" |
| X27 a setting that includes archived records; X29 "updated every 30 minutes"; X30 tax included or not; X31 "at most five seats" | Adopted as forbidden claims | Each is stated by no passage (X29's 30 minutes is about incidents, not the status page) |
| X34: forbid "configurable" or "v2 replaces v1" | Not needed | X34 is unresolved, so its presented answer is empty |
| Add checks that R3/X13 cites ACCESS-2FA-v1 at version 2 and that R1/X14 stays answered after the change | Adopted | Both follow from the version change and the rule that only approvals go stale |

### Recall@k is a measurement, not a check

For each row with gold passages the grader reports the share found in the top k by BM25 alone, embeddings alone and
the hybrid list, and the share shown to the model after its own searches. Rows with no gold passage show n/a, never 0
or 1. This comes with a caution rather than support: retrieval relevance only loosely predicts whether the final
answer is right (Salemi and Zamani, eRAG, SIGIR 2024), so recall is shown next to each row's answer result and is
never counted as PASS or FAIL.

## Consequences

- A FAIL can now be read in two parts: was the gold passage retrieved, and was the answer right.
- Test `reference/test_grade.py` checks the extended counts against the rows' statuses, every quote and authority
  entry against the data, gold passages against current passages, and the recall arithmetic.

## Evidence

- `docs/RESULTS.md` (extended summary and the recall table).
- Salemi and Zamani, https://arxiv.org/abs/2404.13781.
