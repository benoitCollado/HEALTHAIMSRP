from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from app.database import Base

# Modèle SQLAlchemy représentant une consommation alimentaire
class Consommation(Base):
    # Nom de la table dans la base de données
    __tablename__ = "consommation"

    # Identifiant unique de la consommation (clé primaire)
    id_consommation = Column(Integer, primary_key=True, index=True)

    # Date de la consommation
    date_consommation = Column(Date, nullable=False)

    # Quantité consommée en grammes
    quantite_g = Column(Numeric(6, 2), nullable=False)

    # Calories calculées en fonction de la quantité consommée
    calories_calculees = Column(Numeric(6, 2), nullable=False)

    # Référence vers l’aliment consommé
    id_aliment = Column(Integer, ForeignKey("aliment.id_aliment"), nullable=False)

    # Référence vers l’utilisateur
    id_utilisateur = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
