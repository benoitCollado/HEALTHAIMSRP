from app.chat_graph import run_chat_graph
from app.dependencies import get_current_user, get_db
from app.models.objectif import Objectif
from app.models.utilisateur import Utilisateur
from app.object_storage import presigned_image_url, upload_user_image
from app.external_clients import (
    ExternalServiceAuthError,
    ExternalServiceError,
    ExternalServiceResponseError,
    build_chat_fallback_answer,
    call_microservice_ia_recommendations,
    call_photo_processing,
)
from app.cache import cache, chat_cache_ttl_seconds, stable_cache_key
from app.schemas.chat import (
    ChatImageResponse,
    ChatPhotoAnalysisRequest,
    ChatPhotoAnalysisResponse,
    ChatRecommendationResponse,
    ChatRequest,
    ChatResponse,
)
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["Chat IA"])

SYSTEM_PROMPT = """
Tu es l'assistant HealthAI MSPR.
HealthAI MSPR est une plateforme full-stack de suivi sante et d'administration
de flux de donnees. Le projet couvre la gestion des utilisateurs, aliments,
exercices, consommations, activites, metriques sante et objectifs, avec une API
securisee, une interface Vue, des pipelines Airflow, PostgreSQL manage et une
couche d'observabilite.

Reponds simplement en francais. Aide l'utilisateur sur le suivi sante, les
objectifs, l'alimentation, l'activite physique, les metriques, et l'utilisation
de la plateforme. Ne donne pas de diagnostic medical; conseille de consulter un
professionnel de sante en cas de symptome, douleur, urgence ou decision medicale.

Tu disposes d'outils microservice IA (calories, exercices, programmes, ajustements,
feedbacks, contraintes, historique). Appelle-les pour toute question liee au profil,
aux objectifs ou aux recommandations. N'invente jamais de chiffres, exercices ou seances
sans resultat d'outil.
""".strip()


def _current_user_id(user: dict) -> str:
    user_id = str(user.get("sub") or "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Utilisateur invalide")
    return user_id


def _get_user_profile(user_id: str, db: Session) -> Utilisateur:
    try:
        numeric_user_id = int(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Utilisateur invalide") from exc

    utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == numeric_user_id).first()
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return utilisateur


def _objectifs_payload(db: Session, user_id: int) -> list[dict]:
    rows = db.query(Objectif).filter(Objectif.id_utilisateur == user_id).all()
    return [
        {
            "id_objectif": row.id_objectif,
            "type_objectif": row.type_objectif,
            "description": row.description,
            "statut": row.statut,
            "date_debut": row.date_debut.isoformat() if row.date_debut else None,
            "date_fin": row.date_fin.isoformat() if row.date_fin else None,
        }
        for row in rows
    ]


def _profile_payload(utilisateur: Utilisateur) -> dict:
    return {
        "age": int(utilisateur.age),
        "sexe": utilisateur.sexe,
        "taille_cm": float(utilisateur.taille_cm),
        "poids_kg": float(utilisateur.poids_kg),
        "niveau_activite": int(utilisateur.niveau_activite),
        "perte_de_poids": bool(utilisateur.perte_de_poids),
        "performance": bool(utilisateur.performance),
        "endurance": bool(utilisateur.endurance),
        "force": bool(utilisateur.force),
    }


def _format_recommendation_answer(recommendation: dict) -> str:
    calories = recommendation.get("calories") or {}
    exercises = recommendation.get("exercices") or {}
    items = exercises.get("exercices") or []

    lines = ["Voici vos recommandations personnalisees :"]
    if calories.get("calories"):
        lines.append(f"- Repere calories du jour : {calories['calories']} kcal.")
    if calories.get("detail"):
        lines.append(f"- Calories : {calories['detail']}")
    if items:
        names = ", ".join(str(item.get("nom_exercice")) for item in items[:5] if item.get("nom_exercice"))
        if names:
            lines.append(f"- Exercices conseilles : {names}.")
    if exercises.get("detail"):
        lines.append(f"- Activite : {exercises['detail']}")
    lines.append("Ces indications restent informatives et ne remplacent pas un avis medical.")
    return "\n".join(lines)


