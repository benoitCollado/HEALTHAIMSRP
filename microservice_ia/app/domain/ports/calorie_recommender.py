from abc import ABC, abstractmethod

from app.domain.entities.recommendations import CalorieRecommendation
from app.domain.entities.user_profile import UserProfile


class CalorieRecommenderPort(ABC):
    @abstractmethod
    def recommend(self, profile: UserProfile) -> CalorieRecommendation | None:
        pass
