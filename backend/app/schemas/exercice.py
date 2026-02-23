from pydantic import BaseModel
from typing import Optional

# Schéma de base pour un exercice
class ExerciceBase(BaseModel):
    # Nom de l’exercice
    nom_exercice: str
    # Type d’exercice (cardio, musculation, etc.)
    type_exercice: str
    # Niveau de difficulté de l’exercice
    niveau_difficulte: str
    # Équipement nécessaire (optionnel)
    equipement: Optional[str] = None
    # Muscle principal travaillé (optionnel)
    muscle_principal: Optional[str] = None

# Schéma utilisé lors de la création d’un exercice
class ExerciceCreate(ExerciceBase):
    pass

# Schéma utilisé pour la mise à jour partielle d’un exercice
class ExerciceUpdate(BaseModel):
    # Nouveau nom de l’exercice
    nom_exercice: Optional[str] = None
    # Nouveau type d’exercice
    type_exercice: Optional[str] = None
    # Nouveau niveau de difficulté
    niveau_difficulte: Optional[str] = None
    # Nouvel équipement
    equipement: Optional[str] = None
    # Nouveau muscle principal
    muscle_principal: Optional[str] = None

# Schéma de réponse renvoyé par l’API
class ExerciceResponse(ExerciceBase):
    # Identifiant unique de l’exercice
    id_exercice: int

    class Config:
        # Autorise la conversion depuis un objet ORM (SQLAlchemy)
        from_attributes = True
