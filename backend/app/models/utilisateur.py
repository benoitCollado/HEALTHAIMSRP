from sqlalchemy import Column, Integer, String, Date, Boolean
from app.database import Base

# Modèle SQLAlchemy représentant un utilisateur de l’application
class Utilisateur(Base):
    # Nom de la table dans la base de données
    __tablename__ = "utilisateurs"

    # Identifiant unique de l’utilisateur (clé primaire)
    id_utilisateur = Column(Integer, primary_key=True, index=True)

    # Nom d’utilisateur unique pour la connexion
    username = Column(String(50), unique=True, nullable=False)

    # Mot de passe chiffré (hashé), jamais stocké en clair
    password_hash = Column(String(255), nullable=False)

    # Âge de l’utilisateur
    age = Column(Integer, nullable=False)

    # Sexe de l’utilisateur (ex: H / F)
    sexe = Column(String(1), nullable=False)

    # Taille en centimètres
    taille_cm = Column(Integer, nullable=False)

    # Poids en kilogrammes
    poids_kg = Column(Integer, nullable=False)

    # Niveau d’activité physique (ex: 1 à 5)
    niveau_activite = Column(Integer, nullable=False)

    # Type d’abonnement (ex: gratuit, premium)
    type_abonnement = Column(Integer, nullable=False)

    # Date d’inscription de l’utilisateur
    date_inscription = Column(Date, nullable=False)

    # Indique si l’utilisateur a les droits administrateur
    is_admin = Column(Boolean, nullable=False, default=False)
