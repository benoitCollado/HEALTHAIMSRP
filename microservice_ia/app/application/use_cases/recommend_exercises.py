from app.domain.entities.recommendations import ExerciseRecommendation
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.exercise_recommender import ExerciseRecommenderPort


class RecommendExercisesUseCase:
    def __init__(self, recommender: ExerciseRecommenderPort) -> None:
        self._recommender = recommender

    def execute(self, profile: UserProfile, limit: int = 5) -> ExerciseRecommendation:
        return self._recommender.recommend(profile, limit=limit)
