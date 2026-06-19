# Modèle de données MongoDB — Microservice IA HealthAI

En tant que base NoSQL, MongoDB utilise des **collections** (au lieu de tables) et permet d'imbriquer les données pour optimiser les performances en lecture.

Le microservice persiste ses données dans **3 collections principales** lorsque `MONGODB_URI` est configuré.

## 1. Collection `users`

Stocke le profil immuable ou à évolution lente de l'utilisateur, ses préférences et ses contraintes matérielles ou médicales.

```json
{
  "_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c001')",
  "user_ref": 42,
  "age": 28,
  "biometrics": {
    "height_cm": 180,
    "weight_kg": 75,
    "sexe": "H"
  },
  "fitness_profile": {
    "level": "intermediaire",
    "health_goal": "prise_muscle"
  },
  "constraints": {
    "equipment_available": ["domicile_equipe", "poids_du_corps"],
    "physical_limitations": ["epaule"]
  },
  "preferences": {
    "preferred_activities": ["musculation", "hiit"],
    "default_duration_min": 60
  },
  "created_at": "2026-01-15T08:00:00Z",
  "updated_at": "2026-06-19T14:00:00Z"
}
```

- `user_ref` : identifiant entier utilisé par l'API (`user_id` / `profile_id`)
- Index unique sur `user_ref`

## 2. Collection `workout_plans`

Stocke les programmes d'entraînement générés par le moteur de recommandation.

```json
{
  "_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c002')",
  "plan_ref": "uuid-du-programme",
  "user_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c001')",
  "user_ref": 42,
  "generated_at": "2026-06-19T14:30:00Z",
  "status": "active",
  "target_goal": "prise_muscle",
  "longueur_programme_semaines": 4,
  "seances_par_semaine": 3,
  "estimated_duration_min": 60,
  "calories_recommandees": 2700,
  "session_courante_id": "uuid-seance-courante",
  "sessions": [
    {
      "session_id": "uuid-seance-1",
      "title": "Semaine 1 — Séance 1",
      "duration_min": 60,
      "status": "planifiee",
      "exercises": [
        {
          "exercise_id": "EXE_109",
          "category": "developpe_poussee",
          "name": "Développé couché haltères",
          "recommended_sets": 4,
          "recommended_reps": 10,
          "rest_seconds": 90
        }
      ]
    }
  ],
  "exercises": []
}
```

- Un seul plan `active` par utilisateur ; les anciens passent en `archived`
- `longueur_programme_semaines × seances_par_semaine` = nombre total de séances générées

## 3. Collection `session_logs`

Historique d'exécution chronologique de chaque séance avec retours en temps réel (fatigue, complétion). Alimente le ré-entraînement du modèle.

```json
{
  "_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c003')",
  "user_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c001')",
  "user_ref": 42,
  "plan_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c002')",
  "session_id": "uuid-seance-1",
  "session_date": "2026-06-19T17:00:00Z",
  "session_timestamp": 1781974800,
  "metrics_before_session": {
    "current_fatigue_rpe": 3,
    "user_reported_injuries": ["epaule"]
  },
  "performance_metrics": {
    "completion_rate": 0.95,
    "calculated_history_score": 14.2
  },
  "actual_workout_done": {
    "activity_type": "musculation",
    "total_sets_completed": 7,
    "post_session_rpe": 7,
    "validated_exercises": ["Squats", "Pompes"],
    "ressentis": "Bonne séance"
  }
}
```

## Configuration

| Variable | Défaut | Description |
|----------|--------|-------------|
| `MONGODB_URI` | *(non défini → mémoire)* | URI de connexion MongoDB |
| `MONGODB_DB` | `healthai_ia` | Nom de la base |

Sans `MONGODB_URI`, le microservice utilise des dépôts **in-memory** (tests et développement local sans Mongo).

## Fichiers implémentation

- `app/infrastructure/persistence/mongodb/client.py` — connexion
- `app/infrastructure/persistence/mongodb/mappers.py` — mapping domaine ↔ documents BSON
- `app/infrastructure/repositories/mongo_repositories.py` — adaptateurs des ports
