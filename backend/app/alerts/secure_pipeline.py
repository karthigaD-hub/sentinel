import json
from datetime import datetime, timezone
from app.alerts.service import AlertService
from app.quantum.service import quantum_service
from app.websocket.manager import manager


class SecureAlertPipeline:
    @staticmethod
    async def process_detection(detection_result: dict, alert_data: dict, shared_secret: bytes) -> dict:
        alert_bytes = json.dumps(alert_data).encode("utf-8")

        if quantum_service.available and shared_secret:
            secure_payload = quantum_service.encrypt_alert(alert_bytes, shared_secret)
            pipeline_result = {
                "alert_data": alert_data,
                "secure_payload": secure_payload.model_dump(),
                "encrypted": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            pipeline_result = {
                "alert_data": alert_data,
                "secure_payload": None,
                "encrypted": False,
                "reason": "Post-quantum Kyber library not available; alert stored unencrypted",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        await manager.send_to_user("broadcast", {
            "event": "alert_created",
            "data": {
                "detection": detection_result,
                "encrypted": pipeline_result["encrypted"],
                "timestamp": pipeline_result["timestamp"],
            },
        })

        return pipeline_result


secure_alert_pipeline = SecureAlertPipeline()
