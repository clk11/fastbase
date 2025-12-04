"""Web routes for HTML/HTMX responses."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import Client
from typing import Annotated
from app.database import get_db
from app.models.user import UserCreate
from app.services.user_service import get_user_service, DuplicateEmailError, UserServiceError

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/test-connection", response_class=HTMLResponse)
async def test_connection_web(
    request: Request,
    db: Client = Depends(get_db)
):
    service = get_user_service(db)
    try:
        result = await service.test_connection()
        return templates.TemplateResponse(
            "components/connection_status.html",
            {
                "request": request,
                "success": True,
                "database": result["database"],
                "user_count": result["user_count"]
            }
        )
    except UserServiceError as e:
        return templates.TemplateResponse(
            "components/connection_status.html",
            {
                "request": request,
                "success": False,
                "error": str(e)
            }
        )


@router.get("/users", response_class=HTMLResponse)
async def list_users_web(
    request: Request,
    db: Client = Depends(get_db)
):
    service = get_user_service(db)
    try:
        users = await service.get_users()
        return templates.TemplateResponse(
            "components/user_list.html",
            {
                "request": request,
                "users": users
            }
        )
    except UserServiceError as e:
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
    service = get_user_service(db)
    try:
        # Create user model
        user = UserCreate(name=name, email=email)
        await service.create_user(user)

        # Return updated user list
        users = await service.get_users()
        return templates.TemplateResponse(
            "components/user_list.html",
            {
                "request": request,
                "users": users
            }
        )

    except DuplicateEmailError as e:
        return HTMLResponse(
            content=f'<div class="alert alert-error">{str(e)}</div>',
            status_code=400
        )
    except UserServiceError as e:
        return HTMLResponse(
            content=f'<div class="alert alert-error">Error: {str(e)}</div>',
            status_code=500
        )
