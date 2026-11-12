import re
from dataclasses import dataclass

import numpy as np

from app.rag.lexical import BM25Index, tokenize

RRF_K = 60
IDENTIFIER_PATTERN = re.compile(r"\bCVE-\d{4}-\d{4,}\b|\bT\d{4}(?:\.\d{3})?\b", re.IGNORECASE)


def extract_identifiers(text: str) -> set[str]:
    return {match.upper() for match in IDENTIFIER_PATTERN.findall(text)}


@dataclass(frozen=True)
class IndexedChunk:
    chunk_id: str
    document_id: str
    source: str
    external_id: str
    text: str
    text_hash: str
    metadata: dict


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: IndexedChunk
    similarity: float
    lexical_score: float
    matched_identifiers: tuple[str, ...]


class VectorIndex:
    def __init__(self, chunks: list[IndexedChunk], vectors: np.ndarray) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunk and vector counts differ")
        self._chunks = chunks
        self._matrix = vectors.astype(np.float32, copy=False)
        self._bm25 = BM25Index([tokenize(chunk.text) for chunk in chunks])

    @property
    def size(self) -> int:
        return len(self._chunks)

    def search(self, query_vector: np.ndarray, query_text: str, top_k: int, min_similarity: float) -> list[RetrievedChunk]:
        if self.size == 0:
            return []
        similarities = self._matrix @ query_vector.astype(np.float32, copy=False)
        pool = max(top_k * 5, 25)
        dense_order = np.argsort(-similarities)[:pool]
        lexical_scores = self._bm25.scores(tokenize(query_text))
        lexical_order = [int(i) for i in np.argsort(-lexical_scores)[:pool] if lexical_scores[i] > 0]

        fused: dict[int, float] = {}
        for rank, index in enumerate(dense_order):
            fused[int(index)] = fused.get(int(index), 0.0) + 1 / (RRF_K + rank + 1)
        for rank, index in enumerate(lexical_order):
            fused[index] = fused.get(index, 0.0) + 1 / (RRF_K + rank + 1)

        query_identifiers = extract_identifiers(query_text)
        seen_hashes: set[str] = set()
        results: list[RetrievedChunk] = []
        for index in sorted(fused, key=lambda i: -fused[i]):
            chunk = self._chunks[index]
            similarity = float(similarities[index])
            shared = tuple(sorted(query_identifiers & extract_identifiers(chunk.text)))
            if similarity < min_similarity and not shared:
                continue
            if chunk.text_hash in seen_hashes:
                continue
            seen_hashes.add(chunk.text_hash)
            results.append(RetrievedChunk(
                chunk=chunk,
                similarity=similarity,
                lexical_score=float(lexical_scores[index]),
                matched_identifiers=shared,
            ))
            if len(results) >= top_k:
                break
        return results


def empty_index() -> VectorIndex:
    return VectorIndex([], np.zeros((0, 0), dtype=np.float32))
