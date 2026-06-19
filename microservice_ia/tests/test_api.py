from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PROFILE = {
    "age": 30,
    "sexe": "H",
    "taille_cm": 180,
    "poids_kg": 75,
    "niveau_activite": 3,
    "perte_de_poids": False,
    "performance": False,
    "endurance": False,
    "force": False,
}

GENERATE_PAYLOAD = {
    "user_id": 42,
    "objectifs": ["endurance", "perte_de_poids"],
    "niveau": 3,
    "equipements": ["tapis"],
    "limitations": [],
    "disponibilite_minutes": 45,
    "seances_par_semaine": 3,
    "longueur_programme_semaines": 4,
    "profil": {
        "age": 30,
        "sexe": "H",
        "taille_cm": 180,
        "poids_kg": 75,
    },
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "microservice_ia"


def test_recommandation_calorique():
    response = client.post("/recommandation_calorique", json=PROFILE)
    assert response.status_code == 200
    body = response.json()
    assert body["calories"] == 2700
    assert body["metabolisme_basal"] == 1730


def test_recommandation_exercice():
    payload = {**PROFILE, "endurance": True, "limit": 3}
    response = client.post("/recommandation_exercice", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["exercices"]) <= 3
    assert body["exercices"][0]["score"] > 0


def test_generate_program():
    response = client.post("/api/v1/recommendations/generate", json=GENERATE_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == 42
    assert body["calories_recommandees"] == 2300
    assert body["longueur_programme_semaines"] == 4
    assert body["seances_par_semaine"] == 3
    assert len(body["sessions"]) == 12
    assert body["sessions"][0]["titre"] == "Semaine 1 — Séance 1"
    assert body["session_courante_id"] is not None


def test_get_current_program():
    client.post("/api/v1/recommendations/generate", json=GENERATE_PAYLOAD)
    response = client.get("/api/v1/recommendations/current", params={"user_id": 42})
    assert response.status_code == 200
    assert response.json()["user_id"] == 42


def test_get_current_program_not_found():
    response = client.get("/api/v1/recommendations/current", params={"user_id": 9999})
    assert response.status_code == 404


def test_adjust_session():
    generated = client.post("/api/v1/recommendations/generate", json=GENERATE_PAYLOAD).json()
    response = client.post(
        "/api/v1/recommendations/adjust",
        json={"user_id": 42, "fatigue": 8, "douleur": False, "temps_partiel_minutes": 30},
    )
    assert response.status_code == 200
    body = response.json()
    current = next(s for s in body["sessions"] if s["id"] == generated["session_courante_id"])
    assert current["statut"] == "ajustee"
    assert current["duree_minutes"] <= 45


def test_session_feedback():
    generated = client.post("/api/v1/recommendations/generate", json=GENERATE_PAYLOAD).json()
    session_id = generated["session_courante_id"]
    response = client.post(
        f"/api/v1/recommendations/sessions/{session_id}/feedback",
        json={
            "user_id": 42,
            "rpe": 7,
            "exercices_valides": ["Marche rapide"],
            "ressentis": "Bonne séance, un peu essoufflé.",
        },
    )
    assert response.status_code == 200
    assert response.json()["rpe"] == 7


def test_update_profile_constraints():
    response = client.put(
        "/api/v1/profiles/42/constraints",
        json={"equipements_dispo": ["haltères", "tapis"], "blessures_actives": ["genou"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "haltères" in body["equipements_dispo"]
    assert "genou" in body["blessures_actives"]


def test_profile_history():
    client.post("/api/v1/recommendations/generate", json=GENERATE_PAYLOAD)
    generated = client.get("/api/v1/recommendations/current", params={"user_id": 42}).json()
    session_id = generated["session_courante_id"]
    client.post(
        f"/api/v1/recommendations/sessions/{session_id}/feedback",
        json={"user_id": 42, "rpe": 6, "exercices_valides": [], "ressentis": "OK"},
    )
    response = client.get("/api/v1/profiles/42/history")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == 42
    assert len(body["sessions_feedback"]) >= 1


def test_session_progression_after_feedback():
    client.post("/api/v1/recommendations/generate", json=GENERATE_PAYLOAD)
    program = client.get("/api/v1/recommendations/current", params={"user_id": 42}).json()
    sessions = program["sessions"]

    for index in range(4):
        session_id = program["session_courante_id"]
        assert session_id == sessions[index]["id"]
        response = client.post(
            f"/api/v1/recommendations/sessions/{session_id}/feedback",
            json={"user_id": 42, "rpe": 6 + index, "exercices_valides": ["Marche rapide"], "ressentis": "OK"},
        )
        assert response.status_code == 200
        program = client.get("/api/v1/recommendations/current", params={"user_id": 42}).json()

    assert program["session_courante_id"] == sessions[4]["id"]
    terminees = [s for s in program["sessions"] if s["statut"] == "terminee"]
    assert len(terminees) == 4

    adjust = client.post(
        "/api/v1/recommendations/adjust",
        json={"user_id": 42, "fatigue": 7, "douleur": False, "temps_partiel_minutes": 35},
    )
    assert adjust.status_code == 200
    adjusted_session = next(s for s in adjust.json()["sessions"] if s["id"] == sessions[4]["id"])
    assert adjusted_session["statut"] == "ajustee"
