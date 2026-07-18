from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.services import prediction_service
from app.services.audit_service import log_action

router = APIRouter(
    prefix="/api/prediction",
    tags=["prediction"],
)


class PatientFeatures(BaseModel):
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


# ------------------------------------------------------------
# Single Prediction
# ------------------------------------------------------------
@router.post("/predict")
def predict(
    payload: PatientFeatures,
    user: dict = Depends(get_current_user),
):
    try:
        result = prediction_service.predict_single(
            payload.model_dump(),
            created_by=user["email"],
        )

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    log_action(
        actor=user["email"],
        action="predict",
        details=(
            f"patient_id={payload.patient_id}, "
            f"risk={result['risk_label']}, "
            f"score={result['risk_percent']}%"
        ),
    )

    # prediction_service already returns:
    # {
    #   risk_score,
    #   risk_percent,
    #   risk_label,
    #   explanation,
    #   feature_importance
    # }
    return result


# ------------------------------------------------------------
# Batch Prediction
# ------------------------------------------------------------
@router.post("/predict/batch")
def predict_batch(
    payload: list[PatientFeatures],
    user: dict = Depends(get_current_user),
):
    try:
        results = prediction_service.predict_many(
            [p.model_dump() for p in payload],
            created_by=user["email"],
        )

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    log_action(
        actor=user["email"],
        action="predict_batch",
        details=f"count={len(payload)}",
    )

    return results


# ------------------------------------------------------------
# Prediction History
# ------------------------------------------------------------
@router.get("/history")
def history(
    limit: int = 50,
    user: dict = Depends(get_current_user),
):
    return prediction_service.recent_predictions(limit=limit)


# ------------------------------------------------------------
# Global Feature Importance
# ------------------------------------------------------------
@router.get("/feature-importance")
def feature_importance(
    user: dict = Depends(get_current_user),
):
    return prediction_service.model_feature_importance()