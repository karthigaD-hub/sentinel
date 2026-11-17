import numpy as np
import pytest

from app.rag.chunker import chunk_text
from app.rag.lexical import BM25Index, tokenize
from app.rag.retriever import IndexedChunk, VectorIndex, extract_identifiers
from app.rag.service import normalized_hash


def _chunk(index: int, text: str) -> IndexedChunk:
    return IndexedChunk(
        chunk_id=f"c{index}",
        document_id="doc",
        source="test",
        external_id=f"ext-{index}",
        text=text,
        text_hash=normalized_hash(text),
        metadata={},
    )


def test_chunk_text_splits_with_overlap():
    words = [f"w{i}" for i in range(25)]
    chunks = chunk_text(" ".join(words), 10, 2)
    assert len(chunks) >= 3
    assert chunks[0].split()[-2:] == chunks[1].split()[:2]


def test_chunk_text_rejects_overlap_not_smaller_than_chunk():
    with pytest.raises(ValueError):
        chunk_text("a b c d", 5, 5)


def test_tokenize_drops_stopwords_and_lowercases():
    tokens = tokenize("The Brute Force attack on SSH")
    assert "brute" in tokens and "force" in tokens
    assert "the" not in tokens


def test_bm25_ranks_matching_document_highest():
    index = BM25Index([tokenize("ransomware encrypts files"), tokenize("phishing email lure")])
    scores = index.scores(tokenize("phishing"))
    assert scores[1] > scores[0]


def test_extract_identifiers_finds_cve_and_attack_ids():
    found = extract_identifiers("See CVE-2021-44228 and technique t1059.001 and T1110")
    assert found == {"CVE-2021-44228", "T1059.001", "T1110"}


def test_search_applies_threshold_and_dedupes_identical_text():
    chunks = [
        _chunk(0, "ransomware encrypts user files"),
        _chunk(1, "ransomware encrypts user files"),
        _chunk(2, "unrelated cooking recipe"),
    ]
    vectors = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    index = VectorIndex(chunks, vectors)
    hits = index.search(np.array([1.0, 0.0], dtype=np.float32), "ransomware", top_k=5, min_similarity=0.3)
    texts = [hit.chunk.text for hit in hits]
    assert texts == ["ransomware encrypts user files"]


def test_search_threshold_excludes_low_similarity_without_identifier():
    chunks = [_chunk(0, "credential stuffing guidance"), _chunk(1, "dns tunnelling notes")]
    vectors = np.array([[0.1, 0.99], [0.0, 1.0]], dtype=np.float32)
    index = VectorIndex(chunks, vectors)
    hits = index.search(np.array([1.0, 0.0], dtype=np.float32), "unrelated question", top_k=5, min_similarity=0.5)
    assert hits == []


def test_identifier_match_bypasses_similarity_threshold():
    chunks = [_chunk(0, "CVE-2021-44228 allows remote code execution via JNDI lookups")]
    vectors = np.array([[0.0, 1.0]], dtype=np.float32)
    index = VectorIndex(chunks, vectors)
    hits = index.search(np.array([1.0, 0.0], dtype=np.float32), "What is CVE-2021-44228?", top_k=3, min_similarity=0.9)
    assert len(hits) == 1
    assert hits[0].matched_identifiers == ("CVE-2021-44228",)


def test_top_k_limits_results():
    chunks = [_chunk(i, f"alert pattern {i} scanning") for i in range(6)]
    vectors = np.tile(np.array([[1.0, 0.0]], dtype=np.float32), (6, 1))
    index = VectorIndex(chunks, vectors)
    hits = index.search(np.array([1.0, 0.0], dtype=np.float32), "scanning", top_k=2, min_similarity=0.0)
    assert len(hits) == 2


def test_normalized_hash_ignores_case_and_whitespace():
    assert normalized_hash("Port  Scan") == normalized_hash("port scan")
