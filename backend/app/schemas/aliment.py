from pydantic import BaseModel
from typing import Optional

# Schéma de base pour un aliment (champs communs)
class AlimentBase(BaseModel):
    # Nom de l’aliment
    nom_aliment: str
    # Nombre de calories pour 100g (ou unité définie)
    calories: float
    # Quantité de protéines en grammes
    proteines_g: float
    # Quantité de glucides en grammes
    glucides_g: float
    # Quantité de lipides en grammes
    lipides_g: float
    # Catégorie de l’aliment (ex: fruit, viande, boisson)
    categorie: str

# Schéma utilisé lors de la création d’un aliment
class AlimentCreate(AlimentBase):
    pass

# Schéma utilisé pour la mise à jour partielle d’un aliment
class AlimentUpdate(BaseModel):
    # Nouveau nom de l’aliment (optionnel)
    nom_aliment: Optional[str] = None
    # Nouvelle valeur calorique (optionnelle)
    calories: Optional[float] = None
    # Nouvelle quantité de protéines (optionnelle)
    proteines_g: Optional[float] = None
    # Nouvelle quantité de glucides (optionnelle)
    glucides_g: Optional[float] = None
    # Nouvelle quantité de lipides (optionnelle)
    lipides_g: Optional[float] = None
    # Nouvelle catégorie (optionnelle)
    categorie: Optional[str] = None

# Schéma utilisé pour les réponses de l’API
class AlimentResponse(AlimentBase):
    # Identifiant unique de l’aliment
    id_aliment: int

    class Config:
        # Permet la conversion automatique depuis un objet SQLAlchemy
        from_attributes = True
