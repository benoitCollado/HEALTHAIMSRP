from pydantic import BaseModel
from datetime import date
from typing import Optional

class ObjectifBase(BaseModel):
    type_objectif: str
    description: str
    date_debut: date
    date_fin: date
    statut: str
    id_utilisateur: int

class ObjectifCreate(ObjectifBase):
    pass

class ObjectifUpdate(BaseModel):
    type_objectif: Optional[str] = None
    description: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    id_utilisateur: Optional[int] = None

class ObjectifResponse(ObjectifBase):
    id_objectif: int

    class Config:
        from_attributes = True
