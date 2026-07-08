from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.services import report_service
from app.services.audit_service import log_action
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary")
def summary(user: dict = Depends(get_current_user)):
    return report_service.summary_report()


@router.get("/export/patients")
def export_patients(user: dict = Depends(get_current_user)):
    csv_bytes = report_service.export_patients_csv()
    log_action(actor=user["email"], action="export_patients_csv")
    return Response(
        content=csv_bytes, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=patients_export.csv"},
    )
