from fastapi import APIRouter, Depends

from app.services import audit_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs")
def logs(limit: int = 200, user: dict = Depends(get_current_user)):
    return audit_service.get_logs(limit=limit)
