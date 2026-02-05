from pydantic import BaseModel
from datetime import date
from typing import Optional

class ConsommationBase(BaseModel):
    date_consommation: date
    quantite_g: float
    calories_calculees: float
    id_aliment: int
    id_utilisateur: int

class ConsommationCreate(ConsommationBase):
    pass

class ConsommationUpdate(BaseModel):
    date_consommation: Optional[date] = None
    quantite_g: Optional[float] = None
    calories_calculees: Optional[float] = None
    id_aliment: Optional[int] = None
    id_utilisateur: Optional[int] = None

class ConsommationResponse(ConsommationBase):
    id_consommation: int

    class Config:
        from_attributes = True
