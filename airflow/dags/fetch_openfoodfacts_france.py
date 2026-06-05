"""
DAG fetch_openfoodfacts_france : import Open Food Facts → CSV intermédiaire (pas de BDD directe).
Le CSV est horodaté pour traçabilité. L'admin valide puis incorporation_ml charge en BDD.
"""

import csv
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests
from airflow.operators.python import PythonOperator

from airflow import DAG

# Configuration
OFF_API_BASE = "https://world.openfoodfacts.org/api/v2"
PAGE_SIZE = 100
MAX_PAGES = 5
INTERMEDIATE_DIR = Path("/opt/airflow/intermediate/import")


def extract_nutriment(product: dict, key: str, default: float = 0.0) -> float:
    nutriments = product.get("nutriments") or {}
    val = nutriments.get(f"{key}_100g") or nutriments.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def get_calories(product: dict) -> float:
    kcal = extract_nutriment(product, "energy-kcal")
    if kcal > 0:
        return round(kcal, 2)
    kj = extract_nutriment(product, "energy")
    if kj > 0:
        return round(kj / 4.184, 2)
    return 0.0


def sanitize_str(s: str, max_len: int = 50) -> str:
    if not s or not isinstance(s, str):
        return "Inconnu"
    s = re.sub(r"[\t\n\r]", "", s.strip())[:max_len]
    return s or "Inconnu"


def fetch_to_csv(**context):
    """
    Récupère les produits Open Food Facts et écrit dans un CSV intermédiaire horodaté.
    Pas d'insertion en BDD : l'admin valide le CSV, puis incorporation_ml charge.
    """
    run_date = context.get("logical_date") or datetime.now()
    ts = run_date.strftime("%Y%m%d_%H%M%S")
    csv_path = INTERMEDIATE_DIR / f"import_{ts}.csv"
    meta_path = INTERMEDIATE_DIR / f"import_{ts}.json"

    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
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
                sucres = round(extract_nutriment(p, "sugars"), 2)
                acides_gras_satures = round(extract_nutriment(p, "saturated-fat"), 2)

                if calories == 0 and proteines == 0 and glucides == 0 and lipides == 0:
                    skipped += 1
                    continue

                categorie = sanitize_str(p.get("categories", "").split(",")[0] if p.get("categories") else "Aliment")

                rows.append(
                    {
                        "nom_aliment": nom,
                        "calories": calories,
                        "proteines_g": proteines,
                        "glucides_g": glucides,
                        "lipides_g": lipides,
                        "sucres_g": sucres,
                        "acides_gras_satures_g": acides_gras_satures,
                        "categorie": categorie,
                    }
                )
            except Exception as e:
                logging.warning("Produit ignoré %s: %s", p.get("code"), e)
                errors += 1

    fieldnames = [
        "nom_aliment",
        "calories",
        "proteines_g",
        "glucides_g",
        "lipides_g",
        "sucres_g",
        "acides_gras_satures_g",
        "categorie",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "filename": csv_path.name,
        "type": "import",
        "dag_id": "fetch_openfoodfacts_france",
        "run_id": context.get("run_id", ""),
        "created_at": run_date.isoformat(),
        "status": "pending",
        "rows": len(rows),
        "skipped": skipped,
        "errors": errors,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logging.info("Open Food Facts France: %d lignes dans %s (pending validation)", len(rows), csv_path.name)
    return {"file": str(csv_path), "rows": len(rows), "status": "pending"}


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
    description="Import Open Food Facts → CSV intermédiaire (validation admin requise)",
    schedule="0 6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["openfoodfacts", "france", "aliment", "import"],
) as dag:
    fetch_task = PythonOperator(
        task_id="fetch_to_csv",
        python_callable=fetch_to_csv,
    )
