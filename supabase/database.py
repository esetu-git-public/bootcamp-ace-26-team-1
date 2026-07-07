"""
CRUD wrappers around Supabase Postgres tables:
    users, patients, predictions, audit_logs

When Supabase isn't configured, every function transparently falls back to a
local SQLite file (see app.config.settings.local_db_path) with an identical
schema, so the rest of the app never has to branch on which backend is active.
"""
import sqlite3
import json
import time
from contextlib import contextmanager
from typing import Optional

from supabase.client import get_supabase
from app.config import get_settings

settings = get_settings()


# --------------------------------------------------------------------------
# Local SQLite fallback
# --------------------------------------------------------------------------
@contextmanager
def _conn():
    conn = sqlite3.connect(settings.local_db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_local_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'clinician',
                password_hash TEXT NOT NULL,
                created_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                age INTEGER,
                gender TEXT,
                blood_pressure TEXT,
                cholesterol INTEGER,
                bmi REAL,
                diabetes TEXT,
                hypertension TEXT,
                medication_count INTEGER,
                length_of_stay INTEGER,
                discharge_destination TEXT,
                readmitted_30_days TEXT,
                created_by TEXT,
                created_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_ref INTEGER,
                risk_score REAL,
                risk_label TEXT,
                input_payload TEXT,
                created_by TEXT,
                created_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT,
                action TEXT,
                details TEXT,
                created_at REAL
            )
        """)


init_local_db()


# ---------------------------- USERS ---------------------------------------
def get_user_by_email(email: str) -> Optional[dict]:
    sb = get_supabase()
    if sb:
        rows = sb.select("users", {"email": f"eq.{email}", "limit": 1})
        return rows[0] if rows else None
    with _conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def create_user(user_id: str, email: str, full_name: str, role: str, password_hash: str) -> dict:
    record = {
        "id": user_id, "email": email, "full_name": full_name,
        "role": role, "password_hash": password_hash, "created_at": time.time(),
    }
    sb = get_supabase()
    if sb:
        sb.insert("users", record)
        return record
    with _conn() as conn:
        conn.execute(
            "INSERT INTO users (id, email, full_name, role, password_hash, created_at) VALUES (?,?,?,?,?,?)",
            (user_id, email, full_name, role, password_hash, record["created_at"]),
        )
    return record


# ---------------------------- PATIENTS -------------------------------------
def list_patients(limit: int = 100, offset: int = 0, search: str = "") -> list:
    sb = get_supabase()
    if sb:
        params = {"order": "id.desc", "limit": limit, "offset": offset}
        if search:
            params["gender"] = f"ilike.*{search}*"
        return sb.select("patients", params)
    with _conn() as conn:
        if search:
            rows = conn.execute(
                "SELECT * FROM patients WHERE CAST(patient_id AS TEXT) LIKE ? OR gender LIKE ? "
                "ORDER BY id DESC LIMIT ? OFFSET ?",
                (f"%{search}%", f"%{search}%", limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM patients ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
        return [dict(r) for r in rows]


def count_patients() -> int:
    sb = get_supabase()
    if sb:
        return sb.count("patients")
    with _conn() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM patients").fetchone()
        return row["c"]


def insert_patient(record: dict, created_by: str = "") -> dict:
    record = {**record, "created_by": created_by, "created_at": time.time()}
    sb = get_supabase()
    if sb:
        result = sb.insert("patients", record)
        return result[0] if result else record
    with _conn() as conn:
        cur = conn.execute(
            """INSERT INTO patients
               (patient_id, age, gender, blood_pressure, cholesterol, bmi, diabetes,
                hypertension, medication_count, length_of_stay, discharge_destination,
                readmitted_30_days, created_by, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                record.get("patient_id"), record.get("age"), record.get("gender"),
                record.get("blood_pressure"), record.get("cholesterol"), record.get("bmi"),
                record.get("diabetes"), record.get("hypertension"), record.get("medication_count"),
                record.get("length_of_stay"), record.get("discharge_destination"),
                record.get("readmitted_30_days"), created_by, record["created_at"],
            ),
        )
        record["id"] = cur.lastrowid
    return record


