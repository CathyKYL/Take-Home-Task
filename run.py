#!/usr/bin/env python3
"""
Startup script for Finance Automation Backend
Validates environment and starts the server
"""

import os
import sys
from pathlib import Path


def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = []
    
    # Try to load from .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
    
    # Check if all required vars are present
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with:")
        print("   SUPABASE_URL=your_supabase_project_url")
        print("   SUPABASE_KEY=your_supabase_key")
        sys.exit(1)
    
    print("✅ Environment variables configured")


def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import supabase
        import pandas
        import openpyxl
        import rapidfuzz
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("\n📦 Please install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Main startup function"""
    print("🚀 Starting Finance Automation Backend...\n")
    
    # Validate environment
    check_env_vars()
    check_dependencies()
    
    print("\n✨ Starting server...")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("🔗 Health check: http://localhost:8000/health\n")
    
    # Start uvicorn
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()


