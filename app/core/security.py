from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """
    MOCK JWT authentication dependency.
    
    Phase 1 behavior:
    - Accepts ANY Bearer token without validation.
    - Returns a hardcoded mock user dict: {"user_id": "mock-user-001", "email": "mock@example.com"}
    - Still requires the Authorization header to be present (returns 403 if missing)
      so the API contract is established early.
    
    Phase 3 TODO:
    - Decode and validate the JWT token using python-jose.
    - Extract user_id and claims from the token payload.
    - Raise HTTPException(401) for expired/invalid tokens.
    """
    # For Phase 1 — accept any token, return mock user
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing token",
        )
    return {"user_id": "mock-user-001", "email": "mock@example.com", "token": token}
