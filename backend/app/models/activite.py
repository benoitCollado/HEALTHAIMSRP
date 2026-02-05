from sqlalchemy import Column, Integer, Date, Numeric, String, ForeignKey
from database import Base

class Activite(Base):
    __tablename__ = "activite"

    id_activite = Column(Integer, primary_key=True, index=True)
    date_activite = Column(Date, nullable=False)
    duree_minutes = Column(Integer, nullable=False)
    calories_depensees = Column(Numeric(6, 2), nullable=False)
    intensite = Column(String(20))

    id_exercice = Column(Integer, ForeignKey("exercice.id_exercice"), nullable=False)
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
