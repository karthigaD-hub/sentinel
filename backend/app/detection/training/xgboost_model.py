from pathlib import Path
from datetime import datetime, timezone

import numpy as np


class XGBoostModel:
    def __init__(self, params: dict | None = None) -> None:
        self.model = None
        self.label_encoder = None
        self.feature_names: list[str] | None = None
        self.metrics: dict = {}
        self.config: dict = {}
        self.params = params or {
            "objective": "multi:softprob",
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
        }

    def train(self, X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray | None = None, y_val: np.ndarray | None = None, feature_names: list[str] | None = None) -> dict:
        import xgboost as xgb
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

        self.feature_names = feature_names
        num_classes = len(np.unique(y_train))

        params = dict(self.params)
        if num_classes <= 2:
            params["objective"] = "binary:logistic"
        else:
            params["objective"] = "multi:softprob"
            params["num_class"] = num_classes

        self.model = xgb.XGBClassifier(**params)
        eval_set = [(X_val, y_val)] if X_val is not None and y_val is not None else None
        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)

        y_pred = self.model.predict(X_train)
        y_pred_val = self.model.predict(X_val) if X_val is not None else None
        y_true_val = y_val if y_val is not None else y_train
        y_pred_for_metrics = y_pred_val if y_pred_val is not None else y_pred

        average = "weighted" if num_classes > 2 else "binary"
        self.metrics = {
            "accuracy": float(accuracy_score(y_true_val, y_pred_for_metrics)),
            "precision": float(precision_score(y_true_val, y_pred_for_metrics, average=average, zero_division=0)),
            "recall": float(recall_score(y_true_val, y_pred_for_metrics, average=average, zero_division=0)),
            "f1": float(f1_score(y_true_val, y_pred_for_metrics, average=average, zero_division=0)),
            "confusion_matrix": confusion_matrix(y_true_val, y_pred_for_metrics).tolist(),
            "num_classes": num_classes,
            "train_samples": len(X_train),
            "val_samples": len(X_val) if X_val is not None else 0,
        }

        if num_classes <= 2 and X_val is not None:
            from sklearn.metrics import roc_auc_score
            y_proba = self.model.predict_proba(X_val)[:, 1]
            self.metrics["roc_auc"] = float(roc_auc_score(y_val, y_proba))

        self.config = {
            "params": self.params,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "feature_names": feature_names,
        }
        return self.metrics

    def predict(self, X: np.ndarray) -> dict:
        if self.model is None:
            raise RuntimeError("Model not trained")
        labels = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        return {"labels": labels, "probabilities": probabilities}

    def save(self, path: str) -> None:
        import joblib

        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "metrics": self.metrics,
            "config": self.config,
            "feature_names": self.feature_names,
        }, model_path)

    @classmethod
    def load(cls, path: str) -> "XGBoostModel":
        import joblib

        data = joblib.load(path)
        obj = cls(params=data["config"].get("params", {}))
        obj.model = data["model"]
        obj.metrics = data["metrics"]
        obj.config = data["config"]
        obj.feature_names = data["feature_names"]
        return obj