def _format_photo_answer(analysis: dict) -> str:
    for key in ("answer", "message", "description", "detail", "result"):
        value = analysis.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Analyse photo terminee. Les resultats sont disponibles dans la reponse detaillee."


def _ensure_user_image(user_id: str, object_key: str) -> None:
    if not object_key.startswith(f"users/{user_id}/chat/"):
        raise HTTPException(status_code=403, detail="Image non autorisee")


def _cached_chat_response(cached: object) -> ChatResponse | None:
    if isinstance(cached, str):
        return ChatResponse(answer=cached)
    if isinstance(cached, dict) and cached.get("answer"):
        return ChatResponse(
            answer=str(cached["answer"]),
            recommendation=cached.get("recommendation"),
        )
    return None


@router.post("/images", response_model=ChatImageResponse, status_code=201)
def upload_chat_image(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    user_id = _current_user_id(user)
    return upload_user_image(user_id, file)


@router.post("/recommendations", response_model=ChatRecommendationResponse)
def chat_recommendations(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _current_user_id(user)
    utilisateur = _get_user_profile(user_id, db)

    try:
        recommendation = call_microservice_ia_recommendations(_profile_payload(utilisateur))
    except ExternalServiceResponseError as exc:
        raise HTTPException(status_code=502, detail="Reponse microservice IA invalide") from exc
    except ExternalServiceError as exc:
        raise HTTPException(status_code=503, detail="Microservice IA indisponible") from exc

    return ChatRecommendationResponse(
        answer=_format_recommendation_answer(recommendation),
        recommendation=recommendation,
    )


@router.post("/images/analyze", response_model=ChatPhotoAnalysisResponse)
def analyze_chat_image(payload: ChatPhotoAnalysisRequest, user: dict = Depends(get_current_user)):
    user_id = _current_user_id(user)
    _ensure_user_image(user_id, payload.image.object_key)

    image_url = presigned_image_url(payload.image.object_key, public=False)
    request_payload = {
        "image_url": image_url,
        "object_key": payload.image.object_key,
        "filename": payload.image.filename,
        "question": payload.question,
        "user_id": user_id,
    }

    try:
        analysis = call_photo_processing(request_payload)
    except (ExternalServiceResponseError, ExternalServiceError):
        analysis = {
            "status": "degraded",
            "detail": "Microservice photo temporairement indisponible.",
            "object_key": payload.image.object_key,
            "filename": payload.image.filename,
        }

    return ChatPhotoAnalysisResponse(answer=_format_photo_answer(analysis), analysis=analysis)


@router.post("/", response_model=ChatResponse)
def chat_with_mistral(
    payload: ChatRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = _current_user_id(user)

    for image in payload.images:
        _ensure_user_image(user_id, image.object_key)

    user_message = payload.message.strip()
    if payload.images:
        image_lines = [f"- {image.filename or 'image'}: {image.object_key}" for image in payload.images]
        user_message = f"{user_message}\n\nImages jointes par l'utilisateur:\n" + "\n".join(image_lines)

    utilisateur = _get_user_profile(user_id, db)
    profile_payload = _profile_payload(utilisateur)
    objectifs = _objectifs_payload(db, int(user_id))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(message.model_dump() for message in payload.history[-10:])
    messages.append({"role": "user", "content": user_message})

    cache_key = stable_cache_key("chat:mistral", {"user_id": user_id, "messages": messages})
    cached_response = _cached_chat_response(cache.get_json(cache_key))
    if cached_response:
        return cached_response

    try:
        answer, recommendation = run_chat_graph(
            messages,
            user_id=int(user_id),
            profile_payload=profile_payload,
            objectifs=objectifs,
        )
        cache_value: str | dict = answer
        if recommendation:
            cache_value = {"answer": answer, "recommendation": recommendation}
        cache.set_json(cache_key, cache_value, chat_cache_ttl_seconds())
    except ExternalServiceAuthError as exc:
        raise HTTPException(status_code=503, detail="API Mistral non configuree ou refusee") from exc
    except ExternalServiceResponseError as exc:
        raise HTTPException(status_code=502, detail="Reponse Mistral invalide") from exc
    except Exception:
        answer = build_chat_fallback_answer()
        recommendation = None

    return ChatResponse(answer=answer, recommendation=recommendation)
