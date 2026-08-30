from app.models import Detection

class ExplainabilityService:
    @staticmethod
    def available(detection: Detection) -> bool:
        return detection.explanation is not None
