from sqlalchemy import Column, Integer, Date, Numeric, SmallInteger, ForeignKey
from app.database import Base

# Modèle SQLAlchemy représentant des métriques de santé d’un utilisateur
class MetriqueSante(Base):
    # Nom de la table dans la base de données
    __tablename__ = "metrique_sante"

    # Identifiant unique de la métrique (clé primaire)
    id_metrique = Column(Integer, primary_key=True, index=True)

    # Date de la mesure
    date_mesure = Column(Date, nullable=False)

    # Poids de l’utilisateur en kilogrammes
    poids_kg = Column(Numeric(5, 2))

    # Fréquence cardiaque (battements par minute)
    frequence_cardiaque = Column(SmallInteger)

    # Durée de sommeil en heures
    duree_sommeil_h = Column(Numeric(4, 2))

    # Calories brûlées sur la période
    calories_brulees = Column(Integer)

    # Nombre de pas effectués
    pas = Column(Integer)

    # Référence vers l’utilisateur concerné
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