def bulk_insert_patients(records: list, created_by: str = "") -> int:
    sb = get_supabase()
    now = time.time()
    if sb:
        payload = [{**r, "created_by": created_by, "created_at": now} for r in records]
        CHUNK = 500
        total = 0
        for i in range(0, len(payload), CHUNK):
            sb.insert("patients", payload[i:i + CHUNK])
            total += len(payload[i:i + CHUNK])
        return total
    with _conn() as conn:
        conn.executemany(
            """INSERT INTO patients
               (patient_id, age, gender, blood_pressure, cholesterol, bmi, diabetes,
                hypertension, medication_count, length_of_stay, discharge_destination,
                readmitted_30_days, created_by, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [
                (
                    r.get("patient_id"), r.get("age"), r.get("gender"), r.get("blood_pressure"),
                    r.get("cholesterol"), r.get("bmi"), r.get("diabetes"), r.get("hypertension"),
                    r.get("medication_count"), r.get("length_of_stay"),
                    r.get("discharge_destination"), r.get("readmitted_30_days"),
                    created_by, now,
                )
                for r in records
            ],
        )
    return len(records)


def get_patient_stats() -> dict:
    """Aggregate stats used by the dashboard."""
    sb = get_supabase()
    if sb:
        all_rows = sb.select("patients", {
            "select": "age,gender,diabetes,hypertension,discharge_destination,"
                      "readmitted_30_days,length_of_stay",
            "limit": 100000,
        })
    else:
        with _conn() as conn:
            all_rows = [dict(r) for r in conn.execute(
                "SELECT age,gender,diabetes,hypertension,discharge_destination,"
                "readmitted_30_days,length_of_stay FROM patients"
            ).fetchall()]

    total = len(all_rows)
    readmitted = sum(1 for r in all_rows if r.get("readmitted_30_days") == "Yes")
    avg_los = sum(r.get("length_of_stay") or 0 for r in all_rows) / total if total else 0
    by_gender = {}
    by_destination = {}
    for r in all_rows:
        by_gender[r.get("gender") or "Unknown"] = by_gender.get(r.get("gender") or "Unknown", 0) + 1
        dest = r.get("discharge_destination") or "Unknown"
        by_destination[dest] = by_destination.get(dest, 0) + 1
    return {
        "total_patients": total,
        "readmitted_count": readmitted,
        "readmission_rate": round((readmitted / total * 100), 2) if total else 0,
        "avg_length_of_stay": round(avg_los, 2),
        "by_gender": by_gender,
        "by_destination": by_destination,
    }


# ---------------------------- PREDICTIONS ----------------------------------
def insert_prediction(patient_ref, risk_score, risk_label, input_payload: dict, created_by: str) -> dict:
    record = {
        "patient_ref": patient_ref, "risk_score": risk_score, "risk_label": risk_label,
        "input_payload": json.dumps(input_payload), "created_by": created_by,
        "created_at": time.time(),
    }
    sb = get_supabase()
    if sb:
        result = sb.insert("predictions", record)
        return result[0] if result else record
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO predictions (patient_ref, risk_score, risk_label, input_payload, created_by, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (patient_ref, risk_score, risk_label, record["input_payload"], created_by, record["created_at"]),
        )
        record["id"] = cur.lastrowid
    return record


def list_predictions(limit: int = 50) -> list:
    sb = get_supabase()
    if sb:
        return sb.select("predictions", {"order": "id.desc", "limit": limit})
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------- AUDIT LOGS -----------------------------------
def insert_audit_log(actor: str, action: str, details: str = "") -> dict:
    record = {"actor": actor, "action": action, "details": details, "created_at": time.time()}
    sb = get_supabase()
    if sb:
        result = sb.insert("audit_logs", record)
        return result[0] if result else record
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO audit_logs (actor, action, details, created_at) VALUES (?,?,?,?)",
            (actor, action, details, record["created_at"]),
        )
        record["id"] = cur.lastrowid
    return record


def list_audit_logs(limit: int = 200) -> list:
    sb = get_supabase()
    if sb:
        return sb.select("audit_logs", {"order": "id.desc", "limit": limit})
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
