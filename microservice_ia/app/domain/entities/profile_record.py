from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.user_profile import UserProfile


@dataclass
class ProfileConstraints:
    equipements_dispo: tuple[str, ...] = field(default_factory=tuple)
    blessures_actives: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class UserProfileRecord:
    user_id: int
    profile: UserProfile | None = None
    constraints: ProfileConstraints = field(default_factory=ProfileConstraints)
    updated_at: datetime = field(default_factory=datetime.utcnow)
