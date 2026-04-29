from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

# Schéma de base pour un utilisateur
class UtilisateurBase(BaseModel):
    # Âge de l’utilisateur
    age: int
    # Sexe de l’utilisateur (ex: H / F)
    sexe: str
    # Taille en centimètres
    taille_cm: int
    # Poids en kilogrammes
    poids_kg: int
    # Niveau d’activité physique
    niveau_activite: int
    # Type d’abonnement
    type_abonnement: int
    # Date d’inscription
    date_inscription: date

# Schéma utilisé lors de la création d’un utilisateur
class UtilisateurCreate(UtilisateurBase):
    # Nom d’utilisateur (unique)
    username: str
    # Mot de passe en clair (sera hashé côté backend)
    password: str

# Schéma utilisé pour la mise à jour partielle d’un utilisateur
class UtilisateurUpdate(BaseModel):
    # Nouvel âge
    age: Optional[int] = None
    # Nouveau sexe
    sexe: Optional[str] = None
    # Nouvelle taille
    taille_cm: Optional[int] = None
    # Nouveau poids
    poids_kg: Optional[int] = None
    # Nouveau niveau d’activité
    niveau_activite: Optional[int] = None
    # Nouveau type d’abonnement
    type_abonnement: Optional[int] = None
    # Nouvelle date d’inscription
    date_inscription: Optional[date] = None

# Schéma de réponse renvoyé par l’API
class UtilisateurResponse(UtilisateurBase):
    # Identifiant unique de l’utilisateur
    id_utilisateur: int

    model_config = ConfigDict(from_attributes=True)
