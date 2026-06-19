from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.domain.entities.profile_record import ProfileConstraints
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.program_generator import AdjustSessionInput, GenerateProgramInput
from app.presentation.api.mappers.v1_mappers import (
    constraints_to_schema,
    feedback_to_schema,
    history_to_schema,
    program_to_schema,
)
from app.presentation.api.schemas.v1_schemas import (
    AdjustSessionRequest,
    GenerateProgramRequest,
    ProfileConstraintsRequest,
    ProfileConstraintsResponse,
    ProfileHistoryResponse,
    SessionFeedbackRequest,
    SessionFeedbackResponse,
    WorkoutProgramSchema,
)
from app.presentation.dependencies import AppContainer, get_container

router = APIRouter(prefix="/api/v1", tags=["recommendations-v1"])


@router.post("/recommendations/generate", response_model=WorkoutProgramSchema)
def generate_program(
    payload: GenerateProgramRequest,
    container: AppContainer = Depends(get_container),
) -> WorkoutProgramSchema:
    profile = None
    if payload.profil:
        profile = UserProfile(
            age=payload.profil.age,
            sexe=payload.profil.sexe,
            taille_cm=payload.profil.taille_cm,
            poids_kg=payload.profil.poids_kg,
            niveau_activite=payload.niveau,
            perte_de_poids="perte_de_poids" in payload.objectifs or "perte" in payload.objectifs,
            endurance="endurance" in payload.objectifs,
            force="force" in payload.objectifs,
            performance="performance" in payload.objectifs,
        )
        container.profiles.upsert_profile(payload.user_id, profile)

    data = GenerateProgramInput(
        user_id=payload.user_id,
        objectifs=tuple(payload.objectifs),
        niveau=payload.niveau,
        equipements=tuple(payload.equipements),
        limitations=tuple(payload.limitations),
        disponibilite_minutes=payload.disponibilite_minutes,
        seances_par_semaine=payload.seances_par_semaine,
        longueur_programme_semaines=payload.longueur_programme_semaines,
        profile=profile,
    )
    program = container.generate_program.execute(data)
    return program_to_schema(program)


@router.get("/recommendations/current", response_model=WorkoutProgramSchema)
def get_current_program(
    user_id: int = Query(..., gt=0),
    container: AppContainer = Depends(get_container),
) -> WorkoutProgramSchema:
    program = container.get_current_program.execute(user_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Aucun programme actif pour cet utilisateur.")
    return program_to_schema(program)


@router.post("/recommendations/adjust", response_model=WorkoutProgramSchema)
def adjust_session(
    payload: AdjustSessionRequest,
    container: AppContainer = Depends(get_container),
) -> WorkoutProgramSchema:
    data = AdjustSessionInput(
        user_id=payload.user_id,
        fatigue=payload.fatigue,
        douleur=payload.douleur,
        temps_partiel_minutes=payload.temps_partiel_minutes,
    )
    program = container.adjust_session.execute(data)
    if program is None:
        raise HTTPException(status_code=404, detail="Aucun programme actif à ajuster.")
    return program_to_schema(program)


@router.post("/recommendations/sessions/{session_id}/feedback", response_model=SessionFeedbackResponse)
def record_session_feedback(
    session_id: str,
    payload: SessionFeedbackRequest,
    container: AppContainer = Depends(get_container),
) -> SessionFeedbackResponse:
    feedback = container.record_session_feedback.execute(
        session_id=session_id,
        user_id=payload.user_id,
        rpe=payload.rpe,
        exercices_valides=tuple(payload.exercices_valides),
        ressentis=payload.ressentis,
    )
    if feedback is None:
        raise HTTPException(status_code=404, detail="Séance introuvable.")
    return feedback_to_schema(feedback)


@router.put("/profiles/{profile_id}/constraints", response_model=ProfileConstraintsResponse)
def update_profile_constraints(
    profile_id: int,
    payload: ProfileConstraintsRequest,
    container: AppContainer = Depends(get_container),
) -> ProfileConstraintsResponse:
    constraints = ProfileConstraints(
        equipements_dispo=tuple(payload.equipements_dispo),
        blessures_actives=tuple(payload.blessures_actives),
    )
    record = container.update_profile_constraints.execute(profile_id, constraints)
    return constraints_to_schema(record)


@router.get("/profiles/{profile_id}/history", response_model=ProfileHistoryResponse)
def get_profile_history(
    profile_id: int,
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    container: AppContainer = Depends(get_container),
) -> ProfileHistoryResponse:
    data = container.get_profile_history.execute(profile_id, date_from, date_to)
    return history_to_schema(data)
