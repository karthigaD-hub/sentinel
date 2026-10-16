import json
import logging
from datetime import datetime, timezone
from app.quantum.service import quantum_service
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


class SecureAlertPipeline:
    @staticmethod
    async def process_detection(detection_result: dict, alert_data: dict, user_id: str | None) -> dict:
        alert_bytes = json.dumps(alert_data).encode("utf-8")
        timestamp = datetime.now(timezone.utc).isoformat()

        encrypted = False
        secure_payload = None
        reason = None

        if quantum_service.available:
            try:
                keygen = quantum_service.keygen()
                if keygen.available:
                    encaps = quantum_service.encapsulate(keygen.public_key)
                    if encaps.available:
                        shared_secret_handle = encaps.shared_secret_handle
                        shared_secret = quantum_service.kyber.get_shared_secret(shared_secret_handle)
                        if shared_secret:
                            secure_payload = quantum_service.encrypt_alert(alert_bytes, shared_secret)
                            encrypted = True
                            quantum_service.kyber.clear_keys()
                        else:
                            reason = "Failed to retrieve shared secret after encapsulation"
                    else:
                        reason = encaps.reason or "Kyber encapsulation failed"
                else:
                    reason = keygen.reason or "Kyber keygen failed"
            except Exception as exc:
                reason = f"PQC encryption error: {exc}"
                logger.error("PQC encryption error: %s", exc)
        else:
            reason = "Post-quantum Kyber library not installed. Alert stored unencrypted."

        pipeline_result = {
            "alert_data": alert_data,
            "secure_payload": secure_payload.model_dump() if secure_payload else None,
            "encrypted": encrypted,
            "reason": reason if not encrypted else None,
            "timestamp": timestamp,
        }

        target_user = user_id or "broadcast"
        await manager.send_to_user(target_user, {
            "event": "alert_created",
            "data": {
                "detection": detection_result,
                "encrypted": encrypted,
                "timestamp": timestamp,
            },
        })

        if not encrypted:
            logger.warning("Alert %s not encrypted: %s", alert_data.get("alert_id"), reason)

        return pipeline_result


secure_alert_pipeline = SecureAlertPipeline()
