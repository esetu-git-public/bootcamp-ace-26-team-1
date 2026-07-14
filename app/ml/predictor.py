"""
Loads the trained RandomForest model + scaler and exposes a simple predict API.
Regenerate model.pkl / scaler.pkl by running train_model.py at the project root.
"""
import os
import joblib
import numpy as np

from app.ml.feature_engineering import build_feature_row
from app.utils.helpers import risk_bucket

_DIR = os.path.dirname(__file__)
_MODEL_PATH = os.path.join(_DIR, "model.pkl")
_SCALER_PATH = os.path.join(_DIR, "scaler.pkl")
_FEATURES_PATH = os.path.join(_DIR, "feature_cols.pkl")

_model = None
_scaler = None
_feature_cols = None


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

import joblib

model = None
scaler = None
feature_cols = None
label_encoders = None


def load_model():
    global model, scaler, feature_cols, label_encoders

    model = joblib.load("app/ml/model.pkl")
    scaler = joblib.load("app/ml/scaler.pkl")
    feature_cols = joblib.load("app/ml/feature_cols.pkl")