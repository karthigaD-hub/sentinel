import argparse
import json
from pathlib import Path

import numpy as np


def train_all(model_dir: str, epochs: int = 100, batch_size: int = 256, learning_rate: float = 1e-3) -> dict:
    from app.detection.training.autoencoder import AutoencoderModel
    from app.detection.training.xgboost_model import XGBoostModel
    from app.detection.features.feature_schema import FEATURE_SCHEMA

    output = Path(model_dir)
    train_path = output / "train.npz"
    val_path = output / "val.npz"

    if not train_path.exists():
        raise FileNotFoundError(
            f"Prepared dataset not found at {train_path}. "
            "Run prepare_dataset.py first with a CICIDS2017 CSV file."
        )

    train_data = np.load(train_path)
    val_data = np.load(val_path)
    X_train = train_data["X"]
    y_train = train_data["y"]
    X_val = val_data["X"]
    y_val = val_data["y"]

    results: dict = {"feature_count": len(FEATURE_SCHEMA), "train_samples": len(X_train), "val_samples": len(X_val)}

    ae = AutoencoderModel(input_dim=len(FEATURE_SCHEMA), encoding_dim=16, hidden_dims=[64, 32])
    ae_metrics = ae.train(X_train, X_val, epochs=epochs, batch_size=batch_size, learning_rate=learning_rate)
    ae.save(str(output / "autoencoder.pt"))
    results["autoencoder"] = ae_metrics

    xgb = XGBoostModel()
    xgb_metrics = xgb.train(X_train, y_train, X_val, y_val, feature_names=list(FEATURE_SCHEMA))
    xgb.save(str(output / "xgboost.joblib"))
    results["xgboost"] = xgb_metrics

    schema_path = output / "feature_schema.json"
    if schema_path.exists():
        with open(schema_path) as f:
            schema_data = json.load(f)
        results["label_classes"] = schema_data.get("label_classes", [])

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Q-Sentinel detection models from prepared CICIDS2017 data")
    parser.add_argument("--model-dir", default="./models", help="Directory containing prepared data and where models will be saved")
    parser.add_argument("--epochs", type=int, default=100, help="Autoencoder training epochs")
    parser.add_argument("--batch-size", type=int, default=256, help="Autoencoder batch size")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Autoencoder learning rate")
    args = parser.parse_args()

    result = train_all(args.model_dir, args.epochs, args.batch_size, args.learning_rate)
    print("=" * 60)
    print("Q-Sentinel Model Training Complete")
    print("=" * 60)
    print(f"Feature count: {result['feature_count']}")
    print(f"Train samples: {result['train_samples']}")
    print(f"Val samples: {result['val_samples']}")
    print(f"Autoencoder threshold: {result['autoencoder']['threshold']:.6f}")
    print(f"Autoencoder final loss: {result['autoencoder']['final_loss']:.6f}")
    print(f"XGBoost accuracy: {result['xgboost']['accuracy']:.4f}")
    print(f"XGBoost precision: {result['xgboost']['precision']:.4f}")
    print(f"XGBoost recall: {result['xgboost']['recall']:.4f}")
    print(f"XGBoost F1: {result['xgboost']['f1']:.4f}")
    if "label_classes" in result:
        print(f"Label classes: {result['label_classes']}")
    print(f"\nModel artifacts saved to: {args.model_dir}")
    print("  - autoencoder.pt")
    print("  - xgboost.joblib")
    print("  - scaler.joblib")
    print("  - label_encoder.joblib")
    print("  - feature_schema.json")


if __name__ == "__main__":
    main()
