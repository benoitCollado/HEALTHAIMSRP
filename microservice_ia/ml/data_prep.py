"""Préparation des features pour l'entraînement Random Forest."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

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


def prepare_matrices(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, dict]:
    df_encoded = df.copy()
    encoders: dict[str, LabelEncoder] = {}

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
    groups = df["user_id"].astype(str).to_numpy()
    meta = {"encoders": encoders, "feature_columns": feature_columns}
    return x, y_class, y_reg, groups, meta
