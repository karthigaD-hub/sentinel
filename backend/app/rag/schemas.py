from uuid import UUID
from pydantic import BaseModel


class RAGDocumentCreate(BaseModel):
    source: str
    external_id: str
    title: str
    content: str
    metadata: dict = {}


class RAGSearchResult(BaseModel):
    document_id: UUID
    chunk_text: str
    source: str
    external_id: str
    score: float
    lexical_score: float
    matched_identifiers: list[str]
    metadata: dict = {}
