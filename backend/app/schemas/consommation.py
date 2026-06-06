from datetime import date

from pydantic import BaseModel, ConfigDict


# Schéma de base pour une consommation alimentaire
class ConsommationBase(BaseModel):
    # Date de la consommation
    date_consommation: date
    # Quantité consommée en grammes
    quantite_g: float
    # Calories calculées pour cette consommation
    calories_calculees: float
    # Référence vers l’aliment consommé
    id_aliment: int
    # Référence vers l’utilisateur
    id_utilisateur: int


# Schéma utilisé lors de la création d’une consommation
class ConsommationCreate(ConsommationBase):
    pass


# Schéma utilisé pour la mise à jour partielle d’une consommation
class ConsommationUpdate(BaseModel):
    # Nouvelle date de consommation
    date_consommation: date | None = None
    # Nouvelle quantité en grammes
    quantite_g: float | None = None
    # Nouvelles calories calculées
    calories_calculees: float | None = None
    # Nouvel aliment associé
    id_aliment: int | None = None
    # Nouvel utilisateur associé
    id_utilisateur: int | None = None


# Schéma de réponse renvoyé par l’API
class ConsommationResponse(ConsommationBase):
    # Identifiant unique de la consommation
    id_consommation: int

    model_config = ConfigDict(from_attributes=True)
