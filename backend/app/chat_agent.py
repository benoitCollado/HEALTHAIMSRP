"""Tools Mistral et exécution des routes microservice IA."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.external_clients import (
    ExternalServiceError,
    call_microservice_ia_adjust_session,
    call_microservice_ia_calories,
    call_microservice_ia_current_program,
    call_microservice_ia_exercises,
    call_microservice_ia_generate_program,
    call_microservice_ia_health,
    call_microservice_ia_profile_history,
    call_microservice_ia_session_feedback,
    call_microservice_ia_update_constraints,
)

MAX_TOOL_ROUNDS = 6

TOOL_RESULT_KEYS: dict[str, str] = {
    "get_microservice_health": "health",
    "get_calorie_recommendations": "calories",
    "get_exercise_recommendations": "exercices",
    "generate_workout_program": "programme",
    "get_current_workout_program": "programme",
    "adjust_workout_session": "programme",
    "record_session_feedback": "feedback",
    "update_profile_constraints": "constraints",
    "get_profile_history": "history",
}

MICROSERVICE_OBJECTIF_ALIASES: dict[str, str] = {
    "destresse": "perte_de_poids",
    "déstress": "perte_de_poids",
    "stress": "perte_de_poids",
    "sante": "endurance",
    "santé": "endurance",
    "perte de poids": "perte_de_poids",
    "perte_de_poids": "perte_de_poids",
    "perte": "perte_de_poids",
    "performance": "performance",
    "endurance": "endurance",
    "force": "force",
}

REQUIRED_TOOL_PATTERNS: dict[str, re.Pattern[str]] = {
    "get_calorie_recommendations": re.compile(
        r"\b(calor(?:ie|ies|ique)|kcal|metabolisme|repere calorique)\b",
        re.IGNORECASE,
    ),
    "get_exercise_recommendations": re.compile(
        r"\b(exercice|entrainement|entraînement|sport|musculation|workout|seance|séance)\b",
        re.IGNORECASE,
    ),
    "generate_workout_program": re.compile(
        r"\b(programme|plan d.?entrainement|planning|generer un plan|générer un plan)\b",
        re.IGNORECASE,
    ),
    "get_current_workout_program": re.compile(
        r"\b(programme actif|mon programme|programme en cours|programme courant)\b",
        re.IGNORECASE,
    ),
    "adjust_workout_session": re.compile(
        r"\b(ajust(er|ement)|fatigue|seance plus courte|séance plus courte|douleur)\b",
        re.IGNORECASE,
    ),
    "record_session_feedback": re.compile(
        r"\b(feedback|rpe|seance terminee|séance terminée|ressenti(?:s)?)\b",
        re.IGNORECASE,
    ),
    "update_profile_constraints": re.compile(
        r"\b(contrainte|blessure|equipement|équipement|materiel|matériel)\b",
        re.IGNORECASE,
    ),
    "get_profile_history": re.compile(
        r"\b(historique|suivi|performances passees|performances passées)\b",
        re.IGNORECASE,
    ),
    "get_microservice_health": re.compile(
        r"\b(etat du microservice|état du microservice|sante du service ia|santé du service ia)\b",
        re.IGNORECASE,
    ),
}

BROAD_RECOMMENDATION_PATTERN = re.compile(
    r"\b(recommand(?:ation|ations|e|es|er)|conseil(?:s)? personnalise(?:s)?)\b",
    re.IGNORECASE,
)

MISTRAL_MICROSERVICE_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_microservice_health",
            "description": "Verifie l'etat du microservice IA (ML, MongoDB, disponibilite).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_calorie_recommendations",
            "description": "Repere calorique journalier personnalise (profil utilisateur connecte).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exercise_recommendations",
            "description": "Liste d'exercices personnalises pour l'utilisateur connecte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_workout_program",
            "description": "Genere un programme d'entrainement complet (seances, calories, objectifs).",
            "parameters": {
                "type": "object",
                "properties": {
                    "objectifs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ex: endurance, perte_de_poids, force, performance.",
                    },
                    "niveau": {"type": "integer", "minimum": 1, "maximum": 5},
                    "equipements": {"type": "array", "items": {"type": "string"}},
                    "limitations": {"type": "array", "items": {"type": "string"}},
                    "disponibilite_minutes": {"type": "integer", "minimum": 15, "maximum": 180},
                    "seances_par_semaine": {"type": "integer", "minimum": 1, "maximum": 7},
                    "longueur_programme_semaines": {"type": "integer", "minimum": 1, "maximum": 52},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_workout_program",
            "description": "Recupere le programme d'entrainement actif de l'utilisateur connecte.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adjust_workout_session",
            "description": "Ajuste la seance courante (fatigue, douleur, duree reduite).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fatigue": {"type": "integer", "minimum": 1, "maximum": 10},
                    "douleur": {"type": "boolean"},
                    "temps_partiel_minutes": {"type": "integer", "minimum": 10, "maximum": 180},
                },
                "required": ["fatigue"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_session_feedback",
            "description": "Enregistre le feedback apres une seance (RPE, exercices valides, ressentis).",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "rpe": {"type": "integer", "minimum": 1, "maximum": 10},
                    "exercices_valides": {"type": "array", "items": {"type": "string"}},
                    "ressentis": {"type": "string"},
                },
                "required": ["session_id", "rpe"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_profile_constraints",
            "description": "Met a jour equipements disponibles et blessures actives du profil.",
            "parameters": {
                "type": "object",
                "properties": {
                    "equipements_dispo": {"type": "array", "items": {"type": "string"}},
                    "blessures_actives": {"type": "array", "items": {"type": "string"}},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profile_history",
            "description": "Historique profil / seances / feedbacks de l'utilisateur connecte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_from": {"type": "string", "description": "ISO 8601 optionnel."},
                    "date_to": {"type": "string", "description": "ISO 8601 optionnel."},
                },
                "required": [],
            },
        },
    },
]


@dataclass
class AgentContext:
    user_id: int
    profile_payload: dict[str, Any]
    objectifs: list[dict[str, Any]] = field(default_factory=list)
    objectifs_microservice: list[str] = field(default_factory=list)


def normalize_objectif_token(value: str) -> str | None:
    key = value.strip().lower().replace("_", " ")
    if key in MICROSERVICE_OBJECTIF_ALIASES:
        return MICROSERVICE_OBJECTIF_ALIASES[key]
    compact = key.replace(" ", "_")
    if compact in MICROSERVICE_OBJECTIF_ALIASES:
        return MICROSERVICE_OBJECTIF_ALIASES[compact]
    if compact in {"endurance", "force", "performance", "perte_de_poids"}:
        return compact
    return None


def objectifs_from_profile(profile_payload: dict[str, Any]) -> list[str]:
    mapping = {
        "perte_de_poids": "perte_de_poids",
        "performance": "performance",
        "endurance": "endurance",
        "force": "force",
    }
    return [token for flag, token in mapping.items() if profile_payload.get(flag)]


def build_objectifs_microservice(objectifs: list[dict[str, Any]], profile_payload: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for row in objectifs:
        statut = str(row.get("statut") or "").lower()
        if statut and statut not in {"en_cours", "encours", "valide"}:
            continue
        for field_name in ("type_objectif", "description"):
            raw = str(row.get(field_name) or "")
            token = normalize_objectif_token(raw)
            if token and token not in tokens:
                tokens.append(token)
    for token in objectifs_from_profile(profile_payload):
        if token not in tokens:
            tokens.append(token)
    return tokens or ["endurance"]


def build_objectifs_context_message(objectifs: list[dict[str, Any]], objectifs_microservice: list[str]) -> str:
    return (
        "Contexte objectifs HealthAI (PostgreSQL + profil):\n"
        f"{json.dumps(objectifs, ensure_ascii=False)}\n"
        f"Objectifs normalises pour le microservice IA: {objectifs_microservice}\n"
        "Utilise ces objectifs pour les tools generate_workout_program et les recommandations. "
        "N'invente jamais de chiffres, exercices ou seances sans appeler un tool."
    )


def detect_required_tools(user_message: str) -> list[str]:
    text = user_message.strip()
    required: list[str] = []
    for tool_name, pattern in REQUIRED_TOOL_PATTERNS.items():
        if pattern.search(text):
            required.append(tool_name)
    if BROAD_RECOMMENDATION_PATTERN.search(text):
        for tool_name in ("get_calorie_recommendations", "get_exercise_recommendations"):
            if tool_name not in required:
                required.append(tool_name)
    return required


def _parse_tool_arguments(raw_arguments: str | None) -> dict[str, Any]:
    if not raw_arguments:
        return {}
    try:
        parsed = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _biometric_profil(context: AgentContext) -> dict[str, Any]:
    sexe = str(context.profile_payload.get("sexe") or "H")
    if sexe not in {"H", "F"}:
        sexe = "H"
    return {
        "age": int(context.profile_payload["age"]),
        "sexe": sexe,
        "taille_cm": float(context.profile_payload["taille_cm"]),
        "poids_kg": float(context.profile_payload["poids_kg"]),
    }


def _build_generate_program_payload(context: AgentContext, args: dict[str, Any]) -> dict[str, Any]:
    objectifs = args.get("objectifs") or context.objectifs_microservice
    if isinstance(objectifs, str):
        objectifs = [objectifs]
    return {
        "user_id": context.user_id,
        "objectifs": list(objectifs),
        "niveau": int(args.get("niveau", context.profile_payload.get("niveau_activite", 2))),
        "equipements": list(args.get("equipements") or []),
        "limitations": list(args.get("limitations") or []),
        "disponibilite_minutes": int(args.get("disponibilite_minutes", 45)),
        "seances_par_semaine": int(args.get("seances_par_semaine", 3)),
        "longueur_programme_semaines": int(args.get("longueur_programme_semaines", 4)),
        "profil": _biometric_profil(context),
    }


def execute_microservice_tool(
    tool_name: str,
    context: AgentContext,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    args = arguments or {}
    try:
        if tool_name == "get_microservice_health":
            return {"status": "ok", "data": call_microservice_ia_health()}
        if tool_name == "get_calorie_recommendations":
            return {"status": "ok", "data": call_microservice_ia_calories(context.profile_payload)}
        if tool_name == "get_exercise_recommendations":
            limit = max(1, min(10, int(args.get("limit", 5))))
            return {"status": "ok", "data": call_microservice_ia_exercises(context.profile_payload, limit=limit)}
        if tool_name == "generate_workout_program":
            payload = _build_generate_program_payload(context, args)
            return {"status": "ok", "data": call_microservice_ia_generate_program(payload)}
        if tool_name == "get_current_workout_program":
            return {"status": "ok", "data": call_microservice_ia_current_program(context.user_id)}
        if tool_name == "adjust_workout_session":
            payload = {
                "user_id": context.user_id,
                "fatigue": int(args["fatigue"]),
                "douleur": bool(args.get("douleur", False)),
            }
            if args.get("temps_partiel_minutes") is not None:
                payload["temps_partiel_minutes"] = int(args["temps_partiel_minutes"])
            return {"status": "ok", "data": call_microservice_ia_adjust_session(payload)}
        if tool_name == "record_session_feedback":
            session_id = str(args["session_id"])
            payload = {
                "user_id": context.user_id,
                "rpe": int(args["rpe"]),
                "exercices_valides": list(args.get("exercices_valides") or []),
                "ressentis": str(args.get("ressentis") or ""),
            }
            return {"status": "ok", "data": call_microservice_ia_session_feedback(session_id, payload)}
        if tool_name == "update_profile_constraints":
            payload = {
                "equipements_dispo": list(args.get("equipements_dispo") or []),
                "blessures_actives": list(args.get("blessures_actives") or []),
            }
            return {
                "status": "ok",
                "data": call_microservice_ia_update_constraints(context.user_id, payload),
            }
        if tool_name == "get_profile_history":
            return {
                "status": "ok",
                "data": call_microservice_ia_profile_history(
                    context.user_id,
                    date_from=args.get("date_from"),
                    date_to=args.get("date_to"),
                ),
            }
    except ExternalServiceError as exc:
        return {"status": "error", "message": str(exc)}
    return {"status": "error", "message": f"Tool inconnu: {tool_name}"}


def merge_tool_result(tool_results: dict[str, Any], tool_name: str, result: dict[str, Any]) -> None:
    if result.get("status") != "ok":
        tool_results.setdefault("errors", []).append({"tool": tool_name, "message": result.get("message")})
        return
    key = TOOL_RESULT_KEYS.get(tool_name, tool_name)
    tool_results[key] = result.get("data")
