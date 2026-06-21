"""Initialisation idempotente de la base MongoDB (index, schéma logique)."""

from __future__ import annotations

from pymongo.database import Database

from app.infrastructure.persistence.mongodb.client import (
    COLLECTION_SESSION_LOGS,
    COLLECTION_USERS,
    COLLECTION_WORKOUT_PLANS,
)


def ensure_indexes(db: Database) -> None:
    """Crée ou vérifie les index requis — safe à relancer (migration / deploy)."""
    db[COLLECTION_USERS].create_index("user_ref", unique=True)
    db[COLLECTION_WORKOUT_PLANS].create_index([("user_ref", 1), ("status", 1)])
    db[COLLECTION_WORKOUT_PLANS].create_index("plan_ref", unique=True)
    db[COLLECTION_SESSION_LOGS].create_index([("user_ref", 1), ("session_date", -1)])
