import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

from app.detection.features.feature_schema import FEATURE_SCHEMA


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates()
    df = df.replace([np.inf, -np.inf], np.nan)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df


def normalize_labels(df: pd.DataFrame, label_column: str) -> pd.DataFrame:
    df[label_column] = df[label_column].astype(str).str.strip().str.lower()
    df[label_column] = df[label_column].str.replace(r"\s+", "_", regex=True)
    df.loc[df[label_column].str.contains("benign", case=False, na=False), label_column] = "benign"
    return df


def select_features(df: pd.DataFrame, label_column: str) -> tuple[pd.DataFrame, pd.Series]:
    missing = [c for c in FEATURE_SCHEMA if c not in df.columns]
    for col in missing:
        df[col] = 0.0
    X = df[FEATURE_SCHEMA].copy()
    y = df[label_column].copy()
    return X, y


def prepare_dataset(input_path: str, output_dir: str = "./models", label_column: str = "label", test_size: float = 0.2, val_size: float = 0.1, random_state: int = 42) -> dict:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Dataset not found: {input_path}. Download CICIDS2017 and provide the CSV path.")

    df = pd.read_csv(input_file, low_memory=False)
    df = clean_dataset(df)
    df = normalize_labels(df, label_column)
    X, y = select_features(df, label_column)

    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    val_fraction = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=val_fraction, random_state=random_state, stratify=y_train_val)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    label_encoder = LabelEncoder()
    label_encoder.fit(pd.concat([y_train, y_val, y_test], ignore_index=True))
    y_train_enc = label_encoder.transform(y_train)
    y_val_enc = label_encoder.transform(y_val)
    y_test_enc = label_encoder.transform(y_test)

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    import joblib
    joblib.dump(scaler, output / "scaler.joblib")
    joblib.dump(label_encoder, output / "label_encoder.joblib")

    np.savez(output / "train.npz", X=X_train_scaled, y=y_train_enc)
    np.savez(output / "val.npz", X=X_val_scaled, y=y_val_enc)
    np.savez(output / "test.npz", X=X_test_scaled, y=y_test_enc)

    import json
    with open(output / "feature_schema.json", "w") as f:
        json.dump({"feature_names": FEATURE_SCHEMA, "label_classes": list(label_encoder.classes_)}, f, indent=2)

    return {
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "feature_count": len(FEATURE_SCHEMA),
        "classes": list(label_encoder.classes_),
        "output_dir": str(output),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CICIDS2017 dataset for training")
    parser.add_argument("--input", required=True, help="Path to CICIDS2017 CSV file")
    parser.add_argument("--output", default="./models", help="Output directory for prepared data")
    parser.add_argument("--label-column", default="label", help="Name of the label column")
    args = parser.parse_args()

    result = prepare_dataset(args.input, args.output, args.label_column)
    print(f"Dataset prepared: {result}")


if __name__ == "__main__":
    main()
