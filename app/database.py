from supabase import create_client, Client
from functools import lru_cache
from app.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Create and return a cached Supabase client instance.
    Uses lru_cache to ensure only one client is created and reused.
    This improves performance and prevents connection leaks.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)


def get_db() -> Client:
    """
    Dependency injection function for FastAPI routes.
    Returns the cached Supabase client instance.
    """
    return get_supabase_client()
