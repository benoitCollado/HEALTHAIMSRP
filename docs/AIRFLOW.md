# Documentation Apache Airflow – HealthAim

Documentation technique de l'orchestration des tâches planifiées avec Apache Airflow dans le projet HealthAim. Ce document décrit l'architecture, les DAGs, les dépendances Docker et les procédures d'administration.

---

## 1. Introduction et contexte

Le projet HealthAim est une application de suivi santé et nutritionnel. Pour automatiser certaines opérations de données (import de produits alimentaires, export de rapports), Apache Airflow a été intégré comme orchestrateur de tâches planifiées.

Airflow permet de définir des DAGs (Directed Acyclic Graphs), c'est-à-dire des workflows composés de tâches et de dépendances. Chaque DAG peut être exécuté selon une planification (cron) ou manuellement depuis l'interface web.

Cette documentation couvre uniquement la partie Airflow du projet : les services Docker nécessaires, les DAGs implémentés, leur configuration et les procédures d'administration.

---

## 2. Vue d'ensemble des DAGs

Trois DAGs sont en place, avec un flux de validation admin :

| DAG | Description | Planification | Rôle |
|-----|-------------|---------------|------|
| `fetch_openfoodfacts_france` | Import Open Food Facts → CSV intermédiaire horodaté | Tous les jours à 06:00 | Écrit `data/intermediate/import/import_YYYYMMDD_HHMMSS.csv` (status: pending) |
| `export_db_to_csv` | Export BDD → CSV intermédiaire horodaté | Tous les jours à 00:00 | Écrit `data/intermediate/export/export_YYYYMMDD_HHMMSS.csv` (status: pending) |
| `incorporation_ml` | Incorpore les CSV validés : import→BDD, export→ML | Toutes les heures | Charge les CSV avec status=validated : import→table aliment, export→dossier `data/ml/` |

**Flux de validation** : Les DAGs d'import et d'export produisent des CSV intermédiaires avec métadonnées JSON. L'interface admin permet de visualiser, modifier et valider ces CSV avant l'incorporation. Le DAG `incorporation_ml` exécute toutes les heures et charge uniquement les fichiers validés.

---

## 3. Architecture et dépendances Docker

### 3.1 Ordre de démarrage des services

Airflow repose sur plusieurs services Docker Compose qui doivent démarrer dans un ordre précis. Le service `postgres_airflow` héberge les métadonnées d'Airflow (DAGs, runs, logs). Il doit être opérationnel avant les autres. Le service `airflow-init` initialise la base de données Airflow et crée l'utilisateur administrateur ; il s'exécute une seule fois puis s'arrête. Les services `airflow-webserver` et `airflow-scheduler` dépendent de la fin réussie de `airflow-init`. Le webserver expose l'interface web sur le port 8080 ; le scheduler exécute les tâches des DAGs. Enfin, le service `export-init` prépare les permissions du dossier d'export et doit terminer avant le scheduler et le webserver.

### 3.2 Service postgres_airflow

Ce service PostgreSQL est dédié aux métadonnées d'Airflow. Il stocke la définition des DAGs, l'historique des exécutions, les variables et connexions. Il est distinct de la base PostgreSQL métier (postgres) utilisée par l'application HealthAim.

Configuration type : image `postgres:17`, utilisateur `airflow`, mot de passe `airflow`, base `airflow`. Un healthcheck avec `pg_isready -U airflow` permet à Docker Compose de considérer le service comme prêt avant de lancer les services dépendants. Le volume `airflow_db_data` persiste les données entre les redémarrages.

### 3.3 Service airflow-init

Ce service effectue l'initialisation de la base Airflow au premier démarrage. Il exécute `airflow db init` pour créer les tables, puis `airflow users create` pour créer l'utilisateur `airflow` avec le rôle Admin. La commande utilise `|| true` pour éviter l'échec si l'utilisateur existe déjà. Une fois terminé, le conteneur s'arrête. Les autres services utilisent la condition `service_completed_successfully` pour attendre cette fin.

