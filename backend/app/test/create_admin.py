import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.security import hash_password

db = SessionLocal()

admin = db.query(Utilisateur).filter(
    Utilisateur.username == "admin"
).first()

admin.password_hash = hash_password("admin123")
admin.is_admin = True

db.commit()
db.close()

print("Mot de passe admin hashé correctement")
