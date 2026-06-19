from app.domain.entities.program import SessionFeedbackRecord
from app.domain.ports.program_repository import ProgramRepositoryPort


class RecordSessionFeedbackUseCase:
    def __init__(self, programs: ProgramRepositoryPort) -> None:
        self._programs = programs

    def execute(self, session_id: str, user_id: int, rpe: int, exercices_valides: tuple[str, ...], ressentis: str):
        program = self._programs.get_session(session_id)
        if program is None:
            return None
        feedback = SessionFeedbackRecord(
            session_id=session_id,
            user_id=user_id,
            rpe=rpe,
            exercices_valides=exercices_valides,
            ressentis=ressentis,
        )
        return self._programs.save_feedback(feedback)
