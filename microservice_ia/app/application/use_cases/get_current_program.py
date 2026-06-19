from app.domain.entities.program import WorkoutProgram
from app.domain.services.session_progression import resolve_current_session_id
from app.domain.ports.program_repository import ProgramRepositoryPort


class GetCurrentProgramUseCase:
    def __init__(self, programs: ProgramRepositoryPort) -> None:
        self._programs = programs

    def execute(self, user_id: int):
        program = self._programs.get_active_program(user_id)
        if program is None:
            return None

        next_session_id = resolve_current_session_id(program)
        if next_session_id == program.session_courante_id:
            return program

        synced = WorkoutProgram(
            id=program.id,
            user_id=program.user_id,
            objectifs=program.objectifs,
            longueur_programme_semaines=program.longueur_programme_semaines,
            seances_par_semaine=program.seances_par_semaine,
            calories_recommandees=program.calories_recommandees,
            detail_calorique=program.detail_calorique,
            sessions=program.sessions,
            session_courante_id=next_session_id,
            created_at=program.created_at,
        )
        return self._programs.update_program(synced)
