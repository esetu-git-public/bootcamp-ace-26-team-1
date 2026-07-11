#TDD for reports modules

import os
import sys
import uuid
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("LOCAL_DB_PATH", "./test_fallback.db")

from app.main import app 

client = TestClient(app)


def _auth_headers():
    email = f"report_test_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/signup", json={
        "email": email, "password": "password123", "full_name": "Report Tester",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_summary_report():
    headers = _auth_headers()
    resp = client.get("/api/reports/summary", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_predictions_run" in data


def test_export_patients_csv():
    headers = _auth_headers()
    resp = client.get("/api/reports/export/patients", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")


def test_export_predictions_csv():
    headers = _auth_headers()
    resp = client.get("/api/reports/export/predictions", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")


def test_reports_require_auth():
    resp = client.get("/api/reports/summary")
    assert resp.status_code == 401
