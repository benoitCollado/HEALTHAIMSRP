from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Objectif(Base):
    __tablename__ = "objectif"

    id_objectif = Column(Integer, primary_key=True, index=True)
    type_objectif = Column(String(20), nullable=False)
    description = Column(String(250), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    statut = Column(String(10), nullable=False)

    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
