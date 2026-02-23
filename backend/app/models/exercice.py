from sqlalchemy import Column, Integer, String
from app.database import Base

# Modèle SQLAlchemy représentant un exercice physique
class Exercice(Base):
    # Nom de la table dans la base de données
    __tablename__ = "exercice"

    # Identifiant unique de l’exercice (clé primaire)
    id_exercice = Column(Integer, primary_key=True, index=True)

    # Nom de l’exercice
    nom_exercice = Column(String(100), nullable=False)

    # Type d’exercice (cardio, musculation, etc.)
    type_exercice = Column(String(50), nullable=False)

    # Niveau de difficulté de l’exercice
    niveau_difficulte = Column(String(20), nullable=False)

    # Équipement nécessaire pour l’exercice (optionnel)
    equipement = Column(String(50))

    # Muscle principal sollicité par l’exercice (optionnel)
    muscle_principal = Column(String(30))
