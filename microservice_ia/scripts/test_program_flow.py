#!/usr/bin/env python3
"""Script de test manuel : création et ajustement d'un programme via l'API v1."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_URL = os.getenv("MICROSERVICE_URL", "http://localhost:8090").rstrip("/")
USER_ID = int(os.getenv("TEST_USER_ID", "42"))
OUTPUT_FILE = Path(
    os.getenv(
        "TEST_OUTPUT_FILE",
        SCRIPT_DIR / f"test_program_flow_result_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json",
    )
)


def pp(title: str, data: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def _parse_response(response: httpx.Response) -> dict | list | str:
    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


def _record_step(
    report: dict,
    name: str,
    method: str,
    path: str,
    response: httpx.Response,
    body: dict | None = None,
    query: dict | None = None,
) -> dict | list | str:
    response_body = _parse_response(response)
    step = {
        "name": name,
        "request": {
            "method": method,
            "url": f"{BASE_URL}{path}",
            "path": path,
            "query": query or {},
            "body": body,
        },
        "response": {
            "status_code": response.status_code,
            "body": response_body,
        },
    }
    report["steps"].append(step)
    return response_body


def _save_report(report: dict) -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)


def main() -> int:
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    report: dict = {
        "meta": {
            "base_url": BASE_URL,
            "user_id": USER_ID,
            "executed_at": datetime.now(UTC).isoformat(),
            "output_file": str(OUTPUT_FILE),
        },
        "steps": [],
        "summary": {},
    }

    print(f"Microservice : {BASE_URL}")
    print(f"Utilisateur  : {USER_ID}")
    print(f"Résultat     : {OUTPUT_FILE}")

    try:
        exit_code = _run(client, report)
    except httpx.ConnectError:
        report["summary"] = {"success": False, "error": f"Connexion refusée : {BASE_URL}"}
        _save_report(report)
        print(
            f"\nImpossible de joindre {BASE_URL}. "
            "Lancez d'abord : uvicorn app.main:app --reload --port 8090",
            file=sys.stderr,
        )
        print(f"Rapport partiel enregistré → {OUTPUT_FILE}", file=sys.stderr)
        return 1

    _save_report(report)
    print(f"\nRapport enregistré → {OUTPUT_FILE}")
    return exit_code


def _run(client: httpx.Client, report: dict) -> int:
    # 1. Santé
    health = client.get("/health")
    health_body = _record_step(report, "Santé du service", "GET", "/health", health)
    if health.status_code != 200:
        report["summary"] = {"success": False, "failed_step": "health"}
        print(f"Erreur health : {health.status_code}", file=sys.stderr)
        return 1
    pp("GET /health", health_body if isinstance(health_body, dict) else {"raw": health_body})

    # 2. Génération du programme
    generate_payload = {
        "user_id": USER_ID,
        "objectifs": ["endurance", "perte_de_poids"],
        "niveau": 3,
        "equipements": ["tapis", "poids_du_corps"],
        "limitations": [],
        "disponibilite_minutes": 45,
        "seances_par_semaine": 3,
        "longueur_programme_semaines": 4,
        "profil": {
            "age": 30,
            "sexe": "H",
            "taille_cm": 180,
            "poids_kg": 75,
        },
    }
    generated = client.post("/api/v1/recommendations/generate", json=generate_payload)
    program = _record_step(
        report,
        "Génération du programme",
        "POST",
        "/api/v1/recommendations/generate",
        generated,
        body=generate_payload,
    )
    if generated.status_code != 200 or not isinstance(program, dict):
        report["summary"] = {"success": False, "failed_step": "generate"}
        print(f"Erreur generate : {generated.status_code}", file=sys.stderr)
        return 1

    console_generate = {
        "id": program["id"],
        "user_id": program["user_id"],
        "longueur_programme_semaines": program["longueur_programme_semaines"],
        "seances_par_semaine": program["seances_par_semaine"],
        "nb_sessions": len(program["sessions"]),
        "calories_recommandees": program["calories_recommandees"],
        "session_courante_id": program["session_courante_id"],
        "premiere_seance": program["sessions"][0] if program["sessions"] else None,
    }
    pp("POST /api/v1/recommendations/generate", console_generate)

    # 3. Récupération du programme actif
    current_query = {"user_id": USER_ID}
    current = client.get("/api/v1/recommendations/current", params=current_query)
    current_body = _record_step(
        report,
        "Programme actif",
        "GET",
        "/api/v1/recommendations/current",
        current,
        query=current_query,
    )
    if current.status_code != 200 or not isinstance(current_body, dict):
        report["summary"] = {"success": False, "failed_step": "current"}
        print(f"Erreur current : {current.status_code}", file=sys.stderr)
        return 1
    pp("GET /api/v1/recommendations/current", {
        "id": current_body["id"],
        "session_courante_id": current_body["session_courante_id"],
        "nb_sessions": len(current_body["sessions"]),
    })

    session_id = program["session_courante_id"]
    session_avant = next(s for s in program["sessions"] if s["id"] == session_id)

    # 4. Ajustement (fatigue élevée + temps partiel)
    adjust_payload = {
        "user_id": USER_ID,
        "fatigue": 8,
        "douleur": False,
        "temps_partiel_minutes": 30,
    }
    adjusted = client.post("/api/v1/recommendations/adjust", json=adjust_payload)
    program_ajuste = _record_step(
        report,
        "Ajustement de séance",
        "POST",
        "/api/v1/recommendations/adjust",
        adjusted,
        body=adjust_payload,
    )
    if adjusted.status_code != 200 or not isinstance(program_ajuste, dict):
        report["summary"] = {"success": False, "failed_step": "adjust"}
        print(f"Erreur adjust : {adjusted.status_code}", file=sys.stderr)
        return 1

    session_apres = next(s for s in program_ajuste["sessions"] if s["id"] == session_id)
    comparison = {
        "session_id": session_id,
        "avant": {
            "titre": session_avant["titre"],
            "duree_minutes": session_avant["duree_minutes"],
            "statut": session_avant["statut"],
            "nb_exercices": len(session_avant["exercices"]),
        },
        "apres": {
            "titre": session_apres["titre"],
            "duree_minutes": session_apres["duree_minutes"],
            "statut": session_apres["statut"],
            "ajustements": session_apres["ajustements"],
            "nb_exercices": len(session_apres["exercices"]),
        },
    }
    report["summary"] = {"success": True, "adjustment_comparison": comparison}
    pp("POST /api/v1/recommendations/adjust", comparison)

    print("\n✓ Test terminé avec succès.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
