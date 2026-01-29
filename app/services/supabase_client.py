# Supabase client initialization
# Creates and manages the Supabase client instance

from supabase import create_client, Client
from app.config import settings


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Reads credentials from environment variables:
    - SUPABASE_URL
    - SUPABASE_KEY
    
    Returns:
        Client: Configured Supabase client
        
    Raises:
        ValueError: If required environment variables are missing
    """
    try:
        client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        return client
    except Exception as e:
        raise ValueError(f"Failed to create Supabase client: {str(e)}")


# Global client instance (singleton pattern)
_supabase_client: Client = None


def get_client() -> Client:
    """
    Get the global Supabase client instance (singleton).
    Creates the client on first call, reuses on subsequent calls.
    
    Returns:
        Client: Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    
    return _supabase_client


