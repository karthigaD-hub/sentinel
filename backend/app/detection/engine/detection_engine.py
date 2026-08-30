from pathlib import Path
import numpy as np

from app.core.config import settings
from app.detection.engine.anomaly_detector import AnomalyDetector
from app.detection.engine.attack_classifier import AttackClassifier
from app.detection.engine.severity_engine import SeverityEngine


class DetectionResult:
    def __init__(self, label: str, confidence: float, is_anomaly: bool, anomaly_score: float, threshold: float, severity: str, classification: str) -> None:
        self.label = label
        self.confidence = confidence
        self.is_anomaly = is_anomaly
        self.anomaly_score = anomaly_score
        self.threshold = threshold
        self.severity = severity
        self.classification = classification

    @property
    def is_benign(self) -> bool:
        return self.classification == "BENIGN"

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "confidence": self.confidence,
            "is_anomaly": self.is_anomaly,
            "anomaly_score": self.anomaly_score,
            "threshold": self.threshold,
            "severity": self.severity,
            "classification": self.classification,
        }


class DetectionEngine:
    def __init__(self, model_directory: str | None = None) -> None:
        self.model_directory = Path(model_directory or settings.model_directory)
        self.anomaly_detector = AnomalyDetector()
        self.attack_classifier = AttackClassifier()
        self.scaler = None
        self.label_encoder = None
        self._loaded = False

    def load_models(self) -> None:
        ae_path = self.model_directory / "autoencoder.pt"
        xgb_path = self.model_directory / "xgboost.joblib"
        scaler_path = self.model_directory / "scaler.joblib"
        label_encoder_path = self.model_directory / "label_encoder.joblib"

        if ae_path.exists():
            self.anomaly_detector.load(str(ae_path))
        if xgb_path.exists():
            self.attack_classifier.load(str(xgb_path))
        if scaler_path.exists():
            import joblib
            self.scaler = joblib.load(scaler_path)
        if label_encoder_path.exists():
            import joblib
            self.label_encoder = joblib.load(label_encoder_path)
        self._loaded = True

    @property
    def available(self) -> bool:
        if not self._loaded:
            self.load_models()
        return self.anomaly_detector.available and self.attack_classifier.available and self.scaler is not None

    def detect(self, feature_vector: list[float]) -> DetectionResult:
        if not self.available:
            raise RuntimeError("Detection models are not trained. Train the Autoencoder and XGBoost models first.")

        X_raw = np.array([feature_vector], dtype=np.float32)
        X = self.scaler.transform(X_raw)

        anomaly_result = self.anomaly_detector.detect(X)
        anomaly_score = float(anomaly_result["anomaly_score"][0])
        threshold = float(anomaly_result["threshold"])
        is_anomaly = bool(anomaly_result["is_anomaly"][0])

        classification_result = self.attack_classifier.classify(X)
        labels = classification_result["labels"]
        confidences = classification_result["confidences"]
        label_encoded = int(labels[0])
        confidence = float(confidences[0])

        if self.label_encoder is not None:
            label = str(self.label_encoder.inverse_transform([label_encoded])[0])
        else:
            label = str(label_encoded)

        severity = SeverityEngine.evaluate(label, confidence, is_anomaly, anomaly_score, threshold)

        if not is_anomaly and label == "benign":
            classification = "BENIGN"
        elif is_anomaly and label != "benign":
            classification = "KNOWN_ATTACK"
        elif is_anomaly and label == "benign":
            classification = "POTENTIAL_UNKNOWN_ANOMALY"
        else:
            classification = "KNOWN_ATTACK"

        return DetectionResult(
            label=label,
            confidence=confidence,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            threshold=threshold,
            severity=severity,
            classification=classification,
        )


detection_engine = DetectionEngine()
