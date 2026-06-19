from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.profile_record import ProfileConstraints
from app.domain.entities.program import WorkoutProgram
from app.domain.entities.user_profile import UserProfile


@dataclass(frozen=True)
class GenerateProgramInput:
    user_id: int
    objectifs: tuple[str, ...]
    niveau: int
    equipements: tuple[str, ...]
    limitations: tuple[str, ...]
    disponibilite_minutes: int
    seances_par_semaine: int
    longueur_programme_semaines: int
    profile: UserProfile | None = None
    constraints: ProfileConstraints | None = None
    performance_history_score: float = 10.0


@dataclass(frozen=True)
class AdjustSessionInput:
    user_id: int
    fatigue: int
    douleur: bool
    temps_partiel_minutes: int | None


class ProgramGeneratorPort(ABC):
    @abstractmethod
    def generate(self, data: GenerateProgramInput) -> WorkoutProgram:
        pass

    @abstractmethod
    def adjust(self, program: WorkoutProgram, data: AdjustSessionInput) -> WorkoutProgram:
        pass
