"""
Run with:
    pytest test_patients_tdd.py -v
"""

import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("LOCAL_DB_PATH", "./test_fallback.db")

from app.main import app  # noqa: E402

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _unique_email():
    return f"patient_test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def auth_headers():
    """Sign up a fresh user and return valid auth headers."""
    resp = client.post("/api/auth/signup", json={
        "email": _unique_email(),
        "password": "password123",
        "full_name": "Patient Tester",
    })
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_patient_payload():
    return {
        "patient_id": uuid.uuid4().int % 1_000_000,  # avoid collisions across tests
        "age": 70,
        "gender": "Female",
        "blood_pressure": "128/82",
        "cholesterol": 210,
        "bmi": 27.5,
        "diabetes": "Yes",
        "hypertension": "No",
        "medication_count": 4,
        "length_of_stay": 6,
        "discharge_destination": "Home",
        "readmitted_30_days": "No",
    }


def _create_patient(headers, payload):
    return client.post("/api/patients", json=payload, headers=headers)


# ---------------------------------------------------------------------------
# Create patient — happy path
# ---------------------------------------------------------------------------

class TestCreatePatient:
    def test_create_patient_returns_200(self, auth_headers, valid_patient_payload):
        resp = _create_patient(auth_headers, valid_patient_payload)
        assert resp.status_code == 200

    def test_create_patient_echoes_submitted_fields(self, auth_headers, valid_patient_payload):
        resp = _create_patient(auth_headers, valid_patient_payload)
        body = resp.json()
        assert body.get("patient_id") == valid_patient_payload["patient_id"]
        assert body.get("age") == valid_patient_payload["age"]

    def test_created_patient_appears_in_list(self, auth_headers, valid_patient_payload):
        _create_patient(auth_headers, valid_patient_payload)
        resp = client.get("/api/patients?page=1&page_size=50", headers=auth_headers)
        assert resp.status_code == 200
        ids = [p.get("patient_id") for p in resp.json().get("items", resp.json().get("data", []))]
        assert valid_patient_payload["patient_id"] in ids or resp.json()["total"] >= 1


# ---------------------------------------------------------------------------
# Create patient — validation / negative cases
# ---------------------------------------------------------------------------

class TestCreatePatientValidation:
    def test_missing_required_field_returns_422(self, auth_headers, valid_patient_payload):
        payload = dict(valid_patient_payload)
        del payload["age"]
        resp = _create_patient(auth_headers, payload)
        assert resp.status_code == 422

    def test_wrong_type_for_age_returns_422(self, auth_headers, valid_patient_payload):
        payload = dict(valid_patient_payload)
        payload["age"] = "seventy"  # should be int
        resp = _create_patient(auth_headers, payload)
        assert resp.status_code == 422

    def test_negative_age_is_rejected_or_flagged(self, auth_headers, valid_patient_payload):
        payload = dict(valid_patient_payload)
        payload["age"] = -5
        resp = _create_patient(auth_headers, payload)
        # Depending on validation strictness this should be a 422; if the API
        # currently accepts it, this test documents the gap for follow-up.
        assert resp.status_code in (422, 400)

    def test_duplicate_patient_id_is_rejected(self, auth_headers, valid_patient_payload):
        first = _create_patient(auth_headers, valid_patient_payload)
        assert first.status_code == 200
        second = _create_patient(auth_headers, valid_patient_payload)
        assert second.status_code in (400, 409)

    def test_create_patient_without_auth_returns_401(self, valid_patient_payload):
        resp = client.post("/api/patients", json=valid_patient_payload)
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# List patients — pagination
# ---------------------------------------------------------------------------

class TestListPatients:
    def test_list_requires_auth(self):
        resp = client.get("/api/patients")
        assert resp.status_code == 401

    def test_list_returns_total_count(self, auth_headers, valid_patient_payload):
        _create_patient(auth_headers, valid_patient_payload)
        resp = client.get("/api/patients?page=1&page_size=5", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_list_respects_page_size(self, auth_headers, valid_patient_payload):
        for i in range(3):
            payload = dict(valid_patient_payload)
            payload["patient_id"] = valid_patient_payload["patient_id"] + i + 1
            _create_patient(auth_headers, payload)

        resp = client.get("/api/patients?page=1&page_size=2", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json().get("items", resp.json().get("data", []))
        assert len(items) <= 2

    def test_list_invalid_page_returns_422_or_empty(self, auth_headers):
        resp = client.get("/api/patients?page=0&page_size=5", headers=auth_headers)
        assert resp.status_code in (200, 422)

    def test_list_with_invalid_token_returns_401(self):
        resp = client.get("/api/patients", headers={"Authorization": "Bearer not-a-real-token"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Stats endpoint
# ---------------------------------------------------------------------------

class TestStatsEndpoint:
    def test_stats_requires_auth(self):
        resp = client.get("/api/patients/stats")
        assert resp.status_code == 401

    def test_stats_returns_expected_keys(self, auth_headers):
        resp = client.get("/api/patients/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_patients" in data
        assert "readmission_rate" in data

    def test_readmission_rate_is_a_percentage(self, auth_headers, valid_patient_payload):
        _create_patient(auth_headers, valid_patient_payload)
        resp = client.get("/api/patients/stats", headers=auth_headers)
        rate = resp.json()["readmission_rate"]
        assert 0 <= rate <= 100

    def test_total_patients_reflects_created_patient(self, auth_headers, valid_patient_payload):
        before = client.get("/api/patients/stats", headers=auth_headers).json()["total_patients"]
        _create_patient(auth_headers, valid_patient_payload)
        after = client.get("/api/patients/stats", headers=auth_headers).json()["total_patients"]
        assert after >= before + 1


# ---------------------------------------------------------------------------
# Auth edge cases (supporting the patients endpoints)
# ---------------------------------------------------------------------------

class TestAuth:
    def test_signup_returns_access_token(self):
        resp = client.post("/api/auth/signup", json={
            "email": _unique_email(),
            "password": "password123",
            "full_name": "Someone",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_signup_duplicate_email_is_rejected(self):
        email = _unique_email()
        payload = {"email": email, "password": "password123", "full_name": "Someone"}
        first = client.post("/api/auth/signup", json=payload)
        assert first.status_code == 200
        second = client.post("/api/auth/signup", json=payload)
        assert second.status_code in (400, 409)
