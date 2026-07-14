from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

from app.config import get_settings
from app.api import auth, patients, prediction, reports, audit

settings = get_settings()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ---- API routers ----
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(prediction.router)
app.include_router(reports.router)
app.include_router(audit.router)


# ---- Server-rendered pages ----
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "app_name": settings.app_name})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "app_name": settings.app_name})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "app_name": settings.app_name})


@app.get("/patients", response_class=HTMLResponse)
def patients_page(request: Request):
    return templates.TemplateResponse("patients.html", {"request": request, "app_name": settings.app_name})


@app.get("/prediction", response_class=HTMLResponse)
def prediction_page(request: Request):
    return templates.TemplateResponse("prediction.html", {"request": request, "app_name": settings.app_name})


@app.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request, "app_name": settings.app_name})


@app.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request):
    return templates.TemplateResponse("audit.html", {"request": request, "app_name": settings.app_name})


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name, "supabase_configured": settings.supabase_configured}

from app.ml.predictor import load_model

@app.on_event("startup")
def startup_event():
    print("Loading ML model...")

    load_model()

    print("ML model loaded successfully.")