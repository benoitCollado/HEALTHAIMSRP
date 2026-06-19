from app.domain.entities.recommendations import CalorieRecommendation
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.calorie_recommender import CalorieRecommenderPort

ACTIVITY_FACTORS: dict[int, float] = {
    1: 1.2,
    2: 1.375,
    3: 1.55,
    4: 1.725,
    5: 1.9,
}


def _basal_metabolism(profile: UserProfile) -> int:
    sex_adjustment = -161 if profile.sexe == "F" else 5 if profile.sexe == "H" else -78
    return round(
        (10 * profile.poids_kg) + (6.25 * profile.taille_cm) - (5 * profile.age) + sex_adjustment
    )


class MifflinCalorieRecommender(CalorieRecommenderPort):
    """Adaptateur infrastructure : formule Mifflin-St Jeor (alignée sur le frontend HealthAI)."""

    def recommend(self, profile: UserProfile) -> CalorieRecommendation | None:
        if not profile.is_complete_for_calories():
            return None

        bmr = _basal_metabolism(profile)
        factor = ACTIVITY_FACTORS.get(profile.niveau_activite, ACTIVITY_FACTORS[1])
        maintenance = bmr * factor

        goal_adjustment = 0
        goal_detail = "maintien du poids"

        if profile.perte_de_poids:
            goal_adjustment = -400
            goal_detail = "objectif perte de poids"
        elif profile.performance or profile.force:
            goal_adjustment = 250
            goal_detail = "objectif performance ou force"
        elif profile.endurance:
            goal_adjustment = 150
            goal_detail = "objectif endurance"

        minimum = 1200 if profile.sexe == "F" else 1500
        calories = max(minimum, round((maintenance + goal_adjustment) / 50) * 50)

        return CalorieRecommendation(
            calories=calories,
            metabolisme_basal=bmr,
            detail=f"Estimation basée sur le profil, l'activité et {goal_detail}.",
        )
