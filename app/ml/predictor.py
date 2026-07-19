import os
import joblib
import numpy as np
import shap

from app.ml.feature_engineering import build_feature_row
from app.utils.helpers import risk_bucket

_DIR = os.path.dirname(__file__)
_MODEL_PATH = os.path.join(_DIR, "model.pkl")
_SCALER_PATH = os.path.join(_DIR, "scaler.pkl")
_FEATURES_PATH = os.path.join(_DIR, "feature_cols.pkl")

_model = None
_scaler = None
_feature_cols = None
_explainer = None

FEATURE_LABELS = {
    "age": "Age",
    "gender_enc": "Gender",
    "systolic_bp": "Systolic blood pressure",
    "diastolic_bp": "Diastolic blood pressure",
    "cholesterol": "Cholesterol",
    "bmi": "BMI",
    "diabetes_enc": "Diabetes",
    "hypertension_enc": "Hypertension",
    "medication_count": "Medication count",
    "length_of_stay": "Length of stay",
    "discharge_enc": "Discharge destination",
}


def _load():
    global _model, _scaler, _feature_cols
    if _model is None:
        if not os.path.exists(_MODEL_PATH):
            raise RuntimeError(
                "Model artifacts not found. Run `python train_model.py` first "
                "to generate app/ml/model.pkl and scaler.pkl."
            )
        _model = joblib.load(_MODEL_PATH)
        _scaler = joblib.load(_SCALER_PATH)
        _feature_cols = joblib.load(_FEATURES_PATH)
    return _model, _scaler, _feature_cols


def _get_explainer():
    global _explainer
    if _explainer is None:
        model, _, _ = _load()
        _explainer = shap.TreeExplainer(model)
    return _explainer


def _format_value(feature: str, value) -> str:
    if feature == "gender_enc":
        return {0: "Male", 1: "Female", 2: "Other"}.get(value, str(value))
    if feature == "discharge_enc":
        return {0: "Home", 1: "Rehab", 2: "Nursing Facility"}.get(value, str(value))
    if feature in ("diabetes_enc", "hypertension_enc"):
        return "Yes" if value == 1 else "No"
    return str(value)


def _humanize_factor(feature: str, raw_value) -> str:
    """
    Turns a raw feature + value into a natural clause a clinician might
    actually write, e.g. "an elevated BMI of 33.2" instead of "BMI (33.2)".
    Demographic fields (age, gender) are phrased descriptively rather than
    causally, since a SHAP weight reflects a statistical pattern the model
    picked up, not a clinical mechanism.
    """
    if feature == "age":
        age = raw_value
        if age >= 80:
            return f"the patient's advanced age ({age})"
        if age >= 65:
            return f"the patient's older age ({age})"
        if age < 40:
            return f"the patient's relatively young age ({age})"
        return f"the patient's age ({age})"

    if feature == "bmi":
        bmi = raw_value
        if bmi >= 30:
            return f"a high BMI of {bmi}"
        if bmi >= 25:
            return f"an elevated BMI of {bmi}"
        if bmi < 18.5:
            return f"a low BMI of {bmi}"
        return f"a BMI of {bmi} in the typical range"

    if feature == "cholesterol":
        chol = raw_value
        if chol >= 240:
            return f"high cholesterol ({chol} mg/dL)"
        if chol >= 200:
            return f"borderline-high cholesterol ({chol} mg/dL)"
        return f"normal-range cholesterol ({chol} mg/dL)"

    if feature == "systolic_bp":
        bp = raw_value
        if bp >= 140:
            return f"high systolic blood pressure ({bp} mmHg)"
        if bp >= 120:
            return f"elevated systolic blood pressure ({bp} mmHg)"
        return f"normal systolic blood pressure ({bp} mmHg)"

    if feature == "diastolic_bp":
        bp = raw_value
        if bp >= 90:
            return f"high diastolic blood pressure ({bp} mmHg)"
        if bp >= 80:
            return f"elevated diastolic blood pressure ({bp} mmHg)"
        return f"normal diastolic blood pressure ({bp} mmHg)"

    if feature == "medication_count":
        n = raw_value
        if n >= 8:
            return f"a high number of medications ({n})"
        if n <= 2:
            return f"a small number of medications ({n})"
        return f"a moderate number of medications ({n})"

    if feature == "length_of_stay":
        days = raw_value
        if days <= 2:
            return f"a short {days}-day hospital stay"
        if days >= 10:
            return f"an extended {days}-day hospital stay"
        return f"a {days}-day hospital stay"

    if feature == "diabetes_enc":
        return "a history of diabetes" if raw_value == 1 else "no history of diabetes"

    if feature == "hypertension_enc":
        return "a history of hypertension" if raw_value == 1 else "no history of hypertension"

    if feature == "discharge_enc":
        dest = {0: "being discharged home", 1: "being discharged to a rehabilitation facility",
                2: "being discharged to a nursing facility"}.get(raw_value, "the discharge destination")
        return dest

    if feature == "gender_enc":
        gender = {0: "male", 1: "female", 2: "other"}.get(raw_value, str(raw_value))
        return f"the patient being recorded as {gender}"

    return f"{FEATURE_LABELS.get(feature, feature)} ({raw_value})"


