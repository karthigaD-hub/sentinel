from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class RAGDocumentCreate(BaseModel):
    source: str
    external_id: str
    title: str
    content: str
    metadata: dict = {}


class RAGChunk(BaseModel):
    document_id: UUID
    chunk_index: int
    text: str
    source: str
    external_id: str
    metadata: dict = {}


class RAGSearchResult(BaseModel):
    chunk_text: str
    source: str
    external_id: str
    score: float
    metadata: dict = {}


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5


class RAGSearchResponse(BaseModel):
    results: list[RAGSearchResult]
    query: str
