"""
DAG incorporation_ml : exécuté toutes les heures.
Charge les CSV intermédiaires validés par l'admin :
- Import : alimente la table aliment
- Export : copie vers data/ml/ pour usage ML
"""
import csv
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

HEALTH_DB_CONN_ID = "healthaim_postgres"
INTERMEDIATE_IMPORT = Path("/opt/airflow/intermediate/import")
INTERMEDIATE_EXPORT = Path("/opt/airflow/intermediate/export")
ML_DIR = Path("/opt/airflow/ml")


def incorporate_imports(**context):
    """Charge les CSV import validés dans la table aliment."""
    conn_id = context.get("conn_id", HEALTH_DB_CONN_ID)
    pg_hook = PostgresHook(postgres_conn_id=conn_id)
    conn = pg_hook.get_conn()
    cur = conn.cursor()

    total_inserted = 0
    for meta_path in sorted(INTERMEDIATE_IMPORT.glob("import_*.json")):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if meta.get("status") != "validated":
                continue

            csv_path = meta_path.with_suffix(".csv")
            if not csv_path.exists():
                continue

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                inserted = 0
                for row in reader:
                    nom = (row.get("nom_aliment") or "").strip()[:50]
                    if not nom:
                        continue
                    try:
                        calories = float(row.get("calories", 0) or 0)
                        proteines = float(row.get("proteines_g", 0) or 0)
                        glucides = float(row.get("glucides_g", 0) or 0)
                        lipides = float(row.get("lipides_g", 0) or 0)
                        _s = row.get("sucres_g")
                        sucres = float(_s) if _s not in (None, "") else None
                        _a = row.get("acides_gras_satures_g")
                        acides_gras_satures = float(_a) if _a not in (None, "") else None
                        categorie = (row.get("categorie") or "Aliment").strip()[:50]
                    except (ValueError, TypeError):
                        continue

                    cur.execute(
                        """
                        INSERT INTO aliment (nom_aliment, calories, proteines_g, glucides_g, lipides_g, sucres_g, acides_gras_satures_g, categorie)
                        SELECT %s, %s, %s, %s, %s, %s, %s, %s
                        WHERE NOT EXISTS (SELECT 1 FROM aliment WHERE nom_aliment = %s)
                        """,
                        (nom, calories, proteines, glucides, lipides, sucres, acides_gras_satures, categorie, nom),
                    )
                    if cur.rowcount > 0:
                        inserted += 1

                conn.commit()
            total_inserted += inserted

            meta["status"] = "incorporated"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

        except Exception as e:
            import logging
            logging.error("Erreur incorporation import %s: %s", meta_path.name, e)

    cur.close()
    conn.close()
    return {"imported_rows": total_inserted}


def incorporate_exports(**context):
    """Copie les CSV export validés vers data/ml/ pour usage ML."""
    ML_DIR.mkdir(parents=True, exist_ok=True)
    total_copied = 0

    for meta_path in sorted(INTERMEDIATE_EXPORT.glob("export_*.json")):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if meta.get("status") != "validated":
                continue

            csv_path = meta_path.with_suffix(".csv")
            if not csv_path.exists():
                continue

            dest = ML_DIR / csv_path.name
            shutil.copy2(csv_path, dest)
            total_copied += 1

            meta["status"] = "incorporated"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

        except Exception as e:
            import logging
            logging.error("Erreur incorporation export %s: %s", meta_path.name, e)

    return {"export_files_copied": total_copied}


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="incorporation_ml",
    default_args=default_args,
    description="Incorpore les CSV validés : import→BDD, export→ML",
    schedule="0 * * * *",  # Toutes les heures
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["incorporation", "ml", "validation"],
) as dag:
    task_import = PythonOperator(
        task_id="incorporate_imports",
        python_callable=incorporate_imports,
    )
    task_export = PythonOperator(
        task_id="incorporate_exports",
        python_callable=incorporate_exports,
    )
    task_import >> task_export
