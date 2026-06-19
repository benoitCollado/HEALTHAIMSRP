from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class SessionExercise:
    nom_exercice: str
    type_exercice: str
    duree_minutes: int
    series: int | None = None
    repetitions: int | None = None


@dataclass
class WorkoutSession:
    id: str
    titre: str
    duree_minutes: int
    exercices: tuple[SessionExercise, ...]
    statut: str = "planifiee"
    ajustements: tuple[str, ...] = field(default_factory=tuple)

    @staticmethod
    def new_id() -> str:
        return str(uuid4())


@dataclass
class SessionFeedbackRecord:
    session_id: str
    user_id: int
    rpe: int
    exercices_valides: tuple[str, ...]
    ressentis: str
    recorded_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkoutProgram:
    id: str
    user_id: int
    objectifs: tuple[str, ...]
    longueur_programme_semaines: int
    seances_par_semaine: int
    calories_recommandees: int | None
    detail_calorique: str
    sessions: tuple[WorkoutSession, ...]
    session_courante_id: str | None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def new_id() -> str:
        return str(uuid4())
