from unittest.mock import MagicMock, patch

from app.external_clients import call_microservice_ia_recommendations


def test_call_microservice_ia_recommendations_uses_api_prefixed_routes(monkeypatch):
    monkeypatch.setenv("MICROSERVICE_IA_URL", "http://microservice_ia:8090")

    calories_response = MagicMock()
    calories_response.json.return_value = {"calories": 2700}
    exercises_response = MagicMock()
    exercises_response.json.return_value = {"exercices": []}

    with patch(
        "app.external_clients._request_with_resilience",
        side_effect=[calories_response, exercises_response],
    ) as request:
        result = call_microservice_ia_recommendations({"age": 30})

    assert result == {"calories": {"calories": 2700}, "exercices": {"exercices": []}}
    assert request.call_args_list[0].args[2] == "http://microservice_ia:8090/api/recommandation_calorique"
    assert request.call_args_list[1].args[2] == "http://microservice_ia:8090/api/recommandation_exercice"
