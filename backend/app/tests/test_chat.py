from unittest.mock import MagicMock, patch


def test_chat_requires_mistral_key(client, admin_headers, monkeypatch):
    monkeypatch.delenv("KEY_MISTRAL_API", raising=False)
    monkeypatch.delenv("KEY_MISTRALL_API", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    response = client.post("/chat/", headers=admin_headers, json={"message": "Bonjour"})

    assert response.status_code == 503
    assert response.json()["detail"] == "API Mistral non configuree ou refusee"


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
    assert response.json() == {"answer": "HealthAI MSPR peut vous aider a suivre vos objectifs."}

    call_kwargs = mock_client.__enter__.return_value.request.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert call_kwargs["json"]["model"] == "mistral-small-latest"
    assert call_kwargs["json"]["messages"][0]["role"] == "system"
    assert call_kwargs["json"]["messages"][-1]["content"] == "A quoi sert HealthAI MSPR ?"
    set_cache.assert_called_once()


def test_chat_returns_cached_answer_without_calling_mistral(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")

    with (
        patch("app.routers.chat.cache.get_json", return_value="Reponse depuis Redis"),
        patch("app.routers.chat.call_mistral_chat") as call_mistral,
    ):
        response = client.post("/chat/", headers=admin_headers, json={"message": "Bonjour"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Reponse depuis Redis"}
    call_mistral.assert_not_called()


def test_chat_returns_fallback_when_mistral_is_down(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")

    with (
        patch("app.routers.chat.cache.get_json", return_value=None),
        patch("app.routers.chat.cache.set_json") as set_cache,
        patch("app.routers.chat.call_mistral_chat", side_effect=RuntimeError("down")),
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
