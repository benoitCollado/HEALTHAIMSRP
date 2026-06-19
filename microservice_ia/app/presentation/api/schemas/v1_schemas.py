from datetime import datetime

from pydantic import BaseModel, Field


class BiometricProfileSchema(BaseModel):
    age: int = Field(..., gt=0, le=120)
    sexe: str = Field(..., pattern="^[HF]$")
    taille_cm: float = Field(..., gt=0)
    poids_kg: float = Field(..., gt=0)


class GenerateProgramRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    objectifs: list[str] = Field(..., min_length=1)
    niveau: int = Field(..., ge=1, le=5)
    equipements: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    disponibilite_minutes: int = Field(..., ge=15, le=180)
    seances_par_semaine: int = Field(..., ge=1, le=7)
    longueur_programme_semaines: int = Field(..., ge=1, le=52, description="Durée du programme en semaines")
    profil: BiometricProfileSchema | None = None


class SessionExerciseSchema(BaseModel):
    nom_exercice: str
    type_exercice: str
    duree_minutes: int
    series: int | None = None
    repetitions: int | None = None


class WorkoutSessionSchema(BaseModel):
    id: str
    titre: str
    duree_minutes: int
    exercices: list[SessionExerciseSchema]
    statut: str
    ajustements: list[str] = Field(default_factory=list)


class WorkoutProgramSchema(BaseModel):
    id: str
    user_id: int
    objectifs: list[str]
    longueur_programme_semaines: int
    seances_par_semaine: int
    calories_recommandees: int | None
    detail_calorique: str
    sessions: list[WorkoutSessionSchema]
    session_courante_id: str | None
    created_at: datetime


class AdjustSessionRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    fatigue: int = Field(..., ge=1, le=10)
    douleur: bool = False
    temps_partiel_minutes: int | None = Field(default=None, ge=10, le=180)


class SessionFeedbackRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    rpe: int = Field(..., ge=1, le=10)
    exercices_valides: list[str] = Field(default_factory=list)
    ressentis: str = ""


class SessionFeedbackResponse(BaseModel):
    session_id: str
    user_id: int
    rpe: int
    exercices_valides: list[str]
    ressentis: str
    recorded_at: datetime


class ProfileConstraintsRequest(BaseModel):
    equipements_dispo: list[str] = Field(default_factory=list)
    blessures_actives: list[str] = Field(default_factory=list)


class ProfileConstraintsResponse(BaseModel):
    user_id: int
    equipements_dispo: list[str]
    blessures_actives: list[str]
    updated_at: datetime


class ProfileHistoryResponse(BaseModel):
    user_id: int
    profile_updated_at: str | None
    calories_recommandees: int | None
    seances_terminees: int
    session_courante_id: str | None
    performance_history_score: float
    sessions_feedback: list[SessionFeedbackResponse]
