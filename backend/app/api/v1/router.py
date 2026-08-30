from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.operations import capture_router, detection_router, alerts_router, quantum_router
from app.api.v1.endpoints.misc import router as misc_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(capture_router)
router.include_router(detection_router)
router.include_router(alerts_router)
router.include_router(quantum_router)
router.include_router(misc_router)
