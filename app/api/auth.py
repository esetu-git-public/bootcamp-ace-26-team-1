from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from app.services import auth_service
from app.services.audit_service import log_action
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "clinician"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup(payload: SignupRequest):
    try:
        result = auth_service.register_user(
            email=payload.email, password=payload.password,
            full_name=payload.full_name, role=payload.role,
        )
        log_action(actor=payload.email, action="signup", details=f"role={payload.role}")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login")
def login(payload: LoginRequest):
    try:
        result = auth_service.login_user(email=payload.email, password=payload.password)
        log_action(actor=payload.email, action="login")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user
