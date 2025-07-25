from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # or SUPABASE_ANON_KEY
BUCKET_NAME = "userfiles"

# Validate environment variables
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is not set")

# Create the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection on import
try:
    # Simple test to verify connection
    test_response = supabase.table("users").select("id").limit(1).execute()
    print("Supabase connected successfully")
except Exception as e:
    print(f"⚠️  Supabase connection warning: {e}")

# Export the client
__all__ = ['supabase', 'BUCKET_NAME']