# FastAPI application entry point
# Initializes the API server and registers routes

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import runs_router

app = FastAPI(
    title="Finance Automation Backend",
    description="Accounts Payable automation with Supabase integration",
    version="1.0.0"
)

# CORS middleware (configure as needed for your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route blueprints
app.include_router(runs_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "finance-automation-backend"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "finance-automation-backend",
        "version": "1.0.0"
    }

