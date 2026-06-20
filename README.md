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
Redis pour la limitation de charge et le cache intelligent

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
| Résilience / charge | Redis, cache intelligent, rate limiting FastAPI, retries, timeouts, circuit breaker, fallbacks applicatifs |
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
- Profil utilisateur enrichi avec objectifs personnels : reduction du stress, sante generale, perte de poids, performance sportive, endurance et force musculaire.
- Estimation des calories recommandees du jour dans les informations personnelles, calculee depuis le profil utilisateur, le niveau d'activite et les objectifs.
- API REST avec endpoints pour utilisateurs, aliments, exercices, consommations, activités, métriques santé et objectifs.
- Chat IA Mistral avec possibilité de joindre des images stockées dans MiniIO par utilisateur, retries et réponse de secours si l'API externe est indisponible.
- Routes Chat IA dédiées aux microservices : recommandations personnalisées via `microservice_ia` et analyse photo via le microservice de traitement d'image.
- Dashboard d'administration et pages de gestion des flux.
- Gestion robuste des APIs externes Mistral et Airflow : timeouts, retries, circuit breaker et mode dégradé.
- Rate limiting Redis par IP/utilisateur, avec seuils spécifiques pour `/login` et `/chat`.
- Cache Redis intelligent pour les données Airflow : TTL court, cache de secours plus long et restitution de données `stale` si Airflow tombe.
- Cache Redis court pour le Chat IA et les URLs/métadonnées images MiniIO, plafonné à 3 minutes pour limiter les appels répétitifs sans conserver longtemps de données utilisateur.
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
MINIO_PUBLIC_ENDPOINT=127.0.0.1:19100
MICROSERVICE_IA_URL=http://microservice_ia:8090
MICROSERVICE_IA_TIMEOUT_SECONDS=10
PHOTO_PROCESSING_API_URL=http://microservice_photo:8000/analyze
PHOTO_PROCESSING_TIMEOUT_SECONDS=20
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_ENABLED=true
CACHE_ENABLED=true
AIRFLOW_CACHE_TTL_SECONDS=60
AIRFLOW_STALE_CACHE_TTL_SECONDS=900
CHAT_CACHE_TTL_SECONDS=120
MINIO_IMAGE_CACHE_TTL_SECONDS=180
```

`CORS_ALLOWED_ORIGINS` contient les origines frontend autorisees, separees par des virgules. En production, utiliser l'origine du site sans `/api` ni slash final, par exemple `https://healthai.benoitcollado.com`.

Les variables SMTP (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `ADMIN_EMAIL`) activent les alertes email sur erreurs 5xx. Un 403 isole n'envoie pas d'email; une rafale de 403 pour le meme client/utilisateur declenche une alerte securite selon `ERROR_ALERT_403_THRESHOLD`, `ERROR_ALERT_403_WINDOW_SECONDS` et `ERROR_ALERT_403_COOLDOWN_SECONDS`.

Les variables de résilience externe (`EXTERNAL_API_MAX_RETRIES`, `EXTERNAL_API_RETRY_DELAY_SECONDS`, `EXTERNAL_API_CIRCUIT_FAILURES`, `EXTERNAL_API_CIRCUIT_RECOVERY_SECONDS`, `MISTRAL_TIMEOUT_SECONDS`) pilotent les appels Mistral, Airflow et microservices IA. En cas de panne Mistral, le chat renvoie une réponse de continuité de service; en cas de panne Airflow, `/admin/flux` retourne un état `airflow_status=degraded`.

`MICROSERVICE_IA_URL` pointe vers le service de recommandations calories/exercices. `PHOTO_PROCESSING_API_URL` pointe vers l'URL complète du endpoint d'analyse photo.

Le rate limiting Redis est activé par défaut avec `RATE_LIMIT_ENABLED=true`. Les seuils principaux sont `RATE_LIMIT_DEFAULT_LIMIT`, `RATE_LIMIT_LOGIN_LIMIT` et `RATE_LIMIT_CHAT_LIMIT`, chacun associé à une fenêtre en secondes. Si Redis est temporairement indisponible, le middleware laisse passer la requête et journalise l'incident afin de ne pas couper le service.

