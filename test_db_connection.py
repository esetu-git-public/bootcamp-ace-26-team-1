import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# 1. LOAD DOTENV FIRST! 
# This ensures environment variables are loaded into memory BEFORE we import the engine.
load_dotenv()

# Since the file is in the root directory, we just ensure the root is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. NOW import the engine
from app.database.connection import engine

def test_connection():
    """
    Tests the connection to the database by executing a simple SELECT query.
    """
    print("Testing connection to Supabase PostgreSQL...\n")
    
    # Debugging output to see what SQLAlchemy actually parsed from your .env
    # This safely hides your password but confirms the username and host are loaded.
    print(f"🔍 Debug: Host = {engine.url.host}")
    print(f"🔍 Debug: User = {engine.url.username}")
    print(f"🔍 Debug: Port = {engine.url.port}\n")
    
    try:
        # Attempt to connect to the database
        with engine.connect() as connection:
            # Execute a basic query
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ Success! The database connection is working perfectly.")
            else:
                print("⚠️ Connected, but received an unexpected result.")
                
    except Exception as e:
        print("❌ Failed to connect to the database.")
        print(f"Error details:\n{e}")

if __name__ == "__main__":
    test_connection()