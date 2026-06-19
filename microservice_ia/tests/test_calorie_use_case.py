from app.application.use_cases.recommend_calories import RecommendCaloriesUseCase
from app.domain.entities.user_profile import UserProfile
from app.infrastructure.adapters.mifflin_calorie_adapter import MifflinCalorieRecommender


def test_recommend_calories_maintenance():
    profile = UserProfile(
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=3,
    )
    use_case = RecommendCaloriesUseCase(MifflinCalorieRecommender())
    result = use_case.execute(profile)

    assert result is not None
    assert result.calories == 2700
    assert result.metabolisme_basal == 1730


def test_recommend_calories_weight_loss():
    profile = UserProfile(
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=3,
        perte_de_poids=True,
    )
    use_case = RecommendCaloriesUseCase(MifflinCalorieRecommender())
    result = use_case.execute(profile)

    assert result is not None
    assert result.calories == 2300
