"""
Turns a raw patient record (as submitted from the prediction form or CSV row)
into the numeric feature vector the model expects. Mirrors the encoding used
in train_model.py.
"""
from app.utils.helpers import parse_blood_pressure

GENDER_MAP = {"Male": 0, "Female": 1, "Other": 2}
DESTINATION_MAP = {"Home": 0, "Rehab": 1, "Nursing_Facility": 2}
YES_NO_MAP = {"No": 0, "Yes": 1}

FEATURE_ORDER = [
    "age", "gender_enc", "systolic_bp", "diastolic_bp", "cholesterol", "bmi",
    "diabetes_enc", "hypertension_enc", "medication_count", "length_of_stay",
    "discharge_enc",
]


def build_feature_row(patient: dict) -> list:
    systolic, diastolic = parse_blood_pressure(patient["blood_pressure"])

    try:
        gender_enc = GENDER_MAP[patient["gender"]]
    except KeyError:
        raise ValueError(f"gender must be one of {list(GENDER_MAP)}")

    try:
        discharge_enc = DESTINATION_MAP[patient["discharge_destination"]]
    except KeyError:
        raise ValueError(f"discharge_destination must be one of {list(DESTINATION_MAP)}")

    try:
        diabetes_enc = YES_NO_MAP[patient["diabetes"]]
        hypertension_enc = YES_NO_MAP[patient["hypertension"]]
    except KeyError:
        raise ValueError("diabetes/hypertension must be 'Yes' or 'No'")

    row = {
        "age": int(patient["age"]),
        "gender_enc": gender_enc,
        "systolic_bp": systolic,
        "diastolic_bp": diastolic,
        "cholesterol": int(patient["cholesterol"]),
        "bmi": float(patient["bmi"]),
        "diabetes_enc": diabetes_enc,
        "hypertension_enc": hypertension_enc,
        "medication_count": int(patient["medication_count"]),
        "length_of_stay": int(patient["length_of_stay"]),
        "discharge_enc": discharge_enc,
    }
    return [row[col] for col in FEATURE_ORDER]
