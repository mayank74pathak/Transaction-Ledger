
import os

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables from the .env file
load_dotenv()

# Read Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

# Validate configuration
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError(
        "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env"
    )

# Initialize the Supabase client
supabase: Client = create_client(
    SUPABASE_URL.rstrip("/"),
    SUPABASE_SERVICE_ROLE_KEY,
)
