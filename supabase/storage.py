
import os
import uuid
from supabase.client import get_supabase

LOCAL_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
BUCKET_NAME = "uploads"


def save_file(filename: str, content: bytes) -> str:
    """Saves a file and returns a reference path/URL."""
    sb = get_supabase()
    unique_name = f"{uuid.uuid4().hex}_{filename}"

    if sb:
        try:
            return sb.storage_upload(BUCKET_NAME, unique_name, content)
        except Exception as exc:  # pragma: no cover
            print(f"[supabase.storage] Upload failed, falling back to local disk: {exc}")

    os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
    path = os.path.join(LOCAL_UPLOAD_DIR, unique_name)
    with open(path, "wb") as f:
        f.write(content)
    return path


def read_file(path_or_url: str) -> bytes:
    if path_or_url.startswith("http"):
        import httpx
        return httpx.get(path_or_url).content
    with open(path_or_url, "rb") as f:
        return f.read()
