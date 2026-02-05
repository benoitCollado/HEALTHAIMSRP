from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id_utilisateur = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    age = Column(Integer, nullable=False)
    sexe = Column(String(1), nullable=False)
    taille_cm = Column(Integer, nullable=False)
    poids_kg = Column(Integer, nullable=False)
    niveau_activite = Column(Integer, nullable=False)
    type_abonnement = Column(Integer, nullable=False)
    date_inscription = Column(Date, nullable=False)

    is_admin = Column(Boolean, nullable=False, default=False)
