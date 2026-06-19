from pathlib import Path

import pytest

from app.domain.entities.exercise_context import ExerciseRecommendationContext
from app.domain.entities.user_profile import UserProfile
from app.infrastructure.adapters.ml_random_forest_adapter import RandomForestExerciseRecommender

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "workout_rf_bundle.pkl"

PROFILE = UserProfile(
    age=30,
    sexe="H",
    taille_cm=180,
    poids_kg=75,
    niveau_activite=3,
    perte_de_poids=True,
    endurance=False,
    force=False,
    performance=False,
)


@pytest.fixture(scope="module", autouse=True)
def ensure_model():
    if not MODEL_PATH.exists():
        from ml.train_random_forest import main as train_main

        train_main()


def test_ml_recommender_loads_and_predicts():
    recommender = RandomForestExerciseRecommender(MODEL_PATH)
    result = recommender.recommend(
        PROFILE,
        limit=3,
        context=ExerciseRecommendationContext(
            current_fatigue_rpe=4,
            desired_duration_min=45,
            physical_limitation="aucune",
            preferred_activity="hiit",
        ),
    )
    assert len(result.exercices) >= 1
    assert result.exercices[0].recommended_sets is not None or result.exercices[0].type_exercice != "musculation"
    assert "Random Forest" in result.exercices[0].justification
    assert recommender.metrics.get("accuracy_activity", 0) > 0.5


def test_generate_uses_ml_when_model_present():
    from fastapi.testclient import TestClient

    from app.main import app
    from app.presentation.dependencies import reset_container

    if not MODEL_PATH.exists():
        pytest.skip("Modèle ML non entraîné")

    reset_container()
    test_client = TestClient(app)
    payload = {
        "user_id": 100,
        "objectifs": ["perte_de_poids"],
        "niveau": 3,
        "equipements": ["poids_du_corps"],
        "limitations": [],
        "disponibilite_minutes": 45,
        "seances_par_semaine": 2,
        "longueur_programme_semaines": 2,
        "profil": {"age": 30, "sexe": "H", "taille_cm": 180, "poids_kg": 75},
    }
    response = test_client.post("/api/v1/recommendations/generate", json=payload)
    assert response.status_code == 200
    session = response.json()["sessions"][0]
    assert len(session["exercices"]) >= 1
