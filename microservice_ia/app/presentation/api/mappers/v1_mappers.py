from app.domain.entities.profile_record import ProfileConstraints, UserProfileRecord
from app.domain.entities.program import SessionFeedbackRecord, WorkoutProgram, WorkoutSession
from app.presentation.api.schemas.v1_schemas import (
    ProfileConstraintsResponse,
    ProfileHistoryResponse,
    SessionExerciseSchema,
    SessionFeedbackResponse,
    WorkoutProgramSchema,
    WorkoutSessionSchema,
)


def session_to_schema(session: WorkoutSession) -> WorkoutSessionSchema:
    return WorkoutSessionSchema(
        id=session.id,
        titre=session.titre,
        duree_minutes=session.duree_minutes,
        exercices=[
            SessionExerciseSchema(
                nom_exercice=ex.nom_exercice,
                type_exercice=ex.type_exercice,
                duree_minutes=ex.duree_minutes,
                series=ex.series,
                repetitions=ex.repetitions,
            )
            for ex in session.exercices
        ],
        statut=session.statut,
        ajustements=list(session.ajustements),
    )


def program_to_schema(program: WorkoutProgram) -> WorkoutProgramSchema:
    return WorkoutProgramSchema(
        id=program.id,
        user_id=program.user_id,
        objectifs=list(program.objectifs),
        longueur_programme_semaines=program.longueur_programme_semaines,
        seances_par_semaine=program.seances_par_semaine,
        calories_recommandees=program.calories_recommandees,
        detail_calorique=program.detail_calorique,
        sessions=[session_to_schema(s) for s in program.sessions],
        session_courante_id=program.session_courante_id,
        created_at=program.created_at,
    )


def feedback_to_schema(feedback: SessionFeedbackRecord) -> SessionFeedbackResponse:
    return SessionFeedbackResponse(
        session_id=feedback.session_id,
        user_id=feedback.user_id,
        rpe=feedback.rpe,
        exercices_valides=list(feedback.exercices_valides),
        ressentis=feedback.ressentis,
        recorded_at=feedback.recorded_at,
    )


def constraints_to_schema(record: UserProfileRecord) -> ProfileConstraintsResponse:
    return ProfileConstraintsResponse(
        user_id=record.user_id,
        equipements_dispo=list(record.constraints.equipements_dispo),
        blessures_actives=list(record.constraints.blessures_actives),
        updated_at=record.updated_at,
    )


def history_to_schema(data: dict) -> ProfileHistoryResponse:
    return ProfileHistoryResponse(
        user_id=data["user_id"],
        profile_updated_at=data["profile_updated_at"],
        calories_recommandees=data["calories_recommandees"],
        seances_terminees=data["seances_terminees"],
        session_courante_id=data["session_courante_id"],
        performance_history_score=data["performance_history_score"],
        sessions_feedback=[feedback_to_schema(item) for item in data["sessions_feedback"]],
    )
