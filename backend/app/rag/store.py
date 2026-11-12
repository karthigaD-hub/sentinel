from uuid import UUID

import numpy as np
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RAGChunk, RAGDocument
from app.rag.retriever import IndexedChunk


async def find_document(session: AsyncSession, source: str, external_id: str) -> RAGDocument | None:
    result = await session.execute(
        select(RAGDocument).where(RAGDocument.source == source, RAGDocument.external_id == external_id).limit(1)
    )
    return result.scalar_one_or_none()


async def count_chunks_for_document(session: AsyncSession, document_id: UUID) -> int:
    result = await session.execute(select(func.count()).select_from(RAGChunk).where(RAGChunk.document_id == document_id))
    return int(result.scalar_one())


async def replace_document_chunks(session: AsyncSession, document_id: UUID, rows: list[RAGChunk]) -> None:
    await session.execute(delete(RAGChunk).where(RAGChunk.document_id == document_id))
    session.add_all(rows)


async def load_index_rows(session: AsyncSession, embedding_model: str) -> tuple[list[IndexedChunk], np.ndarray]:
    result = await session.execute(
        select(RAGChunk.id, RAGChunk.document_id, RAGChunk.source, RAGChunk.external_id, RAGChunk.text, RAGChunk.text_hash, RAGChunk.metadata_json, RAGChunk.embedding)
        .where(RAGChunk.embedding_model == embedding_model)
        .order_by(RAGChunk.source, RAGChunk.external_id, RAGChunk.chunk_index)
    )
    rows = result.all()
    chunks = [
        IndexedChunk(
            chunk_id=str(row.id),
            document_id=str(row.document_id),
            source=row.source,
            external_id=row.external_id,
            text=row.text,
            text_hash=row.text_hash,
            metadata=row.metadata_json or {},
        )
        for row in rows
    ]
    vectors = np.array([row.embedding for row in rows], dtype=np.float32) if rows else np.zeros((0, 0), dtype=np.float32)
    return chunks, vectors


async def index_summary(session: AsyncSession, embedding_model: str) -> dict:
    documents = int((await session.execute(select(func.count()).select_from(RAGDocument))).scalar_one())
    chunks_total = int((await session.execute(select(func.count()).select_from(RAGChunk))).scalar_one())
    chunks_current = int((await session.execute(
        select(func.count()).select_from(RAGChunk).where(RAGChunk.embedding_model == embedding_model)
    )).scalar_one())
    last_ingested = (await session.execute(select(func.max(RAGDocument.updated_at)))).scalar_one()
    sources = [row[0] for row in (await session.execute(select(RAGDocument.source).distinct().order_by(RAGDocument.source))).all()]
    return {
        "documents": documents,
        "chunks_stored": chunks_total,
        "chunks_with_current_embedding_model": chunks_current,
        "last_ingested_at": last_ingested.isoformat() if last_ingested else None,
        "ingested_sources": sources,
    }
