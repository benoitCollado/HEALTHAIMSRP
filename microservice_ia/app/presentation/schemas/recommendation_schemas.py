from pydantic import BaseModel, Field


class ProfileRequest(BaseModel):
    age: int = Field(..., gt=0, le=120)
    sexe: str = Field(..., pattern="^(H|F|A)$", description="H, F ou A (autre)")
    taille_cm: float = Field(..., gt=0)
    poids_kg: float = Field(..., gt=0)
    niveau_activite: int = Field(..., ge=1, le=5)
    perte_de_poids: bool = False
    performance: bool = False
    endurance: bool = False
    force: bool = False


class CalorieRecommendationResponse(BaseModel):
    calories: int
    metabolisme_basal: int
    detail: str


class ExerciseRecommendationItemResponse(BaseModel):
    nom_exercice: str
    type_exercice: str
    niveau_difficulte: str
    equipement: str | None
    muscle_principal: str | None
    score: float
    justification: str


class ExerciseRecommendationResponse(BaseModel):
    exercices: list[ExerciseRecommendationItemResponse]
    detail: str


class ExerciseRecommendationRequest(ProfileRequest):
    limit: int = Field(default=5, ge=1, le=10)
