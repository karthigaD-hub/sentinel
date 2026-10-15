import asyncio
import json
import logging
from datetime import datetime, timezone
from app.detection.engine.detection_engine import detection_engine, DetectionResult
from app.detection.features.flow_features import FlowFeatures
from app.detection.features.feature_extractor import extract_feature_vector
from app.packet_capture.capture_service import capture_service
from app.packet_capture.schemas import PacketMetadata

logger = logging.getLogger(__name__)

_FLOW_PACKET_THRESHOLD = 4
_EVALUATED_FLOWS: set[str] = set()


class DetectionPipeline:
    def __init__(self) -> None:
        self._flow_features = FlowFeatures()
        self._running = False
        self._db_session_factory = None
        self._loop = None
        self._detection_count = 0
        self._user_id: str | None = None

    @property
    def running(self) -> bool:
        return self._running

    @property
    def detection_count(self) -> int:
        return self._detection_count

    def start(self, db_session_factory, user_id: str | None = None) -> None:
        if self._running:
            return
        if not detection_engine.available:
            raise RuntimeError("Detection models are not trained. Train the Autoencoder and XGBoost models first.")
        self._db_session_factory = db_session_factory
        self._flow_features.reset()
        self._detection_count = 0
        _EVALUATED_FLOWS.clear()
        self._user_id = user_id
        capture_service.set_packet_callback(self._on_packet)
        self._running = True

    def stop(self) -> None:
        if not self._running:
            return
        capture_service.set_packet_callback(lambda _: None)
        self._running = False

    def _on_packet(self, meta: PacketMetadata) -> None:
        flow_key = self._flow_features.add_packet(meta)
        if not detection_engine.available:
            return

        if flow_key in _EVALUATED_FLOWS:
            return

        state = self._flow_features.get_flow_state(flow_key)
        if state is None:
            return
        total_packets = state.fwd_packets + state.bwd_packets
        if total_packets < _FLOW_PACKET_THRESHOLD:
            return

        feature_vector = extract_feature_vector(self._flow_features, flow_key)
        if not any(feature_vector):
            return

        try:
            result = detection_engine.detect(feature_vector)
        except Exception as exc:
            logger.error("Detection error: %s", exc)
            return

        _EVALUATED_FLOWS.add(flow_key)
        self._detection_count += 1

        if result.is_benign:
            logger.info("Benign detection for flow %s — no DB record, no alert", flow_key)
            return

        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()

        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._persist_detection(result, meta, flow_key),
                self._loop,
            )

    async def _persist_detection(self, result: DetectionResult, meta: PacketMetadata, flow_key: str) -> None:
        from app.models import Detection, Alert
        from app.alerts.secure_pipeline import secure_alert_pipeline

        if self._db_session_factory is None:
            return

        async with self._db_session_factory() as session:
            detection = Detection(
                label=result.label,
                confidence=result.confidence,
                model_version=detection_engine.anomaly_detector.model.config.get("trained_at", "unknown") if detection_engine.anomaly_detector.model else "unknown",
                detected_at=datetime.now(timezone.utc),
            )
            session.add(detection)
            await session.flush()

            alert_title = f"{result.classification}: {result.label} from {meta.source_ip}"
            alert = Alert(
                detection_id=detection.id,
                title=alert_title,
                severity=result.severity,
                status="open",
                description=json.dumps(result.to_dict()),
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)

            try:
                await secure_alert_pipeline.process_detection(
                    result.to_dict(),
                    {"alert_id": str(alert.id), "title": alert_title, "severity": result.severity},
                    self._user_id,
                )
            except Exception as exc:
                logger.error("Secure pipeline error: %s", exc)


detection_pipeline = DetectionPipeline()