### 3.4 Services airflow-webserver et airflow-scheduler

Le webserver sert l'interface web sur le port 8080. Le scheduler analyse les DAGs, respecte les planifications et lance les tâches. Avec le LocalExecutor, les tâches s'exécutent dans le même conteneur que le scheduler. Les deux services partagent les mêmes variables d'environnement et volumes. Des hostnames fixes (`airflow-webserver`, `airflow-scheduler`) sont définis pour que le webserver puisse récupérer les logs des tâches via le scheduler.

### 3.5 Service export-init

Ce service Alpine exécute une commande unique : création du dossier `data/export` et `chmod 777` pour permettre à Airflow d'écrire les CSV. Il s'exécute en tant que root et s'arrête immédiatement après. Les services Airflow dépendent de sa complétion pour garantir que le dossier d'export est prêt.

### 3.6 Dépendances externes

Le service `postgres` (base HealthAim) doit être démarré car les DAGs s'y connectent via la connexion `healthaim_postgres`. Le service `export-init` doit avoir terminé pour que le dossier `data/export` ait les bonnes permissions.

### 3.7 Volumes montés

Le dossier `./airflow/dags` est monté dans `/opt/airflow/dags` : les fichiers Python des DAGs sont ainsi chargés automatiquement par Airflow. Le dossier `./data/export` est monté dans `/opt/airflow/export` : c'est là que le DAG `export_db_to_csv` écrit le fichier CSV. Le volume nommé `airflow_db_data` persiste les données de `postgres_airflow`.

### 3.8 Connexion à la base HealthAim

La connexion PostgreSQL métier est fournie par la variable d'environnement `AIRFLOW_CONN_HEALTHAIM_POSTGRES`. La convention Airflow transforme cette variable en connexion nommée `healthaim_postgres` (correspondance entre le préfixe et l'identifiant). La valeur utilisée est `postgresql://healthuser:healthpass@postgres:5432/healthdb`, où `postgres` est le nom du service Docker sur le réseau interne.

---

## 4. Configuration spécifique

### 4.1 Executor et base de données

L'executor `LocalExecutor` exécute les tâches dans des processus locaux du scheduler, sans workers distants. Il convient aux environnements de développement et aux déploiements légers. La connexion à la base Airflow est définie par `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` avec l'URL PostgreSQL vers `postgres_airflow`.

### 4.2 Secret key et logs

La variable `AIRFLOW__WEBSERVER__SECRET_KEY` doit être identique sur le webserver et le scheduler. Elle sert à signer les requêtes internes lorsque le webserver récupère les logs des tâches auprès du scheduler. Sans cette clé partagée, l'utilisateur obtient une erreur 403 Forbidden lors de la consultation des logs. Une valeur par défaut est définie dans le docker-compose ; elle peut être surchargée par `AIRFLOW_SECRET_KEY` dans le fichier `.env`.

### 4.3 Hostnames et résolution des logs

Des hostnames fixes (`airflow-scheduler`, `airflow-webserver`) sont définis pour chaque conteneur. Lorsqu'une tâche s'exécute, Airflow enregistre le hostname du worker (ici le scheduler) dans la base. Pour afficher les logs, le webserver envoie une requête HTTP à ce hostname sur le port 8793. Si le hostname était l'ID du conteneur (par défaut sous Docker), le webserver ne pourrait pas le résoudre. Les hostnames fixes permettent une résolution correcte via le réseau Docker.

### 4.4 Proxy et NO_PROXY

Les variables `NO_PROXY` et `no_proxy` sont définies pour exclure les hostnames Airflow du proxy éventuellement configuré sur la machine. Sans cela, le webserver pourrait tenter de joindre le scheduler via un proxy, ce qui provoquerait des erreurs 403 ou des timeouts.

