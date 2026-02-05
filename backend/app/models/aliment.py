from sqlalchemy import Column, Integer, String, Numeric
from database import Base

class Aliment(Base):
    __tablename__ = "aliment"

    id_aliment = Column(Integer, primary_key=True, index=True)
    nom_aliment = Column(String(50), nullable=False)
    calories = Column(Numeric(6, 2), nullable=False)
    proteines_g = Column(Numeric(6, 2), nullable=False)
    glucides_g = Column(Numeric(6, 2), nullable=False)
    lipides_g = Column(Numeric(6, 2), nullable=False)
    categorie = Column(String(50), nullable=False)
