from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import Client
from typing import Annotated
import logging
from postgrest.exceptions import APIError
from app.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Main page with HTMX interface for user management.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/test-connection", response_class=HTMLResponse)
async def test_connection_web(request: Request, db: Client = Depends(get_db)):
    """
    Test Supabase connection and return HTML fragment.
    """
    try:
        logger.info("Testing Supabase connection (web)")
        response = db.table('users').select('count', count='exact').execute()

        return templates.TemplateResponse(
            "components/connection_status.html",
            {
                "request": request,
                "success": True,
                "database": "users table accessible",
                "user_count": response.count if hasattr(response, 'count') else 0
            }
        )
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return templates.TemplateResponse(
            "components/connection_status.html",
            {
                "request": request,
                "success": False,
                "error": str(e)
            }
        )


@router.get("/users", response_class=HTMLResponse)
async def list_users_web(request: Request, db: Client = Depends(get_db)):
    """
    List all users and return HTML fragment.
    """
    try:
        logger.info("Fetching users for web interface")
        response = db.table('users').select('*').order('created_at', desc=True).execute()

        return templates.TemplateResponse(
            "components/user_list.html",
            {
                "request": request,
                "users": response.data
            }
        )
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return HTMLResponse(
            content=f'<div class="alert alert-error">Error loading users: {str(e)}</div>',
            status_code=500
        )


@router.post("/users", response_class=HTMLResponse)
async def create_user_web(
    request: Request,
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    db: Client = Depends(get_db)
):
    """
    Create a new user and return updated user list.
    """
    try:
        logger.info(f"Creating user via web interface: {email}")

        # Insert user
        response = db.table('users').insert({
            "name": name,
            "email": email
        }).execute()

        if not response.data:
            logger.error("Failed to create user: No data returned")
            return HTMLResponse(
                content='<div class="alert alert-error">Failed to create user</div>',
                status_code=400
            )

        logger.info(f"Successfully created user: {response.data[0].get('id')}")

        # Return updated user list
        all_users = db.table('users').select('*').order('created_at', desc=True).execute()

        return templates.TemplateResponse(
            "components/user_list.html",
            {
                "request": request,
                "users": all_users.data
            }
        )

    except APIError as e:
        # Check for duplicate email
        if e.code == '23505' or 'duplicate key' in e.message.lower():
            logger.warning(f"Duplicate email attempted: {email}")
            return HTMLResponse(
                content='<div class="alert alert-error">A user with this email already exists</div>',
                status_code=400
            )
        logger.error(f"API error creating user: {e.message}")
        return HTMLResponse(
            content=f'<div class="alert alert-error">Error: {e.message}</div>',
            status_code=500
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        return HTMLResponse(
            content=f'<div class="alert alert-error">Error: {str(e)}</div>',
            status_code=500
        )
