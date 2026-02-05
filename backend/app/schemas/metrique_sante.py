from pydantic import BaseModel
from datetime import date
from typing import Optional

class MetriqueSanteBase(BaseModel):
    date_mesure: date
    poids_kg: Optional[float] = None
    frequence_cardiaque: Optional[int] = None
    duree_sommeil_h: Optional[float] = None
    calories_brulees: Optional[int] = None
    pas: Optional[int] = None
    id_utilisateur: int

class MetriqueSanteCreate(MetriqueSanteBase):
    pass

class MetriqueSanteUpdate(BaseModel):
    date_mesure: Optional[date] = None
    poids_kg: Optional[float] = None
    frequence_cardiaque: Optional[int] = None
    duree_sommeil_h: Optional[float] = None
    calories_brulees: Optional[int] = None
    pas: Optional[int] = None
    id_utilisateur: Optional[int] = None

class MetriqueSanteResponse(MetriqueSanteBase):
    id_metrique: int

    class Config:
        from_attributes = True
