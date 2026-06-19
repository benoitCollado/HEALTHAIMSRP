from fastapi import APIRouter, Depends, HTTPException

from app.presentation.dependencies import AppContainer, get_container, profile_from_request
from app.presentation.schemas.recommendation_schemas import (
    CalorieRecommendationResponse,
    ExerciseRecommendationRequest,
    ExerciseRecommendationResponse,
    ExerciseRecommendationItemResponse,
    ProfileRequest,
)

router = APIRouter(tags=["Recommandations IA"])


@router.post(
    "/recommandation_calorique",
    response_model=CalorieRecommendationResponse,
    summary="Recommandation calorique journalière",
)
def recommandation_calorique(
    payload: ProfileRequest,
    container: AppContainer = Depends(get_container),
) -> CalorieRecommendationResponse:
    profile = profile_from_request(payload)
    result = container.recommend_calories.execute(profile)
    if result is None:
        raise HTTPException(status_code=422, detail="Profil incomplet pour le calcul calorique.")
    return CalorieRecommendationResponse(
        calories=result.calories,
        metabolisme_basal=result.metabolisme_basal,
        detail=result.detail,
    )


@router.post(
    "/recommandation_exercice",
    response_model=ExerciseRecommendationResponse,
    summary="Recommandation d'exercices personnalisés",
)
def recommandation_exercice(
    payload: ExerciseRecommendationRequest,
    container: AppContainer = Depends(get_container),
) -> ExerciseRecommendationResponse:
    profile = profile_from_request(payload)
    result = container.recommend_exercises.execute(profile, limit=payload.limit)
    return ExerciseRecommendationResponse(
        exercices=[
            ExerciseRecommendationItemResponse(
                nom_exercice=item.nom_exercice,
                type_exercice=item.type_exercice,
                niveau_difficulte=item.niveau_difficulte,
                equipement=item.equipement,
                muscle_principal=item.muscle_principal,
                score=item.score,
                justification=item.justification,
            )
            for item in result.exercices
        ],
        detail=result.detail,
    )
