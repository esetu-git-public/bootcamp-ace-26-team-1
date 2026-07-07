import io
import pandas as pd

from supabase import database as db
from app.ml.preprocess import validate_and_clean
from app.utils.helpers import paginate


def get_patients_page(page: int, page_size: int, search: str = ""):
    total = db.count_patients()
    page, total_pages, offset = paginate(total, page, page_size)
    rows = db.list_patients(limit=page_size, offset=offset, search=search)
    return {
        "items": rows, "page": page, "page_size": page_size,
        "total": total, "total_pages": total_pages,
    }


def add_patient(patient: dict, created_by: str) -> dict:
    return db.insert_patient(patient, created_by=created_by)


def import_csv(file_bytes: bytes, created_by: str) -> dict:
    df = pd.read_csv(io.BytesIO(file_bytes))
    clean_df, warnings = validate_and_clean(df)
    if clean_df.empty:
        return {"inserted": 0, "warnings": warnings + ["No valid rows to import"]}
    records = clean_df.to_dict(orient="records")
    inserted = db.bulk_insert_patients(records, created_by=created_by)
    return {"inserted": inserted, "warnings": warnings}


def dashboard_stats() -> dict:
    return db.get_patient_stats()
