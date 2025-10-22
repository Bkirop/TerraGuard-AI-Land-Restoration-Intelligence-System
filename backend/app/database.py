"""
Database connection and configuration using Supabase
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY", "")
# Global client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance"""
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            print("⚠️  WARNING: Supabase credentials not configured!")
            print("⚠️  Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
            # Return None instead of raising error for graceful degradation
            return None
        
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            print("✅ Supabase connected successfully")
        except Exception as e:
            print(f"❌ Supabase connection error: {e}")
            return None
    
    return _supabase_client


# Initialize on module import
supabase = get_supabase_client()