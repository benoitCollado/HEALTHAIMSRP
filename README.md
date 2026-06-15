# HealthAI MSPR

HealthAI MSPR est une plateforme full-stack de suivi santé et d'administration de flux de données. Le projet couvre la gestion des utilisateurs, des aliments, des exercices, des consommations, des activités, des métriques santé et des objectifs, avec une API sécurisée, une interface Vue, des pipelines Airflow, une base PostgreSQL managée et une couche d'observabilité.

## Architecture

```text
Navigateur / mobile Capacitor
        |
        v
Frontend Vue 3 + TypeScript servi par Nginx
        |
        v
API FastAPI / Python 3.11
        |
        v
PostgreSQL Neon + migrations Alembic
MiniIO pour le stockage objet des images Chat IA

Airflow orchestre les flux de données et écrit dans les dossiers data/.
Prometheus, Grafana, Loki et Promtail assurent le monitoring et les logs.
```

## Technologies utilisées

| Domaine | Technologies |
| --- | --- |
| Frontend web | Vue 3, TypeScript, Vite, Vue Router 4, CSS, Nginx |
| Mobile | Capacitor 8, Android Gradle, iOS Xcode/Swift |
| Backend | Python 3.11, FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-jose |
| Sécurité | JWT Bearer, passlib/bcrypt, middleware d'en-têtes HTTP, CORS, variables `.env` |
| Base de données | PostgreSQL Neon, Alembic, psycopg2 |
| Stockage objet | MiniIO compatible S3 pour les images utilisateur du Chat IA |
| Données / ETL | Apache Airflow 2.10.4, pandas, requests, DAGs Python, CSV |
| Observabilité | Logs applicatifs, endpoint `/health`, endpoint admin `/metrics`, alertes email SMTP |
| Monitoring infra | Prometheus, Grafana, Loki, Promtail, Node Exporter, Blackbox Exporter |
| Conteneurisation | Docker, Docker Compose, images Python slim, Node Alpine et Nginx |
| Tests | pytest, pytest-cov, Vitest, Vue Test Utils, jsdom, coverage V8 |
| Qualité / CI | Ruff, ESLint, SonarQube, GitHub Actions |

## Structure du dépôt

```text
backend/        API FastAPI, modèles SQLAlchemy, routers, migrations Alembic, tests
Frontend/       Application Vue 3, configuration Vite, tests Vitest, builds web/mobile
airflow/        DAGs d'import, d'export et d'incorporation ML
database/       Scripts SQL d'initialisation et données de démonstration
data/           Données brutes, intermédiaires, exports, logs et fichiers ML
monitoring/     Configuration Prometheus, Grafana, Loki et Promtail
docs/           Documentation technique, déploiement et Airflow
scripts/        Scripts de déploiement et utilitaires SQL
.github/        Pipeline GitHub Actions CI/CD
```

## Fonctionnalités principales

- Authentification par JWT et rôles utilisateur/admin.
- Inscription utilisateur avec adresse email obligatoire et unique.
- API REST avec endpoints pour utilisateurs, aliments, exercices, consommations, activités, métriques santé et objectifs.
- Chat IA Mistral avec possibilité de joindre des images stockées dans MiniIO par utilisateur.
- Dashboard d'administration et pages de gestion des flux.
- Nettoyage et validation des données via pipelines Airflow.
- Migrations versionnées avec Alembic.
- Journalisation backend, alertes email sur erreurs 500 et métriques internes.
- Monitoring optionnel avec Grafana, Prometheus, Loki, Promtail et exporters.
- Tests automatisés backend et frontend, linting et analyse SonarQube en CI.

## Prérequis

- Docker et Docker Compose
- Node.js 22 pour le développement frontend local
- Python 3.11 pour le développement backend local
- Une base PostgreSQL Neon ou compatible PostgreSQL

Copier le fichier d'exemple puis renseigner les secrets :

```bash
cp .env.example .env
```

Variables minimales :

```env
DATABASE_URL=postgresql://<user>:<password>@<host>.neon.tech/<dbname>?sslmode=require&channel_binding=require
SECRET_KEY=<cle-secrete-longue-et-aleatoire>
API_ROOT_PATH=/api
VITE_API_URL=/api
CORS_ALLOWED_ORIGINS=http://localhost:89,http://127.0.0.1:89,https://healthai.benoitcollado.com
GRAFANA_ADMIN_PASSWORD=<mot-de-passe-grafana>
MINIO_ACCESS_KEY=healthai_app
MINIO_SECRET_KEY=<mot-de-passe-minio>
MINIO_BUCKET=healthai-chat-images
MINIO_PUBLIC_ENDPOINT=127.0.0.1:9100
```

