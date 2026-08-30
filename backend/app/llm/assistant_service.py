from app.llm.service import llm_service
from app.rag.service import rag_service


class AssistantService:
    @staticmethod
    def chat(message: str) -> dict:
        if not llm_service.available:
            return {
                "answer": "LLM provider is not configured. Set LLM_PROVIDER, LLM_MODEL, and LLM_API_KEY.",
                "citations": [],
                "available": False,
            }

        rag_results = rag_service.search(message, top_k=5)
        if not rag_results:
            return {
                "answer": "Insufficient retrieved evidence.",
                "citations": [],
                "available": True,
            }

        context_parts: list[str] = []
        citations: list[dict] = []
        for i, result in enumerate(rag_results):
            context_parts.append(f"[{i + 1}] Source: {result.source}, ID: {result.external_id}\n{result.chunk_text}")
            citations.append({"source": result.source, "external_id": result.external_id, "score": result.score})

        context = "\n\n".join(context_parts)
        answer = llm_service.answer(message, context)
        return {"answer": answer, "citations": citations, "available": True}


assistant_service = AssistantService()
