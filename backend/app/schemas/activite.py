from pydantic import BaseModel
from datetime import date
from typing import Optional

# Schéma de base pour une activité (champs communs)
class ActiviteBase(BaseModel):
    # Date à laquelle l’activité a été réalisée
    date_activite: date
    # Durée de l’activité en minutes
    duree_minutes: int
    # Nombre de calories dépensées pendant l’activité
    calories_depensees: float
    # Intensité de l’activité (optionnelle)
    intensite: Optional[str] = None
    # Identifiant de l’exercice associé
    id_exercice: int
    # Identifiant de l’utilisateur ayant réalisé l’activité
    id_utilisateur: int

# Schéma utilisé lors de la création d’une activité
class ActiviteCreate(ActiviteBase):
    pass

# Schéma utilisé pour la mise à jour partielle d’une activité
class ActiviteUpdate(BaseModel):
    # Nouvelle date de l’activité (optionnelle)
    date_activite: Optional[date] = None
    # Nouvelle durée en minutes (optionnelle)
    duree_minutes: Optional[int] = None
    # Nouvelle valeur de calories dépensées (optionnelle)
    calories_depensees: Optional[float] = None
    # Nouvelle intensité (optionnelle)
    intensite: Optional[str] = None
    # Nouvel exercice associé (optionnel)
    id_exercice: Optional[int] = None
    # Nouvel utilisateur associé (optionnel)
    id_utilisateur: Optional[int] = None

# Schéma utilisé pour les réponses de l’API
class ActiviteResponse(ActiviteBase):
    # Identifiant unique de l’activité
    id_activite: int

    class Config:
        # Permet la conversion automatique depuis un objet SQLAlchemy
        from_attributes = True
