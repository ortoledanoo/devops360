"""
Shared FastAPI dependencies for DevOps360.

Includes `require_cognito_token`, a reusable dependency that protects secured routes.
Validates an AWS Cognito JWT from cookie or Authorization header using Depends().
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.cognito import verify_cognito_token

# HTTPBearer is a FastAPI security scheme for extracting Bearer tokens from requests
security = HTTPBearer(auto_error=False)

def require_cognito_token(request: Request, auth: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    FastAPI dependency to protect secured endpoints using AWS Cognito authentication.

    This function validates a JWT token issued by AWS Cognito.
    It first checks for the token in the `cognito_token` cookie.
    If not found, it tries to retrieve the token from the `Authorization` header.
    If a valid token is found and verified, it returns the decoded payload.
    Otherwise, it raises a 401 Unauthorized exception.
    """
    token = request.cookies.get("cognito_token")  # Try to get token from the cookie "cognito_token" first
    if not token and auth:
        token = auth.credentials  # If token is not in cookie, try getting it from Authorization header
    if not token:
        # if no token found, raise 401 Unauthorized
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
