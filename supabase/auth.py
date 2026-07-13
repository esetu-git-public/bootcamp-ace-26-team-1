"""
Login/signup helpers. Uses Supabase Auth (GoTrue REST API) when configured,
otherwise a local bcrypt scheme backed by the `users` table in
supabase/database.py.
"""
import uuid
from passlib.context import CryptContext

from supabase.client import SupabaseUnavailable, get_supabase
from supabase import database as db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def sign_up(email: str, password: str, full_name: str, role: str = "clinician") -> dict:
    if db.get_user_by_email(email):
        raise ValueError("A user with that email already exists")
    sb = get_supabase()
    if sb:
        try:
            result = sb.auth_sign_up(email, password)
            user_id = result.get("id") or result.get("user", {}).get("id") or str(uuid.uuid4())
            db.create_user(user_id, email, full_name, role, hash_password(password))
            return {"id": user_id, "email": email, "full_name": full_name, "role": role}
        except SupabaseUnavailable:
            pass

    if db.get_user_by_email(email):
        raise ValueError("A user with that email already exists")
    user_id = str(uuid.uuid4())
    db.create_user(user_id, email, full_name, role, hash_password(password))
    return {"id": user_id, "email": email, "full_name": full_name, "role": role}


def sign_in(email: str, password: str) -> dict:
    sb = get_supabase()
    if sb:
        try:
            result = sb.auth_sign_in(email, password)
            user = result.get("user", {})
            if not user:
                raise ValueError("Invalid credentials")
            profile = db.get_user_by_email(email) or {}
            return {
                "id": user.get("id"), "email": email,
                "full_name": profile.get("full_name", ""), "role": profile.get("role", "clinician"),
            }
        except SupabaseUnavailable:
            pass

    user = db.get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid credentials")
    return {"id": user["id"], "email": user["email"], "full_name": user["full_name"], "role": user["role"]}
