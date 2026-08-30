import numpy as np
from app.rag.schemas import RAGChunk, RAGSearchResult
from app.rag.embeddings import embedding_service


class Retriever:
    def __init__(self) -> None:
        self.chunks: list[RAGChunk] = []
        self.embeddings: np.ndarray | None = None

    def add_chunks(self, chunks: list[RAGChunk]) -> None:
        if not chunks:
            return
        texts = [c.text for c in chunks]
        new_embeddings = embedding_service.embed(texts)
        self.chunks.extend(chunks)
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

    def search(self, query: str, top_k: int = 5) -> list[RAGSearchResult]:
        if not self.chunks or self.embeddings is None:
            return []
        query_embedding = embedding_service.embed_query(query)
        similarities = self._cosine_similarity(query_embedding, self.embeddings)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results: list[RAGSearchResult] = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append(RAGSearchResult(
                chunk_text=chunk.text,
                source=chunk.source,
                external_id=chunk.external_id,
                score=float(similarities[idx]),
                metadata=chunk.metadata,
            ))
        return results

    @staticmethod
    def _cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
        return np.dot(matrix_norm, query_norm)


retriever = Retriever()
