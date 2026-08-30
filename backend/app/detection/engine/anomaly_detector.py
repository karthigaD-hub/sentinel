import numpy as np
from app.detection.training.autoencoder import AutoencoderModel
from app.detection.features.feature_schema import FEATURE_SCHEMA


class AnomalyDetector:
    def __init__(self, model_path: str | None = None) -> None:
        self.model: AutoencoderModel | None = None
        self.model_path = model_path
        if model_path:
            self.load(model_path)

    def load(self, path: str) -> None:
        self.model = AutoencoderModel.load(path)
        self.model_path = path

    def detect(self, X: np.ndarray) -> dict:
        if self.model is None:
            raise RuntimeError("Autoencoder model not loaded")
        return self.model.predict(X)

    @property
    def available(self) -> bool:
        return self.model is not None and self.model.threshold is not None
