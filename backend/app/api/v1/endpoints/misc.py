from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import PermissionName
from app.database.session import get_db
from app.models import Detection, RAGDocument, AssistantConversation, AssistantMessage, User
from app.schemas import ChatRequest, ChatResponse, PaginatedResponse, RAGQueryRequest
from app.security.dependencies import get_current_user, require_permission
from app.core.config import settings
from app.rag.service import RAGIngestError, rag_service
from app.rag.schemas import RAGDocumentCreate
from app.llm.assistant_service import assistant_service
from app.llm.service import llm_service

router = APIRouter(tags=["Platform"])


class RAGIngestRequest(BaseModel):
    source: str = Field(min_length=1, max_length=200)
    external_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    metadata: dict = {}


@router.get("/detection/{detection_id}/explanation")
async def explanation(detection_id: UUID, _: User = Depends(require_permission(PermissionName.DETECTION_VIEW)), session: AsyncSession = Depends(get_db)) -> dict:
    detection = await session.get(Detection, detection_id)
    if not detection or not detection.explanation:
        raise HTTPException(status_code=404, detail="Explanation not found")
    return {"method": detection.explanation.method, "values": detection.explanation.values}


@router.get("/threat-intel")
async def threat_intel(_: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW)), session: AsyncSession = Depends(get_db)) -> dict:
    status = await rag_service.status(session)
    return {"available": rag_service.available, "documents": status["documents"], "rag_status": status}


@router.get("/threat-intel/{reference_id}")
async def threat_intel_item(reference_id: UUID, session: AsyncSession = Depends(get_db), _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW))) -> dict:
    document = await session.get(RAGDocument, reference_id)
    if not document:
        raise HTTPException(status_code=404, detail="Threat intelligence reference not found")
    return {"id": document.id, "title": document.title, "content": document.content, "source": document.source}


@router.post("/rag/ingest")
async def rag_ingest(data: RAGIngestRequest, _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW)), session: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await rag_service.ingest(session, RAGDocumentCreate(
            source=data.source,
            external_id=data.external_id,
            title=data.title,
            content=data.content,
            metadata=data.metadata,
        ))
    except RAGIngestError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"ingested": True, "status": result.status, "chunks_created": result.chunks_indexed, "document_id": result.document_id}


@router.get("/rag/status")
async def rag_status(_: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW)), session: AsyncSession = Depends(get_db)) -> dict:
    status = await rag_service.status(session)
    status["llm"] = await llm_service.health()
    return status


@router.post("/rag/search")
async def rag_search(data: RAGQueryRequest, _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW))) -> dict:
    if not rag_service.available:
        return {"available": False, "reason": "No threat-intelligence documents are indexed yet.", "results": []}
    retrieval = await rag_service.search(data.query, top_k=data.top_k)
    return {
        "available": True,
        "query": data.query,
        "retrieval_ms": retrieval.duration_ms,
        "results": [
            {
                "document_id": hit.chunk.document_id,
                "chunk_text": hit.chunk.text,
                "source": hit.chunk.source,
                "external_id": hit.chunk.external_id,
                "score": round(hit.similarity, 4),
                "lexical_score": round(hit.lexical_score, 4),
                "matched_identifiers": list(hit.matched_identifiers),
                "metadata": hit.chunk.metadata,
            }
            for hit in retrieval.hits
        ],
    }


@router.post("/rag/query")
async def rag_query(data: RAGQueryRequest, _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW))) -> dict:
    result = await assistant_service.answer(data.query, data.top_k)
    return {
        "status": result.status,
        "answer": result.answer,
        "citations": result.citations,
        "retrieval_ms": result.retrieval_ms,
        "generation_ms": result.generation_ms,
        "model": result.model,
    }


@router.post("/assistant/chat", response_model=ChatResponse)
async def assistant_chat(data: ChatRequest, user: User = Depends(require_permission(PermissionName.ASSISTANT_USE)), session: AsyncSession = Depends(get_db)) -> ChatResponse:
    conversation = await session.get(AssistantConversation, data.conversation_id) if data.conversation_id else None
    if conversation and conversation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not conversation:
        conversation = AssistantConversation(user_id=user.id, title=data.message[:50])
        session.add(conversation)
        await session.flush()

    session.add(AssistantMessage(conversation_id=conversation.id, role="user", content=data.message))

    result = await assistant_service.answer(data.message, settings.rag_default_top_k)

    session.add(AssistantMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=result.answer,
        citations=result.citations,
    ))
    await session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        answer=result.answer,
        citations=result.citations,
        status=result.status,
    )


@router.get("/assistant/history")
async def assistant_history(user: User = Depends(require_permission(PermissionName.ASSISTANT_USE)), session: AsyncSession = Depends(get_db)) -> list[dict]:
    conversations = list((await session.execute(
        select(AssistantConversation)
        .where(AssistantConversation.user_id == user.id)
        .order_by(AssistantConversation.created_at.desc())
    )).scalars().all())
    return [{"id": str(item.id), "title": item.title, "created_at": item.created_at} for item in conversations]


@router.get("/reports")
async def reports(_: User = Depends(require_permission(PermissionName.REPORTS_VIEW))) -> PaginatedResponse:
    return PaginatedResponse(items=[], page=1, page_size=50, total=0)


@router.post("/reports/generate")
async def generate_report(_: User = Depends(require_permission(PermissionName.REPORTS_VIEW))) -> None:
    raise HTTPException(status_code=503, detail="Report generation worker is not configured")
