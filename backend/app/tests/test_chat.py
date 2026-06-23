from unittest.mock import MagicMock, patch
from decimal import Decimal
import json

from app.external_clients import ExternalServiceError
from app.routers.chat import _profile_payload


def test_chat_requires_mistral_key(client, admin_headers, monkeypatch):
    monkeypatch.delenv("KEY_MISTRAL_API", raising=False)
    monkeypatch.delenv("KEY_MISTRALL_API", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    response = client.post("/chat/", headers=admin_headers, json={"message": "Bonjour"})

    assert response.status_code == 503
    assert response.json()["detail"] == "API Mistral non configuree ou refusee"


def test_chat_calls_microservice_when_asking_recommendations(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")
    recommendation = {
        "calories": {"calories": 2700, "detail": "Maintenance"},
        "exercices": {"detail": "HIIT", "exercices": [{"nom_exercice": "Course"}]},
    }

    with (
        patch("app.routers.chat.cache.get_json", return_value=None),
        patch("app.routers.chat.cache.set_json"),
        patch(
            "app.routers.chat.run_chat_with_tools",
            return_value=("Voici vos conseils personnalises.", recommendation),
        ) as run_agent,
    ):
        response = client.post(
            "/chat/",
            headers=admin_headers,
            json={"message": "Quelles calories et exercices me recommandez-vous ?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Voici vos conseils personnalises."
    assert body["recommendation"] == recommendation
    run_agent.assert_called_once()


def test_chat_calls_mistral(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "HealthAI MSPR peut vous aider a suivre vos objectifs."}}]
    }
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.__enter__.return_value.request.return_value = mock_response
    mock_client.__exit__.return_value = False

    with (
        patch("app.routers.chat.cache.get_json", return_value=None),
        patch("app.routers.chat.cache.set_json") as set_cache,
        patch("app.external_clients.httpx.Client", return_value=mock_client),
    ):
        response = client.post(
            "/chat/",
            headers=admin_headers,
            json={
                "message": "A quoi sert HealthAI MSPR ?",
                "history": [{"role": "assistant", "content": "Bonjour"}],
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "HealthAI MSPR peut vous aider a suivre vos objectifs.",
        "recommendation": None,
    }

    call_kwargs = mock_client.__enter__.return_value.request.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert call_kwargs["json"]["model"] == "mistral-small-latest"
    assert call_kwargs["json"]["messages"][0]["role"] == "system"
    assert call_kwargs["json"]["messages"][-1]["content"] == "A quoi sert HealthAI MSPR ?"
    assert "tools" in call_kwargs["json"]
    set_cache.assert_called_once()


def test_chat_returns_cached_answer_without_calling_mistral(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")

    with (
        patch("app.routers.chat.cache.get_json", return_value="Reponse depuis Redis"),
        patch("app.routers.chat.run_chat_with_tools") as run_agent,
    ):
        response = client.post("/chat/", headers=admin_headers, json={"message": "Bonjour"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Reponse depuis Redis", "recommendation": None}
    run_agent.assert_not_called()


def test_chat_returns_fallback_when_mistral_is_down(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")

    with (
        patch("app.routers.chat.cache.get_json", return_value=None),
        patch("app.routers.chat.cache.set_json") as set_cache,
        patch("app.routers.chat.run_chat_with_tools", side_effect=RuntimeError("down")),
    ):
        response = client.post("/chat/", headers=admin_headers, json={"message": "Bonjour"})

    assert response.status_code == 200
    assert "service IA est temporairement indisponible" in response.json()["answer"]
    set_cache.assert_not_called()


def test_chat_upload_image_uses_user_storage(client, admin_headers):
    uploaded = {
        "object_key": "users/1/chat/image.png",
        "url": "http://localhost:9000/healthai-chat-images/users/1/chat/image.png",
        "content_type": "image/png",
        "filename": "image.png",
    }

    with patch("app.routers.chat.upload_user_image", return_value=uploaded) as upload:
        response = client.post(
            "/chat/images",
            headers=admin_headers,
            files={"file": ("image.png", b"fake", "image/png")},
        )

    assert response.status_code == 201
    assert response.json() == uploaded
    assert upload.call_args.args[0] == "1"


def test_chat_recommendations_call_microservice_with_user_profile(client, admin_headers):
    recommendation = {
        "calories": {"calories": 2700, "metabolisme_basal": 1700, "detail": "Maintenance"},
        "exercices": {
            "detail": "Selon vos objectifs.",
            "exercices": [
                {
                    "nom_exercice": "Squat",
                    "type_exercice": "force",
                    "niveau_difficulte": "intermediaire",
                    "equipement": None,
                    "muscle_principal": "jambes",
                    "score": 0.9,
                    "justification": "Objectif force.",
                }
            ],
        },
    }

    with patch("app.routers.chat.call_microservice_ia_recommendations", return_value=recommendation) as call_ia:
        response = client.post("/chat/recommendations", headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert "2700 kcal" in body["answer"]
    assert "Squat" in body["answer"]
    assert body["recommendation"] == recommendation
    assert call_ia.call_args.args[0]["age"] == 30
    assert call_ia.call_args.args[0]["sexe"] == "H"
    assert call_ia.call_args.args[0]["niveau_activite"] == 1


def test_profile_payload_is_json_serializable_with_decimal_values():
    user = MagicMock(
        age=Decimal("30"),
        sexe="H",
        taille_cm=Decimal("180.0"),
        poids_kg=Decimal("75.5"),
        niveau_activite=Decimal("2"),
        perte_de_poids=False,
        performance=True,
        endurance=False,
        force=True,
    )

    payload = _profile_payload(user)

    assert payload["age"] == 30
    assert payload["taille_cm"] == 180.0
    assert payload["poids_kg"] == 75.5
    json.dumps(payload)


def test_chat_analyze_image_calls_photo_microservice(client, admin_headers):
    analysis = {"answer": "Cette assiette semble contenir des legumes.", "calories_estimees": 320}

    with (
        patch("app.routers.chat.presigned_image_url", return_value="http://minio/image.jpg") as presigned,
        patch("app.routers.chat.call_photo_processing", return_value=analysis) as call_photo,
    ):
        response = client.post(
            "/chat/images/analyze",
            headers=admin_headers,
            json={
                "image": {"object_key": "users/1/chat/image.jpg", "filename": "image.jpg"},
                "question": "Analyse mon repas",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"answer": analysis["answer"], "analysis": analysis}
    presigned.assert_called_once_with("users/1/chat/image.jpg", public=False)
    payload = call_photo.call_args.args[0]
    assert payload["image_url"] == "http://minio/image.jpg"
    assert payload["question"] == "Analyse mon repas"
    assert payload["user_id"] == "1"


def test_chat_analyze_image_returns_degraded_when_photo_microservice_is_down(client, admin_headers):
    with (
        patch("app.routers.chat.presigned_image_url", return_value="http://minio/image.jpg"),
        patch("app.routers.chat.call_photo_processing", side_effect=ExternalServiceError("down")),
    ):
        response = client.post(
            "/chat/images/analyze",
            headers=admin_headers,
            json={"image": {"object_key": "users/1/chat/image.jpg", "filename": "image.jpg"}},
        )

    assert response.status_code == 200
    body = response.json()
    assert "temporairement indisponible" in body["answer"]
    assert body["analysis"]["status"] == "degraded"


def test_chat_analyze_image_rejects_image_from_another_user(client, admin_headers):
    response = client.post(
        "/chat/images/analyze",
        headers=admin_headers,
        json={"image": {"object_key": "users/999/chat/image.jpg", "filename": "image.jpg"}},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Image non autorisee"


def test_chat_rejects_image_from_another_user(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")

    response = client.post(
        "/chat/",
        headers=admin_headers,
        json={
            "message": "Analyse cette image",
            "images": [{"object_key": "users/999/chat/image.png", "filename": "image.png"}],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Image non autorisee"
