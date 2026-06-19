from abc import ABC, abstractmethod

from app.domain.entities.profile_record import ProfileConstraints, UserProfileRecord
from app.domain.entities.user_profile import UserProfile


class ProfileRepositoryPort(ABC):
    @abstractmethod
    def get(self, user_id: int) -> UserProfileRecord | None:
        pass

    @abstractmethod
    def upsert_profile(self, user_id: int, profile: UserProfile) -> UserProfileRecord:
        pass

    @abstractmethod
    def update_constraints(self, user_id: int, constraints: ProfileConstraints) -> UserProfileRecord:
        pass
