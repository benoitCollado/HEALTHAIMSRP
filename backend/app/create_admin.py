import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
from app.database import SessionLocal, engine
from app.models.utilisateur import Utilisateur
from app.security import hash_password

# Attendre que la BDD soit prête (retries pour postgres lent à démarrer)
for attempt in range(10):
    try:
        with engine.connect() as _:
            break
    except Exception:
        if attempt < 9:
            time.sleep(2)
        else:
            raise

db = SessionLocal()

admin = db.query(Utilisateur).filter(
    Utilisateur.username == "admin"
).first()

if admin is None:
    admin = Utilisateur(
        username="admin",
        password_hash=hash_password("admin123"),
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=1,
        type_abonnement=1,
        date_inscription=date.today(),
        is_admin=True
    )
    db.add(admin)
    print("Admin créé")
else:
    admin.password_hash = hash_password("admin123")
    admin.is_admin = True
    print("Admin mis à jour")

db.commit()
db.close()
