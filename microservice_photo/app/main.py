from io import BytesIO

import httpx
from fastapi import FastAPI, HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field


class PhotoAnalysisRequest(BaseModel):
    image_url: str = Field(min_length=1)
    object_key: str = Field(min_length=1)
    filename: str | None = None
    question: str | None = None
    user_id: str | None = None


class PhotoAnalysisResponse(BaseModel):
    answer: str
    status: str = "ok"
    filename: str | None = None
    object_key: str
    width: int
    height: int
    format: str | None = None
    mode: str
    question: str | None = None


app = FastAPI(
    title="HealthAI Microservice Photo",
    description="Analyse simple des images jointes au Chat IA.",
    version="1.0.0",
)


@app.get("/health", tags=["monitoring"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "microservice_photo"}


@app.post("/analyze", response_model=PhotoAnalysisResponse)
def analyze_photo(payload: PhotoAnalysisRequest) -> PhotoAnalysisResponse:
    try:
        response = httpx.get(payload.image_url, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Image inaccessible depuis le microservice photo") from exc

    try:
        image = Image.open(BytesIO(response.content))
        image = ImageOps.exif_transpose(image)
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=422, detail="Image invalide") from exc

    width, height = image.size
    image_format = image.format or "image"
    orientation = "portrait" if height > width else "paysage" if width > height else "carree"
    megapixels = round((width * height) / 1_000_000, 2)
    answer = (
        f"Image analysee : format {image_format}, {width} x {height}px, orientation {orientation}, "
        f"environ {megapixels} megapixel(s). "
        "Pour une estimation nutritionnelle ou sportive precise, completez avec le contenu visible de l'image."
    )

    return PhotoAnalysisResponse(
        answer=answer,
        filename=payload.filename,
        object_key=payload.object_key,
        width=width,
        height=height,
        format=image_format,
        mode=image.mode,
        question=payload.question,
    )
