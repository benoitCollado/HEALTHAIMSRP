from unittest.mock import MagicMock, patch


def test_chat_requires_mistral_key(client, admin_headers, monkeypatch):
    monkeypatch.delenv("KEY_MISTRAL_API", raising=False)
    monkeypatch.delenv("KEY_MISTRALL_API", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    response = client.post("/chat/", headers=admin_headers, json={"message": "Bonjour"})

    assert response.status_code == 503
    assert response.json()["detail"] == "API Mistral non configuree"


def test_chat_calls_mistral(client, admin_headers, monkeypatch):
    monkeypatch.setenv("KEY_MISTRAL_API", "test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "HealthAI MSPR peut vous aider a suivre vos objectifs."}}]
    }
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.__enter__.return_value.post.return_value = mock_response
    mock_client.__exit__.return_value = False

    with patch("app.routers.chat.httpx.Client", return_value=mock_client):
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

    call_kwargs = mock_client.__enter__.return_value.post.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert call_kwargs["json"]["model"] == "mistral-small-latest"
    assert call_kwargs["json"]["messages"][0]["role"] == "system"
    assert call_kwargs["json"]["messages"][-1]["content"] == "A quoi sert HealthAI MSPR ?"
