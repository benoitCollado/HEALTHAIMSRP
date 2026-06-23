"""Agent Chat IA — détection d'intention et appel au microservice IA."""

from __future__ import annotations

import json
import re
from typing import Any

from app.external_clients import (
    ExternalServiceError,
    call_microservice_ia_recommendations,
)

_MICROSERVICE_INTENT_PATTERN = re.compile(
    r"\b("
    r"calor(?:ie|ies|ique)|kcal|metabolisme|"
    r"exercice|entrainement|entraînement|programme|sport|musculation|running|hiit|pilates|"
    r"recommand(?:ation|ations|e|es|er)|conseil(?:s)?|"
    r"perte(?:\s+de)?\s+poids|endurance|force|activit(?:e|é)\s+physique|"
    r"seance|séance|workout|entrain(?:er|e)"
    r")\b",
    re.IGNORECASE,
)


def should_call_microservice_ia(message: str) -> bool:
    """True si le message utilisateur demande calories / exercices / recommandations."""
    return bool(_MICROSERVICE_INTENT_PATTERN.search(message.strip()))


def fetch_microservice_recommendations(profile_payload: dict[str, Any]) -> dict[str, Any] | None:
    """Appelle le microservice IA ; retourne None si indisponible."""
    try:
        return call_microservice_ia_recommendations(profile_payload)
    except ExternalServiceError:
        return None


def build_microservice_system_context(recommendation: dict[str, Any]) -> str:
    """Contexte injecté à Mistral avec les données du microservice."""
    return (
        "Donnees du microservice IA HealthAI (recommandations personnalisees calculees pour "
        "l'utilisateur connecte, a partir de son profil):\n"
        f"{json.dumps(recommendation, ensure_ascii=False)}\n\n"
        "Instructions: utilise ces donnees pour repondre en francais. Cite le repere calorique "
        "et les exercices concrets (noms, justification si disponible). Reste concis. "
        "Rappelle que ce sont des indications informatives, pas un avis medical."
    )


def build_microservice_degraded_context() -> str:
    return (
        "Le microservice IA (calories / exercices) est temporairement indisponible. "
        "Reponds sans inventer de chiffres personnalises ; propose des conseils generaux "
        "ou suggere de reessayer plus tard."
    )
