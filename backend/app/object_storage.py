import os
from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException, UploadFile

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _minio_client(endpoint: str | None = None):
    try:
        from minio import Minio
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Stockage image MiniIO non configure") from exc

    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")

    if not access_key or not secret_key:
        raise HTTPException(
            status_code=500,
            detail="Configuration MiniIO invalide"
        )

    return Minio(
        endpoint or os.getenv("MINIO_ENDPOINT", "minio:9000"),
        access_key=access_key,
        secret_key=secret_key,
        secure=_env_bool("MINIO_SECURE", False),
    )


def _bucket_name() -> str:
    return os.getenv("MINIO_BUCKET", "healthai-meal-photos")


def ensure_bucket() -> None:
    client = _minio_client()
    bucket = _bucket_name()
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def presigned_image_url(object_key: str) -> str:
    public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT")
    client = _minio_client(public_endpoint) if public_endpoint else _minio_client()
    return client.presigned_get_object(_bucket_name(), object_key, expires=timedelta(hours=1))


def upload_user_image(user_id: str, file: UploadFile) -> dict[str, str]:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Format image non supporte")

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size <= 0:
        raise HTTPException(status_code=400, detail="Image vide")
    if size > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image trop volumineuse")

    ensure_bucket()
    extension = ALLOWED_IMAGE_TYPES[file.content_type]
    object_key = (
        f"users/{user_id}/meals/{uuid4().hex}{extension}"
    )
    client = _minio_client()
    client.put_object(
        _bucket_name(),
        object_key,
        file.file,
        length=size,
        content_type=file.content_type,
    )

    return {
        "object_key": object_key,
        "url": presigned_image_url(object_key),
        "content_type": file.content_type,
        "filename": file.filename or f"image{extension}",
    }
