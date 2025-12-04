"""User service containing all business logic for user operations."""
from supabase import Client
from typing import List, Dict, Any
import logging
from postgrest.exceptions import APIError
from app.models.user import UserCreate

logger = logging.getLogger(__name__)


class UserServiceError(Exception):
    """Base exception for user service errors."""
    pass


class DuplicateEmailError(UserServiceError):
    """Raised when attempting to create a user with a duplicate email."""
    pass


class UserService:
    """Service class for user-related business logic."""

    def __init__(self, db: Client):
        self.db = db

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the Supabase connection.

        Returns:
            Dict with connection status and user count

        Raises:
            UserServiceError: If connection test fails
        """
        try:
            logger.info("Testing Supabase connection")
            response = self.db.table('users').select('count', count='exact').execute()
            user_count = response.count if hasattr(response, 'count') else 0

            logger.info(f"Connection successful, user count: {user_count}")
            return {
                "success": True,
                "database": "users table accessible",
                "user_count": user_count
            }
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            raise UserServiceError(f"Failed to connect to database: {str(e)}")

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user dictionaries

        Raises:
            UserServiceError: If fetching users fails
        """
        try:
            logger.info(f"Fetching users with skip={skip}, limit={limit}")
            response = self.db.table('users')\
                .select('*')\
                .order('created_at', desc=True)\
                .range(skip, skip + limit - 1)\
                .execute()

            logger.info(f"Successfully fetched {len(response.data)} users")
            return response.data
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            raise UserServiceError(f"Failed to fetch users: {str(e)}")

    async def create_user(self, user: UserCreate) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            user: UserCreate model with user data

        Returns:
            Created user dictionary

        Raises:
            DuplicateEmailError: If email already exists
            UserServiceError: If creation fails for other reasons
        """
        try:
            logger.info(f"Creating user with email: {user.email}")
            response = self.db.table('users').insert(user.model_dump()).execute()

            if not response.data:
                logger.error("Failed to create user: No data returned")
                raise UserServiceError("Failed to create user")

            logger.info(f"Successfully created user with ID: {response.data[0].get('id')}")
            return response.data[0]

        except APIError as e:
            # Check for unique constraint violation
            if e.code == '23505' or 'duplicate key' in e.message.lower():
                logger.warning(f"Duplicate email attempted: {user.email}")
                raise DuplicateEmailError("A user with this email already exists")

            logger.error(f"API error creating user: {e.message}")
            raise UserServiceError(f"Error creating user: {e.message}")

        except DuplicateEmailError:
            raise

        except Exception as e:
            logger.error(f"Unexpected error creating user: {str(e)}")
            raise UserServiceError(f"Error creating user: {str(e)}")


def get_user_service(db: Client) -> UserService:
    """
    Factory function to create a UserService instance.
    Used for dependency injection in FastAPI routes.

    Args:
        db: Supabase client instance

    Returns:
        UserService instance
    """
    return UserService(db)
