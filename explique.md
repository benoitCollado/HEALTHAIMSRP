# Notions et architecture — HealthAI MSPR

## Frontend

### Stack technique
- **Vue 3** — Framework réactif
- **Vue Router 4** — Navigation SPA
- **TypeScript** — Typage statique
- **Vite 5** — Build et dev server

### Architecture utilisée

#### Pas de store centralisé (Pinia / Vuex)
- Aucun store global (Pinia, Vuex)
- État géré par des **services** et **localStorage**

#### Vue Router
- **createWebHistory()** — Mode history (URLs sans `#`)
- **Lazy loading** — `component: () => import('./pages/Connexion.vue')`
- **Navigation guards** — `router.beforeEach()` pour auth et admin
- **Meta** — `requiresAuth`, `requiresAdmin` sur les routes

#### Composition API
- **defineComponent** + **setup()**
- **ref()**, **computed()**, **onMounted()**, **onUnmounted()**
- Pas d'Options API (data, methods, etc.)

#### Composants vs vues (pages)
- **Composants** : `Navbar.vue`, `AppFooter.vue` (réutilisables)
- **Pages / vues** : `Connexion.vue`, `PageAccueil.vue`, `Dashboard.vue`, etc. (routes)

#### Services (couche API)
- **auth.ts** — Login, logout, JWT, localStorage, `isAuthenticated()`, `isAdmin()`
- **api.ts** — Appels API métier (stats, activités, flux, nettoyage)
- **adminApi.ts** — API admin (dashboard, flux, CSV, anomalies, utilisateurs)

#### Gestion de l'état
- **localStorage** — Token JWT (`app_token`), utilisateur (`app_user`)
- **auth.ts** — Singleton partagé entre composants

#### Autres notions
- **Scoped CSS** — Styles limités au composant
- **Props / Emits** — Communication parent ↔ enfant
- **router-link** — Liens de navigation
- **v-model** — Liaison bidirectionnelle
- **Accessibilité** — `aria-label`, `role`, lien d'évitement

---

## Backend

### Stack technique
- **FastAPI** — Framework API REST
- **SQLAlchemy** — ORM
- **Pydantic v2** — Validation et schémas
- **python-jose** — JWT
- **passlib / bcrypt** — Hash des mots de passe
- **Uvicorn** — Serveur ASGI
- **httpx** — Client HTTP (ex. pour Airflow)

### Architecture utilisée

#### Structure en couches
- **Routers** — Endpoints par domaine (`utilisateurs`, `aliments`, `admin`, etc.)
- **Models** — Modèles SQLAlchemy (tables)
- **Schemas** — Schémas Pydantic (entrées/sorties API)
- **database.py** — Connexion, engine, SessionLocal

#### Injection de dépendances
- **Depends()** — `get_db`, `get_current_user`, `require_admin`
- **OAuth2PasswordBearer** — Récupération du token JWT

#### Authentification / autorisation
- **JWT HS256** — Token signé, expiration 8 h
- **OAuth2 Password Flow** — `/login` avec form-urlencoded
- **RBAC** — Rôles `user` et `admin` via `is_admin` dans le token

#### Patterns
- **Repository-like** — Accès BDD via `db.query(Model)`
- **CRUD** — GET, POST, PUT, DELETE par ressource
- **CORS** — Middleware pour le frontend

#### Autres notions
- **APIRouter** — Regroupement des routes par préfixe
- **response_model** — Typage des réponses
- **HTTPException** — Gestion des erreurs 401, 403, 404
- **Session** — Contexte de BDD par requête

---

## Apache Airflow

### Stack technique
- **Apache Airflow 2.10** — Orchestration de pipelines ETL
- **LocalExecutor** — Exécution des tâches dans le même conteneur que le scheduler
- **PostgreSQL** — Métadonnées Airflow (base `postgres_airflow`, distincte de `postgres` HealthAim)
- **PostgresHook** — Connexion à la BDD HealthAim depuis les DAGs
- **Providers** — `apache-airflow-providers-http`, `apache-airflow-providers-postgres`

### Architecture utilisée

#### Services Docker
- **postgres_airflow** — Base métadonnées Airflow (DAGs, runs, logs)
- **airflow-init** — Initialisation unique (`airflow db init`, création user admin)
- **airflow-webserver** — Interface web (port 8080)
- **airflow-scheduler** — Planification et exécution des DAGs
- **export-init** — Création des dossiers `data/` avec permissions 777

