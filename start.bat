@echo off
REM Move to the directory where this script is located
cd /d "%~dp0"
echo ========================================
echo Hospital Readmission Prediction System
echo ========================================

echo.

echo Starting FastAPI Server...

python -m uvicorn app.main:app --reload

pause