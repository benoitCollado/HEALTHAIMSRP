from pydantic import BaseModel
from datetime import date
from typing import Optional

class ActiviteBase(BaseModel):
    date_activite: date
    duree_minutes: int
    calories_depensees: float
    intensite: Optional[str] = None
    id_exercice: int
    id_utilisateur: int

class ActiviteCreate(ActiviteBase):
    pass

class ActiviteUpdate(BaseModel):
    date_activite: Optional[date] = None
    duree_minutes: Optional[int] = None
    calories_depensees: Optional[float] = None
    intensite: Optional[str] = None
    id_exercice: Optional[int] = None
    id_utilisateur: Optional[int] = None

class ActiviteResponse(ActiviteBase):
    id_activite: int

    class Config:
        from_attributes = True
