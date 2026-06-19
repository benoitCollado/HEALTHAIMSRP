from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExerciseRecommendationContext:
    current_fatigue_rpe: int = 5
    desired_duration_min: int = 45
    performance_history_score: float = 10.0
    equipment_available: tuple[str, ...] = field(default_factory=tuple)
    physical_limitation: str = "aucune"
    preferred_activity: str = "musculation"
