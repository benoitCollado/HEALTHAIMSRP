# Guide de déploiement – HealthAI Coach

Ce guide permet à toute équipe technique de reproduire l’environnement et de lancer la solution en **moins de trente minutes**.

---

## 1. Prérequis logiciels

| Logiciel | Version minimale | Vérification |
|----------|------------------|--------------|
| **Docker** | 20.10+ | `docker --version` |
| **Docker Compose** | 2.0+ (plugin ou standalone) | `docker compose version` |
| **Git** | 2.x | `git --version` |

### Installation rapide

- **Linux (Ubuntu/Debian)** : `sudo apt update && sudo apt install docker.io docker-compose-plugin git`
- **macOS** : [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Windows** : [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## 2. Variables d’environnement

### 2.1 Fichier `.env`

À la **racine du projet**, créer un fichier `.env` (ou copier `.env.example` s’il existe) :

```env
# Base de données PostgreSQL (HealthAim)
POSTGRES_PORT=127.0.0.1:5435

# Backend API
BACKEND_PORT=127.0.0.1:8089
SECRET_KEY=healthaim-secret-key-dev-change-in-production

# Backend → Airflow (pour afficher les flux ETL dans l'admin)
AIRFLOW_API_URL=http://airflow-webserver:8080
AIRFLOW_USER=airflow
AIRFLOW_PASSWORD=airflow

# Frontend
FRONTEND_PORT=127.0.0.1:89
VITE_API_URL=
VITE_AIRFLOW_UI_URL=http://localhost:8080

# Airflow (localhost uniquement)
AIRFLOW_PORT=127.0.0.1:8080
AIRFLOW_UID=50000
AIRFLOW_SECRET_KEY=healthaim-airflow-secret-key-dev
```

### 2.2 Description des variables

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `POSTGRES_PORT` | Port d’écoute PostgreSQL (hôte:conteneur) | `127.0.0.1:5435:5432` |
| `BACKEND_PORT` | Port de l’API FastAPI | `127.0.0.1:8089:8000` |
| `FRONTEND_PORT` | Port de l’interface web | `127.0.0.1:89:80` |
| `AIRFLOW_PORT` | Port de l'interface Airflow (localhost uniquement) | `127.0.0.1:8080` |
| `SECRET_KEY` | Clé secrète JWT (à changer en production) | `healthaim-secret-key-dev-change-in-production` |
| `VITE_API_URL` | URL de l’API pour le frontend (vide = proxy nginx) | Vide (même origine) |
| `VITE_AIRFLOW_UI_URL` | URL de l'interface Airflow (liens « Voir dans Airflow ») | `http://localhost:8080` |
| `AIRFLOW_API_URL` | URL de l'API Airflow (backend → Airflow) | `http://airflow-webserver:8080` |
| `AIRFLOW_USER` | Utilisateur Airflow pour l'API | `airflow` |
| `AIRFLOW_PASSWORD` | Mot de passe Airflow pour l'API | `airflow` |

> **Sécurité** : Tous les ports sont liés à `127.0.0.1` (localhost uniquement) pour éviter l'accès depuis le réseau.
> **Production** : Modifier `SECRET_KEY`, les mots de passe PostgreSQL et Airflow.

---

## 3. Procédure de déploiement (< 30 min)

### Étape 1 : Cloner le projet (1 min)

```bash
git clone <url-du-depot> HEALTHAIMSRP
cd HEALTHAIMSRP
```

### Étape 2 : Créer le fichier `.env` (1 min)

```bash
cat > .env << 'EOF'
POSTGRES_PORT=127.0.0.1:5435
BACKEND_PORT=127.0.0.1:8089
FRONTEND_PORT=127.0.0.1:89
AIRFLOW_PORT=127.0.0.1:8080
SECRET_KEY=healthaim-secret-key-dev-change-in-production
VITE_API_URL=
VITE_AIRFLOW_UI_URL=http://localhost:8080
AIRFLOW_API_URL=http://airflow-webserver:8080
AIRFLOW_USER=airflow
AIRFLOW_PASSWORD=airflow
AIRFLOW_UID=50000
AIRFLOW_SECRET_KEY=healthaim-airflow-secret-key-dev
EOF
```

### Étape 3 : Démarrer PostgreSQL (2 min)

```bash
docker compose up -d postgres
```

Attendre que PostgreSQL soit prêt :

```bash
sleep 10
docker exec postgres_health pg_isready -U healthuser -d healthdb
```

### Étape 4 : Préparer les données nettoyées (2 min)

Si le dossier `data/clean/` n’existe pas :

```bash
cd data
python3 clean_csv_data.py
cd ..
```

> Si Python/pandas n’est pas installé localement, les fichiers `data/clean/*.csv` doivent déjà exister dans le dépôt.

### Étape 5 : Démarrer l’application (backend + frontend) (5 min)

```bash
docker compose build backend frontend
docker compose up -d backend frontend
```

Le backend exécute automatiquement au démarrage :
1. `seed_db.py` (import des CSV vers PostgreSQL)
2. `create_admin.py` (création du compte admin)
3. `uvicorn` (serveur API)

### Étape 6 : Vérifier l’application (2 min)

- **Frontend** : http://localhost:89 (ou le port défini par `FRONTEND_PORT`)
- **API** : http://localhost:8089
- **Documentation API** : http://localhost:8089/docs

**Identifiants admin** : `admin` / `admin123` (créés par `create_admin.py`)

### Étape 7 (optionnel) : Démarrer Airflow (10 min)

Pour l’import quotidien Open Food Facts et l’export CSV :

```bash
# Première fois uniquement : initialiser Airflow
docker compose run --rm airflow-init

# Démarrer Airflow
docker compose up -d postgres_airflow export-init airflow-webserver airflow-scheduler
```

- **Interface Airflow** : http://localhost:8080
- **Identifiants** : `airflow` / `airflow`

---

## 4. Récapitulatif des commandes (copier-coller)

```bash
# 1. Cloner et entrer dans le projet
git clone <url> HEALTHAIMSRP && cd HEALTHAIMSRP

# 2. Créer .env (voir section 2)
# 3. Démarrer PostgreSQL
docker compose up -d postgres
sleep 10

# 4. Nettoyer les CSV (si data/clean/ absent)
cd data && python3 clean_csv_data.py 2>/dev/null || true && cd ..

# 5. Build et démarrage
docker compose build backend frontend
docker compose up -d backend frontend

# 6. Vérification
curl -s http://localhost:8089/docs | head -5
```

---

## 5. Ports et accès

| Service | URL | Port par défaut |
|---------|-----|-----------------|
| Frontend | http://localhost:89 | 89 |
| Backend API | http://localhost:8089 | 8089 |
| Documentation API | http://localhost:8089/docs | 8089 |
| PostgreSQL | localhost:5435 | 5435 |
| Airflow | http://localhost:8080 | 8080 |

---

## 6. Vérifications post-déploiement

### 6.1 Conteneurs en cours d’exécution

```bash
docker compose ps
```

Attendu : `postgres_health`, `backend_api`, `frontend_nginx` (et éventuellement les services Airflow) en état `running`.

### 6.2 Test de l’API

```bash
# Connexion
TOKEN=$(curl -s -X POST "http://localhost:8089/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Test d’une route protégée
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8089/utilisateurs/ | head -c 200
```

### 6.3 Test du frontend

Ouvrir http://localhost:89, se connecter avec `admin` / `admin123`, accéder au Dashboard et à la page Utilisateurs.

---

## 7. Dépannage

### Erreur « Unexpected token '<', "<!doctype "... is not valid JSON »

- **Cause** : Le frontend reçoit du HTML au lieu de JSON (proxy nginx mal configuré ou backend arrêté).
- **Solution** : Vérifier que le backend tourne (`docker compose ps`), que nginx inclut bien les routes `/admin` dans le proxy (voir `Frontend/nginx.conf`).

### PostgreSQL « connection refused »

- **Cause** : PostgreSQL n’est pas encore prêt ou le port est incorrect.
- **Solution** : `docker compose up -d postgres && sleep 15`, vérifier `POSTGRES_PORT` dans `.env`.

### Airflow « 403 Forbidden » sur les logs

- **Cause** : `AIRFLOW__WEBSERVER__SECRET_KEY` différent entre webserver et scheduler.
- **Solution** : Utiliser la même valeur pour les deux services (variable `AIRFLOW_SECRET_KEY` dans `.env`).

### Seed échoue (fichiers CSV manquants)

- **Cause** : Le dossier `data/clean/` est vide ou absent.
- **Solution** : Exécuter `python3 data/clean_csv_data.py` depuis la racine (avec `PYTHONPATH=backend` si nécessaire).

### Port déjà utilisé

- **Solution** : Modifier les variables dans `.env` (ex. `BACKEND_PORT=127.0.0.1:8090:8000`).

---

## 8. Arrêt et nettoyage

```bash
# Arrêter tous les services
docker compose down

# Arrêter et supprimer les volumes (données PostgreSQL, Airflow)
docker compose down -v
```

---

*Guide de déploiement – HealthAI Coach – Mise en œuvre en moins de 30 minutes*
