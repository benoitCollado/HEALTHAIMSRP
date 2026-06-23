from unittest.mock import patch

from app.chat_agent import (
    MISTRAL_MICROSERVICE_TOOLS,
    execute_microservice_tool,
    run_chat_with_tools,
)


def test_mistral_tools_declare_calorie_and_exercise_handlers():
    names = {tool["function"]["name"] for tool in MISTRAL_MICROSERVICE_TOOLS}
    assert names == {"get_calorie_recommendations", "get_exercise_recommendations"}


def test_execute_microservice_tool_calories():
    with patch(
        "app.chat_agent.call_microservice_ia_calories",
        return_value={"calories": 2200, "detail": "Maintenance"},
    ) as call_calories:
        result = execute_microservice_tool("get_calorie_recommendations", {"age": 30})

    assert result == {"status": "ok", "data": {"calories": 2200, "detail": "Maintenance"}}
    call_calories.assert_called_once_with({"age": 30})


def test_execute_microservice_tool_exercises_with_limit():
    with patch(
        "app.chat_agent.call_microservice_ia_exercises",
        return_value={"exercices": [{"nom_exercice": "Course"}]},
    ) as call_exercises:
        result = execute_microservice_tool(
            "get_exercise_recommendations",
            {"age": 30},
            {"limit": 3},
        )

    assert result["status"] == "ok"
    call_exercises.assert_called_once_with({"age": 30}, limit=3)


def test_run_chat_with_tools_executes_tool_then_returns_final_answer():
    recommendation = {
        "calories": {"calories": 2700},
        "exercices": {"exercices": [{"nom_exercice": "Squat"}]},
    }

    with patch("app.chat_agent.call_mistral_chat_completion") as mistral:
        mistral.side_effect = [
            {
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_cal",
                        "function": {"name": "get_calorie_recommendations", "arguments": "{}"},
                    },
                    {
                        "id": "call_exe",
                        "function": {"name": "get_exercise_recommendations", "arguments": '{"limit": 5}'},
                    },
                ],
            },
            {"content": "Voici vos conseils personnalises."},
        ]
        with patch("app.chat_agent.execute_microservice_tool") as execute_tool:
            execute_tool.side_effect = [
                {"status": "ok", "data": recommendation["calories"]},
                {"status": "ok", "data": recommendation["exercices"]},
            ]
            answer, merged = run_chat_with_tools([{"role": "user", "content": "Calories ?"}], {"age": 30})

    assert answer == "Voici vos conseils personnalises."
    assert merged == recommendation
    assert mistral.call_count == 2
    assert execute_tool.call_count == 2
