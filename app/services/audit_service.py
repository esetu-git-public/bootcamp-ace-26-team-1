from supabase import database as db
from app.utils.logger import audit_logger


def log_action(actor: str, action: str, details: str = ""):
    audit_logger.info(f"actor={actor} action={action} details={details}")
    return db.insert_audit_log(actor=actor, action=action, details=details)


def get_logs(limit: int = 200) -> list:
    return db.list_audit_logs(limit=limit)
