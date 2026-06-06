from datetime import date

from pydantic import BaseModel, ConfigDict


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
    age: int | None = None
    # Nouveau sexe
    sexe: str | None = None
    # Nouvelle taille
    taille_cm: int | None = None
    # Nouveau poids
    poids_kg: int | None = None
    # Nouveau niveau d’activité
    niveau_activite: int | None = None
    # Nouveau type d’abonnement
    type_abonnement: int | None = None
    # Nouvelle date d’inscription
    date_inscription: date | None = None


# Schéma de réponse renvoyé par l’API
class UtilisateurResponse(UtilisateurBase):
    # Identifiant unique de l’utilisateur
    id_utilisateur: int

    model_config = ConfigDict(from_attributes=True)