### 4.5 Providers Python

Les providers HTTP et PostgreSQL sont installés via `_PIP_ADDITIONAL_REQUIREMENTS` au démarrage des conteneurs. La bibliothèque `requests` est également installée pour les appels à l'API Open Food Facts. Ces dépendances sont ajoutées à l'image de base `apache/airflow:2.10.4-python3.11`.

### 4.6 Healthcheck et depends_on

Le service `postgres_airflow` définit un healthcheck avec `pg_isready -U airflow`. Docker exécute cette commande périodiquement ; un code de retour 0 marque le service comme healthy. Les services `airflow-init`, `airflow-webserver` et `airflow-scheduler` utilisent `condition: service_healthy` pour `postgres_airflow`, garantissant que PostgreSQL est prêt avant toute opération. Pour `airflow-init`, la condition `service_completed_successfully` assure que l'initialisation est terminée avant le démarrage du webserver et du scheduler.

---

## 5. DAG export_db_to_csv

### 5.1 Objectif et planification

Ce DAG exporte quotidiennement les données du jour précédent (consommation alimentaire, activités physiques, métriques santé) vers un fichier CSV. La planification est définie par la chaîne cron `0 0 * * *`, soit tous les jours à minuit (00:00) en temps UTC. Le fichier de sortie est `data/export/export_journalier.csv` sur l'hôte, correspondant à `/opt/airflow/export/export_journalier.csv` dans le conteneur.

### 5.2 Logique métier

La fonction `export_daily_to_csv` reçoit le `logical_date` du contexte Airflow (date logique d'exécution). La date cible pour l'export est le jour précédent. Trois requêtes SQL sont exécutées sur les tables `consommation`, `activite` et `metrique_sante` avec un filtre sur la date. Les résultats sont écrits dans un fichier CSV au format unifié avec des colonnes pour chaque type de donnée. Si le fichier existe déjà, les nouvelles lignes sont ajoutées en mode append sans répéter l'en-tête. Des permissions (chmod 644 sur le fichier, 755 sur le répertoire) sont appliquées pour faciliter la lecture du fichier.

### 5.3 Gestion des erreurs et logs

Les messages de progression sont envoyés via `print()` avec `flush=True` pour garantir leur apparition dans les logs Airflow. En cas d'exception, la traceback complète est affichée avant de propager l'erreur. Le DAG est configuré avec 2 retries et un délai de 5 minutes entre chaque tentative.

### 5.4 Exemple de code (structure principale)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from pathlib import Path
import csv

HEALTH_DB_CONN_ID = "healthaim_postgres"
EXPORT_DIR = Path("/opt/airflow/export")
EXPORT_FILENAME = "export_journalier.csv"

def export_daily_to_csv(**context):
    exec_date = context.get("logical_date") or datetime.now()
    target_date = (exec_date - timedelta(days=1)).date()
    
    pg_hook = PostgresHook(postgres_conn_id=HEALTH_DB_CONN_ID)
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    
    csv_path = EXPORT_DIR / EXPORT_FILENAME
    fieldnames = ["type", "date", "id_utilisateur", "id_consommation", ...]
    
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not csv_path.exists():
            writer.writeheader()
        
        cur.execute("SELECT ... FROM consommation WHERE date_consommation = %s", (target_date,))
        for row in cur.fetchall():
            writer.writerow({...})
        
        cur.execute("SELECT ... FROM activite WHERE date_activite = %s", (target_date,))
        for row in cur.fetchall():
            writer.writerow({...})
        
        cur.execute("SELECT ... FROM metrique_sante WHERE date_mesure = %s", (target_date,))
        for row in cur.fetchall():
            writer.writerow({...})
    
    cur.close()
    conn.close()
    return {"date": str(target_date), "rows_written": rows_written}

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="export_db_to_csv",
    default_args=default_args,
    schedule="0 0 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["export", "csv", "backup"],
) as dag:
    export_task = PythonOperator(
        task_id="export_daily_to_csv",
        python_callable=export_daily_to_csv,
    )
