from app.domain.entities.program import SessionFeedbackRecord, WorkoutProgram, WorkoutSession

COMPLETED_STATUSES = frozenset({"terminee"})


def next_pending_session_id(sessions: tuple[WorkoutSession, ...]) -> str | None:
    """Retourne la première séance non terminée, dans l'ordre du programme."""
    for session in sessions:
        if session.statut not in COMPLETED_STATUSES:
            return session.id
    return None


def resolve_current_session_id(program: WorkoutProgram) -> str | None:
    """Si la séance courante est déjà terminée, avance au prochain créneau."""
    if not program.session_courante_id:
        return next_pending_session_id(program.sessions)

    current = next((s for s in program.sessions if s.id == program.session_courante_id), None)
    if current and current.statut in COMPLETED_STATUSES:
        return next_pending_session_id(program.sessions)
    return program.session_courante_id


def apply_session_completion(program: WorkoutProgram, session_id: str) -> WorkoutProgram:
    """Marque une séance comme terminée et avance session_courante_id."""
    updated_sessions: list[WorkoutSession] = []
    for session in program.sessions:
        if session.id == session_id:
            updated_sessions.append(
                WorkoutSession(
                    id=session.id,
                    titre=session.titre,
                    duree_minutes=session.duree_minutes,
                    exercices=session.exercices,
                    statut="terminee",
                    ajustements=session.ajustements,
                )
            )
        else:
            updated_sessions.append(session)

    sessions_tuple = tuple(updated_sessions)
    return WorkoutProgram(
        id=program.id,
        user_id=program.user_id,
        objectifs=program.objectifs,
        longueur_programme_semaines=program.longueur_programme_semaines,
        seances_par_semaine=program.seances_par_semaine,
        calories_recommandees=program.calories_recommandees,
        detail_calorique=program.detail_calorique,
        sessions=sessions_tuple,
        session_courante_id=next_pending_session_id(sessions_tuple),
        created_at=program.created_at,
    )


def count_completed_sessions(program: WorkoutProgram) -> int:
    return sum(1 for session in program.sessions if session.statut in COMPLETED_STATUSES)


def compute_performance_history_score(feedback: list[SessionFeedbackRecord]) -> float:
    """Score de progression dérivé des feedbacks passés (alimente le modèle ML)."""
    if not feedback:
        return 10.0

    avg_rpe = sum(item.rpe for item in feedback) / len(feedback)
    avg_validated = sum(len(item.exercices_valides) for item in feedback) / len(feedback)
    score = 10.0 + (len(feedback) * 0.3) - (avg_rpe * 0.2) + (avg_validated * 0.1)
    return round(max(5.0, score), 2)
