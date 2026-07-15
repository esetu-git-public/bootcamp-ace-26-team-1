from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional


def _total_pages(total: int, page_size: int) -> int:
    return max(1, (total + page_size - 1) // page_size) if total else 1

from app.services.audit_service import log_action
from app.dependencies import get_current_user
from supabase import database as db  # <-- Using your custom wrapper!

router = APIRouter(prefix="/api/patients", tags=["patients"])

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

@router.post("/")
def create_patient(payload: PatientCreate, user: dict = Depends(get_current_user)):
    # 1. Check for duplicates using your wrapper's search function
    existing_patients = db.list_patients(limit=1000)
    if any(p.get("patient_id") == payload.patient_id for p in existing_patients):
        raise HTTPException(status_code=400, detail="Patient ID already exists")

    # 2. Insert using your custom wrapper
    data = payload.model_dump()
    result = db.insert_patient(data, created_by=user.get("email", "unknown"))
    
    log_action(actor=user.get("email"), action="create_patient", details=f"patient_id={payload.patient_id}")
    return result

@router.get("/")
def get_patients(
    page: int = Query(1, ge=1), 
    page_size: int = Query(50, ge=1, le=100),
    search: str = Query("", description="Optional search term"),
    user: dict = Depends(get_current_user)
):
    # 3. List and Count using your custom wrapper
    offset = (page - 1) * page_size
    items = db.list_patients(limit=page_size, offset=offset, search=search)
    total = db.count_patients()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": _total_pages(total, page_size),
    }

@router.get("/stats")
def get_patient_stats(user: dict = Depends(get_current_user)):
    # 4. Return the aggregated stats (Fixes the 404 errors!)
    return db.get_patient_stats()