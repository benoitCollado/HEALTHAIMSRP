"""
DAG export_db_to_csv : export BDD → CSV intermédiaire horodaté.
L'admin valide le CSV, puis incorporation_ml peut l'utiliser pour ML ou export final.
"""
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

HEALTH_DB_CONN_ID = "healthaim_postgres"
INTERMEDIATE_DIR = Path("/opt/airflow/intermediate/export")


def _log(msg: str) -> None:
    print(msg, flush=True)
    sys.stdout.flush()


def export_daily_to_csv(**context):
    exec_date = context.get("logical_date") or datetime.now()
    if hasattr(exec_date, "subtract"):
        target_date = exec_date.subtract(days=1).date()
    else:
        target_date = (exec_date - timedelta(days=1)).date()
    if hasattr(target_date, "date") and callable(getattr(target_date, "date", None)):
        target_date = target_date.date()

    ts = exec_date.strftime("%Y%m%d_%H%M%S")
    csv_path = INTERMEDIATE_DIR / f"export_{ts}.csv"
    meta_path = INTERMEDIATE_DIR / f"export_{ts}.json"

    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)

    _log(f"Export vers {csv_path} pour la date {target_date}")

    pg_hook = PostgresHook(postgres_conn_id=HEALTH_DB_CONN_ID)
    conn = pg_hook.get_conn()
    cur = conn.cursor()

    fieldnames = [
        "type", "date", "id_utilisateur",
        "id_consommation", "id_aliment", "quantite_g", "calories_calculees",
        "id_activite", "id_exercice", "duree_minutes", "calories_depensees", "intensite",
        "id_metrique", "poids_kg", "frequence_cardiaque", "duree_sommeil_h", "calories_brulees", "pas",
    ]
    rows = []

    cur.execute(
        "SELECT id_consommation, date_consommation, id_utilisateur, id_aliment, quantite_g, calories_calculees "
        "FROM consommation WHERE date_consommation = %s",
        (target_date,),
    )
    for row in cur.fetchall():
        rows.append({
            "type": "consommation",
            "date": str(row[1]),
            "id_utilisateur": row[2],
            "id_consommation": row[0],
            "id_aliment": row[3],
            "quantite_g": row[4],
            "calories_calculees": row[5],
            "id_activite": "", "id_exercice": "", "duree_minutes": "", "calories_depensees": "", "intensite": "",
            "id_metrique": "", "poids_kg": "", "frequence_cardiaque": "", "duree_sommeil_h": "", "calories_brulees": "", "pas": "",
        })

    cur.execute(
        "SELECT id_activite, date_activite, id_utilisateur, id_exercice, duree_minutes, calories_depensees, intensite "
        "FROM activite WHERE date_activite = %s",
        (target_date,),
    )
    for row in cur.fetchall():
        rows.append({
            "type": "activite",
            "date": str(row[1]),
            "id_utilisateur": row[2],
            "id_consommation": "", "id_aliment": "", "quantite_g": "", "calories_calculees": "",
            "id_activite": row[0],
            "id_exercice": row[3],
            "duree_minutes": row[4],
            "calories_depensees": row[5],
            "intensite": row[6] or "",
            "id_metrique": "", "poids_kg": "", "frequence_cardiaque": "", "duree_sommeil_h": "", "calories_brulees": "", "pas": "",
        })

    cur.execute(
        "SELECT id_metrique, date_mesure, id_utilisateur, poids_kg, frequence_cardiaque, duree_sommeil_h, calories_brulees, pas "
        "FROM metrique_sante WHERE date_mesure = %s",
        (target_date,),
    )
    for row in cur.fetchall():
        rows.append({
            "type": "metrique_sante",
            "date": str(row[1]),
            "id_utilisateur": row[2],
            "id_consommation": "", "id_aliment": "", "quantite_g": "", "calories_calculees": "",
            "id_activite": "", "id_exercice": "", "duree_minutes": "", "calories_depensees": "", "intensite": "",
            "id_metrique": row[0],
            "poids_kg": row[3] if row[3] is not None else "",
            "frequence_cardiaque": row[4] if row[4] is not None else "",
            "duree_sommeil_h": row[5] if row[5] is not None else "",
            "calories_brulees": row[6] if row[6] is not None else "",
            "pas": row[7] if row[7] is not None else "",
        })

    cur.close()
    conn.close()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "filename": csv_path.name,
        "type": "export",
        "dag_id": "export_db_to_csv",
        "run_id": context.get("run_id", ""),
        "created_at": exec_date.isoformat() if hasattr(exec_date, "isoformat") else str(exec_date),
        "target_date": str(target_date),
        "status": "pending",
        "rows": len(rows),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    _log(f"Export {target_date} : {len(rows)} lignes → {csv_path.name} (pending validation)")
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
    dag_id="export_db_to_csv",
    default_args=default_args,
    description="Export BDD → CSV intermédiaire (validation admin requise)",
    schedule="0 0 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["export", "csv", "backup"],
) as dag:
    export_task = PythonOperator(
        task_id="export_daily_to_csv",
        python_callable=export_daily_to_csv,
    )