def predict_one(patient: dict) -> dict:
    model, scaler, _ = _load()
    row = build_feature_row(patient)
    X = scaler.transform(np.array([row]))
    proba = float(model.predict_proba(X)[0][1])
    label = risk_bucket(proba)
    return {
        "risk_score": round(proba, 4),
        "risk_percent": round(proba * 100, 1),
        "risk_label": label,
    }


def explain_one(patient: dict, top_n: int = 4) -> dict:
    """
    Returns the top contributing factors behind a single prediction, using
    SHAP values from the trained RandomForest, plus a natural-language
    summary written the way a clinician might phrase it in a note -- rather
    than a mechanical "Feature (value)" list -- for display under the risk
    gauge. Hedged language ("appears associated with", "the model weighted")
    is used deliberately rather than causal claims ("caused", "will lead
    to"), since SHAP values describe what the model learned, not a
    validated clinical mechanism.
    """
    model, scaler, feature_cols = _load()
    explainer = _get_explainer()

    row = build_feature_row(patient)
    X = scaler.transform(np.array([row]))

    shap_values = explainer.shap_values(X)
    if isinstance(shap_values, list):
        class1_values = np.asarray(shap_values[1])[0]
    else:
        arr = np.asarray(shap_values)
        if arr.ndim == 3:
            class1_values = arr[0, :, 1]
        else:
            class1_values = arr[0]

    contributions = []
    for feat, raw_value, shap_val in zip(feature_cols, row, class1_values):
        contributions.append({
            "feature": feat,
            "label": FEATURE_LABELS.get(feat, feat),
            "value": _format_value(feat, raw_value),
            "note": _humanize_factor(feat, raw_value),
            "shap_value": round(float(shap_val), 5),
        })

    contributions.sort(key=lambda c: -abs(c["shap_value"]))
    top = contributions[:top_n]

    increasing = [c for c in top if c["shap_value"] > 0]
    decreasing = [c for c in top if c["shap_value"] < 0]

    def join_clauses(clauses: list) -> str:
        if len(clauses) == 1:
            return clauses[0]
        if len(clauses) == 2:
            return f"{clauses[0]} and {clauses[1]}"
        return ", ".join(clauses[:-1]) + f", and {clauses[-1]}"

    sentences = []
    if increasing:
        clause = join_clauses([c["note"] for c in increasing])
        verb = "appear" if len(increasing) > 1 else "appears"
        sentences.append(f"{clause[0].upper()}{clause[1:]} {verb} to be pushing this patient's predicted risk higher.")
    if decreasing:
        clause = join_clauses([c["note"] for c in decreasing])
        verb = "appear" if len(decreasing) > 1 else "appears"
        lead = "On the other hand, " if increasing else ""
        sentences.append(f"{lead}{clause[0].upper() if not lead else clause[0]}{clause[1:]} {verb} to be working in this patient's favor, pulling the predicted risk back down.")

    if sentences:
        summary = " ".join(sentences)
    else:
        summary = "No single factor stood out strongly for this patient — the prediction reflects a mix of small, roughly offsetting effects."

    caveat = (
        "This reflects patterns the model learned from historical data, not a clinical diagnosis. "
        "Use it alongside your own clinical judgment."
    )

    return {
        "summary": summary,
        "caveat": caveat,
        "top_factors": [
            {
                "label": c["label"],
                "value": c["value"],
                "note": c["note"],
                "direction": "increases_risk" if c["shap_value"] > 0 else "decreases_risk",
                "impact": abs(c["shap_value"]),
            }
            for c in top
        ],
    }


def predict_batch(patients: list) -> list:
    model, scaler, _ = _load()
    rows = [build_feature_row(p) for p in patients]
    X = scaler.transform(np.array(rows))
    probs = model.predict_proba(X)[:, 1]
    return [
        {
            "risk_score": round(float(p), 4),
            "risk_percent": round(float(p) * 100, 1),
            "risk_label": risk_bucket(float(p)),
        }
        for p in probs
    ]


def feature_importance() -> dict:
    model, _, feature_cols = _load()
    return dict(sorted(
        zip(feature_cols, [round(float(x), 4) for x in model.feature_importances_]),
        key=lambda kv: -kv[1],
    ))
