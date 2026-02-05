from database import SessionLocal
from models.utilisateur import Utilisateur

def main():
    db = SessionLocal()

    utilisateurs = db.query(Utilisateur).all()

    for u in utilisateurs:
        print(
            f"id={u.id_utilisateur} | age={u.age} | admin={u.is_admin}"
        )

    db.close()

if __name__ == "__main__":
    main()
