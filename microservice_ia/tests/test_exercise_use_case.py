from app.application.use_cases.recommend_exercises import RecommendExercisesUseCase
from app.domain.entities.user_profile import UserProfile
from app.infrastructure.adapters.rule_based_exercise_adapter import RuleBasedExerciseRecommender


def test_recommend_exercises_for_endurance():
    profile = UserProfile(
        age=28,
        sexe="F",
        taille_cm=165,
        poids_kg=60,
        niveau_activite=2,
        endurance=True,
    )
    use_case = RecommendExercisesUseCase(RuleBasedExerciseRecommender())
    result = use_case.execute(profile, limit=3)

    assert len(result.exercices) <= 3
    assert any("cardio" in ex.type_exercice for ex in result.exercices)


def test_recommend_exercises_for_force():
    profile = UserProfile(
        age=35,
        sexe="H",
        taille_cm=175,
        poids_kg=80,
        niveau_activite=4,
        force=True,
    )
    use_case = RecommendExercisesUseCase(RuleBasedExerciseRecommender())
    result = use_case.execute(profile)

    assert any(ex.type_exercice == "musculation" for ex in result.exercices)
