from datetime import datetime

from app.domain.services.session_progression import apply_session_completion
from app.domain.entities.profile_record import ProfileConstraints, UserProfileRecord
from app.domain.entities.program import SessionFeedbackRecord, WorkoutProgram, WorkoutSession
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.profile_repository import ProfileRepositoryPort
from app.domain.ports.program_repository import ProgramRepositoryPort


class InMemoryProfileRepository(ProfileRepositoryPort):
    def __init__(self) -> None:
        self._profiles: dict[int, UserProfileRecord] = {}

    def get(self, user_id: int) -> UserProfileRecord | None:
        return self._profiles.get(user_id)

    def upsert_profile(self, user_id: int, profile: UserProfile) -> UserProfileRecord:
        existing = self._profiles.get(user_id)
        record = UserProfileRecord(
            user_id=user_id,
            profile=profile,
            constraints=existing.constraints if existing else ProfileConstraints(),
            updated_at=datetime.utcnow(),
        )
        self._profiles[user_id] = record
        return record

    def update_constraints(self, user_id: int, constraints: ProfileConstraints) -> UserProfileRecord:
        existing = self._profiles.get(user_id)
        record = UserProfileRecord(
            user_id=user_id,
            profile=existing.profile if existing else None,
            constraints=constraints,
            updated_at=datetime.utcnow(),
        )
        self._profiles[user_id] = record
        return record


class InMemoryProgramRepository(ProgramRepositoryPort):
    def __init__(self) -> None:
        self._programs_by_user: dict[int, WorkoutProgram] = {}
        self._programs_by_id: dict[str, WorkoutProgram] = {}
        self._feedback: list[SessionFeedbackRecord] = []

    def save_program(self, program: WorkoutProgram) -> WorkoutProgram:
        self._programs_by_user[program.user_id] = program
        self._programs_by_id[program.id] = program
        return program

    def get_active_program(self, user_id: int) -> WorkoutProgram | None:
        return self._programs_by_user.get(user_id)

    def get_session(self, session_id: str) -> WorkoutProgram | None:
        for program in self._programs_by_id.values():
            if any(session.id == session_id for session in program.sessions):
                return program
        return None

    def update_program(self, program: WorkoutProgram) -> WorkoutProgram:
        return self.save_program(program)

    def save_feedback(self, feedback: SessionFeedbackRecord) -> SessionFeedbackRecord:
        self._feedback.append(feedback)
        program = self.get_session(feedback.session_id)
        if program:
            updated = apply_session_completion(program, feedback.session_id)
            self.save_program(updated)
        return feedback

    def list_feedback(self, user_id: int, date_from=None, date_to=None) -> list[SessionFeedbackRecord]:
        items = [item for item in self._feedback if item.user_id == user_id]
        if date_from:
            items = [item for item in items if item.recorded_at >= date_from]
        if date_to:
            items = [item for item in items if item.recorded_at <= date_to]
        return sorted(items, key=lambda item: item.recorded_at, reverse=True)
