from sqlalchemy import Column, Integer, Date, Numeric, String, ForeignKey
from app.database import Base

# Modèle SQLAlchemy représentant une activité physique
class Activite(Base):
    # Nom de la table dans la base de données
    __tablename__ = "activite"

    # Identifiant unique de l’activité (clé primaire)
    id_activite = Column(Integer, primary_key=True, index=True)

    # Date à laquelle l’activité a été réalisée
    date_activite = Column(Date, nullable=False)

    # Durée de l’activité en minutes
    duree_minutes = Column(Integer, nullable=False)

    # Nombre de calories dépensées pendant l’activité
    calories_depensees = Column(Numeric(6, 2), nullable=False)

    # Intensité de l’activité (ex: faible, moyenne, élevée)
    intensite = Column(String(20))

    # Référence vers l’exercice associé à cette activité
    id_exercice = Column(Integer, ForeignKey("exercice.id_exercice"), nullable=False)

    # Référence vers l’utilisateur ayant effectué l’activité
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
