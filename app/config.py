# Configuration management
# Loads environment variables securely

import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    Required environment variables:
    - SUPABASE_URL: Supabase project URL
    - SUPABASE_KEY: Supabase anon/service role key
    """
    
    def __init__(self):
        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
        
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY environment variable is required")
    
    def validate(self) -> None:
        """Validate that all required settings are present"""
        if not self.SUPABASE_URL or not self.SUPABASE_KEY:
            raise ValueError("Missing required environment variables")


# Global settings instance
settings = Settings()


