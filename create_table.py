import sys
import os
from dotenv import load_dotenv

# 1. Load environment variables first
load_dotenv()

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine

# 2. IMPORTANT: We are ONLY importing the User model here.
# This ensures SQLAlchemy only knows about the User table for now.
from app.models.user import User

def create_user_table():
    """
    Creates ONLY the 'users' table in the database for storing user details.
    """
    print("Initiating User table creation in Supabase PostgreSQL...")
    
    try:
        # User.__table__.create strictly builds the users table.
        # checkfirst=True ensures it doesn't crash if the table already exists.
        User.__table__.create(bind=engine, checkfirst=True)
        print("✅ Success! The 'users' table has been created.")
    except Exception as e:
        print("❌ Failed to create the users table.")
        print(f"Error details:\n{e}")

if __name__ == "__main__":
    # Calling the correct function
    create_user_table()