```

### 5.5 Tables et schéma

Le DAG lit les tables `consommation` (id_consommation, date_consommation, id_utilisateur, id_aliment, quantite_g, calories_calculees), `activite` (id_activite, date_activite, id_utilisateur, id_exercice, duree_minutes, calories_depensees, intensite) et `metrique_sante` (id_metrique, date_mesure, id_utilisateur, poids_kg, frequence_cardiaque, duree_sommeil_h, calories_brulees, pas). Le CSV produit contient une colonne `type` pour distinguer les trois sources et des colonnes communes pour tous les champs.

---

## 6. DAG fetch_openfoodfacts_france

### 6.1 Objectif et planification

Ce DAG importe des produits alimentaires vendus en France depuis l'API Open Food Facts. La planification est `0 6 * * *`, soit tous les jours à 06:00 UTC. L'objectif est d'enrichir progressivement la table `aliment` avec des produits réels, tout en respectant les limites de l'API (rate limiting).

### 6.2 API Open Food Facts

L'API utilisée est `https://world.openfoodfacts.org/api/v2/search`. Les paramètres incluent `countries_tags_en: france` pour filtrer les produits vendus en France, `page_size: 100` et `page` pour la pagination. Les champs demandés sont `code`, `product_name`, `categories` et `nutriments`. Les nutriments sont fournis pour 100 g (energy-kcal_100g, proteins_100g, carbohydrates_100g, fat_100g). Une conversion des kilojoules en kilocalories est effectuée si nécessaire (1 kcal = 4,184 kJ).

### 6.3 Logique d'insertion

Pour chaque produit, le nom est nettoyé (suppression des caractères problématiques, troncature à 50 caractères). Les valeurs nutritionnelles sont extraites ; les produits sans données nutritionnelles sont ignorés. La catégorie est dérivée du premier élément du champ `categories`. L'insertion utilise une requête avec `WHERE NOT EXISTS (SELECT 1 FROM aliment WHERE nom_aliment = %s)` pour éviter les doublons sur le nom d'aliment.

### 6.4 Exemple de code (structure principale)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
from datetime import datetime, timedelta

OFF_API_BASE = "https://world.openfoodfacts.org/api/v2"
PAGE_SIZE = 100
MAX_PAGES = 5
HEALTH_DB_CONN_ID = "healthaim_postgres"

def extract_nutriment(product, key, default=0.0):
    nutriments = product.get("nutriments") or {}
    val = nutriments.get(f"{key}_100g") or nutriments.get(key)
    return float(val) if val is not None else default

def fetch_and_insert_off_products(**context):
    pg_hook = PostgresHook(postgres_conn_id=HEALTH_DB_CONN_ID)
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    inserted, skipped, errors = 0, 0, 0
    
    for page in range(1, MAX_PAGES + 1):
        url = f"{OFF_API_BASE}/search"
        params = {
            "countries_tags_en": "france",
            "page_size": PAGE_SIZE,
            "page": page,
            "fields": "code,product_name,categories,nutriments",
        }
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        products = data.get("products") or []
        
        for p in products:
            nom = sanitize_str(p.get("product_name"))
            calories = get_calories(p)
            proteines = extract_nutriment(p, "proteins")
            glucides = extract_nutriment(p, "carbohydrates")
            lipides = extract_nutriment(p, "fat")
            if calories == 0 and proteines == 0 and glucides == 0 and lipides == 0:
                skipped += 1
                continue
            cur.execute(
                """INSERT INTO aliment (nom_aliment, calories, proteines_g, glucides_g, lipides_g, categorie)
                   SELECT %s, %s, %s, %s, %s, %s
                   WHERE NOT EXISTS (SELECT 1 FROM aliment WHERE nom_aliment = %s)""",
                (nom, calories, proteines, glucides, lipides, categorie, nom),
            )
            if cur.rowcount > 0:
                inserted += 1
    
    conn.commit()
    cur.close()
    conn.close()
    return {"inserted": inserted, "skipped": skipped, "errors": errors}

