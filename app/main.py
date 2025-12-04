from fastapi import FastAPI, Depends
from app.config import get_settings, Settings
from app import routes, web

# Initialize FastAPI app
app = FastAPI(
    title="FastBase",
    description="FastAPI + Supabase + HTMX User Management App",
    version="0.1.0"
)

# Register routers
app.include_router(web.router, prefix="/web", tags=["Web"])
app.include_router(routes.router, prefix="/api", tags=["API"])


@app.get("/")
async def root():
    """Redirect to web interface."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/web/")


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
