# Microservice IA — HealthAI

Microservice FastAPI dédié aux **recommandations caloriques**, **d'exercices** et **de programmes d'entraînement personnalisés**. Il suit une **Clean Architecture** : le domaine et les cas d'usage restent indépendants de FastAPI et de MongoDB.

## Rôle dans l'écosystème HealthAI

| Composant | Rôle |
|-----------|------|
| Backend principal (`backend/`) | Auth JWT, CRUD utilisateurs/aliments/exercices, Chat Mistral |
| **Microservice IA** (`microservice_ia/`) | Génération de programmes, ajustement de séances, feedback RPE, profil contraintes |
| Frontend | Affichage profil, calories (Mifflin-St Jeor aligné), consommation API |

Le calcul calorique du microservice reprend la même formule que `Frontend/src/services/calorieCalculator.ts`.

## Architecture

```text
microservice_ia/
├── app/
│   ├── domain/              # Entités + ports (interfaces)
│   ├── application/         # Cas d'usage
│   ├── infrastructure/      # Adaptateurs + dépôts
│   │   ├── adapters/        # Mifflin, exercices rule-based, générateur de programmes
│   │   ├── persistence/
│   │   │   └── mongodb/     # Client, mappers BSON
│   │   └── repositories/    # In-memory ou MongoDB
│   ├── presentation/        # Routes FastAPI, schémas Pydantic
│   └── main.py
├── docs/
│   └── mongodb_schema.md    # Schéma des 3 collections MongoDB
└── tests/
```

| Couche | Contenu |
|--------|---------|
| **Domain** | `UserProfile`, `WorkoutProgram`, `WorkoutSession`, ports `ProgramGeneratorPort`, `ProgramRepositoryPort`, `ProfileRepositoryPort` |
| **Application** | `GenerateProgramUseCase`, `AdjustSessionUseCase`, `RecordSessionFeedbackUseCase`, … |
| **Infrastructure** | `MifflinCalorieRecommender`, `RuleBasedExerciseRecommender`, `CompositeProgramGenerator`, dépôts MongoDB ou mémoire |
| **Presentation** | Routes `/api/v1/*` + routes legacy `/recommandation_*` |

## Démarrage

```bash
cd microservice_ia
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

Documentation interactive : http://localhost:8090/docs

## API v1 — Recommandations & Profil

| Méthode | Route | Description | Données clés |
|---------|-------|-------------|--------------|
| `POST` | `/api/v1/recommendations/generate` | Programme complet sur-mesure | objectifs, niveau, équipements, limitations, dispo, **longueur** |
| `GET` | `/api/v1/recommendations/current` | Programme actif | `user_id` (query) |
| `POST` | `/api/v1/recommendations/adjust` | Ajuste la séance immédiate | user_id, fatigue, douleur, temps partiel |
| `POST` | `/api/v1/recommendations/sessions/{id}/feedback` | Retour post-séance | RPE (1–10), exercices validés, ressentis |
| `PUT` | `/api/v1/profiles/{id}/constraints` | Matériel et restrictions médicales | équipements, blessures |
| `GET` | `/api/v1/profiles/{id}/history` | Historique performances | `user_id`, filtres `date_from` / `date_to` |

### Génération de programme

Le nombre total de séances produites est :

```text
longueur_programme_semaines × seances_par_semaine
```

Chaque séance est nommée `Semaine N — Séance M`.

**Corps de la requête (`POST /api/v1/recommendations/generate`)**

| Champ | Type | Description |
|-------|------|-------------|
| `user_id` | int | Identifiant utilisateur |
| `objectifs` | string[] | Ex. `endurance`, `perte_de_poids`, `force`, `performance` |
| `niveau` | int (1–5) | Niveau d'activité |
| `equipements` | string[] | Matériel disponible |
| `limitations` | string[] | Blessures ou restrictions |
| `disponibilite_minutes` | int (15–180) | Durée d'une séance |
| `seances_par_semaine` | int (1–7) | Fréquence hebdomadaire |
| `longueur_programme_semaines` | int (1–52) | Durée totale du programme en semaines |
| `profil` | object (optionnel) | `age`, `sexe` (`H`/`F`), `taille_cm`, `poids_kg` pour le calcul calorique |

```bash
curl -X POST http://localhost:8090/api/v1/recommendations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "objectifs": ["endurance", "perte_de_poids"],
    "niveau": 3,
    "equipements": ["tapis"],
    "limitations": [],
    "disponibilite_minutes": 45,
    "seances_par_semaine": 3,
    "longueur_programme_semaines": 4,
    "profil": {
      "age": 30,
      "sexe": "H",
      "taille_cm": 180,
      "poids_kg": 75
    }
  }'
```

Réponse (extrait) : programme avec `longueur_programme_semaines`, `seances_par_semaine`, `calories_recommandees`, `sessions[]`, `session_courante_id`.

### Ajustement de séance

```bash
curl -X POST http://localhost:8090/api/v1/recommendations/adjust \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "fatigue": 8,
    "douleur": false,
    "temps_partiel_minutes": 30
  }'
