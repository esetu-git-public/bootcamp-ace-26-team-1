#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

echo "========================================"
echo "Hospital Readmission Prediction System"
echo "========================================"

echo "Starting FastAPI Server..."

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "Backend: http://localhost:8000"
echo "Swagger: http://localhost:8000/docs"

wait
