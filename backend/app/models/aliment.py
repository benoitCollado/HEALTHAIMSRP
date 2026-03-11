from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

# Modèle SQLAlchemy représentant un aliment
class Aliment(Base):
    # Nom de la table dans la base de données
    __tablename__ = "aliment"

    # Identifiant unique de l’aliment (clé primaire)
    id_aliment = Column(Integer, primary_key=True, index=True)

    # Nom de l’aliment
    nom_aliment = Column(String(50), nullable=False)

    # Nombre de calories pour l’aliment
    calories = Column(Numeric(6, 2), nullable=False)

    # Quantité de protéines (en grammes)
    proteines_g = Column(Numeric(6, 2), nullable=False)

    # Quantité de glucides (en grammes)
    glucides_g = Column(Numeric(6, 2), nullable=False)

    # Quantité de lipides (en grammes)
    lipides_g = Column(Numeric(6, 2), nullable=False)

    sucres_g = Column(Numeric(6, 2), nullable=True)
    acides_gras_satures_g = Column(Numeric(6, 2), nullable=True)

    # Catégorie de l’aliment (ex: fruit, légume, viande)
    categorie = Column(String(50), nullable=False)
