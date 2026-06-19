import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Classe de base pour tous les modèles SQLAlchemy
Base = declarative_base()

# Récupération de l’URL de la base de données depuis les variables d’environnement
DATABASE_URL = os.getenv("DATABASE_URL")

# Création du moteur de connexion à la base de données
engine_options = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    engine_options.update(
        {
            "pool_size": 2,
            "max_overflow": 5,
            "connect_args": {"connect_timeout": 5},
        }
    )

engine = create_engine(DATABASE_URL, **engine_options)

# Fabrique de sessions pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fonction simple pour tester la connexion à la base de données
def test_connection():
    try:
        # Tentative d’ouverture d’une connexion
        with engine.connect():
            return True
    except Exception:
        # Retourne False si la connexion échoue
        return False
