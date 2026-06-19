"""Entraîne les Random Forest (activité + séries) et exporte le bundle .pkl."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from ml.generate_training_data import OUTPUT_CSV, OUTPUT_DIR, generate_dataset

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
BUNDLE_PATH = MODELS_DIR / "workout_rf_bundle.pkl"

CATEGORICAL_FEATURES = [
    "fitness_level",
    "health_goal",
    "equipment_available",
    "preferred_activity",
    "physical_limitation",
]
NUMERIC_FEATURES = [
    "session_timestamp",
    "age",
    "height_cm",
    "weight_kg",
    "current_fatigue_rpe",
    "desired_duration_min",
    "performance_history_score",
]
TARGET_CLASS = "recommended_activity"
TARGET_REG = "recommended_sets"


def load_or_generate_csv() -> pd.DataFrame:
    if not OUTPUT_CSV.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        df = generate_dataset()
        df.to_csv(OUTPUT_CSV, index=False)
        return df
    return pd.read_csv(OUTPUT_CSV)


def prepare_matrices(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, dict]:
    df_encoded = df.copy()
    encoders: dict = {}

    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    le_target = LabelEncoder()
    df_encoded[TARGET_CLASS] = le_target.fit_transform(df[TARGET_CLASS].astype(str))
    encoders[TARGET_CLASS] = le_target

    feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    x = df_encoded[feature_columns]
    y_class = df_encoded[TARGET_CLASS].to_numpy()
    y_reg = df_encoded[TARGET_REG].to_numpy()
    return x, y_class, y_reg, {"encoders": encoders, "feature_columns": feature_columns}


def train() -> dict:
    df = load_or_generate_csv()
    x, y_class, y_reg, meta = prepare_matrices(df)

    x_train, x_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
        x, y_class, y_reg, test_size=0.2, random_state=42
    )

    classifier = RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42, n_jobs=-1)
    regressor = RandomForestRegressor(n_estimators=120, max_depth=10, random_state=42, n_jobs=-1)

    classifier.fit(x_train, y_class_train)
    regressor.fit(x_train, y_reg_train)

    class_pred = classifier.predict(x_test)
    reg_pred = regressor.predict(x_test)

    metrics = {
        "accuracy_activity": round(float(accuracy_score(y_class_test, class_pred)), 4),
        "mae_sets": round(float(mean_absolute_error(y_reg_test, reg_pred)), 4),
        "train_samples": len(x_train),
        "test_samples": len(x_test),
    }

    bundle = {
        "version": "1.0",
        "classifier": classifier,
        "regressor": regressor,
        "encoders": meta["encoders"],
        "feature_columns": meta["feature_columns"],
        "metrics": metrics,
    }
    return bundle


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    bundle = train()
    joblib.dump(bundle, BUNDLE_PATH)
    print(f"Modèle exporté → {BUNDLE_PATH}")
    print(f"Métriques : {bundle['metrics']}")


if __name__ == "__main__":
    main()
