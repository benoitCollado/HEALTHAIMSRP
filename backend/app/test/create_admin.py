from datetime import date
from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.security import hash_password

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
