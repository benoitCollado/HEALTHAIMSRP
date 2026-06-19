from __future__ import annotations

import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from app.domain.entities.exercise_context import ExerciseRecommendationContext
from app.domain.entities.recommendations import ExerciseItem, ExerciseRecommendation
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.exercise_recommender import ExerciseRecommenderPort

ACTIVITY_EXERCISES: dict[str, tuple[tuple[str, str, str, str | None, str | None], ...]] = {
    "musculation": (
        ("Squats", "musculation", "debutant", None, "jambes"),
        ("Pompes", "musculation", "debutant", None, "pectoraux"),
        ("Gainage planche", "musculation", "intermediaire", "tapis", "abdominaux"),
        ("Tractions", "musculation", "avance", "barre", "dos"),
    ),
    "running": (
        ("Course à pied", "cardio", "intermediaire", "chaussures running", "jambes"),
        ("Marche rapide", "cardio", "debutant", None, "jambes"),
        ("Vélo", "cardio", "debutant", "vélo", "jambes"),
    ),
    "hiit": (
        ("HIIT", "cardio", "avance", None, "corps entier"),
        ("Squats", "musculation", "debutant", None, "jambes"),
        ("Gainage planche", "musculation", "intermediaire", "tapis", "abdominaux"),
    ),
    "pilates": (
        ("Étirements", "souplesse", "debutant", "tapis", "corps entier"),
        ("Gainage planche", "musculation", "intermediaire", "tapis", "abdominaux"),
        ("Marche rapide", "cardio", "debutant", None, "jambes"),
    ),
}

LEVEL_FROM_ACTIVITY: dict[int, str] = {1: "debutant", 2: "debutant", 3: "intermediaire", 4: "avance", 5: "avance"}


class RandomForestExerciseRecommender(ExerciseRecommenderPort):
    """Adaptateur ML : inférence activité + volume via Random Forest (.pkl)."""

    def __init__(self, model_path: str | Path) -> None:
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Modèle introuvable : {path}")
        self._bundle = joblib.load(path)
        self._classifier = self._bundle["classifier"]
        self._regressor = self._bundle["regressor"]
        self._encoders: dict[str, LabelEncoder] = self._bundle["encoders"]
        self._feature_columns: list[str] = self._bundle["feature_columns"]
        self._metrics = self._bundle.get("metrics", {})

    @property
    def metrics(self) -> dict:
        return self._metrics

    def recommend(
        self,
        profile: UserProfile,
        limit: int = 5,
        context: ExerciseRecommendationContext | None = None,
    ) -> ExerciseRecommendation:
        ctx = context or ExerciseRecommendationContext()
        features = self._build_feature_row(profile, ctx)
        activity_idx = int(self._classifier.predict(features)[0])
        sets = int(round(float(self._regressor.predict(features)[0])))
        sets = int(np.clip(sets, 2, 6))

        activity_encoder = self._encoders["recommended_activity"]
        activity = activity_encoder.inverse_transform([activity_idx])[0]

        catalog = ACTIVITY_EXERCISES.get(activity, ACTIVITY_EXERCISES["musculation"])
        items = []
        for index, (nom, typ, niveau, equip, muscle) in enumerate(catalog[: max(1, limit)]):
            items.append(
                ExerciseItem(
                    nom_exercice=nom,
                    type_exercice=typ,
                    niveau_difficulte=niveau,
                    equipement=equip,
                    muscle_principal=muscle,
                    score=round(1.0 - index * 0.1, 2),
                    recommended_sets=sets if typ == "musculation" else None,
                    justification=(
                        f"Random Forest — activité « {activity} », {sets} séries recommandées "
                        f"(fatigue RPE {ctx.current_fatigue_rpe})."
                    ),
                )
            )

        detail = (
            f"Prédiction ML : activité={activity}, séries={sets}. "
            f"Précision entraînement activité={self._metrics.get('accuracy_activity', 'n/a')}."
        )
        return ExerciseRecommendation(exercices=tuple(items), detail=detail)

    def _build_feature_row(self, profile: UserProfile, ctx: ExerciseRecommendationContext) -> pd.DataFrame:
        fitness_level = LEVEL_FROM_ACTIVITY.get(profile.niveau_activite, "intermediaire")
        health_goal = _health_goal_from_profile(profile)
        equipment = ctx.equipment_available[0] if ctx.equipment_available else "poids_du_corps"

        raw = {
            "session_timestamp": int(time.time()),
            "age": profile.age,
            "height_cm": profile.taille_cm,
            "weight_kg": profile.poids_kg,
            "fitness_level": fitness_level,
            "health_goal": health_goal,
            "equipment_available": equipment,
            "preferred_activity": ctx.preferred_activity,
            "physical_limitation": ctx.physical_limitation,
            "current_fatigue_rpe": ctx.current_fatigue_rpe,
            "desired_duration_min": ctx.desired_duration_min,
            "performance_history_score": ctx.performance_history_score,
        }

        encoded_row = []
        for col in self._feature_columns:
            value = raw[col]
            if col in self._encoders and col != "recommended_activity":
                encoded_row.append(_safe_encode(self._encoders[col], str(value)))
            else:
                encoded_row.append(float(value))
        return pd.DataFrame([encoded_row], columns=self._feature_columns)

    @staticmethod
    def from_env(default_path: str = "models/workout_rf_bundle.pkl") -> RandomForestExerciseRecommender | None:
        path = Path(default_path)
        if path.exists():
            return RandomForestExerciseRecommender(path)
        return None


def _safe_encode(encoder: LabelEncoder, value: str) -> int:
    if value in encoder.classes_:
        return int(encoder.transform([value])[0])
    return int(encoder.transform([encoder.classes_[0]])[0])


def _health_goal_from_profile(profile: UserProfile) -> str:
    if profile.perte_de_poids:
        return "perte_graisse"
    if profile.endurance:
        return "endurance"
    if profile.force or profile.performance:
        return "renforcement_musculaire"
    return "sante_generale"
