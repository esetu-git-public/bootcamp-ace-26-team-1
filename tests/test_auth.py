import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("LOCAL_DB_PATH", "./test_fallback.db")

from app.main import app  # noqa: E402

client = TestClient(app)


def _unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_signup_and_login():
    email = _unique_email()
    resp = client.post("/api/auth/signup", json={
        "email": email, "password": "password123", "full_name": "Test User", "role": "clinician",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == email

    resp2 = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert resp2.status_code == 200
    assert "access_token" in resp2.json()


def test_login_wrong_password():
    email = _unique_email()
    client.post("/api/auth/signup", json={
        "email": email, "password": "password123", "full_name": "Test User",
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_requires_token():
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_signup_short_password_rejected():
    resp = client.post("/api/auth/signup", json={
        "email": _unique_email(), "password": "123", "full_name": "Short Pass",
    })
    assert resp.status_code == 400
