from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.constants import PermissionName
from app.database.session import get_db
from app.models import Alert, Detection, User
from app.schemas import AlertRead, PaginatedResponse
from app.security.dependencies import get_current_user, require_permission
from app.packet_capture import capture_service, list_interfaces
from app.packet_capture.exceptions import (
    CaptureAlreadyRunningError,
    CaptureNotRunningError,
    InvalidInterfaceError,
    PermissionDeniedError,
    InterfaceUnavailableError,
)
from app.detection.engine import detection_engine
from app.detection.pipeline import detection_pipeline
from app.database.session import AsyncSessionLocal

capture_router = APIRouter(prefix="/capture", tags=["Capture"])
detection_router = APIRouter(prefix="/detection", tags=["Detection"])
alerts_router = APIRouter(prefix="/alerts", tags=["Alerts"])
quantum_router = APIRouter(prefix="/quantum", tags=["Quantum"])


@capture_router.get("/interfaces")
async def interfaces(_: User = Depends(require_permission(PermissionName.CAPTURE_VIEW))) -> list[dict[str, str]]:
    try:
        return list_interfaces()
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except InterfaceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@capture_router.get("/status")
async def capture_status(_: User = Depends(require_permission(PermissionName.CAPTURE_VIEW))) -> dict:
    return capture_service.status().model_dump()


