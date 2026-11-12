from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.v1.router import router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.database.session import AsyncSessionLocal
from app.database.health import database_health
from app.middleware.security import RequestSecurityMiddleware
from app.websocket.manager import manager

@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    async with AsyncSessionLocal() as session:
        await rag_service.reload(session)
    yield

app = FastAPI(title="Q-Sentinel API", version="1.0.0", lifespan=lifespan)
app.add_middleware(RequestSecurityMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["*"])
app.include_router(router)

@app.get("/health")
async def health() -> dict[str, object]:
    async with AsyncSessionLocal() as session:
        db_ok = await database_health(session)
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}

@app.get("/api/v1/system/status")
async def system_status() -> dict[str, object]:
    return {"api": True, "database_configured": bool(settings.database_url), "redis_configured": bool(settings.redis_url), "model_directory": settings.model_directory}

@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    from app.core.security_config import decode_access_token
    user_id = decode_access_token(token)
    if not user_id:
        await websocket.close(code=1008)
        return
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
