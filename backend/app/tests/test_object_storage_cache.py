from unittest.mock import MagicMock, patch

from app.cache import minio_image_cache_ttl_seconds
from app.object_storage import presigned_image_url


def test_presigned_image_url_uses_cache_without_minio_call():
    with (
        patch("app.object_storage.cache.get_json", return_value="http://cached-url"),
        patch("app.object_storage._minio_client") as minio_client,
    ):
        url = presigned_image_url("users/1/chat/image.jpg")

    assert url == "http://cached-url"
    minio_client.assert_not_called()


def test_presigned_image_url_writes_cache_with_max_three_minutes(monkeypatch):
    monkeypatch.setenv("MINIO_IMAGE_CACHE_TTL_SECONDS", "600")

    client = MagicMock()
    client.presigned_get_object.return_value = "http://fresh-url"

    with (
        patch("app.object_storage.cache.get_json", return_value=None),
        patch("app.object_storage.cache.set_json") as set_cache,
        patch("app.object_storage._minio_client", return_value=client),
    ):
        url = presigned_image_url("users/1/chat/image.jpg")

    assert url == "http://fresh-url"
    assert minio_image_cache_ttl_seconds() == 180
    assert set_cache.call_args.args[2] == 180
