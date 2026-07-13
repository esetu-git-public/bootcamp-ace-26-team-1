"""
TDD test suite — Login/Signup authentication, tested from the CLIENT side.

Unlike tests/test_auth.py (which uses FastAPI's in-process TestClient and
never actually leaves the Python process), these tests act like a real
browser: they send plain HTTP requests over the network to a running
instance of the app, using the exact same endpoints and JSON payloads that
static/js/login.js sends via fetch().

This file follows the Red-Green-Refactor TDD cycle:
    Red      -> the test is written first and fails, since the behaviour
                either doesn't exist yet or hasn't been verified end-to-end.
    Green    -> the app already implements (or is updated to implement)
                the behaviour, so the test passes.
    Refactor -> shared setup is pulled into fixtures/helpers so the suite
                stays easy to extend as new validation rules are added.

HOW TO RUN
----------
1. Install the one extra dependency this file needs (pytest is already in
   requirements.txt; `requests` is the only addition):

       pip install requests

2. In one terminal, start the app exactly as usual:

       uvicorn app.main:app --reload

3. In a second terminal (same venv), run this file from the project root:

       pytest tests/test_auth_client.py -v

   By default it targets http://127.0.0.1:8000. To point it at a different
   host/port, set APP_BASE_URL first:

       $env:APP_BASE_URL = "http://127.0.0.1:8000"   # PowerShell
       pytest tests/test_auth_client.py -v

If the server isn't reachable, every test in this file is skipped (rather
than failing with a confusing connection error) so it won't break a normal
`pytest tests/` run that only starts the in-process TestClient suite.
"""

import os
import uuid

import pytest
import requests

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
SIGNUP_URL = f"{BASE_URL}/api/auth/signup"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
ME_URL = f"{BASE_URL}/api/auth/me"


def _unique_email() -> str:
    return f"client_test_{uuid.uuid4().hex[:8]}@example.com"


def _server_is_up() -> bool:
    try:
        requests.get(BASE_URL, timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        return False


# Skip the whole file cleanly if nobody has `uvicorn app.main:app --reload`
# running yet, instead of every test failing with a raw connection error.
pytestmark = pytest.mark.skipif(
    not _server_is_up(),
    reason=f"App is not running at {BASE_URL} — start it with "
           f"'uvicorn app.main:app --reload' before running this file.",
)


@pytest.fixture
def registered_user():
    """
    Red:   a test that needs a real, already-signed-up account fails until
           this fixture exists.
    Green: signs a fresh user up over HTTP and returns their credentials so
           individual tests don't have to repeat the signup boilerplate.
    """
    email = _unique_email()
    password = "clientPass123"
    resp = requests.post(SIGNUP_URL, json={
        "email": email,
        "password": password,
        "full_name": "Client Test User",
        "role": "clinician",
    })
    assert resp.status_code == 200, f"fixture signup failed: {resp.text}"
    return {"email": email, "password": password, "token": resp.json()["access_token"]}


# ---------------------------------------------------------------------------
# Signup — mirrors the "Create account" tab in login.html
# ---------------------------------------------------------------------------

def test_signup_with_valid_details_succeeds():
    """TC-01: valid email, password >= 6 chars, full name -> 200 + token."""
    email = _unique_email()
    resp = requests.post(SIGNUP_URL, json={
        "email": email,
        "password": "securePass1",
        "full_name": "Jane Doe",
        "role": "clinician",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == email


def test_signup_with_short_password_is_rejected():
    """TC-02: password under 6 characters -> 400, no token issued."""
    resp = requests.post(SIGNUP_URL, json={
        "email": _unique_email(),
        "password": "123",
        "full_name": "Short Pass",
    })
    assert resp.status_code == 400
    assert "access_token" not in resp.json()


def test_signup_with_malformed_email_is_rejected():
    """TC-03: not a real email shape -> 422 from schema validation."""
    resp = requests.post(SIGNUP_URL, json={
        "email": "not-an-email",
        "password": "securePass1",
        "full_name": "Bad Email",
    })
    assert resp.status_code == 422


def test_signup_with_duplicate_email_is_rejected(registered_user):
    """TC-04: signing up twice with the same email -> 400 on the 2nd try."""
    resp = requests.post(SIGNUP_URL, json={
        "email": registered_user["email"],
        "password": "anotherPass1",
        "full_name": "Duplicate Attempt",
    })
    assert resp.status_code == 400


def test_signup_missing_full_name_is_rejected():
    """TC-08 (server-side mirror of the client's `required` attribute):
    the API itself must not accept a blank full_name either, since a
    client-side check alone can always be bypassed by calling the API
    directly (e.g. with curl or Postman), skipping the browser entirely.

    RED: as of this writing, this test FAILS -- app/api/auth.py currently
    accepts an empty full_name and returns 200. That's a real gap: the
    login.html `required` attribute only stops the *browser* form, not a
    direct API call. Leaving this test here (rather than deleting it) is
    the point of TDD -- it documents the fix still needed in
    app/services/auth_service.py (or a Pydantic validator on
    SignupRequest) before this can turn GREEN.
    """
    resp = requests.post(SIGNUP_URL, json={
        "email": _unique_email(),
        "password": "securePass1",
        "full_name": "",
    })
    assert resp.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Login — mirrors the "Sign in" tab in login.html
# ---------------------------------------------------------------------------

def test_login_with_correct_credentials_succeeds(registered_user):
    """TC-05: correct email + correct password -> 200 + token."""
    resp = requests.post(LOGIN_URL, json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_wrong_password_is_rejected(registered_user):
    """TC-06: correct email, wrong password -> 401, no token."""
    resp = requests.post(LOGIN_URL, json={
        "email": registered_user["email"],
        "password": "totallyWrongPassword",
    })
    assert resp.status_code == 401
    assert "access_token" not in resp.json()


def test_login_with_unknown_email_is_rejected():
    """TC-07: an email that never signed up -> 401 (not a 404 — this avoids
    leaking which emails are registered)."""
    resp = requests.post(LOGIN_URL, json={
        "email": _unique_email(),
        "password": "whatever123",
    })
    assert resp.status_code == 401


def test_login_response_never_echoes_password(registered_user):
    """Extra client-facing safety check: the JSON the browser receives back
    must never contain the plaintext or hashed password."""
    resp = requests.post(LOGIN_URL, json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    body_text = resp.text.lower()
    assert "password" not in body_text


# ---------------------------------------------------------------------------
# Session / protected route — what happens after login.js stores the token
# ---------------------------------------------------------------------------

def test_protected_route_without_token_is_rejected():
    """TC-08: calling /me with no Authorization header -> 401."""
    resp = requests.get(ME_URL)
    assert resp.status_code == 401


def test_protected_route_with_valid_token_succeeds(registered_user):
    """The token login.js stores after a successful login must actually
    work on a protected endpoint."""
    resp = requests.get(
        ME_URL,
        headers={"Authorization": f"Bearer {registered_user['token']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == registered_user["email"]


def test_protected_route_with_garbage_token_is_rejected():
    """A tampered/garbage token must not be accepted."""
    resp = requests.get(
        ME_URL,
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401
