from datetime import date

from pydantic import BaseModel, ConfigDict


# Schéma de base pour une métrique de santé
class MetriqueSanteBase(BaseModel):
    # Date de la mesure
    date_mesure: date
    # Poids de l’utilisateur en kilogrammes (optionnel)
    poids_kg: float | None = None
    # Fréquence cardiaque en battements par minute (optionnel)
    frequence_cardiaque: int | None = None
    # Durée de sommeil en heures (optionnel)
    duree_sommeil_h: float | None = None
    # Calories brûlées sur la période (optionnel)
    calories_brulees: int | None = None
    # Nombre de pas effectués (optionnel)
    pas: int | None = None
    # Identifiant de l’utilisateur associé
    id_utilisateur: int


# Schéma utilisé lors de la création d’une métrique de santé
class MetriqueSanteCreate(MetriqueSanteBase):
    pass


# Schéma utilisé pour la mise à jour partielle d’une métrique de santé
class MetriqueSanteUpdate(BaseModel):
    # Nouvelle date de mesure
    date_mesure: date | None = None
    # Nouveau poids
    poids_kg: float | None = None
    # Nouvelle fréquence cardiaque
    frequence_cardiaque: int | None = None
    # Nouvelle durée de sommeil
    duree_sommeil_h: float | None = None
    # Nouvelles calories brûlées
    calories_brulees: int | None = None
    # Nouveau nombre de pas
    pas: int | None = None
    # Nouvel identifiant utilisateur
    id_utilisateur: int | None = None


# Schéma de réponse renvoyé par l’API
class MetriqueSanteResponse(MetriqueSanteBase):
    # Identifiant unique de la métrique
    id_metrique: int

    model_config = ConfigDict(from_attributes=True)