@capture_router.post("/start")
async def capture_start(interface: str, _: User = Depends(require_permission(PermissionName.CAPTURE_START))) -> dict:
    try:
        capture_service.start_capture(interface)
        return {"status": "started", "interface": interface}
    except (InvalidInterfaceError, InterfaceUnavailableError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except CaptureAlreadyRunningError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@capture_router.post("/stop")
async def capture_stop(_: User = Depends(require_permission(PermissionName.CAPTURE_STOP))) -> dict:
    try:
        capture_service.stop_capture()
        return {"status": "stopped"}
    except CaptureNotRunningError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@capture_router.get("/statistics")
async def capture_statistics(_: User = Depends(require_permission(PermissionName.CAPTURE_VIEW))) -> dict:
    status = capture_service.status()
    flows = capture_service.flow_tracker.get_active_flows()
    return {
        "available": status.available,
        "running": status.running,
        "interface": status.interface,
        "packets_captured": status.packets_captured,
        "active_flows": len(flows),
        "flow_details": [f.model_dump() for f in flows[:20]],
    }


@capture_router.get("/packets")
async def capture_packets(_: User = Depends(require_permission(PermissionName.CAPTURE_VIEW))) -> dict:
    status = capture_service.status()
    return {
        "available": status.available,
        "running": status.running,
        "packets_captured": status.packets_captured,
        "reason": status.reason,
    }


@detection_router.get("/status")
async def detection_status(_: User = Depends(get_current_user)) -> dict:
    return {
        "running": detection_pipeline.running,
        "capture_running": capture_service.running,
        "model_available": detection_engine.available,
        "detections_count": detection_pipeline.detection_count,
    }


@detection_router.post("/start")
async def detection_start(interface: str, user: User = Depends(require_permission(PermissionName.CAPTURE_START))) -> dict:
    if not detection_engine.available:
        raise HTTPException(status_code=503, detail="Detection models are not trained. Train the Autoencoder and XGBoost models first.")
    if not capture_service.running:
        try:
            capture_service.start_capture(interface)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    detection_pipeline.start(AsyncSessionLocal, str(user.id))
    return {"status": "detection_started", "interface": interface}


@detection_router.post("/stop")
async def detection_stop(_: User = Depends(require_permission(PermissionName.CAPTURE_STOP))) -> dict:
    detection_pipeline.stop()
    if capture_service.running:
        try:
            capture_service.stop_capture()
        except Exception:
            pass
    return {"status": "detection_stopped"}


@detection_router.get("/results")
async def detection_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    _: User = Depends(require_permission(PermissionName.DETECTION_VIEW)),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    count_q = select(func.count()).select_from(Detection)
    total = int((await session.execute(count_q)).scalar_one())
    rows = list((await session.execute(
        select(Detection).order_by(Detection.detected_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )).scalars().all())
    return PaginatedResponse(
        items=[
            {
                "id": str(r.id),
                "label": r.label,
                "confidence": r.confidence,
                "model_version": r.model_version,
                "detected_at": r.detected_at.isoformat(),
                "source_ip": r.source_ip,
                "destination_ip": r.destination_ip,
                "protocol": r.protocol,
                "source_port": r.source_port,
                "destination_port": r.destination_port,
                "severity": r.severity,
                "classification": r.classification,
                "anomaly_score": r.anomaly_score,
            }
            for r in rows
        ],
        page=page,
        page_size=page_size,
        total=total,
    )


@detection_router.get("/statistics")
async def detection_statistics(_: User = Depends(require_permission(PermissionName.DETECTION_VIEW)), session: AsyncSession = Depends(get_db)) -> dict:
    total = int((await session.execute(select(func.count()).select_from(Detection))).scalar_one())

    by_label_rows = (await session.execute(
        select(Detection.label, func.count()).group_by(Detection.label)
    )).all()
    by_label = {label: int(count) for label, count in by_label_rows}

    by_severity_rows = (await session.execute(
        select(Detection.severity, func.count()).group_by(Detection.severity)
    )).all()
    by_severity = {(severity or "unknown"): int(count) for severity, count in by_severity_rows}

    by_classification_rows = (await session.execute(
        select(Detection.classification, func.count()).group_by(Detection.classification)
    )).all()
    by_classification = {(cls or "unknown"): int(count) for cls, count in by_classification_rows}

    return {
        "total_detections": total,
        "by_label": by_label,
        "by_severity": by_severity,
        "by_classification": by_classification,
    }


@detection_router.get("/history")
async def detection_history(
    hours: int = Query(24, ge=1, le=168),
    _: User = Depends(require_permission(PermissionName.DETECTION_VIEW)),
    session: AsyncSession = Depends(get_db),
) -> dict:
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import case, literal_column

    now = datetime.now(timezone.utc)
    bucket_start = now - timedelta(hours=hours)
    bucket_interval = timedelta(minutes=max(1, hours * 60 // 24))

    rows = (await session.execute(
        select(
            func.date_trunc("hour", Detection.detected_at).label("hour"),
            func.count().label("count"),
            func.sum(case((Detection.severity == "critical", 1), else_=0)).label("critical"),
            func.sum(case((Detection.severity == "high", 1), else_=0)).label("high"),
            func.sum(case((Detection.severity == "medium", 1), else_=0)).label("medium"),
            func.sum(case((Detection.severity == "low", 1), else_=0)).label("low"),
        )
        .where(Detection.detected_at >= bucket_start)
        .group_by(literal_column("hour"))
        .order_by(literal_column("hour"))
    )).all()

    buckets = []
    for hour, count, critical, high, medium, low in rows:
        buckets.append({
            "timestamp": hour.isoformat() if hour else "",
            "total": int(count),
            "critical": int(critical or 0),
            "high": int(high or 0),
            "medium": int(medium or 0),
            "low": int(low or 0),
        })

    return {"hours": hours, "buckets": buckets}


@detection_router.get("/model/status")
async def model_status(_: User = Depends(get_current_user)) -> dict:
    model_dir = Path(settings.model_directory)
    ae_path = model_dir / "autoencoder.pt"
    xgb_path = model_dir / "xgboost.joblib"
    schema_path = model_dir / "feature_schema.json"

    scaler_path = model_dir / "scaler.joblib"
    label_encoder_path = model_dir / "label_encoder.joblib"

    model_available = ae_path.exists() and xgb_path.exists() and scaler_path.exists()
    feature_schema_available = schema_path.exists()

    model_version = None
    training_timestamp = None
    metrics = None

    if xgb_path.exists():
        try:
            import joblib
            data = joblib.load(xgb_path)
            config = data.get("config", {})
            model_version = config.get("trained_at", "unknown")
            training_timestamp = config.get("trained_at")
            metrics = data.get("metrics")
        except Exception:
            pass

    return {
        "model_available": model_available,
        "model_version": model_version,
        "training_timestamp": training_timestamp,
        "feature_schema_available": feature_schema_available,
        "metrics_available": metrics is not None,
        "metrics": metrics,
        "scaler_available": scaler_path.exists(),
        "label_encoder_available": label_encoder_path.exists(),
    }


@detection_router.get("/model/metrics")
async def model_metrics(_: User = Depends(get_current_user)) -> dict:
    model_dir = Path(settings.model_directory)
    xgb_path = model_dir / "xgboost.joblib"
    if not xgb_path.exists():
        return {"available": False, "reason": "Model not trained"}
    try:
        import joblib
        data = joblib.load(xgb_path)
        metrics = data.get("metrics")
        if metrics:
            return {"available": True, "metrics": metrics}
        return {"available": False, "reason": "No metrics found in model file"}
    except Exception as exc:
        return {"available": False, "reason": str(exc)}


@alerts_router.get("", response_model=PaginatedResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    _: User = Depends(require_permission(PermissionName.ALERTS_VIEW)),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    count_q = select(func.count()).select_from(Alert)
    total = int((await session.execute(count_q)).scalar_one())
    rows = list((await session.execute(
        select(Alert).order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )).scalars().all())
    return PaginatedResponse(
        items=[AlertRead.model_validate(row).model_dump() for row in rows],
        page=page,
        page_size=page_size,
        total=total,
    )


@alerts_router.get("/{alert_id}", response_model=AlertRead)
async def get_alert(alert_id: UUID, _: User = Depends(require_permission(PermissionName.ALERTS_VIEW)), session: AsyncSession = Depends(get_db)) -> Alert:
    alert = await session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@alerts_router.post("/{alert_id}/{action}", response_model=AlertRead)
async def update_alert(alert_id: UUID, action: str, _: User = Depends(require_permission(PermissionName.ALERTS_UPDATE)), session: AsyncSession = Depends(get_db)) -> Alert:
    if action not in {"acknowledge", "resolve", "reopen"}:
        raise HTTPException(status_code=404, detail="Unknown alert action")
    from app.services.alerts import AlertService
    try:
        return await AlertService.update_status(session, alert_id, {"acknowledge": "acknowledged", "resolve": "resolved", "reopen": "open"}[action])
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@quantum_router.get("/status")
async def quantum_status(_: User = Depends(get_current_user)) -> dict:
    from app.quantum.service import quantum_service
    return quantum_service.status()


@quantum_router.post("/keygen")
async def quantum_keygen(_: User = Depends(require_permission(PermissionName.QUANTUM_VIEW))) -> dict:
    from app.quantum.service import quantum_service
    result = quantum_service.keygen()
    return result.model_dump()


@quantum_router.post("/test")
async def quantum_test(_: User = Depends(require_permission(PermissionName.QUANTUM_VIEW))) -> dict:
    from app.quantum.service import quantum_service
    keygen = quantum_service.keygen()
    if not keygen.available:
        return {"available": False, "reason": keygen.reason}
    encaps = quantum_service.encapsulate(keygen.public_key)
    if not encaps.available:
        return {"available": False, "reason": encaps.reason}
    decaps = quantum_service.decapsulate(keygen.private_key_handle, encaps.ciphertext)
    if not decaps.available:
        return {"available": False, "reason": decaps.reason}
    return {
        "available": True,
        "keygen": "success",
        "encapsulation": "success",
        "decapsulation": "success",
        "shared_secret_verified": decaps.verified,
    }
