import os

import httpx
from app.dependencies import get_current_user
from app.object_storage import upload_user_image
from app.schemas.chat import ChatImageResponse, ChatRequest, ChatResponse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

router = APIRouter(prefix="/chat", tags=["Chat IA"])

MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
DEFAULT_MODEL = "mistral-small-latest"

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


def _get_mistral_api_key() -> str | None:
    return os.getenv("KEY_MISTRAL_API") or os.getenv("KEY_MISTRALL_API") or os.getenv("MISTRAL_API_KEY")


@router.post("/images", response_model=ChatImageResponse, status_code=201)
def upload_chat_image(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    user_id = str(user.get("sub") or "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Utilisateur invalide")
    return upload_user_image(user_id, file)


@router.post("/", response_model=ChatResponse)
def chat_with_mistral(payload: ChatRequest, user: dict = Depends(get_current_user)):
    user_id = str(user.get("sub") or "")
    api_key = _get_mistral_api_key()
    if not api_key:
        raise HTTPException(status_code=503, detail="API Mistral non configuree")

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
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                MISTRAL_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": os.getenv("MISTRAL_MODEL", DEFAULT_MODEL),
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        if status_code in (401, 403):
            raise HTTPException(status_code=503, detail="Cle API Mistral invalide ou refusee") from exc
        raise HTTPException(status_code=502, detail="Erreur API Mistral") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="API Mistral indisponible") from exc

    data = response.json()
    try:
        answer = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise HTTPException(status_code=502, detail="Reponse Mistral invalide") from exc

    if not answer:
        raise HTTPException(status_code=502, detail="Reponse Mistral vide")

    return ChatResponse(answer=answer)
