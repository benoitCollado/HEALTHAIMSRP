import os
from dataclasses import dataclass
from pathlib import Path

from app.application.use_cases.adjust_session import AdjustSessionUseCase
from app.application.use_cases.generate_program import GenerateProgramUseCase
from app.application.use_cases.get_current_program import GetCurrentProgramUseCase
from app.application.use_cases.get_profile_history import GetProfileHistoryUseCase
from app.application.use_cases.recommend_calories import RecommendCaloriesUseCase
from app.application.use_cases.recommend_exercises import RecommendExercisesUseCase
from app.application.use_cases.record_session_feedback import RecordSessionFeedbackUseCase
from app.application.use_cases.update_profile_constraints import UpdateProfileConstraintsUseCase
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.exercise_recommender import ExerciseRecommenderPort
from app.domain.ports.profile_repository import ProfileRepositoryPort
from app.domain.ports.program_repository import ProgramRepositoryPort
from app.infrastructure.adapters.composite_program_generator import CompositeProgramGenerator
from app.infrastructure.adapters.mifflin_calorie_adapter import MifflinCalorieRecommender
from app.infrastructure.adapters.ml_random_forest_adapter import RandomForestExerciseRecommender
from app.infrastructure.adapters.rule_based_exercise_adapter import RuleBasedExerciseRecommender
from app.infrastructure.repositories.in_memory_repositories import (
    InMemoryProfileRepository,
    InMemoryProgramRepository,
)

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "workout_rf_bundle.pkl"


@dataclass
class AppContainer:
    recommend_calories: RecommendCaloriesUseCase
    recommend_exercises: RecommendExercisesUseCase
    generate_program: GenerateProgramUseCase
    get_current_program: GetCurrentProgramUseCase
    adjust_session: AdjustSessionUseCase
    record_session_feedback: RecordSessionFeedbackUseCase
    update_profile_constraints: UpdateProfileConstraintsUseCase
    get_profile_history: GetProfileHistoryUseCase
    profiles: ProfileRepositoryPort
    programs: ProgramRepositoryPort
    exercise_recommender: ExerciseRecommenderPort


_container: AppContainer | None = None


def _build_repositories() -> tuple[ProfileRepositoryPort, ProgramRepositoryPort]:
    if os.getenv("MONGODB_URI"):
        from app.infrastructure.persistence.mongodb.client import get_database
        from app.infrastructure.repositories.mongo_repositories import MongoProfileRepository, MongoProgramRepository

        db = get_database()
        profiles = MongoProfileRepository(db)
        programs = MongoProgramRepository(db, profiles)
        return profiles, programs

    profiles = InMemoryProfileRepository()
    programs = InMemoryProgramRepository()
    return profiles, programs


def _build_exercise_recommender() -> ExerciseRecommenderPort:
    model_path = os.getenv("ML_MODEL_PATH", str(DEFAULT_MODEL_PATH))
    use_ml = os.getenv("ML_ENABLED", "auto").lower()

    if use_ml == "false":
        return RuleBasedExerciseRecommender()

    ml_recommender = RandomForestExerciseRecommender.from_env(model_path)
    if ml_recommender is not None:
        return ml_recommender

    if use_ml == "true":
        raise FileNotFoundError(
            f"ML_ENABLED=true mais modèle introuvable : {model_path}. "
            "Lancez `python -m ml.train_random_forest`."
        )

    return RuleBasedExerciseRecommender()


def build_container() -> AppContainer:
    calorie_adapter = MifflinCalorieRecommender()
    exercise_adapter = _build_exercise_recommender()
    profiles, programs = _build_repositories()
    generator = CompositeProgramGenerator(calorie_adapter, exercise_adapter)

    return AppContainer(
        recommend_calories=RecommendCaloriesUseCase(calorie_adapter),
        recommend_exercises=RecommendExercisesUseCase(exercise_adapter),
        generate_program=GenerateProgramUseCase(generator, programs, profiles),
        get_current_program=GetCurrentProgramUseCase(programs),
        adjust_session=AdjustSessionUseCase(generator, programs),
        record_session_feedback=RecordSessionFeedbackUseCase(programs),
        update_profile_constraints=UpdateProfileConstraintsUseCase(profiles),
        get_profile_history=GetProfileHistoryUseCase(programs, profiles),
        profiles=profiles,
        programs=programs,
        exercise_recommender=exercise_adapter,
    )


def get_container() -> AppContainer:
    global _container
    if _container is None:
        _container = build_container()
    return _container


def reset_container() -> None:
    global _container
    _container = None


def profile_from_request(data) -> UserProfile:
    return UserProfile(
        age=data.age,
        sexe=data.sexe,
        taille_cm=data.taille_cm,
        poids_kg=data.poids_kg,
        niveau_activite=data.niveau_activite,
        perte_de_poids=data.perte_de_poids,
        performance=data.performance,
        endurance=data.endurance,
        force=data.force,
    )
