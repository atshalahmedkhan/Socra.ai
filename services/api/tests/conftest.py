import os
import sys
from pathlib import Path

# Unit tests must never connect to live services or inherit credentials from .env.
os.environ["DATABASE_URL"] = ""
os.environ["SUPABASE_PUBLISHABLE_KEY"] = ""
os.environ["SUPABASE_ANON_KEY"] = ""
os.environ["SUPABASE_SECRET_KEY"] = ""
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = ""
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_JWT_ISSUER"] = ""
os.environ["SUPABASE_JWKS_URL"] = ""
os.environ["SUPABASE_JWT_SECRET"] = ""

sys.path.insert(0, str(Path(__file__).parents[1]))
