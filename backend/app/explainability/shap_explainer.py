import numpy as np
from pathlib import Path
from app.core.config import settings


class ShapExplainer:
    def __init__(self, model_path: str | None = None) -> None:
        self.model = None
        self.explainer = None
        self.feature_names: list[str] = []
        self._loaded = False
        if model_path:
            self.load(model_path)

    def load(self, model_path: str) -> None:
        import joblib
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"XGBoost model not found: {model_path}")
        data = joblib.load(path)
        self.model = data["model"]
        self.feature_names = data.get("feature_names") or []
        self._loaded = True

    @property
    def available(self) -> bool:
        if not self._loaded:
            model_path = Path(settings.model_directory) / "xgboost.joblib"
            if model_path.exists():
                try:
                    self.load(str(model_path))
                except Exception:
                    return False
        return self.model is not None

    def explain(self, X: np.ndarray) -> dict:
        if not self.available:
            return {
                "available": False,
                "reason": "Model not trained",
            }

        import shap
        if self.explainer is None:
            self.explainer = shap.TreeExplainer(self.model)

        shap_values = self.explainer.shap_values(X)

        if isinstance(shap_values, list):
            shap_values_arr = shap_values[0]
        else:
            shap_values_arr = shap_values

        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, np.ndarray)):
            base_value = float(np.array(base_value).ravel()[0])
        else:
            base_value = float(base_value)

        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        max_prob = float(np.max(probabilities))

        sample_shap = shap_values_arr[0] if shap_values_arr.ndim > 1 else shap_values_arr
        feature_contributions = list(zip(self.feature_names, sample_shap.tolist())) if self.feature_names else []
        sorted_features = sorted(feature_contributions, key=lambda x: abs(x[1]), reverse=True)
        top_features = sorted_features[:10]

        return {
            "available": True,
            "prediction": int(prediction),
            "confidence": max_prob,
            "base_value": base_value,
            "features": self.feature_names,
            "shap_values": sample_shap.tolist(),
            "top_features": [{"name": name, "shap_value": value} for name, value in top_features],
        }


shap_explainer = ShapExplainer()
