# Guide de lancement - HealthAim

Ce guide décrit l'ordre recommandé pour démarrer l'application HealthAim : intégration des données, Airflow, puis l'application complète.

---

## Vue d'ensemble

| Étape | Objectif |
|-------|----------|
| 1. Intégration des données | Remplir la base PostgreSQL avec les CSV (utilisateurs, aliments, exercices, etc.) |
| 2. Airflow | Configurer l'orchestration des tâches planifiées (import quotidien Open Food Facts) |
| 3. Application | Lancer backend, frontend et accéder à l'application |

---

## Étape 1 : Intégration des données

Avant de lancer l'application, la base de données doit contenir les données initiales.

### 1.1 Nettoyer les CSV (optionnel)

Si le dossier `data/clean/` n'existe pas ou si vous avez modifié les sources :

```bash
cd data
python clean_csv_data.py
cd ..
```

### 1.2 Démarrer PostgreSQL et importer les données

Depuis la **racine du projet** :

```bash
# Démarrer PostgreSQL (crée les tables via database/init/)
docker compose up -d postgres

# Attendre que la base soit prête
sleep 5

# Lancer l'import des CSV vers la base
docker compose --profile seed run --rm seed
```

**Résultat** : la base `healthdb` contient utilisateurs (P0001–P1000), aliments, exercices, activités, consommations.

**Identifiants de test** : `P0001` / `HealthAim2025!`

---

## Étape 2 : Airflow

Airflow gère les tâches planifiées, notamment l'import quotidien des produits Open Food Facts vendus en France.

### 2.1 Pourquoi `airflow-init` est utile ?

`airflow-init` est un service qui s'exécute **une seule fois** (au premier démarrage d'Airflow). Il :

1. **Initialise la base métadonnées Airflow** (`airflow db init`)
   - Crée les tables nécessaires à Airflow (DAGs, tâches, exécutions, logs, etc.) dans `postgres_airflow`.

2. **Crée l'utilisateur admin**
   - Utilisateur : `airflow`
   - Mot de passe : `airflow`
   - Sans cette étape, vous ne pourriez pas vous connecter à l'interface web.

3. **Configure l'environnement**
   - Vérifie que la connexion à la base Airflow fonctionne.

**Sans `airflow-init`** : le webserver et le scheduler ne trouveraient pas de schéma de base ni d'utilisateur, et ne démarreraient pas correctement.

### 2.2 Lancer Airflow

```bash
# Première fois uniquement : initialiser Airflow
docker compose --profile airflow run --rm airflow-init

# Démarrer Airflow (webserver + scheduler)
docker compose --profile airflow up -d
```

**Accès** : http://localhost:8080 — identifiants : `airflow` / `airflow`

---

## Étape 3 : Lancement global de l'application

Une fois les données et Airflow en place, lancez l'application complète.

```bash
# Démarrer tous les services (postgres, backend, frontend)
docker compose up -d
```

### Services et accès

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:89 | Interface utilisateur Vue.js |
| Backend API | http://localhost:8089 | API FastAPI |
| Airflow | http://localhost:8080 | Orchestration des tâches planifiées |

> Les ports sont configurables via `.env` (ex. `FRONTEND_PORT`, `BACKEND_PORT`, `AIRFLOW_PORT`).

---

## Récapitulatif : ordre de lancement complet

```bash
# 1. Données
docker compose up -d postgres
sleep 5
docker compose --profile seed run --rm seed

# 2. Airflow (première fois)
docker compose --profile airflow run --rm airflow-init
docker compose --profile airflow up -d

# 3. Application
docker compose up -d
```

---

## En cas de problème

- **Base vide** : voir `data/README.md` pour réinitialiser et réimporter.
- **Airflow** : voir `airflow/README.md` pour le DAG Open Food Facts.
- **Ports** : vérifier `.env.example` et créer un `.env` si besoin.
