"""Decision 040: hybrid retrieval over current passages, deterministic, with embeddings recorded and replayed.

Embeddings here are SIMULATED word-count vectors (conftest), except in the replay test, which uses a saved
file shaped like a real recording.
"""

import dataclasses
import json

import pytest

from conftest import SimulatedClient
from qa.dataset import ROOT, Passage, load_dataset
from qa.llm import Embedding, ModelCallError, ReplayClient, embedding_fingerprint, load_settings
from qa.retrieval import (
    RetrievalError,
    bm25_ranking,
    bm25_scores,
    fuse,
    hit_ids,
    load_retrieval_settings,
    search,
)

EXTENDED = ROOT / "data" / "additions" / "extended.json"


def test_bm25_ranks_shared_rare_words_first_and_skips_passages_with_no_shared_word():
    passages = [
        Passage("A:p1", "A", "Inactive sessions are signed out after 8 hours."),
        Passage("B:p1", "B", "Passwords do not expire."),
        Passage("C:p1", "C", "Sessions and passwords are covered here."),
    ]
    assert bm25_ranking("When are inactive sessions signed out?", passages, 1.2, 0.75) == ["A:p1", "C:p1"]


def test_reciprocal_rank_fusion_rewards_agreement_and_breaks_ties_by_id():
    fused = fuse([["X", "Y", "Z"], ["Y", "X"]], rrf_k=60)
    assert fused["X"] == fused["Y"] > fused["Z"]
    assert sorted(fused, key=lambda pid: (-fused[pid], pid)) == ["X", "Y", "Z"]


def test_search_returns_top_k_current_passages_only_and_the_same_result_every_time():
    dataset = load_dataset(additions_path=EXTENDED)
    settings = load_retrieval_settings()
    first = search("How many rows can a single CSV export contain?", dataset, SimulatedClient(), settings)
    again = search("How many rows can a single CSV export contain?", dataset, SimulatedClient(), settings)
    assert first == again
    assert len(first["hits"]) == settings.top_k
    assert hit_ids(first)[0] == "EXPORT-LIMITS-v2:p1"
    assert set(hit_ids(first)) <= dataset.current_passage_ids
    assert "EXPORT-LIMITS-v1:p1" not in hit_ids(first)
    assert first["embedding_labels"] == ["SIMULATED"]


def test_embeddings_replay_from_saved_files_and_a_missing_one_is_a_visible_error(tmp_path):
    settings = load_settings()
    fp = embedding_fingerprint("Passwords do not expire.", "RETRIEVAL_DOCUMENT", settings)
    (tmp_path / f"embed-{fp[:16]}.json").write_text(json.dumps({"fingerprint": fp, "vector": [0.6, 0.8]}))
    client = ReplayClient(settings, tmp_path)
    [saved] = client.embed(["Passwords do not expire."], "RETRIEVAL_DOCUMENT")
    assert (saved.vector, saved.label) == ([0.6, 0.8], "REPLAYED")
    with pytest.raises(ModelCallError) as missing:
        client.embed(["Passwords do not expire."], "RETRIEVAL_QUERY")
    assert missing.value.reason == "no_recording"


def test_a_bm25_score_matches_the_hand_computed_value():
    # "apple" is in 1 of 2 passages: idf = ln(1 + (2 - 1 + 0.5) / (1 + 0.5)) = ln 2 = 0.693147.
    # Passage A has 2 words, the average is 2.5: norm = 1.2 * (1 - 0.75 + 0.75 * 2 / 2.5) = 1.02.
    # score = idf * 1 * (1.2 + 1) / (1 + 1.02) = 0.754913. Stopwords ("the") are dropped first.
    passages = [Passage("A:p1", "A", "The red apple"), Passage("B:p1", "B", "green pear pear")]
    assert bm25_scores("the apple", passages, 1.2, 0.75) == {"A:p1": pytest.approx(0.754913, abs=1e-6)}


def test_an_empty_corpus_and_a_bad_embedding_are_visible_errors():
    dataset = load_dataset(additions_path=EXTENDED)
    settings = load_retrieval_settings()
    empty = dataclasses.replace(dataset, documents={})
    with pytest.raises(RetrievalError) as nothing:
        search("Is phone support offered?", empty, SimulatedClient(), settings)
    assert nothing.value.reason == "no_passages"

    class ZeroVectors(SimulatedClient):
        def embed(self, texts, task_type):
            return [Embedding([0.0] * 64, "SIMULATED") for _ in texts]

    with pytest.raises(RetrievalError) as bad:
        search("Is phone support offered?", dataset, ZeroVectors(), settings)
    assert bad.value.reason == "invalid_embedding"


def test_the_first_retrieval_keeps_its_bm25_and_dense_lists_for_measurement():
    dataset = load_dataset(additions_path=EXTENDED)
    result = search("Are export files encrypted?", dataset, SimulatedClient(), load_retrieval_settings())
    assert len(result["bm25_top"]) <= result["top_k"] and len(result["dense_top"]) == result["top_k"]
    assert result["bm25_top"][0] == "EXPORT-ENCRYPTION-v1:p1"
