@echo off
echo ========================================
echo Hospital Readmission Prediction System
echo ========================================

echo.

echo Starting FastAPI Server...

python -m uvicorn app.main:app --reload

pause