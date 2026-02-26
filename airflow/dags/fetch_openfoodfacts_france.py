"""
DAG Airflow : import quotidien des nouveaux produits Open Food Facts vendus en France.

Exécution quotidienne à 6h00.
Récupère les produits via l'API Open Food Facts et les insère dans la table aliment.
"""

from datetime import datetime, timedelta
import logging
import re

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Configuration
OFF_API_BASE = "https://world.openfoodfacts.org/api/v2"
PAGE_SIZE = 100
MAX_PAGES = 5  # Limite pour respecter les rate limits (10 req/min)
HEALTH_DB_CONN_ID = "healthaim_postgres"

# Mapping des nutriments Open Food Facts (pour 100g)
def extract_nutriment(product: dict, key: str, default: float = 0.0) -> float:
    """Extrait une valeur nutritionnelle du produit."""
    nutriments = product.get("nutriments") or {}
    # Clés possibles : energy-kcal_100g, energy_100g (en kJ), proteins_100g, etc.
    val = nutriments.get(f"{key}_100g") or nutriments.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def get_calories(product: dict) -> float:
    """Calories pour 100g. OFF peut fournir energy-kcal_100g ou energy_100g (kJ)."""
    kcal = extract_nutriment(product, "energy-kcal")
    if kcal > 0:
        return round(kcal, 2)
    kj = extract_nutriment(product, "energy")
    if kj > 0:
        return round(kj / 4.184, 2)  # kJ -> kcal
    return 0.0


def sanitize_str(s: str, max_len: int = 50) -> str:
    """Nettoie et tronque une chaîne."""
    if not s or not isinstance(s, str):
        return "Inconnu"
    s = re.sub(r"[\t\n\r]", "", s.strip())[:max_len]
    return s or "Inconnu"


def fetch_and_insert_off_products(**context):
    """
    Récupère les produits vendus en France depuis Open Food Facts
    et les insère dans la table aliment (sans doublons sur nom_aliment).
    """
    conn_id = context.get("conn_id", HEALTH_DB_CONN_ID)
    pg_hook = PostgresHook(postgres_conn_id=conn_id)
    conn = pg_hook.get_conn()
    cur = conn.cursor()

    inserted = 0
    skipped = 0
    errors = 0

    for page in range(1, MAX_PAGES + 1):
        url = f"{OFF_API_BASE}/search"
        params = {
            "countries_tags_en": "france",
            "page_size": PAGE_SIZE,
            "page": page,
            "fields": "code,product_name,categories,nutriments",
        }
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logging.error("Erreur API Open Food Facts: %s", e)
            errors += 1
            continue

        products = data.get("products") or []
        if not products:
            break

        for p in products:
            try:
                nom = sanitize_str(p.get("product_name") or "")
                if nom == "Inconnu":
                    skipped += 1
                    continue

                calories = get_calories(p)
                proteines = round(extract_nutriment(p, "proteins"), 2)
                glucides = round(extract_nutriment(p, "carbohydrates"), 2)
                lipides = round(extract_nutriment(p, "fat"), 2)

                # Ignorer les produits sans données nutritionnelles
                if calories == 0 and proteines == 0 and glucides == 0 and lipides == 0:
                    skipped += 1
                    continue

                categorie = sanitize_str(
                    p.get("categories", "").split(",")[0] if p.get("categories") else "Aliment"
                )

                # Insertion si pas déjà présent (ON CONFLICT ou check)
                cur.execute(
                    """
                    INSERT INTO aliment (nom_aliment, calories, proteines_g, glucides_g, lipides_g, categorie)
                    SELECT %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM aliment WHERE nom_aliment = %s)
                    """,
                    (nom, calories, proteines, glucides, lipides, categorie, nom),
                )
                if cur.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                logging.warning("Produit ignoré %s: %s", p.get("code"), e)
                errors += 1

    conn.commit()
    cur.close()
    conn.close()

    logging.info(
        "Open Food Facts France: %d insérés, %d ignorés, %d erreurs",
        inserted, skipped, errors,
    )
    return {"inserted": inserted, "skipped": skipped, "errors": errors}


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fetch_openfoodfacts_france",
    default_args=default_args,
    description="Import quotidien des nouveaux produits Open Food Facts vendus en France",
    schedule="0 6 * * *",  # Tous les jours à 6h00 (cron)
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["openfoodfacts", "france", "aliment"],
) as dag:
    fetch_task = PythonOperator(
        task_id="fetch_and_insert_off_france",
        python_callable=fetch_and_insert_off_products,
        op_kwargs={"conn_id": HEALTH_DB_CONN_ID},
    )
