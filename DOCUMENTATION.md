# HealthAI Coach — Documentation Technique

> **Projet** : HealthAI Coach — Plateforme de suivi santé & fitness
> **Contexte** : Projet de fin d'études / Examen — Gestion de données de santé
> **Stack** : Python · FastAPI · PostgreSQL · Vue 3 · Apache Airflow · Docker

---

## Table des matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Architecture globale](#2-architecture-globale)
3. [Sources de données](#3-sources-de-données)
4. [Pipeline de données (ETL)](#4-pipeline-de-données-etl)
5. [Base de données](#5-base-de-données)
6. [Backend — API REST (FastAPI)](#6-backend--api-rest-fastapi)
7. [Frontend — Interface utilisateur (Vue 3)](#7-frontend--interface-utilisateur-vue-3)
8. [Orchestration — Apache Airflow](#8-orchestration--apache-airflow)
9. [Sécurité](#9-sécurité)
10. [Conteneurisation — Docker](#10-conteneurisation--docker)
11. [Qualité des données](#11-qualité-des-données)
12. [Lancement du projet](#12-lancement-du-projet)
13. [Glossaire](#13-glossaire)

---

## 1. Présentation du projet

### Objectif

**HealthAI Coach** est une application web complète de gestion santé et fitness. Elle permet à des utilisateurs de :

- Suivre leur **alimentation quotidienne** (calories, macronutriments)
- Enregistrer leurs **activités physiques** (type d'exercice, durée, calories brûlées)
- Consulter leurs **métriques de santé** (poids, fréquence cardiaque, sommeil, pas)
- Définir et suivre des **objectifs** de santé personnalisés
- Visualiser des **tableaux de bord analytiques** avec indicateurs clés (KPIs)

### Contexte académique

Ce projet illustre les compétences suivantes :
- **Ingénierie des données** : collecte, nettoyage, transformation, chargement (pipeline ETL)
- **Développement backend** : API REST sécurisée avec authentification JWT
- **Développement frontend** : interface utilisateur réactive avec Vue 3
- **DevOps** : conteneurisation complète avec Docker et orchestration avec Airflow
- **Modélisation de base de données** : schéma relationnel normalisé (3NF)

---

## 2. Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                        SOURCES DE DONNÉES                    │
│  Kaggle CSV  │  ExerciseDB API  │  Open Food Facts API       │
└──────────────────────────┬──────────────────────────────────┘
                           │  ETL (extraction, nettoyage)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE DONNÉES                            │
│            PostgreSQL 17  (7 tables relationnelles)          │
│     seed_db.py (init)  │  Airflow DAG (enrichissement)       │
└──────────────────────────┬──────────────────────────────────┘
                           │  SQLAlchemy ORM
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE APPLICATION                        │
│          FastAPI (Python 3.11) — 8 endpoints REST            │
│         Authentification JWT · Contrôle d'accès RBAC         │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP / REST
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   COUCHE PRÉSENTATION                        │
│           Vue 3 + TypeScript + Vite (SPA)                    │
│      Dashboard · Gestion flux · Nettoyage · Connexion        │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION                              │
│        Apache Airflow 2.10.4  — DAG quotidien 6h00           │
│        Récupération automatique Open Food Facts (France)     │
└─────────────────────────────────────────────────────────────┘
```

### Structure des répertoires

```
HEALTHAIMSRP/
├── backend/                  # API FastAPI
│   ├── app/
│   │   ├── main.py           # Point d'entrée de l'application
│   │   ├── models/           # Modèles SQLAlchemy (ORM)
│   │   ├── routers/          # Endpoints REST par ressource
│   │   ├── schemas/          # Schémas Pydantic (validation)
│   │   └── database.py       # Connexion à la base de données
│   └── requirements.txt
├── Frontend/                 # Application Vue 3
│   ├── src/
│   │   ├── views/            # Pages de l'application
│   │   ├── components/       # Composants réutilisables
│   │   └── router/           # Définition des routes
│   └── package.json
├── airflow/                  # Orchestration
│   ├── dags/
│   │   └── fetch_openfoodfacts_france.py
│   └── requirements.txt
├── data/                     # Scripts ETL
│   ├── clean_csv_data.py     # Nettoyage des CSV bruts
│   └── seed_db.py            # Chargement initial en base
├── database/
│   └── init/
│       ├── 01_create_tables.sql   # Schéma DDL
│       └── 02_insert_test_data.sql
├── Divers/                   # Maquettes, MLD, supports
├── docker-compose.yml        # Orchestration des conteneurs
└── .env                      # Variables d'environnement
```

---

## 3. Sources de données

Le projet ingère des données depuis **6 sources hétérogènes** :

| # | Source | Format | Type d'ingestion | Contenu |
|---|--------|--------|-----------------|---------|
| 1 | Daily Food & Nutrition Dataset (Kaggle) | CSV | Batch (initial) | Données nutritionnelles par aliment |
| 2 | Diet Recommendations Dataset (Kaggle) | CSV | Batch (initial) | Profils utilisateurs, recommandations |
| 3 | ExerciseDB API (GitHub) | JSON | Batch (initial) | Catalogue d'exercices (1000+) |
| 4 | Gym Members Exercise Dataset (Kaggle) | CSV | Batch (initial) | Profils biométriques, sessions gym |
| 5 | Fitness Tracker Dataset (Kaggle) | CSV | Batch (initial) | Historique d'activités |
| 6 | Open Food Facts API | JSON | **Temps réel** (Airflow, quotidien) | Produits alimentaires France |

### Pourquoi plusieurs sources ?

Chaque source couvre une dimension différente de la santé :
- Les données **Kaggle** fournissent une base de données initiale riche et diversifiée
- **Open Food Facts** permet un enrichissement continu et automatique du catalogue alimentaire
- La **combinaison** de ces sources permet d'avoir des données complètes sur la nutrition ET l'activité physique

---

## 4. Pipeline de données (ETL)

### Étape 1 — Extraction

Les fichiers CSV bruts sont téléchargés depuis Kaggle et placés dans le dossier `data/raw/`.

### Étape 2 — Nettoyage (`data/clean_csv_data.py`)

Le script de nettoyage applique les transformations suivantes :

```python
# Suppression des caractères parasites
df.columns = [col.strip().replace('\t', '').replace('\n', '') for col in df.columns]

# Gestion des valeurs manquantes
df['Gender'].fillna('Other', inplace=True)
df['Disease_Type'].fillna('no_disease', inplace=True)
df['Allergies'].fillna('no_allergies', inplace=True)

# Fusion des jeux de données gym + exercices
merged_df = gym_df.merge(exercise_df, on='Workout_Type', how='left')
```

**Règles de qualité appliquées :**
- Suppression des doublons
- Vérification des types de données (numérique, texte, date)
- Détection et traitement des valeurs aberrantes (outliers)
- Standardisation des unités (kJ → kcal pour les calories)
- Filtrage des entrées sans données nutritionnelles

### Étape 3 — Chargement (`data/seed_db.py`)

```python
# Exemple de chargement des utilisateurs
for _, row in diet_df.iterrows():
    user = Utilisateur(
        nom=row['Name'],
        age=int(row['Age']),
        poids_kg=float(row['Weight (kg)']),
        taille_cm=float(row['Height (cm)']),
        niveau_activite=map_activity_level(row['Activity Level']),
        mot_de_passe=hash_password("HealthAim2025!")
    )
    session.add(user)
```

Le script :
- Attend que la base de données soit disponible (retry logic)
- Charge ~1000 utilisateurs, aliments, exercices
- Génère 500 consommations alimentaires synthétiques
- Hache les mots de passe avec **bcrypt**

### Résumé du flux ETL

```
CSV bruts (raw/)
     │
     ▼  clean_csv_data.py
CSV propres (clean/)
     │
     ▼  seed_db.py
PostgreSQL (tables: utilisateurs, aliments, exercices...)
     │
     ▼  Airflow DAG (quotidien)
Enrichissement Open Food Facts → table aliment
```

---

## 5. Base de données

### Système : PostgreSQL 17

### Schéma relationnel (7 tables)

```
utilisateurs ──────────────────────────────┐
     │ id_utilisateur (PK)                 │
     │ nom, prenom, email                  │
     │ age, poids_kg, taille_cm            │
     │ niveau_activite, is_admin           │
     │ mot_de_passe (bcrypt)               │
     │                                     │
     ├──── objectif                        │
     │      id_objectif (PK)               │
     │      description, date_debut        │
     │      date_fin, statut               │
     │      id_utilisateur (FK)            │
     │                                     │
     ├──── consommation ───── aliment       │
     │      id_consommation (PK)    │       │
     │      date_consommation       │       │
     │      quantite_g              │       │
     │      calories_calculees      │       │
     │      id_utilisateur (FK)     │       │
     │      id_aliment (FK) ────────┘       │
     │         │ id_aliment (PK)            │
     │         │ nom_aliment                │
     │         │ calories_pour_100g         │
     │         │ proteines_g, glucides_g    │
     │         │ lipides_g, categorie       │
     │                                     │
     ├──── activite ───── exercice          │
     │      id_activite (PK)  │             │
     │      date_activite     │             │
     │      duree_minutes     │             │
     │      calories_brulees  │             │
     │      intensite         │             │
     │      id_utilisateur (FK)             │
     │      id_exercice (FK) ───────────────┘
     │         │ id_exercice (PK)
     │         │ nom_exercice
     │         │ type_exercice, difficulte
     │         │ equipement, muscle_principal
     │
     └──── metrique_sante
            id_metrique (PK)
            date_mesure
            poids_kg, frequence_cardiaque
            duree_sommeil_h, calories_brulees
            nombre_pas
            id_utilisateur (FK)
```

### Contraintes d'intégrité

- **Clés primaires** : auto-incrémentées (SERIAL)
- **Clés étrangères** : avec `ON DELETE CASCADE` pour maintenir la cohérence
- **Normalisation** : 3NF — pas de redondance, chaque fait dans une seule table

### Script SQL de création (extrait)

```sql
CREATE TABLE utilisateurs (
    id_utilisateur SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    age INTEGER CHECK (age > 0 AND age < 150),
    poids_kg FLOAT CHECK (poids_kg > 0),
    taille_cm FLOAT CHECK (taille_cm > 0),
    niveau_activite VARCHAR(50),
    mot_de_passe VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE consommation (
    id_consommation SERIAL PRIMARY KEY,
    date_consommation DATE NOT NULL,
    quantite_g FLOAT NOT NULL,
    calories_calculees FLOAT,
    id_utilisateur INTEGER REFERENCES utilisateurs(id_utilisateur) ON DELETE CASCADE,
    id_aliment INTEGER REFERENCES aliment(id_aliment) ON DELETE CASCADE
);
```

---

## 6. Backend — API REST (FastAPI)

### Technologie : FastAPI (Python 3.11)

FastAPI est un framework web moderne et performant qui génère automatiquement la documentation Swagger UI.

### Point d'entrée (`backend/app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Autoriser les requêtes du frontend
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Enregistrement des 7 routers
app.include_router(utilisateurs.router, prefix="/utilisateurs")
app.include_router(aliments.router, prefix="/aliments")
app.include_router(exercices.router, prefix="/exercices")
app.include_router(consommations.router, prefix="/consommations")
app.include_router(activites.router, prefix="/activites")
app.include_router(metriques_sante.router, prefix="/metriques_sante")
app.include_router(objectifs.router, prefix="/objectifs")
```

### Authentification

Le système utilise **OAuth2 avec tokens JWT** (JSON Web Tokens) :

```
Client                        Serveur
  │                              │
  │  POST /login                 │
  │  { username, password }      │
  │ ─────────────────────────►   │
  │                              │  Vérifie mot de passe (bcrypt)
  │  { access_token, type }      │  Génère JWT signé (30 min)
  │ ◄─────────────────────────   │
  │                              │
  │  GET /utilisateurs           │
  │  Authorization: Bearer <JWT> │
  │ ─────────────────────────►   │
  │                              │  Décode et vérifie JWT
  │  { données utilisateurs }    │
  │ ◄─────────────────────────   │
```

### Endpoints REST

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| POST | `/login` | Public | Authentification, retourne JWT |
| GET | `/utilisateurs/` | Auth | Liste tous les utilisateurs |
| GET | `/utilisateurs/{id}` | Auth | Détails d'un utilisateur |
| POST | `/utilisateurs/` | Admin | Créer un utilisateur |
| PUT | `/utilisateurs/{id}` | Admin | Modifier un utilisateur |
| DELETE | `/utilisateurs/{id}` | Admin | Supprimer un utilisateur |
| GET | `/aliments/` | Auth | Liste des aliments |
| POST | `/aliments/` | Admin | Ajouter un aliment |
| GET | `/consommations/` | Auth | Historique alimentaire |
| POST | `/consommations/` | Auth | Enregistrer une consommation |
| GET | `/activites/` | Auth | Historique des activités |
| POST | `/activites/` | Auth | Enregistrer une activité |
| GET | `/metriques_sante/` | Auth | Métriques de santé |
| GET | `/objectifs/` | Auth | Objectifs utilisateur |

### Modèles SQLAlchemy (ORM)

```python
# backend/app/models/consommation.py
class Consommation(Base):
    __tablename__ = "consommation"

    id_consommation = Column(Integer, primary_key=True, index=True)
    date_consommation = Column(Date, nullable=False)
    quantite_g = Column(Float, nullable=False)
    calories_calculees = Column(Float)
    id_aliment = Column(Integer, ForeignKey("aliment.id_aliment"))
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"))
```

### Schémas Pydantic (validation des données)

```python
class ConsommationCreate(BaseModel):
    date_consommation: date
    quantite_g: float
    id_aliment: int
    id_utilisateur: int

class ConsommationResponse(ConsommationCreate):
    id_consommation: int
    calories_calculees: Optional[float]

    class Config:
        from_attributes = True
```

### Documentation automatique

FastAPI génère automatiquement une interface interactive :
- **Swagger UI** : `http://localhost:8089/docs`
- **ReDoc** : `http://localhost:8089/redoc`

---

## 7. Frontend — Interface utilisateur (Vue 3)

### Technologie : Vue 3 + TypeScript + Vite

### Pages principales

| Page | Fichier | Description |
|------|---------|-------------|
| Accueil | `PageAccueil.vue` | Page d'accueil avec présentation |
| Connexion | `Connexion.vue` | Formulaire de login (JWT) |
| Tableau de bord | `Dashboard.vue` | KPIs, graphiques analytiques |
| Gestion des flux | `GestionFlux.vue` | Vue des flux de données |
| Détail flux | `FluxDetail.vue` | Détail d'un flux de données |
| Nettoyage | `Nettoyage.vue` | Validation et nettoyage des données |
| Test backend | `TestBackend.vue` | Interface de test des API |

### Dashboard — Indicateurs clés (KPIs)

Le tableau de bord affiche :
- **Top 3 exercices** les plus pratiqués (graphique en barres)
- **Top 3 aliments** les plus consommés (graphique en barres)
- **Statistiques moyennes** : taille, poids, âge des utilisateurs
- **Ratio exercices/utilisateur**

```typescript
// Exemple d'interface TypeScript dans Dashboard.vue
interface GlobalMetrics {
  avg_height: number
  avg_weight: number
  avg_age: number
  avg_exercises_per_user: number
}

interface TopItem {
  name: string
  count: number
}
```

### Routing (Vue Router)

```javascript
const routes = [
  { path: '/', component: PageAccueil },
  { path: '/login', component: Connexion },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/flux', component: GestionFlux, meta: { requiresAuth: true } },
  { path: '/nettoyage', component: Nettoyage, meta: { requiresAuth: true } },
]
```

---

## 8. Orchestration — Apache Airflow

### Rôle d'Airflow

Apache Airflow est un outil d'orchestration de workflows. Il permet de **planifier et exécuter automatiquement** des pipelines de données.

### DAG : `fetch_openfoodfacts_france`

```
Tous les jours à 6h00
        │
        ▼
  fetch_products()
  ├── Appel API Open Food Facts
  │   (pays: France, max 5 pages)
  ├── Extraction: nom, calories, protéines,
  │   glucides, lipides
  ├── Conversion kJ → kcal
  └── Insertion en base (doublons ignorés)
```

**Code du DAG (extrait) :**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='fetch_openfoodfacts_france',
    default_args=default_args,
    schedule_interval='0 6 * * *',   # Tous les jours à 6h00
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_and_insert_products',
        python_callable=fetch_and_insert_products,
    )
```

**Logique de récupération :**

```python
def fetch_and_insert_products():
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "action": "process",
        "tagtype_0": "countries",
        "tag_0": "france",
        "json": 1,
        "page_size": 100
    }

    for page in range(1, 6):   # Max 5 pages par exécution
        params["page"] = page
        response = requests.get(url, params=params)
        products = response.json().get("products", [])

        for product in products:
            # Conversion kJ → kcal si nécessaire
            energy_kj = nutriments.get("energy_100g", 0)
            calories = energy_kj / 4.184 if energy_kj > 0 else 0

            # Insertion avec prévention des doublons
            cursor.execute("""
                INSERT INTO aliment (nom_aliment, calories_pour_100g, ...)
                VALUES (%s, %s, ...)
                ON CONFLICT (nom_aliment) DO NOTHING
            """, (nom, calories, ...))
```

### Interface Airflow

Accessible à `http://localhost:8080` — permet de :
- Visualiser l'état des DAGs (succès / échec / en cours)
- Consulter les logs d'exécution
- Déclencher manuellement un DAG
- Voir le graphe des dépendances entre tâches

---

## 9. Sécurité

### Authentification — JWT (JSON Web Tokens)

```
┌─────────────────────────────────────────────────────┐
│  JWT Token = Header.Payload.Signature                │
│                                                     │
│  Header:  { alg: "HS256", typ: "JWT" }              │
│  Payload: { user_id: 1, is_admin: false, exp: ... } │
│  Signature: HMAC-SHA256(header+payload, SECRET_KEY) │
└─────────────────────────────────────────────────────┘
```

- Durée de validité : **30 minutes**
- Algorithme : **HS256**
- Secret stocké dans `.env` (jamais en dur dans le code)

### Hachage des mots de passe — bcrypt

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hachage lors de la création
hashed = pwd_context.hash("HealthAim2025!")

# Vérification lors du login
is_valid = pwd_context.verify(plain_password, hashed_password)
```

bcrypt ajoute automatiquement un **sel** (salt) aléatoire : même mot de passe → hash différent à chaque fois.

### Contrôle d'accès — RBAC

| Action | Utilisateur standard | Administrateur |
|--------|---------------------|----------------|
| Consulter données | ✅ | ✅ |
| Créer utilisateur | ❌ | ✅ |
| Modifier utilisateur | ❌ | ✅ |
| Supprimer utilisateur | ❌ | ✅ |
| Gérer aliments | ❌ | ✅ |
| Gérer exercices | ❌ | ✅ |

```python
# Vérification admin dans les routers
def require_admin(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return current_user
```

### Protection contre les injections SQL

SQLAlchemy ORM génère des requêtes paramétrées automatiquement :

```python
# SAFE : SQLAlchemy génère des requêtes préparées
user = db.query(Utilisateur).filter(Utilisateur.email == email).first()

# Équivalent SQL sécurisé : SELECT * FROM utilisateurs WHERE email = $1
```

### Variables d'environnement (`.env`)

```env
DATABASE_URL=postgresql://user:password@postgres:5432/healthdb
SECRET_KEY=your_very_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 10. Conteneurisation — Docker

### Architecture Docker

Le projet définit **8 services** dans `docker-compose.yml` :

```yaml
services:
  postgres:            # Base de données principale (port 5435)
  backend:             # API FastAPI (port 8089)
  frontend:            # Nginx + Vue.js (port 89)
  seed:                # Chargement initial des données
  postgres_airflow:    # Base de données Airflow (métadonnées)
  airflow-init:        # Initialisation Airflow (one-shot)
  airflow-webserver:   # Interface Airflow (port 8080)
  airflow-scheduler:   # Planificateur des DAGs
```

Tous les services communiquent via le réseau interne `health_net`.

### Commandes Docker essentielles

```bash
# Démarrer tous les services
docker compose up -d

# Voir les logs d'un service
docker compose logs backend

# Arrêter tous les services
docker compose down

# Reconstruire après modification
docker compose build backend
docker compose up -d backend
```

### Ports exposés

| Service | Port externe | Port interne |
|---------|-------------|-------------|
| Frontend | 89 | 80 |
| Backend API | 8089 | 8000 |
| Airflow UI | 8080 | 8080 |
| PostgreSQL | 5435 | 5432 |

---

## 11. Qualité des données

### Règles de validation appliquées

| Règle | Type | Action |
|-------|------|--------|
| Valeurs nulles sur champs obligatoires | Complétude | Remplissage ou suppression |
| Doublons (même nom d'aliment) | Unicité | `ON CONFLICT DO NOTHING` |
| Calories négatives | Cohérence | Rejet de la ligne |
| Âge hors plage (0-150) | Validité | Contrainte CHECK SQL |
| Unités kJ vs kcal | Standardisation | Conversion (÷ 4.184) |
| Caractères parasites (\t, \n) | Propreté | Strip et remplacement |

### Métriques de qualité surveillées

- **Taux de complétude** : % de champs renseignés
- **Taux de doublons** : doublons détectés / total lignes
- **Cohérence des types** : colonnes numériques sans valeurs texte
- **Plages valides** : min/max des variables quantitatives

---

## 12. Lancement du projet

### Prérequis

- Docker Desktop installé et démarré
- Git

### Séquence de lancement

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd HEALTHAIMSRP

# 2. Configurer les variables d'environnement
cp .env.example .env   # puis éditer .env

# 3. Démarrer la base de données et charger les données initiales
docker compose up -d postgres
sleep 5
docker compose --profile seed run --rm seed

# 4. Initialiser Airflow (première fois uniquement)
docker compose --profile airflow run --rm airflow-init

# 5. Démarrer tous les services
docker compose up -d

# 6. Vérifier que tout fonctionne
docker compose ps
```

### Comptes de test

| Rôle | Identifiant | Mot de passe |
|------|------------|-------------|
| Utilisateur standard | P0001 (jusqu'à P1000) | HealthAim2025! |
| Administrateur | admin | admin123 |

### URLs d'accès

| Service | URL |
|---------|-----|
| Application web | http://localhost:89 |
| Documentation API | http://localhost:8089/docs |
| Interface Airflow | http://localhost:8080 |

---

## 13. Glossaire

| Terme | Définition |
|-------|-----------|
| **ETL** | Extract, Transform, Load — processus d'extraction, transformation et chargement de données |
| **FastAPI** | Framework Python pour créer des APIs REST performantes, avec génération automatique de documentation |
| **JWT** | JSON Web Token — format standard pour transmettre des informations d'authentification de manière sécurisée |
| **bcrypt** | Algorithme de hachage de mots de passe avec sel automatique, résistant aux attaques brute force |
| **ORM** | Object-Relational Mapping — couche d'abstraction qui traduit des objets Python en requêtes SQL |
| **SQLAlchemy** | ORM Python utilisé pour interagir avec PostgreSQL sans écrire de SQL brut |
| **Pydantic** | Bibliothèque Python de validation de données, utilisée par FastAPI pour valider les entrées/sorties |
| **Vue 3** | Framework JavaScript progressif pour créer des interfaces utilisateur réactives |
| **SPA** | Single Page Application — application web qui ne recharge pas la page complète lors de la navigation |
| **Airflow DAG** | Directed Acyclic Graph — graphe de tâches à exécuter dans un ordre défini, sans cycle |
| **Docker Compose** | Outil pour définir et gérer des applications multi-conteneurs |
| **CORS** | Cross-Origin Resource Sharing — mécanisme permettant au frontend de communiquer avec le backend sur un domaine différent |
| **RBAC** | Role-Based Access Control — contrôle d'accès basé sur les rôles (ex: admin vs utilisateur) |
| **3NF** | Troisième Forme Normale — niveau de normalisation d'une base de données relationnelle qui élimine la redondance |
| **Swagger UI** | Interface graphique générée automatiquement par FastAPI pour tester les endpoints de l'API |
| **Seed** | Chargement initial de données de test dans la base de données |
| **Open Food Facts** | Base de données collaborative et ouverte sur les produits alimentaires |

---

