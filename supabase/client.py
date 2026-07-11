"""
Lightweight Supabase REST client built on `httpx`.

NOTE: This package is intentionally named `supabase/` to match the required
project layout, which means it shadows the third-party `supabase` pip
package for any code running from the project root. To avoid that collision
entirely we talk to Supabase's PostgREST + Auth HTTP APIs directly with
`httpx` instead of importing the `supabase-py` SDK.

If SUPABASE_URL / SUPABASE_KEY are not set, `get_supabase()` returns None and
every module in `supabase/*.py` transparently falls back to a local SQLite
database (see supabase/database.py) so the whole application still runs
end-to-end without a live Supabase project.
"""
from functools import lru_cache
import httpx

from app.config import get_settings

settings = get_settings()


class SupabaseUnavailable(RuntimeError):
    """Raised when the configured Supabase service is unavailable."""


class SupabaseREST:
    """Minimal PostgREST + GoTrue (Auth) client, just enough for this app."""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key
        self.rest_base = f"{self.url}/rest/v1"
        self.auth_base = f"{self.url}/auth/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    def _request(self, method, url: str, **kwargs):
        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as exc:
            raise SupabaseUnavailable(str(exc)) from exc

    # ---- table (PostgREST) helpers ----
    def select(self, table: str, params: dict | None = None) -> list:
        response = self._request(httpx.get, f"{self.rest_base}/{table}", headers=self.headers, params=params or {}, timeout=10)
        return response.json()

    def insert(self, table: str, records: list | dict) -> list:
        headers = {**self.headers, "Prefer": "return=representation"}
        response = self._request(httpx.post, f"{self.rest_base}/{table}", headers=headers, json=records, timeout=10)
        return response.json()

    def count(self, table: str, params: dict | None = None) -> int:
        headers = {**self.headers, "Prefer": "count=exact"}
        response = self._request(httpx.head, f"{self.rest_base}/{table}", headers=headers, params=params or {}, timeout=10)
        content_range = response.headers.get("content-range", "0")
        return int(content_range.split("/")[-1]) if "/" in content_range else 0

    # ---- auth (GoTrue) helpers ----
    def auth_sign_up(self, email: str, password: str) -> dict:
        response = self._request(
            httpx.post,
            f"{self.auth_base}/signup",
            headers=self.headers,
            json={"email": email, "password": password},
            timeout=10,
        )
        return response.json()

    def auth_sign_in(self, email: str, password: str) -> dict:
        response = self._request(
            httpx.post,
            f"{self.auth_base}/token?grant_type=password",
            headers=self.headers,
            json={"email": email, "password": password},
            timeout=10,
        )
        return response.json()

    # ---- storage helpers ----
    def storage_upload(self, bucket: str, path: str, content: bytes) -> str:
        r = httpx.post(
            f"{self.url}/storage/v1/object/{bucket}/{path}",
            headers={"apikey": self.key, "Authorization": f"Bearer {self.key}"},
            content=content, timeout=30,
        )
        r.raise_for_status()
        return f"{self.url}/storage/v1/object/public/{bucket}/{path}"


@lru_cache
def get_supabase():
    if not settings.supabase_configured:
        return None
    try:
        return SupabaseREST(settings.supabase_url, settings.supabase_key)
    except Exception as exc:  # pragma: no cover
        print(f"[supabase.client] Failed to create Supabase client: {exc}")
        return None
