from unittest.mock import MagicMock, patch

from app.external_clients import (
    call_microservice_ia_adjust_session,
    call_microservice_ia_current_program,
    call_microservice_ia_generate_program,
    call_microservice_ia_health,
    call_microservice_ia_profile_history,
    call_microservice_ia_recommendations,
    call_microservice_ia_session_feedback,
    call_microservice_ia_update_constraints,
)


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


def test_call_microservice_ia_v1_routes(monkeypatch):
    monkeypatch.setenv("MICROSERVICE_IA_URL", "http://microservice_ia:8090")

    health_response = MagicMock()
    health_response.json.return_value = {"status": "ok"}
    generate_response = MagicMock()
    generate_response.json.return_value = {"id": "prog-1"}
    current_response = MagicMock()
    current_response.json.return_value = {"id": "prog-1"}
    adjust_response = MagicMock()
    adjust_response.json.return_value = {"id": "prog-1", "sessions": []}
    feedback_response = MagicMock()
    feedback_response.json.return_value = {"session_id": "s1"}
    constraints_response = MagicMock()
    constraints_response.json.return_value = {"user_id": 1}
    history_response = MagicMock()
    history_response.json.return_value = {"user_id": 1, "seances_terminees": 0}

    with patch(
        "app.external_clients._request_with_resilience",
        side_effect=[
            health_response,
            generate_response,
            current_response,
            adjust_response,
            feedback_response,
            constraints_response,
            history_response,
        ],
    ) as request:
        assert call_microservice_ia_health() == {"status": "ok"}
        assert call_microservice_ia_generate_program({"user_id": 1}) == {"id": "prog-1"}
        assert call_microservice_ia_current_program(1) == {"id": "prog-1"}
        assert call_microservice_ia_adjust_session({"user_id": 1, "fatigue": 5}) == {"id": "prog-1", "sessions": []}
        assert call_microservice_ia_session_feedback("s1", {"user_id": 1, "rpe": 7}) == {"session_id": "s1"}
        assert call_microservice_ia_update_constraints(1, {"equipements_dispo": []}) == {"user_id": 1}
        assert call_microservice_ia_profile_history(1) == {"user_id": 1, "seances_terminees": 0}

    urls = [call.args[2] for call in request.call_args_list]
    assert urls[0] == "http://microservice_ia:8090/health"
    assert urls[1] == "http://microservice_ia:8090/api/v1/recommendations/generate"
    assert urls[2] == "http://microservice_ia:8090/api/v1/recommendations/current"
    assert urls[3] == "http://microservice_ia:8090/api/v1/recommendations/adjust"
    assert urls[4] == "http://microservice_ia:8090/api/v1/recommendations/sessions/s1/feedback"
    assert urls[5] == "http://microservice_ia:8090/api/v1/profiles/1/constraints"
    assert urls[6] == "http://microservice_ia:8090/api/v1/profiles/1/history"
