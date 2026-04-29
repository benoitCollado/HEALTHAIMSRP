# 1. Définition des sources de données

## 1.1 Typologie des sources

HealthAI Coach s’appuie sur des **sources hétérogènes**, internes et externes, afin de couvrir l’ensemble du parcours utilisateur (nutrition, sport, biométrie).

| Source                         | Origine             | Format   | Fréquence       | Justification                                         |
| ------------------------------ | ------------------- | -------- | --------------- | ----------------------------------------------------- |
| Daily Food & Nutrition Dataset | Open Data (Kaggle)  | CSV      | Batch (mensuel) | Base nutritionnelle fiable pour analyses alimentaires |
| Diet Recommendations Dataset   | Open Data (Kaggle)  | CSV/JSON | Batch           | Profils santé et recommandations IA simulées          |
| ExerciseDB API                 | API publique GitHub | JSON     | Quotidienne     | Catalogue d’exercices riche et structuré              |
| Gym Members Exercise Dataset   | Open Data (Kaggle)  | CSV      | Batch           | Profils utilisateurs et biométrie simulée             |
| Fitness Tracker Dataset        | Open Data (Kaggle)  | CSV      | Batch           | Activité quotidienne et engagement                    |

**Justification du choix**
Ces datasets couvrent **au minimum deux sources** comme exigé, et représentent un **échantillon réaliste des données métiers** qu’exploiterait HealthAI Coach en production.

---

# 2. Outils et architecture de collecte

## 2.1 Stack technologique retenue

| Besoin             | Outil                       |
| ------------------ | --------------------------- |
| Ingestion & ETL    | Python (pandas, requests)   |
| Orchestration      | Apache Airflow              |
| Validation qualité | pandas + règles métiers     |
| Stockage           | PostgreSQL serverless (Neon)|
| Migrations BDD     | Alembic                     |
| API                | FastAPI                     |
| Visualisation      | Metabase / Superset         |
| Conteneurisation   | Docker / Docker Compose     |

**Justification**
Cette stack est **open source**, industrialisable, et compatible avec une montée en charge future (micro-services IA).

---

## 2.2 Architecture des flux de données (logique)

```
Sources externes
   ↓
Zone de staging (raw)
   ↓
Validation & nettoyage (ETL)
   ↓
Base relationnelle PostgreSQL
   ↓
API REST sécurisée
   ↓
Dashboard & services IA
```

Cette séparation **raw / cleaned / exposed** garantit traçabilité, qualité et reproductibilité.

---

# 3. Collecte sécurisée et automatisée

## 3.1 Sécurité des flux

* Accès API via HTTPS
* Variables sensibles stockées dans `.env`
* Contrôle d’accès par rôle (admin / lecture)
* Journalisation des traitements sans données personnelles
* Données fictives → conformité RGPD respectée par design
* En-têtes de sécurité HTTP sur toutes les réponses (voir ci-dessous)
* Alertes email automatiques à l’administrateur sur toute erreur 500

### En-têtes de sécurité HTTP

Le middleware backend ajoute automatiquement les en-têtes OWASP recommandés à chaque réponse :

| En-tête | Valeur | Protection |
| ------- | ------ | ---------- |
| `X-Frame-Options` | `DENY` | Clickjacking |
| `X-Content-Type-Options` | `nosniff` | MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | XSS (navigateurs legacy) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS (1 an) |
| `Content-Security-Policy` | `default-src ‘self’; ...` | Sources de contenu autorisées |

### Alertes email

En cas d’erreur 500 non gérée, un email HTML est envoyé automatiquement à l’administrateur (configurable via `SMTP_*` et `ADMIN_EMAIL` dans `.env`). Un cooldown de 60 s par type d’erreur évite le flood.

## 3.2 Automatisation

* Scripts Python exécutés par cron
* Chaque job :

  * Télécharge la source
  * Vérifie le schéma
  * Loggue les erreurs
  * Alimente la base

Chaque exécution de pipeline est horodatée et journalisée afin d’assurer la traçabilité des traitements et la reproductibilité des résultats.

---

# 4. Analyse, nettoyage et qualité des données

## 4.1 Règles de qualité appliquées

| Problème             | Traitement                    |
| -------------------- | ----------------------------- |
| Valeurs manquantes   | Suppression ou imputation     |
| Doublons             | Détection par clé métier      |
| Types incohérents    | Cast explicite                |
| Valeurs aberrantes   | Détection IQR / seuils métier |
| Données hors domaine | Filtrage                      |

## 4.2 Objectif Data Science

Le nettoyage vise à :

* réduire le biais des modèles IA,
* garantir la stabilité des analyses,
* fournir une donnée directement exploitable par les data scientists.

---

# 5. Modèle de données relationnel

## 5.1 Choix de modélisation

* **Modèle relationnel normalisé (3NF)** pour backend métier
* Compatible avec un futur schéma analytique (étoile)

## 5.2 Entités principales

* `utilisateurs`
* `aliments`
* `exercices`
* `activites`
* `metriques_sante`
* `objectifs`

Ces entités constituent le socle des indicateurs exposés dans les tableaux de bord analytiques et servent de base aux futurs modules de recommandation IA.

---

# 6. Exploitation et visualisation

## 6.1 Requêtage automatisé

* Agrégations par période
* Analyse de progression
* KPI engagement & activité
* Exposition via API REST

## 6.2 Tableaux de bord

* KPI utilisateurs
* Tendances nutritionnelles
* Statistiques sportives
* Qualité des données

**Accessibilité RGAA AA**

* Contraste respecté
* Libellés explicites
* Navigation simple
* Pas de dépendance exclusive à la couleur

---

# 7. Conformité aux attendus E6.1

| Exigence RNCP              | Couverture |
| -------------------------- | ---------- |
| Sources hétérogènes        | Oui        |
| Collecte sécurisée         | Oui        |
| ETL automatisé             | Oui        |
| Nettoyage & qualité        | Oui        |
| Modèle de données          | Oui        |
| Visualisation              | Oui        |
| Exploitation IA-ready      | Oui        |
| En-têtes sécurité HTTP     | Oui        |
| Migrations versionnées     | Oui        |
| Alertes erreurs admin      | Oui        |
| Tests + couverture ≥ 70 %  | Oui        |

---

# 8. Démarrage rapide

## Prérequis — base de données Neon

La base est hébergée sur [Neon](https://neon.tech) (PostgreSQL serverless).  
Avant le premier lancement :

1. Copier `.env.example` → `.env` et renseigner `DATABASE_URL` avec la connection string Neon
2. (Optionnel) Insérer les données de test via le **SQL Editor Neon** :
   - `database/init/02_insert_test_data.sql`

> Les tables sont créées automatiquement par **Alembic** au premier démarrage du backend (`alembic upgrade head`). L'exécution manuelle de `01_create_tables.sql` n'est plus nécessaire.

## Services Docker

```bash
docker compose up -d                              # Backend (+ migrations auto), frontend, Airflow
docker compose --profile seed run --rm seed       # Import des données CSV
```

**Identifiants par défaut** : `admin` / `password`

## Airflow

```bash
docker compose up -d                    # Démarre tout (Airflow inclus)
```

Interface : http://localhost:8080 (airflow / airflow). Voir `airflow/README.md`.

> **Note** : PostgreSQL local supprimé. Seule la base Airflow de métadonnées (`postgres_airflow`) reste en Docker. La base applicative `healthdb` est sur Neon.

