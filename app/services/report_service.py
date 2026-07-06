import io
import csv
from supabase import database as db


def summary_report() -> dict:
    stats = db.get_patient_stats()
    predictions = db.list_predictions(limit=1000)
    if predictions:
        avg_risk = sum(p["risk_score"] for p in predictions) / len(predictions)
        high_risk = sum(1 for p in predictions if p["risk_label"] == "High")
    else:
        avg_risk, high_risk = 0, 0
    return {
        **stats,
        "total_predictions_run": len(predictions),
        "avg_predicted_risk": round(avg_risk * 100, 1),
        "high_risk_predictions": high_risk,
    }


def export_patients_csv() -> bytes:
    rows = db.list_patients(limit=100000, offset=0)
    buffer = io.StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def export_predictions_csv() -> bytes:
    rows = db.list_predictions(limit=100000)
    buffer = io.StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")
