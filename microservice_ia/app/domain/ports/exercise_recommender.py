from abc import ABC, abstractmethod

from app.domain.entities.exercise_context import ExerciseRecommendationContext
from app.domain.entities.recommendations import ExerciseRecommendation
from app.domain.entities.user_profile import UserProfile


class ExerciseRecommenderPort(ABC):
    @abstractmethod
    def recommend(
        self,
        profile: UserProfile,
        limit: int = 5,
        context: ExerciseRecommendationContext | None = None,
    ) -> ExerciseRecommendation:
        pass
