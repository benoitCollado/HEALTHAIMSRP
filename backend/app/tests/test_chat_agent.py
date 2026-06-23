from unittest.mock import patch

from app.chat_agent import (
    MISTRAL_MICROSERVICE_TOOLS,
    AgentContext,
    build_objectifs_microservice,
    detect_required_tools,
    execute_microservice_tool,
    merge_tool_result,
)


def test_mistral_tools_cover_all_microservice_routes():
    names = {tool["function"]["name"] for tool in MISTRAL_MICROSERVICE_TOOLS}
    assert names == {
        "get_microservice_health",
        "get_calorie_recommendations",
        "get_exercise_recommendations",
        "generate_workout_program",
        "get_current_workout_program",
        "adjust_workout_session",
        "record_session_feedback",
        "update_profile_constraints",
        "get_profile_history",
    }


def test_build_objectifs_microservice_from_postgresql_rows():
    objectifs = [
        {"type_objectif": "Endurance", "description": "Gagner en endurance", "statut": "en_cours"},
        {"type_objectif": "Force", "description": "Developper ma force musculaire", "statut": "en_cours"},
    ]
    profile = {"endurance": False, "force": True, "perte_de_poids": False, "performance": False}
    tokens = build_objectifs_microservice(objectifs, profile)
    assert "endurance" in tokens
    assert "force" in tokens


def test_detect_required_tools_for_broad_recommendation():
    required = detect_required_tools("Quelles recommandations personnalisees me proposez-vous ?")
    assert "get_calorie_recommendations" in required
    assert "get_exercise_recommendations" in required


def test_execute_microservice_tool_generate_program():
    context = AgentContext(
        user_id=42,
        profile_payload={
            "age": 30,
            "sexe": "H",
            "taille_cm": 180,
            "poids_kg": 75,
            "niveau_activite": 3,
            "perte_de_poids": False,
            "performance": False,
            "endurance": True,
            "force": False,
        },
        objectifs_microservice=["endurance"],
    )
    with patch(
        "app.chat_agent.call_microservice_ia_generate_program",
        return_value={"id": "prog-1", "sessions": []},
    ) as generate:
        result = execute_microservice_tool("generate_workout_program", context, {})

    assert result["status"] == "ok"
    assert generate.call_args.args[0]["user_id"] == 42
    assert generate.call_args.args[0]["objectifs"] == ["endurance"]


def test_merge_tool_result_groups_programme():
    tool_results: dict = {}
    merge_tool_result(tool_results, "generate_workout_program", {"status": "ok", "data": {"id": "p1"}})
    assert tool_results["programme"] == {"id": "p1"}


def test_run_chat_graph_executes_tools_then_returns_answer():
    from app.chat_graph import run_chat_graph

    with patch("app.chat_graph.call_mistral_chat_completion") as mistral:
        mistral.side_effect = [
            {
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_cal",
                        "function": {"name": "get_calorie_recommendations", "arguments": "{}"},
                    }
                ],
            },
            {"content": "Voici vos conseils personnalises."},
        ]
        with patch("app.chat_graph.execute_microservice_tool") as execute_tool:
            execute_tool.return_value = {"status": "ok", "data": {"calories": 2700}}
            answer, recommendation = run_chat_graph(
                [{"role": "system", "content": "sys"}, {"role": "user", "content": "Calories ?"}],
                user_id=1,
                profile_payload={"age": 30, "sexe": "H", "taille_cm": 180, "poids_kg": 75, "niveau_activite": 2,
                                 "perte_de_poids": False, "performance": False, "endurance": False, "force": False},
                objectifs=[{"type_objectif": "Force", "statut": "en_cours", "description": "Force"}],
            )

    assert answer == "Voici vos conseils personnalises."
    assert recommendation is not None
    assert recommendation["calories"] == {"calories": 2700}
    assert "objectifs" in recommendation