with DAG(
    dag_id="fetch_openfoodfacts_france",
    schedule="0 6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["openfoodfacts", "france", "aliment"],
) as dag:
    fetch_task = PythonOperator(
        task_id="fetch_and_insert_off_france",
        python_callable=fetch_and_insert_off_products,
        op_kwargs={"conn_id": HEALTH_DB_CONN_ID},
    )
```

### 6.5 Limites et paramètres

La constante `MAX_PAGES` est fixée à 5 pour limiter le nombre de requêtes et respecter les contraintes de l'API (environ 10 requêtes par minute recommandées). Chaque page retourne jusqu'à 100 produits. Les produits sans nutriments ou avec un nom invalide sont ignorés. Les erreurs réseau ou de parsing sont loguées sans faire échouer l'ensemble du DAG.

---

## 7. Lancement et administration

### 7.1 Démarrage des services

Depuis la racine du projet, la commande `docker compose up -d` démarre tous les services, y compris Airflow. Pour ne lancer que les services nécessaires à Airflow : `docker compose up -d postgres postgres_airflow export-init airflow-init airflow-webserver airflow-scheduler`. Le service `postgres` est requis car les DAGs s'y connectent. L'ordre de démarrage est géré par les conditions `depends_on`.

### 7.2 Premier démarrage

Lors du premier démarrage, `airflow-init` crée les tables et l'utilisateur. Les services webserver et scheduler attendent sa fin. L'interface web est accessible après quelques secondes. En cas de redémarrage, `airflow-init` peut être ignoré (il a déjà terminé) ; les services Airflow reprennent normalement.

### 7.3 Accès à l'interface web

L'URL par défaut est http://localhost:8080. Le port peut être modifié via la variable `AIRFLOW_PORT` dans le fichier `.env`. Les identifiants par défaut sont `airflow` / `airflow`. Il est recommandé de changer le mot de passe en production.

### 7.4 Commandes d'administration

Pour lister les DAGs chargés : `docker compose exec airflow-scheduler airflow dags list`. Pour détecter les erreurs d'import des DAGs : `docker compose exec airflow-scheduler airflow dags list-import-errors`. Pour consulter les logs du scheduler : `docker compose logs airflow-scheduler --tail 100`. Pour accéder à un shell dans le scheduler : `docker compose exec -it airflow-scheduler bash`. Pour consulter les logs d'une tâche directement dans le conteneur : `docker compose exec airflow-scheduler cat /opt/airflow/logs/dag_id=export_db_to_csv/run_id=.../task_id=export_daily_to_csv/attempt=1.log`.

### 7.5 Déclenchement manuel et consultation des logs

Pour lancer un DAG manuellement, ouvrir l'interface, activer le DAG avec le toggle, puis cliquer sur Trigger DAG. Pour consulter les logs d'une tâche, aller dans l'onglet Graph ou Grid, cliquer sur la tâche concernée, puis ouvrir l'onglet Log. Les logs sont servis par le scheduler ; si une erreur 403 apparaît, vérifier la configuration de la secret key et des hostnames.

### 7.6 Redémarrage et reconstruction

Pour redémarrer les services Airflow : `docker compose restart airflow-webserver airflow-scheduler`. Pour reconstruire les images sans cache : `docker compose build --no-cache` puis `docker compose up -d`. Pour forcer la recréation des conteneurs : `docker compose up -d --force-recreate`.

---

## 8. Dépannage

### 8.1 Erreur 403 Forbidden sur les logs

Cette erreur survient lorsque le webserver ne peut pas récupérer les logs auprès du scheduler. Causes fréquentes : secret key différente entre webserver et scheduler, ou hostname du scheduler non résolvable. Vérifier que `AIRFLOW__WEBSERVER__SECRET_KEY` est identique sur les deux services. Vérifier que les hostnames `airflow-scheduler` et `airflow-webserver` sont bien définis. Redémarrer les deux services après modification. Les anciens runs peuvent conserver un hostname obsolète (ID conteneur) ; lancer un nouveau run pour tester.

### 8.2 Permission denied sur le fichier CSV

Le DAG écrit dans `/opt/airflow/export/` (monté depuis `data/export/`). Si le dossier appartient à root ou a des permissions restrictives, l'utilisateur airflow ne peut pas écrire. Le service `export-init` applique `chmod 777` au démarrage. En dernier recours, exécuter manuellement : `chmod 777 data/export/` (ou `sudo chown` pour attribuer le dossier à l'utilisateur airflow).

### 8.3 DAGs non visibles dans l'interface

Si la liste des DAGs est vide, une erreur d'import Python est probable. Exécuter `docker compose exec airflow-scheduler airflow dags list-import-errors` pour afficher les erreurs. Corriger la syntaxe ou les imports dans le fichier DAG, puis redémarrer le scheduler. Vérifier également que les fichiers sont bien présents dans `airflow/dags/` et que le volume est correctement monté.

### 8.4 Erreur de résolution de nom (Failed to resolve hostname)

Si les logs indiquent une erreur de résolution pour un hostname de type ID conteneur (ex. c71cac22d13d), le webserver ne peut pas joindre le scheduler. Recréer les conteneurs avec les hostnames fixes : `docker compose up -d --force-recreate airflow-scheduler airflow-webserver`. Les runs créés avant cette modification conserveront l'ancien hostname ; seuls les nouveaux runs auront des logs accessibles.

### 8.5 Connexion à la base HealthAim échouée

Vérifier que le service `postgres` est démarré. Vérifier que la variable `AIRFLOW_CONN_HEALTHAIM_POSTGRES` est bien définie dans l'environnement du scheduler et du webserver. Tester la connexion depuis le conteneur : `docker compose exec airflow-scheduler python -c "from airflow.providers.postgres.hooks.postgres import PostgresHook; h = PostgresHook('healthaim_postgres'); print(h.get_conn())"`.

### 8.6 Reconstruire complètement

Pour repartir de zéro : `docker compose down`, puis `docker builder prune -f` pour vider le cache de build, puis `docker compose build --no-cache` et `docker compose up -d`. Attention : `docker compose down -v` supprimerait les volumes, y compris les métadonnées Airflow et les données PostgreSQL.

---

## 9. Structure des fichiers et références

### 9.1 Arborescence

Le dossier `airflow/` contient le sous-dossier `dags/` avec les fichiers Python des DAGs : `export_db_to_csv.py` et `fetch_openfoodfacts_france.py`. Le fichier `airflow/README.md` fournit un résumé rapide. Le dossier `data/export/` reçoit le fichier `export_journalier.csv` généré par le DAG d'export. Les services Airflow sont définis dans le `docker-compose.yml` à la racine du projet.

### 9.2 Expressions cron

La syntaxe cron utilisée par Airflow suit le format standard : minute, heure, jour du mois, mois, jour de la semaine. `0 0 * * *` signifie minute 0, heure 0, tous les jours. `0 6 * * *` signifie minute 0, heure 6, tous les jours. Le fuseau horaire par défaut est UTC.

### 9.3 Références

Documentation officielle Apache Airflow : https://airflow.apache.org/docs/. Documentation de l'API Open Food Facts : https://wiki.openfoodfacts.org/API. Documentation Docker Compose sur depends_on et conditions : https://docs.docker.com/compose/compose-file/compose-file-v3/#depends_on. Configuration Airflow (secret key, executor, etc.) : https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html.
