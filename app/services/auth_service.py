from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import get_settings
from supabase import auth as supa_auth

settings = get_settings()


def create_access_token(user: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "role": user.get("role", "clinician"),
        "full_name": user.get("full_name", ""),
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc


def register_user(email: str, password: str, full_name: str, role: str = "clinician") -> dict:
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")
    user = supa_auth.sign_up(email=email, password=password, full_name=full_name, role=role)
    token = create_access_token(user)
    return {"user": user, "access_token": token, "token_type": "bearer"}


def login_user(email: str, password: str) -> dict:
    user = supa_auth.sign_in(email=email, password=password)
    token = create_access_token(user)
    return {"user": user, "access_token": token, "token_type": "bearer"}
