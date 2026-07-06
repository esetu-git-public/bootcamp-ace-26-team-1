import sys
import os
from dotenv import load_dotenv

# 1. Load environment variables first
load_dotenv()

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine
from app.database.base import Base

# 2. IMPORTANT: Import ALL models here!
# SQLAlchemy needs to see these to know what tables to build.
from app.models.user import User
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.audit import AuditLog
from app.models.report import Report

def create_all_tables():
    """
    Creates all missing tables in the database based on the imported models.
    """
    print("Initiating full table creation in Supabase PostgreSQL...")
    
    try:
        # Base.metadata.create_all inspects all imported models and builds missing tables
        Base.metadata.create_all(bind=engine)
        print("✅ Success! All database tables (patients, predictions, reports, etc.) have been created.")
    except Exception as e:
        print("❌ Failed to create tables.")
        print(f"Error details:\n{e}")

if __name__ == "__main__":
    create_all_tables()