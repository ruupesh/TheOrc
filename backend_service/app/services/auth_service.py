"""Auth service — user registration, login, and session ownership."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_session import UserSession
from app.core.security import get_password_hash, verify_password, create_access_token
from app.utils.logging import logger


async def register_user(
    db: AsyncSession, email: str, username: str, password: str
) -> User:
    """Register a new user with hashed password.

    Raises ValueError if email or username is already taken.
    """
    # Check for existing email
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValueError(f"Email '{email}' is already registered")

    # Check for existing username
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise ValueError(f"Username '{username}' is already taken")

    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("User registered", user_id=str(user.id), email=email)
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    """Authenticate a user by email and password. Returns User or None."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_token(user: User) -> str:
    """Create a JWT access token for the given user."""
    return create_access_token(
        data={"sub": str(user.id), "email": user.email, "username": user.username}
    )


async def get_or_create_user_session(
    db: AsyncSession, user_id: uuid.UUID, adk_session_id: str, app_name: str = "orchestrator_api"
) -> UserSession:
    """Get or create a UserSession record linking an ADK session to a user."""
    result = await db.execute(
        select(UserSession).where(UserSession.adk_session_id == adk_session_id)
    )
    user_session = result.scalar_one_or_none()

    if user_session:
        # Validate ownership
        if user_session.user_id != user_id:
            raise PermissionError("Session does not belong to this user")
        return user_session

    user_session = UserSession(
        user_id=user_id,
        adk_session_id=adk_session_id,
        app_name=app_name,
    )
    db.add(user_session)
    await db.commit()
    await db.refresh(user_session)
    logger.info(
        "Created user session mapping",
        user_id=str(user_id),
        adk_session_id=adk_session_id,
    )
    return user_session


async def validate_session_ownership(
    db: AsyncSession, user_id: uuid.UUID, adk_session_id: str
) -> bool:
    """Check if the given ADK session belongs to the user. Returns True if valid."""
    result = await db.execute(
        select(UserSession).where(
            UserSession.adk_session_id == adk_session_id,
            UserSession.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None
