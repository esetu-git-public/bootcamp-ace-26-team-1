from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from pydantic import BaseModel

from app.services import patient_service
from app.services.audit_service import log_action
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/patients", tags=["patients"])


class PatientIn(BaseModel):
    patient_id: int | None = None
    age: int
    gender: str
    blood_pressure: str
    cholesterol: int
    bmi: float
    diabetes: str
    hypertension: str
    medication_count: int
    length_of_stay: int
    discharge_destination: str
    readmitted_30_days: str | None = None


@router.get("")
def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: str = Query(""),
    user: dict = Depends(get_current_user),
):
    return patient_service.get_patients_page(page, page_size, search)


@router.get("/stats")
def stats(user: dict = Depends(get_current_user)):
    return patient_service.dashboard_stats()


@router.post("")
def create_patient(payload: PatientIn, user: dict = Depends(get_current_user)):
    record = patient_service.add_patient(payload.model_dump(), created_by=user["email"])
    log_action(actor=user["email"], action="create_patient", details=f"patient_id={payload.patient_id}")
    return record


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")
    content = await file.read()
    result = patient_service.import_csv(content, created_by=user["email"])
    log_action(actor=user["email"], action="upload_csv", details=f"inserted={result['inserted']}")
    return result
