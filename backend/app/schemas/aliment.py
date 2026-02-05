from pydantic import BaseModel
from typing import Optional

class AlimentBase(BaseModel):
    nom_aliment: str
    calories: float
    proteines_g: float
    glucides_g: float
    lipides_g: float
    categorie: str

class AlimentCreate(AlimentBase):
    pass

class AlimentUpdate(BaseModel):
    nom_aliment: Optional[str] = None
    calories: Optional[float] = None
    proteines_g: Optional[float] = None
    glucides_g: Optional[float] = None
    lipides_g: Optional[float] = None
    categorie: Optional[str] = None

class AlimentResponse(AlimentBase):
    id_aliment: int

    class Config:
        from_attributes = True
