"""Auth API routes — register and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import register_user, authenticate_user, create_user_token
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user account."""
    try:
        user = await register_user(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
        )
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login with email and password. Returns a JWT access token."""
    user = await authenticate_user(db=db, email=request.email, password=request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_user_token(user)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get the current authenticated user's profile."""
    from app.models.user import User
    from sqlalchemy import select

    result = await db.execute(
        select(User).where(User.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)
