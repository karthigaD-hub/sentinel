from datetime import datetime, timezone
from pathlib import Path

from app.rag.schemas import RAGDocumentCreate, RAGSearchResult
from app.rag.chunker import chunk_document
from app.rag.embeddings import embedding_service
from app.rag.retriever import retriever


class RAGService:
    def __init__(self) -> None:
        self.ingested_sources: list[str] = []
        self.failed_sources: list[dict] = []

    @property
    def available(self) -> bool:
        return embedding_service.available and len(retriever.chunks) > 0

    def ingest_document(self, doc: RAGDocumentCreate) -> int:
        chunks = chunk_document(
            document_id=None,
            source=doc.source,
            external_id=doc.external_id,
            content=doc.content,
            metadata=doc.metadata,
        )
        retriever.add_chunks(chunks)
        if doc.source not in self.ingested_sources:
            self.ingested_sources.append(doc.source)
        return len(chunks)

    def ingest_from_file(self, file_path: str, source: str, external_id: str, title: str, metadata: dict | None = None) -> int:
        path = Path(file_path)
        if not path.exists():
            self.failed_sources.append({"source": source, "external_id": external_id, "reason": f"File not found: {file_path}", "timestamp": datetime.now(timezone.utc).isoformat()})
            return 0
        content = path.read_text(encoding="utf-8", errors="replace")
        doc = RAGDocumentCreate(source=source, external_id=external_id, title=title, content=content, metadata=metadata or {})
        return self.ingest_document(doc)

    def search(self, query: str, top_k: int = 5) -> list[RAGSearchResult]:
        if not self.available:
            return []
        return retriever.search(query, top_k)

    def get_status(self) -> dict:
        return {
            "available": self.available,
            "embedding_available": embedding_service.available,
            "chunks_indexed": len(retriever.chunks),
            "ingested_sources": self.ingested_sources,
            "failed_sources": self.failed_sources,
        }


rag_service = RAGService()
