import numpy as np
from app.detection.training.xgboost_model import XGBoostModel


class AttackClassifier:
    def __init__(self, model_path: str | None = None) -> None:
        self.model: XGBoostModel | None = None
        self.model_path = model_path
        if model_path:
            self.load(model_path)

    def load(self, path: str) -> None:
        self.model = XGBoostModel.load(path)
        self.model_path = path

    def classify(self, X: np.ndarray) -> dict:
        if self.model is None:
            raise RuntimeError("XGBoost model not loaded")
        result = self.model.predict(X)
        labels = result["labels"]
        probabilities = result["probabilities"]
        max_probs = np.max(probabilities, axis=1) if probabilities is not None else np.ones(len(labels))
        return {"labels": labels, "confidences": max_probs, "probabilities": probabilities}

    @property
    def available(self) -> bool:
        return self.model is not None
