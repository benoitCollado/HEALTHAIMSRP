# Rapport technique – HealthAI Coach

**Mémoire du projet** – Contexte, choix technologiques, résultats, difficultés et perspectives

---

## 1. Contexte et objectifs

### 1.1 Contexte

HealthAI Coach est une application de suivi santé et nutritionnel développée pour la startup HealthAI. Le projet vise à fournir une plateforme complète permettant de collecter, stocker, exploiter et visualiser des données utilisateurs (nutrition, activité physique, métriques de santé) dans une logique industrielle et reproductible.

### 1.2 Objectifs du projet

Les objectifs principaux étaient :

- **Collecte et ingestion** : Intégrer des sources de données hétérogènes (CSV, API externes) avec des pipelines automatisés.
- **Qualité des données** : Appliquer des règles de nettoyage et d’homogénéisation pour garantir la fiabilité des données.
- **Stockage relationnel** : Mettre en place une base PostgreSQL structurée et normalisée.
- **Exposition API** : Offrir une API REST sécurisée, documentée et testée.
- **Interface d’administration** : Proposer un tableau de bord interactif pour visualiser les flux, les anomalies, les KPIs et exporter les données nettoyées.
- **Accessibilité** : Respecter les standards RGAA niveau AA pour l’interface web.

---

## 2. Choix technologiques

### 2.1 Stack globale

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Backend API** | FastAPI (Python 3.11) | Performance, documentation OpenAPI native, typage fort, écosystème asynchrone |
| **Base de données** | PostgreSQL 17 | Fiabilité, support JSON, contraintes et clés étrangères |
| **ORM** | SQLAlchemy | Abstraction SQL, migrations, compatibilité PostgreSQL |
| **Authentification** | JWT (python-jose) + bcrypt | Standard, stateless, mots de passe hashés |
| **Frontend** | Vue.js 3 + TypeScript | Réactivité, composants, écosystème mature |
| **Orchestration ETL** | Apache Airflow 2.10 | Planification cron, DAGs, logs et retry intégrés |
| **Conteneurisation** | Docker / Docker Compose | Reproductibilité, isolation, déploiement simplifié |

### 2.2 Architecture des flux de données

Le flux de données suit une architecture en trois zones :

1. **Zone brute** : fichiers CSV sources (Daily Food, Diet Recommendations, Exercise Tracker) et API Open Food Facts.
2. **Zone nettoyée** : scripts Python (`clean_csv_data.py`) appliquent des règles de qualité, puis `seed_db.py` charge les données dans PostgreSQL.
3. **Zone exposée** : API REST FastAPI et interface Vue.js consomment les données.

L’orchestration Airflow assure deux tâches planifiées :

- **fetch_openfoodfacts_france** : import quotidien (6h00) des produits Open Food Facts vendus en France vers la table `aliment`.
- **export_db_to_csv** : export quotidien (minuit) des consommations, activités et métriques vers un fichier CSV consolidé.

### 2.3 Sécurité

- Mots de passe hashés avec bcrypt.
- JWT signé avec une clé secrète (`SECRET_KEY`).
- Rôles admin / utilisateur avec vérification côté backend.
- Variables sensibles dans `.env` (non versionné).
- CORS configuré pour le frontend.

---

## 3. Résultats obtenus

### 3.1 API REST

L’API expose les endpoints suivants :

| Ressource | Endpoints | Rôle admin requis |
|-----------|-----------|-------------------|
| Utilisateurs | CRUD, register | Création/modification/suppression |
| Aliments | CRUD | Non |
| Exercices | CRUD | Non |
| Consommations | CRUD | Non |
| Activités | CRUD | Non |
| Métriques santé | CRUD | Non |
| Objectifs | CRUD | Non |
| Admin | `/admin/dashboard`, `/admin/flux`, `/admin/anomalies`, `/admin/utilisateurs`, `/admin/export` | Oui |

La documentation OpenAPI est disponible sur `/docs` (Swagger UI). Les tests Pytest couvrent l’authentification, les rôles et les routes principales.

### 3.2 Interface d’administration

L’interface web comprend :

- **Dashboard** : KPIs (qualité des données, progression utilisateurs, tendances nutrition/activité, objectifs, KPIs business).
- **Gestion des flux** : visualisation des flux ETL (DAGs Airflow : import Open Food Facts, export CSV) avec métadonnées des données en base (consommations, activités, métriques).
- **Nettoyage** : liste des anomalies (objectifs refusés, consommations invalides, métriques aberrantes), validation/correction, export CSV.
- **Utilisateurs** : recherche par nom d’utilisateur, liste avec statistiques, détail des données par utilisateur (consommations, activités, métriques, objectifs).

L’accessibilité RGAA (niveau AA) est prise en compte : lien d’évitement, focus visible, labels ARIA, structure sémantique, contraste.

### 3.3 Pipelines ETL