#### DAGs (Directed Acyclic Graphs)
- **PythonOperator** — Tâches définies en Python (callables)
- **Schedule** — Cron (`0 * * * *` = toutes les heures, `0 6 * * *` = 6h quotidien)
- **default_args** — `owner`, `retries`, `retry_delay`, `depends_on_past`
- **Chaînage** — `task_import >> task_export` (séquence de tâches)

#### Connexions
- **AIRFLOW_CONN_HEALTHAIM_POSTGRES** — Variable d'environnement → connexion `healthaim_postgres`
- Convention Airflow : `AIRFLOW_CONN_<ID>` crée automatiquement la connexion `<id>` (minuscules)
- Défini dans `docker-compose.yml` pour webserver et scheduler

#### Flux de données (3 DAGs)
1. **fetch_openfoodfacts_france** — API Open Food Facts → `data/intermediate/import/import_YYYYMMDD_HHMMSS.csv` + `.json`
2. **export_db_to_csv** — BDD HealthAim → `data/intermediate/export/export_YYYYMMDD_HHMMSS.csv` + `.json`
3. **incorporation_ml** — CSV validés → BDD (import) + copie vers `data/ml/` (export)

#### Notions
- **Chemin conteneur** — `/opt/airflow/intermediate`, `/opt/airflow/ml`, `/opt/airflow/export` (montés depuis `./data/`)
- **Métadonnées JSON** — Fichier `.json` associé à chaque CSV (statut : `pending`, `validated`, `rejected`, `incorporated`)
- **Validation admin** — Les DAGs écrivent des CSV ; l'admin valide via l'interface ; `incorporation_ml` charge uniquement les `validated`
- **Hostnames fixes** — `airflow-webserver`, `airflow-scheduler` pour la résolution des logs
- **Healthcheck** — `postgres_airflow` avec `pg_isready` pour `depends_on: condition: service_healthy`

---

## Dossier data/

### Structure

```
data/
├── clean/                              # CSV nettoyés (entrée pour seed_db.py)
│   ├── daily_food_nutrition_clean.csv
│   ├── diet_recommendations_clean.csv
│   └── exercise_tracker_clean.csv
├── intermediate/                       # CSV intermédiaires (produits par Airflow)
│   ├── import/                        # Import Open Food Facts
│   │   ├── import_YYYYMMDD_HHMMSS.csv
│   │   └── import_YYYYMMDD_HHMMSS.json
│   └── export/                        # Export BDD
│       ├── export_YYYYMMDD_HHMMSS.csv
│       └── export_YYYYMMDD_HHMMSS.json
├── export/                            # Export journalier (legacy)
├── ml/                                # CSV export validés (usage ML) — chemin local : ./data/ml
├── clean_csv_data.py                  # Nettoyage des CSV sources
├── seed_db.py                         # Import initial vers PostgreSQL
└── *.csv                              # Sources brutes (datasets)
```

### Rôle des scripts

| Script | Rôle |
|--------|------|
| **clean_csv_data.py** | Nettoie les CSV sources → `clean/` |
| **seed_db.py** | Charge `clean/*.csv` → PostgreSQL (utilisateurs, aliments, exercices, activités, consommations) |

### Flux des données

1. **Sources brutes** → `clean_csv_data.py` → **clean/**
2. **clean/** → `seed_db.py` → **PostgreSQL** (import initial)
3. **Airflow fetch** → **intermediate/import/** (CSV + JSON)
4. **Airflow export** → **intermediate/export/** (CSV + JSON)
5. **Admin valide** → statut `validated` dans le JSON
6. **incorporation_ml** → import validés → BDD ; export validés → **ml/**

### Notions data/

- **Chemin sur la machine** — `data/ml/` = `/home/benoit/mspr1/HEALTHAIMSRP/data/ml`
- **Chemin dans le conteneur Airflow** — `/opt/airflow/ml` (monté depuis `./data/ml`)
- **Volume Docker** — `./data:/data` pour le backend ; `./data/intermediate`, `./data/export`, `./data/ml` pour Airflow
- **DATA_DIR** — Variable d'environnement backend pointant vers `/data` (ou `./data` en local)
