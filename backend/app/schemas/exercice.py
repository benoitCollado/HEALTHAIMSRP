from pydantic import BaseModel
from typing import Optional

class ExerciceBase(BaseModel):
    nom_exercice: str
    type_exercice: str
    niveau_difficulte: str
    equipement: Optional[str] = None
    muscle_principal: Optional[str] = None

class ExerciceCreate(ExerciceBase):
    pass

class ExerciceUpdate(BaseModel):
    nom_exercice: Optional[str] = None
    type_exercice: Optional[str] = None
    niveau_difficulte: Optional[str] = None
    equipement: Optional[str] = None
    muscle_principal: Optional[str] = None

class ExerciceResponse(ExerciceBase):
    id_exercice: int

    class Config:
        from_attributes = True