- **Nettoyage** : `clean_csv_data.py` traite les CSV sources (valeurs manquantes, types, doublons).
- **Import initial** : `seed_db.py` charge les données nettoyées dans PostgreSQL (aliments, utilisateurs, exercices, activités, consommations).
- **Import quotidien** : DAG Airflow `fetch_openfoodfacts_france` enrichit la base alimentaire.
- **Export quotidien** : DAG Airflow `export_db_to_csv` produit `data/export/export_journalier.csv`.

### 3.4 Base de données

- Tables : `utilisateurs`, `objectif`, `aliment`, `consommation`, `exercice`, `activite`, `metrique_sante`.
- Scripts SQL : `database/init/01_create_tables.sql` (création), `02_insert_test_data.sql` (données de test).
- Contraintes : clés étrangères, ON DELETE CASCADE, vérifications (ex. sexe).

---

## 4. Difficultés rencontrées

### 4.1 Intégration et proxy

**Problème** : Les erreurs « Unexpected token '<', "<!doctype "... is not valid JSON » indiquaient que les requêtes API renvoyaient du HTML au lieu de JSON.

**Cause** : Le frontend (nginx) ne proxyfiait pas les routes `/admin/*` vers le backend. Les requêtes tombaient sur le fallback SPA et renvoyaient `index.html`.

**Solution** : Ajout de `admin` dans la configuration nginx (`location ~ ^/(...|admin)(/.*)?$`) pour proxy vers le backend.

### 4.2 Ordre de démarrage Airflow

**Problème** : Les services Airflow (webserver, scheduler) dépendent de l’initialisation de la base Airflow et de l’utilisateur admin.

**Solution** : Service `airflow-init` exécuté une seule fois avec `service_completed_successfully`, puis `depends_on` sur les autres services. Hostnames fixes (`airflow-webserver`, `airflow-scheduler`) pour la résolution des logs.

### 4.3 Connexion Airflow → PostgreSQL métier

**Problème** : Les DAGs doivent se connecter à la base HealthAim (postgres) distincte de la base Airflow (postgres_airflow).

**Solution** : Variable `AIRFLOW_CONN_HEALTHAIM_POSTGRES` définie dans `.env` et transmise aux services Airflow.

### 4.4 Flux de données « réels » vs objectifs

**Problème** : Le cahier des charges demandait la visualisation des flux de données. Les consommations, activités et métriques sont les flux réels ; les objectifs étaient utilisés comme proxy.

**Solution** : Création d’un routeur admin `/admin/flux` qui interroge l'API Airflow pour afficher les flux ETL (DAGs fetch_openfoodfacts_france, export_db_to_csv) avec leur statut (en cours, réussis, en échec), et métadonnées des données en base (consommations, activités, métriques). Détection des anomalies sur les données réelles (consommations invalides, métriques aberrantes).

### 4.5 Export des données nettoyées

**Problème** : L’export devait exclure les anomalies (consommations avec quantités négatives, métriques hors plages réalistes).

**Solution** : Endpoint `/admin/export` avec filtres SQL sur les tables (consommations, activités, métriques, objectifs) pour ne renvoyer que les données valides.

---

## 5. Perspectives d’évolution

### 5.1 Court terme

- **Migrations de schéma** : Introduire Alembic (ou équivalent) pour versionner les schémas SQL et gérer les évolutions.
- **Schéma Merise/UML** : Documenter le modèle de données au format MCD/MLD/MPD ou UML.
- **Diagramme des flux** : Produire un diagramme visuel (Mermaid, draw.io) du cheminement des données.
- **Rapport d’inventaire** : Document structuré listant toutes les sources, formats, fréquences et règles de qualité.

### 5.2 Moyen terme

- **Tests end-to-end** : Tests Cypress ou Playwright pour valider les parcours critiques de l'interface admin.
- **CI/CD** : Pipeline GitHub Actions ou GitLab CI pour build, tests et déploiement automatisé.
- **Diagramme des flux** : Produire un diagramme visuel (Mermaid, draw.io) du cheminement des données.
- **Rapport d’inventaire** : Document structuré listant toutes les sources, formats, fréquences et règles de qualité.

### 5.3 Long terme

- **Modules IA** : Recommandations nutritionnelles, prédictions d’objectifs, détection d’anomalies par apprentissage.
- **Scalabilité** : Passage à un executor Celery pour Airflow, mise en place de workers dédiés.
- **Observabilité** : Métriques Prometheus, traces distribuées, alerting sur les échecs de DAGs.
- **Audit RGAA** : Audit complet et déclaration de conformité formelle.

---

## 6. Conclusion

Le projet HealthAI Coach a atteint les objectifs principaux : pipelines ETL opérationnels (Airflow + scripts Python), base de données relationnelle structurée, API REST sécurisée et documentée, interface d’administration avec tableau de bord, gestion des anomalies et export des données nettoyées. L’accessibilité RGAA a été prise en compte dans l’interface.

Les difficultés rencontrées (proxy nginx, ordre de démarrage Airflow, connexions multiples) ont été résolues par des ajustements de configuration et d’architecture. Les perspectives d’évolution (migrations, schémas formels, IA) permettront de renforcer la maintenabilité et la valeur métier du projet.

---

*Document rédigé dans le cadre de la mémoire du projet HealthAI Coach.*
