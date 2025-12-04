from fastapi import FastAPI, Depends
from app.config import get_settings, Settings
from app import routes

app = FastAPI(
    title="FastBase",
    description="FastAPI + Supabase + HTMX User Management App",
    version="0.1.0"
)

app.include_router(routes.router, tags=["HTMX"])

@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Health check endpoint that returns app configuration.
    Tests that Pydantic Settings are working correctly.
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "debug": settings.debug
    }


@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    """
    Configuration endpoint that displays current settings.
    Useful for testing environment variable loading.
    """
    return {
        "app_name": settings.app_name,
        "debug": settings.debug
    }
