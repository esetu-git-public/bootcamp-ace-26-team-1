"""
Loads the trained RandomForest model + scaler and exposes
prediction and SHAP explainability APIs.

Compatible with:
- Python 3.11
- SHAP 0.51+
- scikit-learn RandomForestClassifier
"""

import os
import joblib
import numpy as np
import shap

from app.ml.feature_engineering import build_feature_row
from app.utils.helpers import risk_bucket

# ---------------------------------------------------------------------
# Model paths
# ---------------------------------------------------------------------

_DIR = os.path.dirname(__file__)

_MODEL_PATH = os.path.join(_DIR, "model.pkl")
_SCALER_PATH = os.path.join(_DIR, "scaler.pkl")
_FEATURES_PATH = os.path.join(_DIR, "feature_cols.pkl")

# ---------------------------------------------------------------------
# Cached objects
# ---------------------------------------------------------------------

_model = None
_scaler = None
_feature_cols = None
_explainer = None

# ---------------------------------------------------------------------
# Friendly feature names
# ---------------------------------------------------------------------

FEATURE_LABELS = {
    "age": "Age",
    "gender_enc": "Gender",
    "systolic_bp": "Systolic Blood Pressure",
    "diastolic_bp": "Diastolic Blood Pressure",
    "cholesterol": "Cholesterol",
    "bmi": "BMI",
    "diabetes_enc": "Diabetes",
    "hypertension_enc": "Hypertension",
    "medication_count": "Medication Count",
    "length_of_stay": "Length of Stay",
    "discharge_enc": "Discharge Destination",
}

# ---------------------------------------------------------------------
# Load model once
# ---------------------------------------------------------------------


def _load():
    global _model, _scaler, _feature_cols

    if _model is None:

        if not os.path.exists(_MODEL_PATH):
            raise RuntimeError(
                "Model artifacts not found.\n"
                "Run train_model.py first."
            )

        _model = joblib.load(_MODEL_PATH)
        _scaler = joblib.load(_SCALER_PATH)
        _feature_cols = joblib.load(_FEATURES_PATH)

    return _model, _scaler, _feature_cols


# ---------------------------------------------------------------------
# Create SHAP explainer once
# ---------------------------------------------------------------------


def _get_explainer():
    global _explainer

    if _explainer is None:
        model, _, _ = _load()
        _explainer = shap.TreeExplainer(model)

    return _explainer


# ---------------------------------------------------------------------
# Convert encoded values into readable text
# ---------------------------------------------------------------------


def _format_value(feature, value):

    if feature == "gender_enc":
        return {
            0: "Male",
            1: "Female",
            2: "Other"
        }.get(value, str(value))

    if feature == "diabetes_enc":
        return "Yes" if value == 1 else "No"

    if feature == "hypertension_enc":
        return "Yes" if value == 1 else "No"

    if feature == "discharge_enc":
        return {
            0: "Home",
            1: "Rehab",
            2: "Nursing Facility"
        }.get(value, str(value))

    return str(value)
# ---------------------------------------------------------------------
# Single prediction
# ---------------------------------------------------------------------


def predict_one(patient: dict) -> dict:
    """
    Predict readmission risk for a single patient.
    """

    model, scaler, _ = _load()

    row = build_feature_row(patient)

    X = scaler.transform(np.array([row]))

    probability = float(model.predict_proba(X)[0][1])

    return {
        "risk_score": round(probability, 4),
        "risk_percent": round(probability * 100, 1),
        "risk_label": risk_bucket(probability),
    }


# ---------------------------------------------------------------------
# SHAP Explainability
# ---------------------------------------------------------------------


def explain_one(patient: dict, top_n: int = 5) -> dict:
    """
    Returns a patient-specific explanation using SHAP.

    Output:
    {
        summary: "...",
        top_factors: [...]
    }
    """

    _, scaler, feature_cols = _load()

    explainer = _get_explainer()

    row = build_feature_row(patient)

    X = scaler.transform(np.array([row]))

    shap_values = explainer.shap_values(X)

    # Compatible with SHAP 0.51+
    if isinstance(shap_values, list):
        class_values = np.asarray(shap_values[1])[0]
    else:
        arr = np.asarray(shap_values)

        if arr.ndim == 3:
            class_values = arr[0, :, 1]
        else:
            class_values = arr[0]

    contributions = []

    for feature, value, shap_value in zip(
        feature_cols,
        row,
        class_values,
    ):

        contributions.append(
            {
                "feature": feature,
                "label": FEATURE_LABELS.get(feature, feature),
                "value": _format_value(feature, value),
                "impact": round(abs(float(shap_value)), 5),
                "direction": (
                    "increases_risk"
                    if shap_value > 0
                    else "decreases_risk"
                ),
                "shap_value": float(shap_value),
            }
        )

    contributions.sort(
        key=lambda x: abs(x["shap_value"]),
        reverse=True,
    )

    top = contributions[:top_n]

    higher = [
        f"{x['label']} ({x['value']})"
        for x in top
        if x["direction"] == "increases_risk"
    ]

    lower = [
        f"{x['label']} ({x['value']})"
        for x in top
        if x["direction"] == "decreases_risk"
    ]

    summary_parts = []

    if higher:
        summary_parts.append(
            "Risk increased mainly because of "
            + ", ".join(higher)
        )

    if lower:
        summary_parts.append(
            "Risk reduced because of "
            + ", ".join(lower)
        )

    if summary_parts:
        summary = ". ".join(summary_parts) + "."
    else:
        summary = (
            "No single clinical factor dominated this prediction. "
            "The model considered several features with relatively "
            "small individual contributions."
        )

    return {
        "summary": summary,
        "top_factors": [
            {
                "label": item["label"],
                "value": item["value"],
                "direction": item["direction"],
                "impact": item["impact"],
            }
            for item in top
        ],
    }
# ---------------------------------------------------------------------
# Batch prediction
# ---------------------------------------------------------------------


def predict_batch(patients: list) -> list:
    """
    Predict readmission risk for multiple patients.
    """

    model, scaler, _ = _load()

    rows = [build_feature_row(patient) for patient in patients]

    X = scaler.transform(np.array(rows))

    probabilities = model.predict_proba(X)[:, 1]

    return [
        {
            "risk_score": round(float(probability), 4),
            "risk_percent": round(float(probability) * 100, 1),
            "risk_label": risk_bucket(float(probability)),
        }
        for probability in probabilities
    ]


# ---------------------------------------------------------------------
# Global feature importance
# ---------------------------------------------------------------------


def feature_importance() -> dict:
    """
    Returns the trained Random Forest's global feature importances.

    Used for analytics pages and optional visualizations.
    """

    model, _, feature_cols = _load()

    importance = [
        round(float(value), 4)
        for value in model.feature_importances_
    ]

    ranked = sorted(
        zip(feature_cols, importance),
        key=lambda item: item[1],
        reverse=True,
    )

    return dict(ranked)


# ---------------------------------------------------------------------
# Convenience helper
# ---------------------------------------------------------------------


def model_loaded() -> bool:
    """
    Returns True if the model has already been loaded into memory.
    """

    return _model is not None


# ---------------------------------------------------------------------
# Warm-start model
# ---------------------------------------------------------------------

try:
    _load()
except Exception:
    # During development or before train_model.py has been run,
    # the artifacts may not yet exist. We simply defer loading
    # until the first prediction request.
    pass