# 043 · Add harder cases so retrieval has to work: paraphrases, multi-fact and buried passages, date traps

- Status: accepted
- Requirements: `data/seed/domain.md` rules 1 and 2 ("An undocumented feature is unknown", "A document may replace
  another only through its explicit supersedes field. A newer date alone does not establish authority."); the
  starter pack's `generate-assignment-data` skill.

## Context

After decision 039, recall@k was 1.00 for every row: the questions shared their key words with the passages that
answer them, so any retriever would have found them. A review asked for cases where retrieval can actually fail, and
for the two authority traps the first set did not have.

## Decision

Nine questions and twelve documents were added to `data/additions/extended.json`, following `domain.md`, in the same
four topics:

| Case | Questions | What makes it hard |
|---|---|---|
| Paraphrase with little word overlap | X27, X28, X29 | "moved to the archive … downloaded file" vs "Archived records are left out of every export"; "payment confirmation email" vs "Receipts"; "stops working on a Sunday" vs "outage … at any time of day or week" |
| Multi-fact passage | X30, X31 | BILLING-SEATS-v1:p1 states three facts; each question needs a different sentence |
| Conflict partner worded differently, buried in a longer passage | X32, X33 | "encrypted at rest" vs "stored without any encryption" (sentence 3 of 4); "can be given read-only access" vs "no way to restrict someone to viewing only" (inside an overview) |
| Unlinked pair where the newer document is version 2 and named -v2 | X34 | EXPORT-DELIMITER-v2 is newer, version 2, and has no `supersedes` link, so it does not win |
| `supersedes` pair where the replacing document has the older date | X35 | BILLING-RETRY-v2 (2026-06-01) supersedes v1 (2026-09-01), so v2 wins |

Key rows were written from the passages only, then re-derived blind (decision 042). The blind agent also checked
that none of the new passages changes the result of X1–X26.

## Consequences

- The extended questionnaire has 35 questions: 21 answered and 14 unresolved when every draft is right.
- Measured result (`docs/RESULTS.md`): BM25 alone missed X27 and X29 (recall 0.94); embeddings alone and the hybrid
  list found every gold passage (1.00). The paraphrases separated keyword search from embeddings, but nothing
  separated embeddings from hybrid. That is a negative result for hybrid retrieval on this data.
- The cases are still short and invented; harder real documents could behave differently.

## Evidence

- `tests/test_extended_data.py` (the date traps and the unlinked pairs).
- `docs/research/extended-key-blind-rederivation-2.md` (the blind key for X27–X35 and the cross-check).
