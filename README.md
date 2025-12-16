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
| Orchestration      | Cron / Airflow (conceptuel) |
| Validation qualité | pandas + règles métiers     |
| Stockage           | PostgreSQL                  |
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

## 3.2 Automatisation

* Scripts Python exécutés par cron
* Chaque job :

  * Télécharge la source
  * Vérifie le schéma
  * Loggue les erreurs
  * Alimente la base

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

* `users`
* `nutrition_foods`
* `exercises`
* `activity_metrics`
* `health_metrics`
* `user_goals`

Chaque table est documentée (types, contraintes, clés).

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

| Exigence RNCP         | Couverture |
| --------------------- | ---------- |
| Sources hétérogènes   | Oui        |
| Collecte sécurisée    | Oui        |
| ETL automatisé        | Oui        |
| Nettoyage & qualité   | Oui        |
| Modèle de données     | Oui        |
| Visualisation         | Oui        |
| Exploitation IA-ready | Oui        |

