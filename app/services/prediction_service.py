from app.ml import predictor
from supabase import database as db


def predict_single(patient: dict, created_by: str) -> dict:
    # Core prediction
    result = predictor.predict_one(patient)

    # SHAP Explainability (optional)
    try:
        result["explanation"] = predictor.explain_one(patient)
    except Exception as exc:
        # Never fail the prediction because explainability failed.
        print(
            f"[prediction_service.predict_single] "
            f"SHAP explanation failed: {exc}"
        )

        result["explanation"] = {
            "summary": (
                "Clinical explanation is currently unavailable for "
                "this prediction."
            ),
            "top_factors": []
        }

    db.insert_prediction(
        patient_ref=patient.get("patient_id"),
        risk_score=result["risk_score"],
        risk_label=result["risk_label"],
        input_payload=patient,
        created_by=created_by,
    )

    return result


def predict_many(patients: list, created_by: str) -> list:
    results = predictor.predict_batch(patients)

    for patient, result in zip(patients, results):
        db.insert_prediction(
            patient_ref=patient.get("patient_id"),
            risk_score=result["risk_score"],
            risk_label=result["risk_label"],
            input_payload=patient,
            created_by=created_by,
        )

    return results


def recent_predictions(limit: int = 50) -> list:
    return db.list_predictions(limit=limit)


def model_feature_importance() -> dict:
    return predictor.feature_importance()