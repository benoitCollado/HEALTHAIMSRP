from pydantic import BaseModel
from datetime import date
from typing import Optional

class UtilisateurBase(BaseModel):
    age: int
    sexe: str
    taille_cm: int
    poids_kg: int
    niveau_activite: int
    type_abonnement: int
    date_inscription: date

class UtilisateurCreate(UtilisateurBase):
    username: str
    password: str

class UtilisateurUpdate(BaseModel):
    age: Optional[int] = None
    sexe: Optional[str] = None
    taille_cm: Optional[int] = None
    poids_kg: Optional[int] = None
    niveau_activite: Optional[int] = None
    type_abonnement: Optional[int] = None
    date_inscription: Optional[date] = None

class UtilisateurResponse(UtilisateurBase):
    id_utilisateur: int

    class Config:
        from_attributes = True
