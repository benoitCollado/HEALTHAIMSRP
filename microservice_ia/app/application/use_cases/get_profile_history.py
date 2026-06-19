from datetime import datetime

from app.domain.services.session_progression import compute_performance_history_score, count_completed_sessions
from app.domain.ports.profile_repository import ProfileRepositoryPort
from app.domain.ports.program_repository import ProgramRepositoryPort


class GetProfileHistoryUseCase:
    def __init__(self, programs: ProgramRepositoryPort, profiles: ProfileRepositoryPort) -> None:
        self._programs = programs
        self._profiles = profiles

    def execute(self, user_id: int, date_from: datetime | None = None, date_to: datetime | None = None):
        feedback = self._programs.list_feedback(user_id, date_from, date_to)
        profile = self._profiles.get(user_id)
        program = self._programs.get_active_program(user_id)
        return {
            "user_id": user_id,
            "profile_updated_at": profile.updated_at.isoformat() if profile else None,
            "calories_recommandees": program.calories_recommandees if program else None,
            "seances_terminees": count_completed_sessions(program) if program else 0,
            "session_courante_id": program.session_courante_id if program else None,
            "performance_history_score": compute_performance_history_score(feedback),
            "sessions_feedback": feedback,
        }
