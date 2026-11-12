import hashlib
import logging
import time
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import RAGChunk, RAGDocument
from app.rag import store
from app.rag.chunker import chunk_text
from app.rag.embeddings import embedding_service
from app.rag.retriever import RetrievedChunk, VectorIndex, empty_index
from app.rag.schemas import RAGDocumentCreate

logger = logging.getLogger(__name__)


class RAGIngestError(ValueError):
    pass


@dataclass(frozen=True)
class IngestResult:
    status: str
    document_id: str
    chunks_indexed: int


@dataclass(frozen=True)
class RetrievalResult:
    hits: list[RetrievedChunk]
    duration_ms: float


def normalized_hash(text: str) -> str:
    return hashlib.sha256(" ".join(text.lower().split()).encode("utf-8")).hexdigest()


class RAGService:
    def __init__(self) -> None:
        self._index: VectorIndex = empty_index()
        self._last_retrieval_ms: float | None = None

    @property
    def available(self) -> bool:
        return self._index.size > 0

    async def reload(self, session: AsyncSession) -> int:
        chunks, vectors = await store.load_index_rows(session, embedding_service.model_name)
        self._index = VectorIndex(chunks, vectors) if chunks else empty_index()
        logger.info("rag index loaded chunks=%d embedding_model=%s", len(chunks), embedding_service.model_name)
        return len(chunks)

    async def ingest(self, session: AsyncSession, doc: RAGDocumentCreate) -> IngestResult:
        content = doc.content.strip()
        if not content:
            raise RAGIngestError("Document content is empty")
        if len(content) > settings.rag_max_document_chars:
            raise RAGIngestError(f"Document exceeds the {settings.rag_max_document_chars} character limit")

        content_hash = normalized_hash(f"{doc.title}\n{content}")
        existing = await store.find_document(session, doc.source, doc.external_id)
        if existing and existing.content_hash == content_hash:
            chunk_count = await store.count_chunks_for_document(session, existing.id)
            return IngestResult("unchanged", str(existing.id), chunk_count)

        texts = self._unique_chunks(chunk_text(content, settings.rag_chunk_words, settings.rag_chunk_overlap_words))
        if not texts:
            raise RAGIngestError("Document produced no indexable text")
        vectors = await embedding_service.embed(texts)

        if existing:
            document = existing
            document.title = doc.title
            document.content = doc.content
            document.metadata_json = doc.metadata
            document.content_hash = content_hash
            status = "updated"
        else:
            document = RAGDocument(
                source=doc.source,
                external_id=doc.external_id,
                title=doc.title,
                content=doc.content,
                metadata_json=doc.metadata,
                content_hash=content_hash,
            )
            session.add(document)
            await session.flush()
            status = "created"

        rows = [
            RAGChunk(
                document_id=document.id,
                chunk_index=index,
                source=doc.source,
                external_id=doc.external_id,
                text=text,
                text_hash=normalized_hash(text),
                embedding=[float(value) for value in vector],
                embedding_model=embedding_service.model_name,
                metadata_json=doc.metadata,
            )
            for index, (text, vector) in enumerate(zip(texts, vectors, strict=True))
        ]
        await store.replace_document_chunks(session, document.id, rows)
        await session.commit()
        await self.reload(session)
        return IngestResult(status, str(document.id), len(rows))

    async def search(self, query: str, top_k: int, min_similarity: float | None = None) -> RetrievalResult:
        threshold = settings.rag_min_similarity if min_similarity is None else min_similarity
        started = time.perf_counter()
        if self._index.size == 0:
            return RetrievalResult([], 0.0)
        query_vector = (await embedding_service.embed([query]))[0]
        hits = self._index.search(query_vector, query, top_k, threshold)
        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        self._last_retrieval_ms = duration_ms
        logger.info("rag retrieval top_k=%d returned=%d duration_ms=%.1f", top_k, len(hits), duration_ms)
        return RetrievalResult(hits, duration_ms)

    async def status(self, session: AsyncSession) -> dict:
        summary = await store.index_summary(session, embedding_service.model_name)
        return {
            "available": self.available,
            "embedding_available": embedding_service.library_installed(),
            "embedding_loaded": embedding_service.loaded,
            "embedding_model": embedding_service.model_name,
            "chunks_indexed": self._index.size,
            "min_similarity": settings.rag_min_similarity,
            "last_retrieval_ms": self._last_retrieval_ms,
            **summary,
        }

    @staticmethod
    def _unique_chunks(texts: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []
        for text in texts:
            key = normalized_hash(text)
            if key not in seen:
                seen.add(key)
                unique.append(text)
        return unique


rag_service = RAGService()
