from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user model with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Model for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Model for updating an existing user. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="User's email address")


class UserResponse(UserBase):
    """Model for user responses including database fields."""
    id: UUID = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="Timestamp when user was created")

    model_config = {"from_attributes": True}
