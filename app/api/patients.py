from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.services.audit_service import log_action
from supabase import database as db


router = APIRouter(
    prefix="/api/patients",
    tags=["patients"],
)


def _total_pages(total: int, page_size: int) -> int:
    return max(1, (total + page_size - 1) // page_size)


class PatientCreate(BaseModel):
    patient_id: int
    age: int = Field(..., ge=0)
    gender: str
    blood_pressure: Optional[str] = None
    cholesterol: Optional[int] = None
    bmi: Optional[float] = None
    diabetes: Optional[str] = None
    hypertension: Optional[str] = None
    medication_count: Optional[int] = None
    length_of_stay: Optional[int] = None
    discharge_destination: Optional[str] = None
    readmitted_30_days: Optional[str] = None


# ------------------------------------------------------------------
# Create Patient
# POST /api/patients
# ------------------------------------------------------------------
@router.post("")
def create_patient(
    payload: PatientCreate,
    user: dict = Depends(get_current_user),
):
    existing = db.list_patients(limit=1000)

    if any(p.get("patient_id") == payload.patient_id for p in existing):
        raise HTTPException(
            status_code=400,
            detail="Patient ID already exists",
        )

    patient = db.insert_patient(
        payload.model_dump(),
        created_by=user.get("email", "unknown"),
    )

    log_action(
        actor=user.get("email"),
        action="create_patient",
        details=f"patient_id={payload.patient_id}",
    )

    return patient


# ------------------------------------------------------------------
# List Patients
# GET /api/patients?page=1&page_size=15
# ------------------------------------------------------------------
@router.get("")
def get_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: str = Query(""),
    user: dict = Depends(get_current_user),
):
    offset = (page - 1) * page_size

    items = db.list_patients(
        limit=page_size,
        offset=offset,
        search=search,
    )

    total = db.count_patients()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": _total_pages(total, page_size),
    }


# ------------------------------------------------------------------
# Dashboard Stats
# GET /api/patients/stats
# ------------------------------------------------------------------
@router.get("/stats")
def get_patient_stats(
    user: dict = Depends(get_current_user),
):
    return db.get_patient_stats()

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    user: dict = Depends(get_current_user)
):
    print(f"Deleting patient_id = {patient_id}")

    deleted = db.delete_patient(patient_id)

    print(f"delete_patient() returned: {deleted}")

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    log_action(
        actor=user.get("email"),
        action="delete_patient",
        details=f"id={patient_id}"
    )

    return {
        "success": True,
        "message": "Patient deleted successfully"
    }