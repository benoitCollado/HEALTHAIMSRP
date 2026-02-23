from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

# Modèle SQLAlchemy représentant un objectif défini par un utilisateur
class Objectif(Base):
    # Nom de la table dans la base de données
    __tablename__ = "objectif"

    # Identifiant unique de l’objectif (clé primaire)
    id_objectif = Column(Integer, primary_key=True, index=True)

    # Type d’objectif (ex: poids, activité, nutrition)
    type_objectif = Column(String(20), nullable=False)

    # Description détaillée de l’objectif
    description = Column(String(250), nullable=False)

    # Date de début de l’objectif
    date_debut = Column(Date, nullable=False)

    # Date de fin prévue de l’objectif
    date_fin = Column(Date, nullable=False)

    # Statut de l’objectif (ex: en_cours, atteint, abandonne)
    statut = Column(String(10), nullable=False)

    # Référence vers l’utilisateur propriétaire de l’objectif
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
