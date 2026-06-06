from pydantic import BaseModel, ConfigDict


# Schéma de base pour un exercice
class ExerciceBase(BaseModel):
    # Nom de l’exercice
    nom_exercice: str
    # Type d’exercice (cardio, musculation, etc.)
    type_exercice: str
    # Niveau de difficulté de l’exercice
    niveau_difficulte: str
    # Équipement nécessaire (optionnel)
    equipement: str | None = None
    # Muscle principal travaillé (optionnel)
    muscle_principal: str | None = None


# Schéma utilisé lors de la création d’un exercice
class ExerciceCreate(ExerciceBase):
    pass


# Schéma utilisé pour la mise à jour partielle d’un exercice
class ExerciceUpdate(BaseModel):
    # Nouveau nom de l’exercice
    nom_exercice: str | None = None
    # Nouveau type d’exercice
    type_exercice: str | None = None
    # Nouveau niveau de difficulté
    niveau_difficulte: str | None = None
    # Nouvel équipement
    equipement: str | None = None
    # Nouveau muscle principal
    muscle_principal: str | None = None


# Schéma de réponse renvoyé par l’API
class ExerciceResponse(ExerciceBase):
    # Identifiant unique de l’exercice
    id_exercice: int

    model_config = ConfigDict(from_attributes=True)
