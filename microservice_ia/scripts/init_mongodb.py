#!/usr/bin/env python3
"""Ping MongoDB et applique les index (migration idempotente)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Racine microservice_ia (parent de scripts/) — requis hors pytest / Docker WORKDIR
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> int:
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        print("MONGODB_URI non défini — initialisation MongoDB ignorée.")
        return 0

    from app.infrastructure.persistence.mongodb.client import get_database, get_mongo_client
    from app.infrastructure.persistence.mongodb.init_db import ensure_indexes

    db_name = os.getenv("MONGODB_DB", "healthai_ia")
    print(f"==> Connexion MongoDB ({db_name})...")
    client = get_mongo_client()
    client.admin.command("ping")

    db = get_database()
    ensure_indexes(db)
    collections = sorted(db.list_collection_names())
    print(f"==> MongoDB prêt — index vérifiés, collections : {collections or '(aucune encore)'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Erreur initialisation MongoDB : {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
