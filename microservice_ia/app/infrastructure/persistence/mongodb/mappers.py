from datetime import UTC, datetime

from bson import ObjectId

from app.domain.entities.profile_record import ProfileConstraints, UserProfileRecord
from app.domain.entities.program import SessionExercise, SessionFeedbackRecord, WorkoutProgram, WorkoutSession
from app.domain.entities.user_profile import UserProfile

LEVEL_BY_ACTIVITY: dict[int, str] = {
    1: "debutant",
    2: "debutant",
    3: "intermediaire",
    4: "avance",
    5: "expert",
}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def user_profile_to_document(user_ref: int, profile: UserProfile, constraints: ProfileConstraints) -> dict:
    return {
        "user_ref": user_ref,
        "age": profile.age,
        "biometrics": {
            "height_cm": profile.taille_cm,
            "weight_kg": profile.poids_kg,
            "sexe": profile.sexe,
        },
        "fitness_profile": {
            "level": LEVEL_BY_ACTIVITY.get(profile.niveau_activite, "intermediaire"),
            "health_goal": _resolve_health_goal(profile),
        },
        "constraints": {
            "equipment_available": list(constraints.equipements_dispo),
            "physical_limitations": list(constraints.blessures_actives),
        },
        "preferences": {
            "preferred_activities": _resolve_activities(profile),
            "default_duration_min": 45,
        },
        "updated_at": _utcnow(),
    }


def document_to_user_profile_record(doc: dict) -> UserProfileRecord:
    biometrics = doc.get("biometrics", {})
    fitness = doc.get("fitness_profile", {})
    constraints_doc = doc.get("constraints", {})
    level = fitness.get("level", "intermediaire")
    niveau = _level_to_int(level)
    goal = fitness.get("health_goal", "maintien")

    profile = UserProfile(
        age=doc.get("age", 30),
        sexe=biometrics.get("sexe", "H"),
        taille_cm=biometrics.get("height_cm", 175),
        poids_kg=biometrics.get("weight_kg", 70),
        niveau_activite=niveau,
        perte_de_poids=goal in {"perte_de_poids", "perte"},
        endurance=goal == "endurance",
        force=goal in {"force", "prise_muscle"},
        performance=goal in {"performance", "prise_muscle"},
    )
    constraints = ProfileConstraints(
        equipements_dispo=tuple(constraints_doc.get("equipment_available", [])),
        blessures_actives=tuple(constraints_doc.get("physical_limitations", [])),
    )
    updated_at = doc.get("updated_at") or doc.get("created_at") or _utcnow()
    return UserProfileRecord(
        user_id=doc["user_ref"],
        profile=profile,
        constraints=constraints,
        updated_at=updated_at,
    )


def constraints_to_document(constraints: ProfileConstraints) -> dict:
    return {
        "constraints": {
            "equipment_available": list(constraints.equipements_dispo),
            "physical_limitations": list(constraints.blessures_actives),
        },
        "updated_at": _utcnow(),
    }


def program_to_document(program: WorkoutProgram, user_oid: ObjectId) -> dict:
    target_goal = program.objectifs[0] if program.objectifs else "maintien"
    sessions_doc = []
    exercises_flat = []

    for session in program.sessions:
        session_exercises = [_session_exercise_to_plan_exercise(ex, index) for index, ex in enumerate(session.exercices)]
        exercises_flat.extend(session_exercises)
        sessions_doc.append(
            {
                "session_id": session.id,
                "title": session.titre,
                "duration_min": session.duree_minutes,
                "status": session.statut,
                "adjustments": list(session.ajustements),
                "exercises": session_exercises,
            }
        )

    return {
        "plan_ref": program.id,
        "user_id": user_oid,
        "user_ref": program.user_id,
        "generated_at": program.created_at,
        "status": "active",
        "target_goal": target_goal,
        "longueur_programme_semaines": program.longueur_programme_semaines,
        "seances_par_semaine": program.seances_par_semaine,
        "estimated_duration_min": program.sessions[0].duree_minutes if program.sessions else 45,
        "calories_recommandees": program.calories_recommandees,
        "detail_calorique": program.detail_calorique,
        "objectifs": list(program.objectifs),
        "session_courante_id": program.session_courante_id,
        "sessions": sessions_doc,
        "exercises": exercises_flat,
    }