`CORS_ALLOWED_ORIGINS` contient les origines frontend autorisees, separees par des virgules. En production, utiliser l'origine du site sans `/api` ni slash final, par exemple `https://healthai.benoitcollado.com`.

Les variables SMTP (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `ADMIN_EMAIL`) activent les alertes email sur erreurs 5xx. Un 403 isole n'envoie pas d'email; une rafale de 403 pour le meme client/utilisateur declenche une alerte securite selon `ERROR_ALERT_403_THRESHOLD`, `ERROR_ALERT_403_WINDOW_SECONDS` et `ERROR_ALERT_403_COOLDOWN_SECONDS`.

## Démarrage avec Docker

```bash
docker compose up -d --build
docker compose up -d --build backend frontend
docker compose logs -f backend
```

Services exposés par défaut :

| Service | URL |
| --- | --- |
| Frontend | http://localhost:89 |
| API via Nginx | http://localhost:89/api |
| Swagger / OpenAPI | http://localhost:89/api/docs |
| Backend direct | http://localhost:8089 |
| Airflow | http://localhost:8080 |
| MiniIO API | http://localhost:9100 |
| MiniIO Console | http://localhost:9101 |

Identifiants Airflow par défaut : `airflow` / `airflow`.
Identifiants MiniIO : valeurs de `MINIO_ACCESS_KEY` et `MINIO_SECRET_KEY` dans `.env`.

Les images jointes au Chat IA sont stockées dans le bucket `MINIO_BUCKET`, avec un préfixe par utilisateur :

```text
users/{id_utilisateur}/chat/{uuid}.{extension}
```

Import des données de départ :

```bash
docker compose --profile seed run --rm seed
```

## Monitoring

Le monitoring infra est séparé dans `docker-compose.monitoring.yml`. Il utilise le réseau Docker créé par le compose principal.

```bash
docker compose up -d
docker compose -f docker-compose.monitoring.yml up -d
```

Services monitoring :

| Service | URL par défaut | Rôle |
| --- | --- | --- |
| Grafana | http://localhost:3000 | Visualisation Prometheus/Loki |
| Prometheus | http://localhost:9090 | Collecte de métriques |
| Loki | http://localhost:3100 | Stockage des logs |
| Node Exporter | http://localhost:9100 | Métriques système |
| Blackbox Exporter | http://localhost:9115 | Sondes HTTP frontend/backend |

## Développement local

Backend :

```bash
cd backend
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8089
```

En développement local hors Docker, le backend attend un service MiniIO joignable via `MINIO_ENDPOINT`.

Frontend :

```bash
cd Frontend
npm ci
npm run dev
```

Le serveur Vite proxy les appels `/api` vers `http://localhost:8089`.

## Tests et qualité

Backend :

```bash
cd backend
python -m pytest
ruff check app migrations ../airflow/dags
ruff format --check app migrations ../airflow/dags
```

Frontend :

```bash
cd Frontend
npm run lint
npm run test:coverage
npm run build
```

La CI GitHub Actions lance les tests backend, les tests frontend, le build Vite, Ruff, ESLint, puis l'analyse SonarQube et le déploiement SSH sur `main`.

## Documentation

- [Documentation technique](docs/documentation_technique.html)
- [Documentation CI/CD](CICD.md)
- [Guide Airflow](docs/AIRFLOW.md)
- [Guide de déploiement](docs/GUIDE_DEPLOIEMENT.md)
- [Rapport technique](docs/RAPPORT_TECHNIQUE.md)
- [Backend](backend/README.md)
- [Frontend](Frontend/README.md)
- [Base de données](database/README.md)

## Sécurité

- Les secrets restent dans `.env` et ne doivent pas être versionnés.
- `DATABASE_URL` pointe vers PostgreSQL Neon en production.
- Les tokens JWT sont signés avec `SECRET_KEY`.
- Les erreurs 500 non gérées sont journalisées et peuvent déclencher une alerte email.
- Les en-têtes HTTP de sécurité sont ajoutés par middleware backend.
