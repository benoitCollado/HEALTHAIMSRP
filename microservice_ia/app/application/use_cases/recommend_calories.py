from app.domain.entities.recommendations import CalorieRecommendation
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.calorie_recommender import CalorieRecommenderPort


class RecommendCaloriesUseCase:
    def __init__(self, recommender: CalorieRecommenderPort) -> None:
        self._recommender = recommender

    def execute(self, profile: UserProfile) -> CalorieRecommendation | None:
        return self._recommender.recommend(profile)