```

Réduit volume et durée si fatigue élevée ; bascule vers exercices doux en cas de douleur.

### Feedback post-séance

```bash
curl -X POST http://localhost:8090/api/v1/recommendations/sessions/{session_id}/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "rpe": 7,
    "exercices_valides": ["Marche rapide", "Squats"],
    "ressentis": "Bonne séance, un peu essoufflé."
  }'
```

### Contraintes profil

```bash
curl -X PUT http://localhost:8090/api/v1/profiles/1/constraints \
  -H "Content-Type: application/json" \
  -d '{
    "equipements_dispo": ["haltères", "tapis"],
    "blessures_actives": ["genou"]
  }'
```

## Routes legacy (v0)

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/health` | Santé du microservice |
| `POST` | `/recommandation_calorique` | Calories journalières (Mifflin-St Jeor) |
| `POST` | `/recommandation_exercice` | Exercices recommandés (rule-based) |

## Persistance MongoDB

Sans base externe, les données sont stockées **en mémoire** (tests et dev local). Avec MongoDB, le microservice utilise **3 collections** :

| Collection | Rôle |
|------------|------|
| `users` | Profil, biométrie, contraintes matérielles/médicales, préférences |
| `workout_plans` | Programmes générés avec séances et exercices imbriqués |
| `session_logs` | Historique d'exécution (RPE, complétion, ressentis) pour ré-entraînement |

Schéma détaillé avec exemples JSON : [`docs/mongodb_schema.md`](docs/mongodb_schema.md)

Documentation technique complète (architecture, flux, ML, tests) : [`docs/DOCUMENTATION_TECHNIQUE.md`](docs/DOCUMENTATION_TECHNIQUE.md)

```bash
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DB="healthai_ia"
uvicorn app.main:app --reload --port 8090
```

Un seul plan `active` est conservé par utilisateur ; les anciens passent en `archived`.

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `API_ROOT_PATH` | *(vide)* | Préfixe public derrière un reverse proxy |
| `MONGODB_URI` | *(vide → mémoire)* | URI de connexion MongoDB |
| `MONGODB_DB` | `healthai_ia` | Nom de la base MongoDB |
| `ML_MODEL_PATH` | `models/workout_rf_bundle.pkl` | Chemin du modèle Random Forest |
| `ML_ENABLED` | `auto` | `auto` (charge le .pkl s'il existe), `true` (obligatoire), `false` (rule-based) |

## Machine Learning — Random Forest

Pipeline complet pour entraîner et servir un modèle `.pkl` :

```text
ml/
├── generate_training_data.py   # Dataset synthétique (1500 sessions)
├── train_random_forest.py      # Entraînement + export bundle
└── data/                       # CSV généré (gitignored)
models/
└── workout_rf_bundle.pkl       # Classifier activité + regressor séries
```

### 1. Générer les données

```bash
cd microservice_ia
python -m ml.generate_training_data
```

Produit `ml/data/microservice_workout_training_data.csv` (profil utilisateur, fatigue RPE, objectifs, labels activité/séries).

### 2. Entraîner le modèle

```bash
python -m ml.train_random_forest
```

Exporte `models/workout_rf_bundle.pkl` contenant :

| Composant | Rôle |
|-----------|------|
| `classifier` | RandomForestClassifier → activité (`musculation`, `running`, `hiit`, `pilates`) |
| `regressor` | RandomForestRegressor → nombre de séries (2–6) |
| `encoders` | LabelEncoder par feature catégorielle |
| `feature_columns` | Ordre des colonnes pour l'inférence |

### 3. Inférence via l'API

Dès que le `.pkl` est présent, le microservice bascule automatiquement (`ML_ENABLED=auto`) :

- `POST /recommandation_exercice` — exercices prédits par le modèle
- `POST /api/v1/recommendations/generate` — programme complet avec séries ML

Vérification : `GET /health` retourne `"ml_engine": "loaded"`.

```bash
export ML_ENABLED=auto
uvicorn app.main:app --reload --port 8090
```

Forcer le mode rule-based : `ML_ENABLED=false`.

### Test manuel du flux programme

Avec le microservice lancé sur le port 8090 :

```bash
python scripts/test_program_flow.py
# ou : MICROSERVICE_URL=http://localhost:8090 TEST_USER_ID=1 python scripts/test_program_flow.py
```

Le script enchaîne : `GET /health` → génération → récupération du programme actif → ajustement de séance.
Il enregistre un rapport JSON dans `scripts/test_program_flow_result_<timestamp>.json` avec chaque requête (méthode, URL, body/query) et la réponse complète.

Variable optionnelle : `TEST_OUTPUT_FILE` pour fixer le chemin du fichier de sortie.

## Tests

```bash
cd microservice_ia
pip install -r requirements.txt
pytest
```

Les tests utilisent les dépôts in-memory (pas de MongoDB requis). Les tests ML entraînent le modèle automatiquement si le `.pkl` est absent.

## Évolutions prévues

- Branchement du backend principal vers ce microservice (proxy ou appels HTTP internes)
- Intégration Docker Compose avec service MongoDB dédié
- Ré-entraînement périodique depuis `session_logs` MongoDB
