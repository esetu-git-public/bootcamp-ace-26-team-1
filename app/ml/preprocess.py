"""
Validates and cleans a raw uploaded CSV of patient records before it is
persisted or scored. Expected columns match hospital_readmissions_30k.csv.
"""
import pandas as pd

REQUIRED_COLUMNS = [
    "patient_id", "age", "gender", "blood_pressure", "cholesterol", "bmi",
    "diabetes", "hypertension", "medication_count", "length_of_stay",
    "discharge_destination",
]

OPTIONAL_COLUMNS = ["readmitted_30_days"]

VALID_GENDER = {"Male", "Female", "Other"}
VALID_YN = {"Yes", "No"}
VALID_DESTINATION = {"Home", "Rehab", "Nursing_Facility"}


def validate_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    errors = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
        return df, errors

    df = df.copy()
    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    if len(df) < before:
        errors.append(f"Dropped {before - len(df)} rows with missing required values")

    bad_gender = ~df["gender"].isin(VALID_GENDER)
    bad_diabetes = ~df["diabetes"].isin(VALID_YN)
    bad_hyper = ~df["hypertension"].isin(VALID_YN)
    bad_dest = ~df["discharge_destination"].isin(VALID_DESTINATION)
    bad_bp = ~df["blood_pressure"].astype(str).str.match(r"^\d{2,3}/\d{2,3}$")

    bad_mask = bad_gender | bad_diabetes | bad_hyper | bad_dest | bad_bp
    if bad_mask.any():
        errors.append(f"Dropped {int(bad_mask.sum())} rows with invalid categorical/format values")
        df = df[~bad_mask]

    if "readmitted_30_days" not in df.columns:
        df["readmitted_30_days"] = None

    return df, errors
