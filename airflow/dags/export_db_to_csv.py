import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

HEALTH_DB_CONN_ID = "healthaim_postgres"
EXPORT_DIR = Path("/opt/airflow/export")
EXPORT_FILENAME = "export_journalier.csv"


def _log(msg: str) -> None:
    print(msg, flush=True)
    sys.stdout.flush()


def export_daily_to_csv(**context):
    _log("Début export_db_to_csv")
    try:
        exec_date = context.get("logical_date") or datetime.now()
        _log(f"logical_date reçu: {exec_date} (type: {type(exec_date).__name__})")

        if hasattr(exec_date, "subtract"):
            target_date = exec_date.subtract(days=1).date()
        else:
            target_date = (exec_date - timedelta(days=1)).date()
        if hasattr(target_date, "date") and callable(getattr(target_date, "date", None)):
            target_date = target_date.date()
        _log(f"Date cible export: {target_date}")

        _log(f"Connexion à la base {HEALTH_DB_CONN_ID}...")
        pg_hook = PostgresHook(postgres_conn_id=HEALTH_DB_CONN_ID)
        conn = pg_hook.get_conn()
        cur = conn.cursor()

        _log("Création du dossier export...")
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = EXPORT_DIR / EXPORT_FILENAME
        file_exists = csv_path.exists()

        fieldnames = [
            "type", "date", "id_utilisateur",
            "id_consommation", "id_aliment", "quantite_g", "calories_calculees",
            "id_activite", "id_exercice", "duree_minutes", "calories_depensees", "intensite",
            "id_metrique", "poids_kg", "frequence_cardiaque", "duree_sommeil_h", "calories_brulees", "pas",
        ]
        rows_written = 0

        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            cur.execute(
                "SELECT id_consommation, date_consommation, id_utilisateur, id_aliment, quantite_g, calories_calculees "
                "FROM consommation WHERE date_consommation = %s",
                (target_date,),
            )
            for row in cur.fetchall():
                writer.writerow({
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
                rows_written += 1

            cur.execute(
                "SELECT id_activite, date_activite, id_utilisateur, id_exercice, duree_minutes, calories_depensees, intensite "
                "FROM activite WHERE date_activite = %s",
                (target_date,),
            )
            for row in cur.fetchall():
                writer.writerow({
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
                rows_written += 1

            cur.execute(
                "SELECT id_metrique, date_mesure, id_utilisateur, poids_kg, frequence_cardiaque, duree_sommeil_h, calories_brulees, pas "
                "FROM metrique_sante WHERE date_mesure = %s",
                (target_date,),
            )
            for row in cur.fetchall():
                writer.writerow({
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
                rows_written += 1

        cur.close()
        conn.close()

        try:
            os.chmod(EXPORT_DIR, 0o755)
            if csv_path.exists():
                os.chmod(csv_path, 0o644)
        except OSError as e:
            _log(f"chmod sur export: {e}")

        _log(f"Export journalier {target_date} : {rows_written} lignes écrites dans {csv_path}")
        return {"date": str(target_date), "rows_written": rows_written, "file": str(csv_path)}

    except Exception as e:
        import traceback
        _log(f"ERREUR export_db_to_csv: {e}")
        _log(traceback.format_exc())
        raise


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
    description="Export quotidien des données journalières (consommation, activité, métriques) vers CSV",
    schedule="0 0 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["export", "csv", "backup"],
) as dag:
    export_task = PythonOperator(
        task_id="export_daily_to_csv",
        python_callable=export_daily_to_csv,
    )
