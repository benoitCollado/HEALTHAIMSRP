from app.dependencies import get_current_user
from app.external_clients import (
    ExternalServiceAuthError,
    ExternalServiceResponseError,
    build_chat_fallback_answer,
    call_mistral_chat,
)
from app.object_storage import upload_user_image
from app.schemas.chat import ChatImageResponse, ChatRequest, ChatResponse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

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
""".strip()


@router.post("/images", response_model=ChatImageResponse, status_code=201)
def upload_chat_image(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    user_id = str(user.get("sub") or "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Utilisateur invalide")
    return upload_user_image(user_id, file)


@router.post("/", response_model=ChatResponse)
def chat_with_mistral(payload: ChatRequest, user: dict = Depends(get_current_user)):
    user_id = str(user.get("sub") or "")

    for image in payload.images:
        if not image.object_key.startswith(f"users/{user_id}/chat/"):
            raise HTTPException(status_code=403, detail="Image non autorisee")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(message.model_dump() for message in payload.history[-10:])
    user_message = payload.message.strip()
    if payload.images:
        image_lines = [f"- {image.filename or 'image'}: {image.object_key}" for image in payload.images]
        user_message = f"{user_message}\n\nImages jointes par l'utilisateur:\n" + "\n".join(image_lines)
    messages.append({"role": "user", "content": user_message})

    try:
        answer = call_mistral_chat(messages)
    except ExternalServiceAuthError as exc:
        raise HTTPException(status_code=503, detail="API Mistral non configuree ou refusee") from exc
    except ExternalServiceResponseError as exc:
        raise HTTPException(status_code=502, detail="Reponse Mistral invalide") from exc
    except Exception:
        answer = build_chat_fallback_answer()

    return ChatResponse(answer=answer)
