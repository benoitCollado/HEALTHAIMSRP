from app.domain.entities.profile_record import ProfileConstraints
from app.domain.ports.profile_repository import ProfileRepositoryPort


class UpdateProfileConstraintsUseCase:
    def __init__(self, profiles: ProfileRepositoryPort) -> None:
        self._profiles = profiles

    def execute(self, user_id: int, constraints: ProfileConstraints):
        return self._profiles.update_constraints(user_id, constraints)
