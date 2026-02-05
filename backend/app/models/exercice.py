from sqlalchemy import Column, Integer, String
from app.database import Base

class Exercice(Base):
    __tablename__ = "exercice"

    id_exercice = Column(Integer, primary_key=True, index=True)
    nom_exercice = Column(String(100), nullable=False)
    type_exercice = Column(String(50), nullable=False)
    niveau_difficulte = Column(String(20), nullable=False)
    equipement = Column(String(50))
    muscle_principal = Column(String(30))
