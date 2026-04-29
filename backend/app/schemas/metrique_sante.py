from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

# Schéma de base pour une métrique de santé
class MetriqueSanteBase(BaseModel):
    # Date de la mesure
    date_mesure: date
    # Poids de l’utilisateur en kilogrammes (optionnel)
    poids_kg: Optional[float] = None
    # Fréquence cardiaque en battements par minute (optionnel)
    frequence_cardiaque: Optional[int] = None
    # Durée de sommeil en heures (optionnel)
    duree_sommeil_h: Optional[float] = None
    # Calories brûlées sur la période (optionnel)
    calories_brulees: Optional[int] = None
    # Nombre de pas effectués (optionnel)
    pas: Optional[int] = None
    # Identifiant de l’utilisateur associé
    id_utilisateur: int

# Schéma utilisé lors de la création d’une métrique de santé
class MetriqueSanteCreate(MetriqueSanteBase):
    pass

# Schéma utilisé pour la mise à jour partielle d’une métrique de santé
class MetriqueSanteUpdate(BaseModel):
    # Nouvelle date de mesure
    date_mesure: Optional[date] = None
    # Nouveau poids
    poids_kg: Optional[float] = None
    # Nouvelle fréquence cardiaque
    frequence_cardiaque: Optional[int] = None
    # Nouvelle durée de sommeil
    duree_sommeil_h: Optional[float] = None
    # Nouvelles calories brûlées
    calories_brulees: Optional[int] = None
    # Nouveau nombre de pas
    pas: Optional[int] = None
    # Nouvel identifiant utilisateur
    id_utilisateur: Optional[int] = None

# Schéma de réponse renvoyé par l’API
class MetriqueSanteResponse(MetriqueSanteBase):
    # Identifiant unique de la métrique
    id_metrique: int

    model_config = ConfigDict(from_attributes=True)
