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
from app.rag.service import rag_service
from app.rag.schemas import RAGDocumentCreate
from app.llm.assistant_service import assistant_service

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
    from sqlalchemy import func
    count = int((await session.execute(select(func.count()).select_from(RAGDocument))).scalar_one())
    return {"available": rag_service.available, "documents": count, "rag_status": rag_service.get_status()}


@router.get("/threat-intel/{reference_id}")
async def threat_intel_item(reference_id: UUID, session: AsyncSession = Depends(get_db), _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW))) -> dict:
    document = await session.get(RAGDocument, reference_id)
    if not document:
        raise HTTPException(status_code=404, detail="Threat intelligence reference not found")
    return {"id": document.id, "title": document.title, "content": document.content, "source": document.source}


@router.post("/rag/ingest")
async def rag_ingest(data: RAGIngestRequest, _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW)), session: AsyncSession = Depends(get_db)) -> dict:
    doc = RAGDocumentCreate(
        source=data.source,
        external_id=data.external_id,
        title=data.title,
        content=data.content,
        metadata=data.metadata,
    )
    chunks_created = rag_service.ingest_document(doc)

    db_doc = RAGDocument(
        source=data.source,
        external_id=data.external_id,
        title=data.title,
        content=data.content,
        metadata_json=data.metadata,
    )
    session.add(db_doc)
    await session.commit()

    return {"ingested": True, "chunks_created": chunks_created, "document_id": str(db_doc.id)}


@router.get("/rag/status")
async def rag_status(_: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW))) -> dict:
    return rag_service.get_status()


@router.post("/rag/search")
async def rag_search(data: RAGQueryRequest, _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW))) -> dict:
    if not rag_service.available:
        return {"available": False, "reason": "RAG index is not configured. Ingest documents first.", "results": []}
    results = rag_service.search(data.query, top_k=data.top_k)
    return {
        "available": True,
        "query": data.query,
        "results": [r.model_dump() for r in results],
    }


@router.post("/rag/query")
async def rag_query(data: RAGQueryRequest, _: User = Depends(require_permission(PermissionName.THREATINTEL_VIEW))) -> dict:
    if not rag_service.available:
        return {"available": False, "reason": "RAG index is not configured. Ingest documents first.", "answer": "Insufficient retrieved evidence."}
    results = rag_service.search(data.query, top_k=data.top_k)
    if not results:
        return {"available": True, "answer": "Insufficient retrieved evidence.", "citations": []}
    from app.llm.service import llm_service
    if not llm_service.available:
        return {"available": False, "reason": "LLM provider is not configured", "answer": "Insufficient retrieved evidence.", "citations": []}
    context = "\n\n".join(f"[{i+1}] Source: {r.source}\n{r.chunk_text}" for i, r in enumerate(results))
    answer = llm_service.answer(data.query, context)
    citations = [{"source": r.source, "external_id": r.external_id, "score": r.score} for r in results]
    return {"available": True, "answer": answer, "citations": citations}


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

    result = assistant_service.chat(data.message)

    session.add(AssistantMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=result["answer"],
        citations=result.get("citations", []),
    ))
    await session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        answer=result["answer"],
        citations=result.get("citations", []),
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
