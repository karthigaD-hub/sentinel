from app.rag.schemas import RAGChunk


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    if not text or not text.strip():
        return []
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def chunk_document(document_id, source: str, external_id: str, content: str, metadata: dict | None = None, chunk_size: int = 512, overlap: int = 50) -> list[RAGChunk]:
    text_chunks = chunk_text(content, chunk_size, overlap)
    return [
        RAGChunk(
            document_id=document_id,
            chunk_index=i,
            text=chunk,
            source=source,
            external_id=external_id,
            metadata=metadata or {},
        )
        for i, chunk in enumerate(text_chunks)
    ]
