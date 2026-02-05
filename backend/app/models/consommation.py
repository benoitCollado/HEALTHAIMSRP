from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from database import Base

class Consommation(Base):
    __tablename__ = "consommation"

    id_consommation = Column(Integer, primary_key=True, index=True)
    date_consommation = Column(Date, nullable=False)
    quantite_g = Column(Numeric(6, 2), nullable=False)
    calories_calculees = Column(Numeric(6, 2), nullable=False)

    id_aliment = Column(Integer, ForeignKey("aliment.id_aliment"), nullable=False)
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
