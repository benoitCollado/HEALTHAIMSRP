from dataclasses import dataclass


@dataclass(frozen=True)
class CalorieRecommendation:
    calories: int
    metabolisme_basal: int
    detail: str


@dataclass(frozen=True)
class ExerciseItem:
    nom_exercice: str
    type_exercice: str
    niveau_difficulte: str
    equipement: str | None
    muscle_principal: str | None
    score: float
    justification: str
    recommended_sets: int | None = None


@dataclass(frozen=True)
class ExerciseRecommendation:
    exercices: tuple[ExerciseItem, ...]
    detail: str