def document_to_program(doc: dict) -> WorkoutProgram:
    sessions = tuple(_session_from_document(item) for item in doc.get("sessions", []))
    return WorkoutProgram(
        id=doc.get("plan_ref", str(doc["_id"])),
        user_id=doc["user_ref"],
        objectifs=tuple(doc.get("objectifs", [doc.get("target_goal", "maintien")])),
        longueur_programme_semaines=doc.get("longueur_programme_semaines", 1),
        seances_par_semaine=doc.get("seances_par_semaine", len(sessions) or 1),
        calories_recommandees=doc.get("calories_recommandees"),
        detail_calorique=doc.get("detail_calorique", ""),
        sessions=sessions,
        session_courante_id=doc.get("session_courante_id"),
        created_at=doc.get("generated_at", _utcnow()),
    )


def feedback_to_session_log(
    feedback: SessionFeedbackRecord,
    user_oid: ObjectId,
    plan_oid: ObjectId,
    total_exercises: int,
) -> dict:
    completion = len(feedback.exercices_valides) / total_exercises if total_exercises else 1.0
    return {
        "user_id": user_oid,
        "user_ref": feedback.user_id,
        "plan_id": plan_oid,
        "session_id": feedback.session_id,
        "session_date": feedback.recorded_at,
        "session_timestamp": int(feedback.recorded_at.timestamp()),
        "metrics_before_session": {},
        "performance_metrics": {
            "completion_rate": round(completion, 2),
            "calculated_history_score": round(feedback.rpe * 2 + completion * 10, 1),
        },
        "actual_workout_done": {
            "activity_type": "mixed",
            "total_sets_completed": len(feedback.exercices_valides),
            "post_session_rpe": feedback.rpe,
            "validated_exercises": list(feedback.exercices_valides),
            "ressentis": feedback.ressentis,
        },
    }


def session_log_to_feedback(doc: dict) -> SessionFeedbackRecord:
    actual = doc.get("actual_workout_done", {})
    return SessionFeedbackRecord(
        session_id=doc.get("session_id", ""),
        user_id=doc["user_ref"],
        rpe=actual.get("post_session_rpe", 5),
        exercices_valides=tuple(actual.get("validated_exercises", [])),
        ressentis=actual.get("ressentis", ""),
        recorded_at=doc.get("session_date", _utcnow()),
    )


def _session_exercise_to_plan_exercise(exercise: SessionExercise, index: int) -> dict:
    exercise_id = f"EXE_{index + 1:03d}"
    payload = {
        "exercise_id": exercise_id,
        "category": exercise.type_exercice,
        "name": exercise.nom_exercice,
    }
    if exercise.series is not None:
        payload["recommended_sets"] = exercise.series
    if exercise.repetitions is not None:
        payload["recommended_reps"] = exercise.repetitions
    if exercise.type_exercice == "cardio":
        payload["recommended_duration_sec"] = exercise.duree_minutes * 60
    payload["rest_seconds"] = 60 if exercise.type_exercice == "cardio" else 90
    return payload


def _session_from_document(doc: dict) -> WorkoutSession:
    exercises = tuple(_plan_exercise_to_session_exercise(item) for item in doc.get("exercises", []))
    return WorkoutSession(
        id=doc["session_id"],
        titre=doc.get("title", "Séance"),
        duree_minutes=doc.get("duration_min", 45),
        exercices=exercises,
        statut=doc.get("status", "planifiee"),
        ajustements=tuple(doc.get("adjustments", [])),
    )


def _plan_exercise_to_session_exercise(doc: dict) -> SessionExercise:
    duration_min = doc.get("recommended_duration_sec", 0) // 60 or 10
    return SessionExercise(
        nom_exercice=doc.get("name", "Exercice"),
        type_exercice=doc.get("category", "musculation"),
        duree_minutes=duration_min,
        series=doc.get("recommended_sets"),
        repetitions=doc.get("recommended_reps"),
    )


def _resolve_health_goal(profile: UserProfile) -> str:
    if profile.perte_de_poids:
        return "perte_de_poids"
    if profile.endurance:
        return "endurance"
    if profile.force:
        return "prise_muscle"
    if profile.performance:
        return "performance"
    return "maintien"


def _resolve_activities(profile: UserProfile) -> list[str]:
    activities: list[str] = []
    if profile.endurance:
        activities.append("cardio")
    if profile.force or profile.performance:
        activities.append("musculation")
    if profile.perte_de_poids:
        activities.append("hiit")
    return activities or ["cardio"]


def _level_to_int(level: str) -> int:
    mapping = {"debutant": 2, "intermediaire": 3, "avance": 4, "expert": 5}
    return mapping.get(level, 3)
