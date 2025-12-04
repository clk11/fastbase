from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import List
import logging
from postgrest.exceptions import APIError
from app.database import get_db
from app.models.user import UserCreate, UserResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test-connection")
async def test_connection(db: Client = Depends(get_db)):
    """
    Test the Supabase connection.
    Verifies that the API can connect to Supabase and query the database.
    """
    try:
        logger.info("Testing Supabase connection")
        response = db.table('users').select('count', count='exact').execute()

        logger.info(f"Connection successful, user count: {response.count if hasattr(response, 'count') else 0}")
        return {
            "status": "success",
            "message": "Successfully connected to Supabase",
            "database": "users table accessible",
            "user_count": response.count if hasattr(response, 'count') else 0
        }
    except APIError as e:
        logger.error(f"Supabase API error during connection test: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Supabase: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during connection test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Supabase: {str(e)}"
        )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Client = Depends(get_db)
):
    """
    List users from the database with pagination.
    Returns users ordered by created_at descending (newest first).

    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    """
    try:
        logger.info(f"Fetching users with skip={skip}, limit={limit}")
        response = db.table('users').select('*').order('created_at', desc=True).range(skip, skip + limit - 1).execute()

        logger.info(f"Successfully fetched {len(response.data)} users")
        return response.data
    except APIError as e:
        logger.error(f"Supabase API error while fetching users: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Client = Depends(get_db)):
    """
    Create a new user in the database.

    Returns:
    - 201: User created successfully
    - 400: Duplicate email or validation error
    - 500: Internal server error
    """
    try:
        logger.info(f"Creating user with email: {user.email}")
        response = db.table('users').insert(user.model_dump()).execute()

        if not response.data:
            logger.error("Failed to create user: No data returned")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        logger.info(f"Successfully created user with ID: {response.data[0].get('id')}")
        return response.data[0]
    except APIError as e:
        # Check for unique constraint violation using error code
        if e.code == '23505' or 'duplicate key' in e.message.lower():
            logger.warning(f"Duplicate email attempted: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        logger.error(f"Supabase API error while creating user: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {e.message}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )
