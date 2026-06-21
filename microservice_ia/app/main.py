import os

from fastapi import FastAPI

from app.presentation.api.routes.recommendation_routes import router as recommendation_router
from app.presentation.api.routes.v1_routes import router as v1_router

app = FastAPI(
    title="HealthAI Microservice IA",
    description="Microservice de recommandations caloriques, exercices et programmes (Clean Architecture).",
    version="1.1.0",
    root_path=os.getenv("API_ROOT_PATH", ""),
)

app.include_router(recommendation_router)
app.include_router(recommendation_router, prefix="/api")
app.include_router(v1_router)


@app.get("/health", tags=["monitoring"])
def health() -> dict[str, str]:
    from pathlib import Path

    model_path = Path(os.getenv("ML_MODEL_PATH", "models/workout_rf_bundle.pkl"))
    ml_status = "loaded" if model_path.exists() and os.getenv("ML_ENABLED", "auto") != "false" else "rule_based"

    persistence = "memory"
    mongodb_uri = os.getenv("MONGODB_URI", "").strip()
    if mongodb_uri:
        try:
            from app.infrastructure.persistence.mongodb.client import get_mongo_client

            get_mongo_client().admin.command("ping")
            persistence = "mongodb"
        except Exception:
            persistence = "mongodb_unavailable"

    return {
        "status": "ok",
        "service": "microservice_ia",
        "ml_engine": ml_status,
        "persistence": persistence,
    }
