from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

# Schéma de base pour un objectif
class ObjectifBase(BaseModel):
    # Type d’objectif (ex: perte de poids, performance, santé)
    type_objectif: str
    # Description détaillée de l’objectif
    description: str
    # Date de début de l’objectif
    date_debut: date
    # Date de fin prévue de l’objectif
    date_fin: date
    # Statut de l’objectif (ex: en_cours, termine)
    statut: str
    # Identifiant de l’utilisateur associé
    id_utilisateur: int

# Schéma utilisé lors de la création d’un objectif
class ObjectifCreate(ObjectifBase):
    pass

# Schéma utilisé pour la mise à jour partielle d’un objectif
class ObjectifUpdate(BaseModel):
    # Nouveau type d’objectif
    type_objectif: Optional[str] = None
    # Nouvelle description
    description: Optional[str] = None
    # Nouvelle date de début
    date_debut: Optional[date] = None
    # Nouvelle date de fin
    date_fin: Optional[date] = None
    # Nouveau statut
    statut: Optional[str] = None
    # Nouvel identifiant utilisateur
    id_utilisateur: Optional[int] = None

# Schéma de réponse renvoyé par l’API
class ObjectifResponse(ObjectifBase):
    # Identifiant unique de l’objectif
    id_objectif: int

    model_config = ConfigDict(from_attributes=True)
