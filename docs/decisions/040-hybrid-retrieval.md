# 040 · Hybrid retrieval over current passages: BM25 plus Gemini embeddings, fused by reciprocal rank

- Status: accepted
- Requirements: the assignment's "Use a model to draft concise answers with supporting passage references"; RULE-2
  ("A document may replace another only through its explicit supersedes field"); GEN-2 (save real responses, replay
  without a key).

## Context

Until now every current passage was sent with every question. With five documents that is fine; with the extended
data (decision 039) it would put 30 passages, most of them off the point, in every prompt. Models are distracted by
irrelevant context (Shi et al., ICML 2023), and related-but-wrong passages hurt most (Cuconasu et al., SIGIR 2024).

## Options considered

1. **Keep sending everything.** Simple, but does not scale and gives distractors to the model.
2. **BM25 only.** A strong, explainable baseline (BEIR, Thakur et al., NeurIPS 2021), but misses paraphrases
   ("first reply" vs "respond").
3. **Embeddings only.** Handles paraphrase, but dense retrievers lose ground on new domains (Chen et al., ECIR 2022).
4. **Both, merged with reciprocal rank fusion.** RRF uses only ranks, so the two scores never need to be calibrated
   (Cormack, Clarke and Büttcher, SIGIR 2009). Tuned score blending can beat it (Bruch et al., TOIS 2023), but we have
   too few rows to tune anything. Chosen.

## Decision

Option 4, in `src/qa/retrieval.py`, with the settings in `config/retrieval.toml`:

- The corpus is `dataset.authoritative_passages()`: superseded passages are removed before retrieval, so a replaced
  passage can never reach the model (decisions 001, 004).
- BM25 (Okapi, k1 = 1.2, b = 0.75, inside the range Robertson and Zaragoza give) over lower-case words, no stemming.
- Gemini `gemini-embedding-001` at 768 dimensions; passages as `RETRIEVAL_DOCUMENT`, queries as `RETRIEVAL_QUERY`.
  That model was chosen because the API docs say `gemini-embedding-2` does not take task types, and its model ID
  differed between two docs pages on 2026-10-08. Similarity is cosine, because shortened vectors are not unit length.
- RRF with k = 60 (the paper's value, "not critical"); top_k = 5. Every ranking breaks ties by passage ID.
- The first search uses the question text. Results keep fused-rank order, so the best passage comes first (Liu et al.,
  *Lost in the Middle*, TACL 2024).
- Embeddings are recorded like model calls: one file per text under `runs/recordings/embed-<fingerprint>.json`,
  keyed by model, size, task type and text. Replay reads only those files, so retrieval needs no key and two replays
  are byte-identical.
- The support check now sees the cited passages plus the other passages the model was shown, not the whole corpus.
  The approval guard's support check uses the passages retrieved for the question.

## Consequences

- Retrieval can miss. If one side of a conflict is not retrieved, the model cannot report it. That is why the key has
  gold passages for both sides and the grader reports recall@k per row (decision 042).
- A new embedding model or size gives new fingerprints, so it needs one new record run.
- With the seed's four current passages and top_k = 5, the seed scenario still sees every passage.

## Evidence

- `tests/test_retrieval.py`: BM25 ordering, RRF ties, current passages only, deterministic results, embedding replay
  and the `no_recording` error.
- `docs/research/retrieval-and-agent.md` (sources, API quotes, open points).
- Robertson and Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*, 2009,
  https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf; Cormack et al., SIGIR 2009,
  http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf; Thakur et al., BEIR, https://arxiv.org/abs/2104.08663; Chen et
  al., ECIR 2022, https://arxiv.org/abs/2201.10582; Lee et al., *Gemini Embedding*, 2025,
  https://arxiv.org/abs/2503.07891; Lewis et al., *Retrieval-Augmented Generation*, NeurIPS 2020,
  https://arxiv.org/abs/2005.11401.
