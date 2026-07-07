import os
import httpx
from dotenv import load_dotenv

# 1. Load the credentials directly from your .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_raw_connection():
    print("Testing raw REST connection to Supabase...\n")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Could not find SUPABASE_URL or SUPABASE_KEY.")
        print("Make sure your .env file is saved in the root folder!")
        return

    # 2. Set up the exact headers Supabase requires
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # 3. Try to fetch 1 row from the patients table
    # (Even if the table is empty, a 200 OK status means the connection works)
    test_url = f"{SUPABASE_URL}/rest/v1/patients?limit=1"

    try:
        response = httpx.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Your URL and Key are perfectly valid.")
            print("Your local code can officially talk to your Supabase cloud database.")
        else:
            print(f"❌ Connection failed with Status Code: {response.status_code}")
            print(f"Message from Supabase: {response.text}")
            
    except Exception as e:
        print(f"❌ Network Error: Could not reach Supabase.")
        print(f"Details: {e}")

if __name__ == "__main__":
    test_raw_connection()