from abc import ABC, abstractmethod

from app.domain.entities.program import SessionFeedbackRecord, WorkoutProgram


class ProgramRepositoryPort(ABC):
    @abstractmethod
    def save_program(self, program: WorkoutProgram) -> WorkoutProgram:
        pass

    @abstractmethod
    def get_active_program(self, user_id: int) -> WorkoutProgram | None:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> WorkoutProgram | None:
        pass

    @abstractmethod
    def update_program(self, program: WorkoutProgram) -> WorkoutProgram:
        pass

    @abstractmethod
    def save_feedback(self, feedback: SessionFeedbackRecord) -> SessionFeedbackRecord:
        pass

    @abstractmethod
    def list_feedback(self, user_id: int, date_from=None, date_to=None) -> list[SessionFeedbackRecord]:
        pass
