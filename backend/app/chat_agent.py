"""Agent Chat IA — tools Mistral et appels au microservice IA."""

from __future__ import annotations

import json
from typing import Any

from app.external_clients import (
    ExternalServiceError,
    ExternalServiceResponseError,
    call_microservice_ia_calories,
    call_microservice_ia_exercises,
    call_mistral_chat_completion,
)

MAX_TOOL_ROUNDS = 3

MISTRAL_MICROSERVICE_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_calorie_recommendations",
            "description": (
                "Obtient le repere calorique journalier personnalise pour l'utilisateur connecte "
                "(calcul base sur son profil HealthAI : age, sexe, taille, poids, niveau d'activite, objectifs)."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exercise_recommendations",
            "description": (
                "Obtient une liste d'exercices personnalises pour l'utilisateur connecte "
                "(profil et objectifs HealthAI : perte de poids, endurance, force, performance)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum d'exercices a retourner (defaut 5, max 10).",
                        "minimum": 1,
                        "maximum": 10,
                    }
                },
                "required": [],
            },
        },
    },
]


def execute_microservice_tool(
    tool_name: str,
    profile_payload: dict[str, Any],
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute un tool microservice IA et retourne un payload JSON-serialisable."""
    args = arguments or {}
    try:
        if tool_name == "get_calorie_recommendations":
            return {"status": "ok", "data": call_microservice_ia_calories(profile_payload)}
        if tool_name == "get_exercise_recommendations":
            limit = max(1, min(10, int(args.get("limit", 5))))
            return {"status": "ok", "data": call_microservice_ia_exercises(profile_payload, limit=limit)}
    except ExternalServiceError as exc:
        return {"status": "error", "message": str(exc)}
    return {"status": "error", "message": f"Tool inconnu: {tool_name}"}


def _parse_tool_arguments(raw_arguments: str | None) -> dict[str, Any]:
    if not raw_arguments:
        return {}
    try:
        parsed = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _merge_tool_result(recommendation: dict[str, Any], tool_name: str, result: dict[str, Any]) -> None:
    if result.get("status") != "ok":
        return
    data = result.get("data") or {}
    if tool_name == "get_calorie_recommendations":
        recommendation["calories"] = data
    elif tool_name == "get_exercise_recommendations":
        recommendation["exercices"] = data


def run_chat_with_tools(
    messages: list[dict[str, Any]],
    profile_payload: dict[str, Any],
    *,
    max_rounds: int = MAX_TOOL_ROUNDS,
) -> tuple[str, dict[str, Any] | None]:
    """Boucle agent : Mistral choisit les tools, execution, puis second appel Mistral."""
    working_messages = list(messages)
    recommendation: dict[str, Any] = {}

    for _ in range(max_rounds):
        assistant_message = call_mistral_chat_completion(
            working_messages,
            tools=MISTRAL_MICROSERVICE_TOOLS,
        )
        tool_calls = assistant_message.get("tool_calls")
        if not tool_calls:
            content = (assistant_message.get("content") or "").strip()
            if not content:
                raise ExternalServiceResponseError("Reponse Mistral vide")
            return content, recommendation or None

        working_messages.append(assistant_message)

        for tool_call in tool_calls:
            function = tool_call.get("function") or {}
            tool_name = function.get("name", "")
            arguments = _parse_tool_arguments(function.get("arguments"))
            result = execute_microservice_tool(tool_name, profile_payload, arguments)
            _merge_tool_result(recommendation, tool_name, result)
            working_messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_call_id": tool_call.get("id", ""),
                    "name": tool_name,
                }
            )

    raise ExternalServiceResponseError("Nombre maximal d'appels tools Mistral depasse")
