# Apache Airflow - HealthAim

Airflow est configuré pour exécuter des tâches planifiées, notamment l'import quotidien des nouveaux produits Open Food Facts vendus en France.

## Démarrage

Depuis la **racine du projet** :

```bash
# 1. Démarrer PostgreSQL (base HealthAim)
docker compose up -d postgres

# 2. Première fois uniquement : initialiser la base Airflow
docker compose --profile airflow run --rm airflow-init

# 3. Démarrer Airflow (webserver + scheduler)
docker compose --profile airflow up -d
```

## Accès

- **Interface web** : http://localhost:8080 (ou port défini par `AIRFLOW_PORT` dans `.env`)
- **Identifiants** : `airflow` / `airflow`

## DAG : fetch_openfoodfacts_france

Exécution **quotidienne** à 6h00 pour :
1. Récupérer les produits vendus en France via l'API Open Food Facts
2. Insérer les produits valides (avec nutriments) dans la table `aliment` de la base HealthAim
3. Ignorer les doublons (même `nom_aliment`)

**Lancement manuel** : dans l'interface Airflow, activer le DAG puis cliquer sur "Trigger DAG".

## Structure

```
airflow/
├── dags/
│   └── fetch_openfoodfacts_france.py   # DAG quotidien
└── README.md
```

> **Note** : L'image officielle `apache/airflow:2.10.4` est utilisée directement. Les providers (postgres, http) sont installés via `_PIP_ADDITIONAL_REQUIREMENTS`.