Le cache intelligent Redis est activé par `CACHE_ENABLED=true`. Les runs Airflow sont mis en cache avec `AIRFLOW_CACHE_TTL_SECONDS`; une copie de secours est conservée plus longtemps via `AIRFLOW_STALE_CACHE_TTL_SECONDS` pour continuer à afficher les flux admin en cas de panne Airflow. Le Chat IA utilise `CHAT_CACHE_TTL_SECONDS` pour réutiliser brièvement une réponse identique du même utilisateur. Les URLs et métadonnées images MiniIO utilisent `MINIO_IMAGE_CACHE_TTL_SECONDS`, plafonné à 180 secondes maximum.

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
| Microservice IA | http://localhost:8090 |
| Microservice photo | http://localhost:8001 |
| Airflow | http://localhost:8080 |
| MiniIO API | http://localhost:19100 |
| MiniIO Console | http://localhost:19101 |
| Redis | interne Docker, `redis:6379` |

Identifiants Airflow par défaut : `airflow` / `airflow`.
Identifiants MiniIO : valeurs de `MINIO_ACCESS_KEY` et `MINIO_SECRET_KEY` dans `.env`.

Les images jointes au Chat IA sont stockées dans le bucket `MINIO_BUCKET`, avec un préfixe par utilisateur :

```text
users/{id_utilisateur}/chat/{uuid}.{extension}
```

Avant stockage, le backend redimensionne les images à 640 x 640 pixels maximum et les convertit en JPEG optimisé.
Les URLs présignées et métadonnées d'image sont mises en cache Redis pendant 3 minutes maximum afin d'éviter des appels MiniIO répétés tout en gardant une durée courte pour les données utilisateur.

## Chat IA et microservices

Le module Chat IA expose plusieurs routes protégées par JWT :

| Route | Usage |
| --- | --- |
| `POST /chat/` | Conversation HealthAI via Mistral avec historique court et images déjà uploadées. |
| `POST /chat/images` | Upload d'une image utilisateur vers MiniIO sous `users/{id_utilisateur}/chat/`. |
| `POST /chat/recommendations` | Récupère le profil de l'utilisateur connecté et appelle `microservice_ia` pour la recommandation calorique et les exercices. |
| `POST /chat/images/analyze` | Vérifie que l'image appartient à l'utilisateur, génère une URL présignée MiniIO et transmet la photo au microservice de traitement d'image. |

`/chat/recommendations` appelle les endpoints legacy du microservice IA :
`/recommandation_calorique` et `/recommandation_exercice`.
La réponse contient un texte prêt à afficher dans Chat IA (`answer`) et les données brutes du microservice (`recommendation`).

`/chat/images/analyze` attend une image déjà envoyée par `/chat/images` :

```json
{
  "image": {
    "object_key": "users/1/chat/uuid.jpg",
    "filename": "repas.jpg"
  },
  "question": "Analyse mon repas"
}
```

La réponse contient `answer` pour le chat et `analysis` avec la réponse complète du microservice photo.

Import des données de départ :

```bash
docker compose --profile seed run --rm seed
```

Appliquer les migrations sur la base Docker locale :

```bash
docker compose up -d --build postgres backend
docker exec backend_api alembic upgrade head
docker exec backend_api alembic current
```

La migration `0004` ajoute les preferences/objectifs booleens de la table `utilisateurs` :
`destresse`, `sante`, `perte_de_poids`, `performance`, `endurance`, `force`.

## Calcul calories recommandees

La page utilisateur `Informations personnelles` affiche une estimation des calories recommandees pour la journee.
Le calcul est realise cote frontend dans `Frontend/src/pages/PageAccueil.vue`.

1. Metabolisme de base, formule Mifflin-St Jeor :
   `10 * poids_kg + 6.25 * taille_cm - 5 * age + ajustement_sexe`
   avec `+5` pour `H`, `-161` pour `F` et `-78` pour autre/non renseigne.
2. Multiplication par le niveau d'activite :
   `1 = 1.2`, `2 = 1.375`, `3 = 1.55`, `4 = 1.725`, `5 = 1.9`.
3. Ajustement objectif :
   `perte_de_poids = -400 kcal`, `performance` ou `force = +250 kcal`, `endurance = +150 kcal`, sinon `0`.

Le resultat est arrondi au multiple de 50 kcal le plus proche, avec un minimum de `1200 kcal` pour `F` et `1500 kcal` sinon.
Cette valeur reste une estimation indicative, pas une recommandation medicale.

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
- Les routes sont protégées par un rate limiting Redis configurable; `/health` reste exclu pour les sondes de disponibilité.
