from dataclasses import dataclass

from app.domain.entities.exercise_context import ExerciseRecommendationContext
from app.domain.entities.recommendations import ExerciseItem, ExerciseRecommendation
from app.domain.entities.user_profile import UserProfile
from app.domain.ports.exercise_recommender import ExerciseRecommenderPort


@dataclass(frozen=True)
class CatalogExercise:
    nom_exercice: str
    type_exercice: str
    niveau_difficulte: str
    equipement: str | None
    muscle_principal: str | None
    tags: frozenset[str]


DEFAULT_CATALOG: tuple[CatalogExercise, ...] = (
    CatalogExercise("Marche rapide", "cardio", "debutant", None, "jambes", frozenset({"cardio", "perte", "endurance"})),
    CatalogExercise("Course à pied", "cardio", "intermediaire", "chaussures running", "jambes", frozenset({"cardio", "endurance", "perte"})),
    CatalogExercise("Vélo", "cardio", "debutant", "vélo", "jambes", frozenset({"cardio", "endurance", "perte"})),
    CatalogExercise("Natation", "cardio", "intermediaire", "piscine", "corps entier", frozenset({"cardio", "endurance"})),
    CatalogExercise("HIIT", "cardio", "avance", None, "corps entier", frozenset({"cardio", "perte", "performance"})),
    CatalogExercise("Squats", "musculation", "debutant", None, "jambes", frozenset({"force", "performance"})),
    CatalogExercise("Pompes", "musculation", "debutant", None, "pectoraux", frozenset({"force", "performance"})),
    CatalogExercise("Tractions", "musculation", "avance", "barre", "dos", frozenset({"force", "performance"})),
    CatalogExercise("Étirements", "souplesse", "debutant", "tapis", "corps entier", frozenset({"recuperation"})),
    CatalogExercise("Gainage planche", "musculation", "intermediaire", "tapis", "abdominaux", frozenset({"force", "performance"})),
)

DIFFICULTY_BY_ACTIVITY: dict[int, set[str]] = {
    1: {"debutant"},
    2: {"debutant", "intermediaire"},
    3: {"debutant", "intermediaire"},
    4: {"debutant", "intermediaire", "avance"},
    5: {"debutant", "intermediaire", "avance"},
}


class RuleBasedExerciseRecommender(ExerciseRecommenderPort):
    """Adaptateur infrastructure : scoring rule-based sur un catalogue d'exercices."""

    def __init__(self, catalog: tuple[CatalogExercise, ...] = DEFAULT_CATALOG) -> None:
        self._catalog = catalog

    def recommend(
        self,
        profile: UserProfile,
        limit: int = 5,
        context: ExerciseRecommendationContext | None = None,
    ) -> ExerciseRecommendation:
        target_tags = self._resolve_target_tags(profile)
        allowed_levels = DIFFICULTY_BY_ACTIVITY.get(profile.niveau_activite, {"debutant"})

        scored: list[tuple[float, CatalogExercise, str]] = []
        for exercise in self._catalog:
            if exercise.niveau_difficulte not in allowed_levels:
                continue
            score, reason = self._score(exercise, target_tags, profile.niveau_activite)
            if score > 0:
                scored.append((score, exercise, reason))

        scored.sort(key=lambda item: item[0], reverse=True)
        top = scored[: max(1, limit)]

        if not top:
            fallback = self._catalog[0]
            items = (
                ExerciseItem(
                    nom_exercice=fallback.nom_exercice,
                    type_exercice=fallback.type_exercice,
                    niveau_difficulte=fallback.niveau_difficulte,
                    equipement=fallback.equipement,
                    muscle_principal=fallback.muscle_principal,
                    score=1.0,
                    justification="Exercice par défaut adapté à un profil débutant.",
                ),
            )
            return ExerciseRecommendation(exercices=items, detail="Recommandation par défaut (profil peu spécifique).")

        items = tuple(
            ExerciseItem(
                nom_exercice=ex.nom_exercice,
                type_exercice=ex.type_exercice,
                niveau_difficulte=ex.niveau_difficulte,
                equipement=ex.equipement,
                muscle_principal=ex.muscle_principal,
                score=round(score, 2),
                justification=reason,
            )
            for score, ex, reason in top
        )
        detail = f"{len(items)} exercice(s) recommandé(s) selon les objectifs : {', '.join(sorted(target_tags))}."
        return ExerciseRecommendation(exercices=items, detail=detail)

    @staticmethod
    def _resolve_target_tags(profile: UserProfile) -> set[str]:
        if profile.perte_de_poids:
            return {"cardio", "perte"}
        if profile.endurance:
            return {"cardio", "endurance"}
        if profile.force or profile.performance:
            return {"force", "performance"}
        return {"cardio", "recuperation"}

    @staticmethod
    def _score(exercise: CatalogExercise, target_tags: set[str], activity_level: int) -> tuple[float, str]:
        overlap = exercise.tags & target_tags
        if not overlap:
            return 0.0, ""

        score = float(len(overlap) * 2)
        if exercise.type_exercice == "cardio" and "cardio" in target_tags:
            score += 1.0
        if exercise.type_exercice == "musculation" and "force" in target_tags:
            score += 1.0
        if activity_level <= 2 and exercise.niveau_difficulte == "debutant":
            score += 0.5

        matched = ", ".join(sorted(overlap))
        reason = f"Correspond aux objectifs ({matched}) et au niveau d'activité {activity_level}."
        return score, reason
