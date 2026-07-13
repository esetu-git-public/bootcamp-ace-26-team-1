from functools import lru_cache
import httpx

from app.config import get_settings

settings = get_settings()


class SupabaseREST:

    def __init__(self, url: str, anon_key: str, service_role_key: str = ""):
        self.url = url.rstrip("/")
        self.anon_key = anon_key
        # Fall back to the anon key if no service role key is configured,
        # so the app still runs -- just subject to whatever RLS you've set.
        self.service_key = service_role_key or anon_key

        self.rest_base = f"{self.url}/rest/v1"
        self.auth_base = f"{self.url}/auth/v1"

        self.headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
        }
        self.auth_headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
        }

    # ---- table (PostgREST) helpers ----
    def select(self, table: str, params: dict | None = None) -> list:
        r = httpx.get(f"{self.rest_base}/{table}", headers=self.headers, params=params or {}, timeout=10)
        r.raise_for_status()
        return r.json()

    def insert(self, table: str, records: list | dict) -> list:
        headers = {**self.headers, "Prefer": "return=representation"}
        r = httpx.post(f"{self.rest_base}/{table}", headers=headers, json=records, timeout=10)
        r.raise_for_status()
        return r.json()

    def count(self, table: str, params: dict | None = None) -> int:
        headers = {**self.headers, "Prefer": "count=exact"}
        r = httpx.head(f"{self.rest_base}/{table}", headers=headers, params=params or {}, timeout=10)
        r.raise_for_status()
        content_range = r.headers.get("content-range", "0")
        return int(content_range.split("/")[-1]) if "/" in content_range else 0

    # ---- auth (GoTrue) helpers ----
    def auth_sign_up(self, email: str, password: str) -> dict:
        r = httpx.post(f"{self.auth_base}/signup", headers=self.auth_headers,
                        json={"email": email, "password": password}, timeout=10)
        r.raise_for_status()
        return r.json()

    def auth_sign_in(self, email: str, password: str) -> dict:
        r = httpx.post(
            f"{self.auth_base}/token?grant_type=password", headers=self.auth_headers,
            json={"email": email, "password": password}, timeout=10,
        )
        r.raise_for_status()
        return r.json()

    # ---- storage helpers ----
    def storage_upload(self, bucket: str, path: str, content: bytes) -> str:
        r = httpx.post(
            f"{self.url}/storage/v1/object/{bucket}/{path}",
            headers={"apikey": self.service_key, "Authorization": f"Bearer {self.service_key}"},
            content=content, timeout=30,
        )
        r.raise_for_status()
        return f"{self.url}/storage/v1/object/public/{bucket}/{path}"


@lru_cache
def get_supabase():
    if not settings.supabase_configured:
        return None
    try:
        return SupabaseREST(settings.supabase_url, settings.supabase_key, settings.supabase_service_role_key)
    except Exception as exc:  # pragma: no cover
        print(f"[supabase.client] Failed to create Supabase client: {exc}")
        return None