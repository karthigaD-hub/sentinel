import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import RAGChunk, RAGDocument
from app.rag import store
from app.rag.embeddings import embedding_service
from app.rag.service import normalized_hash

BACKEND_DIR = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not set; persistence tests need Postgres")


@pytest.fixture
async def db_session():
    test_engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(test_engine, expire_on_commit=False)
    async with maker() as session:
        yield session
    await test_engine.dispose()


STATUS_SCRIPT = """
import asyncio, json
from app.database.session import AsyncSessionLocal
from app.rag.service import rag_service

async def main():
    async with AsyncSessionLocal() as session:
        await rag_service.reload(session)
        status = await rag_service.status(session)
    print(json.dumps({"chunks_indexed": status["chunks_indexed"], "ingested_sources": status["ingested_sources"]}))

asyncio.run(main())
"""


def _fresh_process_status() -> dict:
    completed = subprocess.run(
        [sys.executable, "-c", STATUS_SCRIPT],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout.strip().splitlines()[-1])


async def _delete_source(source: str) -> None:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        await session.execute(delete(RAGDocument).where(RAGDocument.source == source))
        await session.commit()
    await engine.dispose()


@pytest.mark.asyncio
async def test_indexed_chunks_survive_process_restart(db_session):
    source = f"pytest-persist-{uuid.uuid4().hex[:8]}"
    texts = ["persistence probe alpha record", "persistence probe beta record"]
    vectors = np.eye(2, 4, dtype=np.float32)
    try:
        async with db_session as session:
            document = RAGDocument(source=source, external_id="probe", title="probe", content=" ".join(texts), metadata_json={}, content_hash="probe")
            session.add(document)
            await session.flush()
            rows = [
                RAGChunk(
                    document_id=document.id,
                    chunk_index=i,
                    source=source,
                    external_id="probe",
                    text=text,
                    text_hash=normalized_hash(text),
                    embedding=[float(v) for v in vectors[i]],
                    embedding_model=embedding_service.model_name,
                    metadata_json={},
                )
                for i, text in enumerate(texts)
            ]
            await store.replace_document_chunks(session, document.id, rows)
            await session.commit()

        status = _fresh_process_status()
        assert source in status["ingested_sources"]
        assert status["chunks_indexed"] >= 2
    finally:
        await _delete_source(source)


@pytest.mark.asyncio
@pytest.mark.skipif(not embedding_service.library_installed(), reason="sentence-transformers is not installed")
async def test_real_embedding_ingest_and_search_after_restart(db_session):
    from app.rag.schemas import RAGDocumentCreate
    from app.rag.service import rag_service

    source = f"pytest-real-{uuid.uuid4().hex[:8]}"
    try:
        async with db_session as session:
            result = await rag_service.ingest(session, RAGDocumentCreate(
                source=source,
                external_id="T1059",
                title="Command and scripting interpreter",
                content="T1059 Command and Scripting Interpreter: adversaries abuse PowerShell and shell interpreters to execute commands.",
                metadata={},
            ))
        assert result.status == "created"
        assert result.chunks_indexed >= 1

        status = _fresh_process_status()
        assert source in status["ingested_sources"]

        retrieval_engine = create_async_engine(os.environ["DATABASE_URL"])
        retrieval_maker = async_sessionmaker(retrieval_engine, expire_on_commit=False)
        async with retrieval_maker() as session:
            await rag_service.reload(session)
            retrieval = await rag_service.search("How do attackers abuse PowerShell?", top_k=3, min_similarity=0.0)
        await retrieval_engine.dispose()
        assert any(hit.chunk.source == source for hit in retrieval.hits)
    finally:
        await _delete_source(source)
