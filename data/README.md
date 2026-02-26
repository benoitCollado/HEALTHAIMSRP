# Données et import

Ce dossier contient les fichiers CSV sources, les scripts de nettoyage et d'import vers la base de données.

## Structure

```
data/
├── clean/                          # CSV nettoyés (générés par clean_csv_data.py)
│   ├── daily_food_nutrition_clean.csv
│   ├── diet_recommendations_clean.csv
│   └── exercise_tracker_clean.csv
├── daily_food_nutrition_dataset.csv # Sources brutes
├── diet_recommendations_dataset.csv
├── gym_meber.csv
├── exercices.csv
├── clean_csv_data.py                # Nettoyage des CSV
├── seed_db.py                       # Import vers PostgreSQL
└── README.md
```

## Prérequis

- PostgreSQL démarré (via Docker ou local)
- Python 3.11+ avec pandas, sqlalchemy, psycopg2-binary, passlib

---

## 1. Nettoyer les données (optionnel)

Si le dossier `clean/` n'existe pas ou si vous avez modifié les CSV sources :

```bash
cd data
python clean_csv_data.py
```

**Fichiers requis :**
- `daily_food_nutrition_dataset.csv`
- `diet_recommendations_dataset.csv`
- `gym_meber.csv`
- `exercices.csv`

Les fichiers nettoyés sont créés dans `clean/`.

---

## 2. Lancer l'import

### Option A : Via Docker (recommandé)

Depuis la **racine du projet** :

```bash
# 1. Démarrer PostgreSQL
docker compose up -d postgres

# 2. Attendre quelques secondes que la base soit prête
sleep 5

# 3. Lancer le seed
docker compose --profile seed run --rm seed
```

### Option B : En local (sans Docker)

Depuis la **racine du projet** :

```bash
# Adapter le port si nécessaire (5435 = défaut docker-compose)
export DATABASE_URL="postgresql://healthuser:healthpass@localhost:5435/healthdb"
PYTHONPATH=backend python data/seed_db.py
```

Ou en une ligne :

```bash
PYTHONPATH=backend DATABASE_URL=postgresql://healthuser:healthpass@localhost:5435/healthdb python data/seed_db.py
```

> **Port** : Par défaut PostgreSQL écoute sur `127.0.0.1:5435` (configurable via `POSTGRES_PORT` dans `.env`).

---

## Données importées

| Table        | Source                          |
|-------------|----------------------------------|
| aliment     | `daily_food_nutrition_clean.csv` |
| exercice    | 4 types fixes (Yoga, HIIT, Cardio, Strength) |
| utilisateurs| `diet_recommendations_clean.csv` |
| activite    | `exercise_tracker_clean.csv`     |
| consommation| 500 enregistrements synthétiques |

---

## Identifiants de connexion

- **Utilisateurs** : `P0001` à `P1000` (Patient_ID du CSV)
- **Mot de passe** : `HealthAim2025!`

---

## Réinitialiser la base

Pour repartir de zéro :

```bash
# Arrêter les conteneurs
docker compose down

# Supprimer les données PostgreSQL (dossier database/db)
rm -rf database/db
mkdir -p database/db

# Relancer PostgreSQL (ré-exécute les scripts init)
docker compose up -d postgres
sleep 5

# Relancer le seed
docker compose --profile seed run --rm seed
```
