"""
Shared FastAPI dependencies for DevOps360.

Includes security dependencies such as require_cognito_token, which is used to protect routes that require authentication.
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.cognito import verify_cognito_token

# HTTPBearer is a FastAPI security scheme for extracting Bearer tokens from requests
security = HTTPBearer(auto_error=False)

def require_cognito_token(request: Request, auth: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    FastAPI dependency to protect endpoints.
    - Requires a valid Cognito JWT token from either a cookie or Authorization header.
    - Returns the decoded token if valid, otherwise raises an exception.
    """
    token = request.cookies.get("cognito_token")  # Try to get token from cookie first
    if not token and auth:
        token = auth.credentials  # Fallback to Authorization header
    if not token:
        # No token found, raise 401 Unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    decoded = verify_cognito_token(token)
    if not decoded:
        # Token is invalid or expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )
    return decoded
