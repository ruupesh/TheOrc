"""Pydantic schemas for authentication (register, login, token response)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """New user registration request."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response after successful login."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user information."""
    id: uuid.UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
