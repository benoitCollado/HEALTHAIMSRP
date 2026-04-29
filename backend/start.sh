#!/bin/bash
set -e

python - <<'EOF'
import os, sys
from sqlalchemy import create_engine, inspect, text

url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL non défini, migrations ignorées.")
    sys.exit(0)

try:
    engine = create_engine(url, connect_args={"connect_timeout": 10})
    with engine.connect() as conn:
        tables = inspect(engine).get_table_names()
        has_alembic = "alembic_version" in tables
        has_data    = "utilisateurs" in tables

        if has_data and not has_alembic:
            # Base existante non encore gérée par Alembic → on marque sans rejouer
            print("Base existante détectée – marquage Alembic (stamp head)...")
            os.system("alembic stamp head")
        else:
            print("Application des migrations Alembic...")
            os.system("alembic upgrade head")
except Exception as e:
    print(f"Avertissement migration : {e}", file=sys.stderr)
EOF

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
