from sqlalchemy import Column, Integer, Date, Numeric, SmallInteger, ForeignKey
from database import Base

class MetriqueSante(Base):
    __tablename__ = "metrique_sante"

    id_metrique = Column(Integer, primary_key=True, index=True)
    date_mesure = Column(Date, nullable=False)
    poids_kg = Column(Numeric(5, 2))
    frequence_cardiaque = Column(SmallInteger)
    duree_sommeil_h = Column(Numeric(4, 2))
    calories_brulees = Column(Integer)
    pas = Column(Integer)

    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
