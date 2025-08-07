"""
FastAPI dependencies for authentication and common functionality.

This module provides dependency functions that can be injected into
FastAPI endpoints for authentication, database access, and other
common operations.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.schemas import User, UserRole, TokenData
from app.utils.security import verify_token

# Security scheme for Bearer token authentication
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        TokenData: The current user's token data
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    return verify_token(credentials.credentials, credentials_exception)


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Dependency to get the current active user.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        TokenData: The current active user's token data
        
    Raises:
        HTTPException: If user is inactive
    """
    # In a real implementation, you would check user status from database
    # For now, we assume all users are active
    return current_user


def require_role(required_role: UserRole):
    """
    Create a dependency that requires a specific user role.
    
    Args:
        required_role: The role required to access the endpoint
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: TokenData = Depends(get_current_active_user)) -> TokenData:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    
    return role_checker


def require_employer():
    """
    Dependency that requires employer role.
    
    Returns:
        TokenData: Current user if they have employer role
    """
    return require_role(UserRole.EMPLOYER)


def require_student():
    """
    Dependency that requires student role.
    
    Returns:
        TokenData: Current user if they have student role
    """
    return require_role(UserRole.STUDENT)


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)) -> Optional[TokenData]:
    """
    Dependency to optionally get the current user (for public endpoints that can benefit from user context).
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Optional[TokenData]: The current user's token data or None
    """
    if not credentials:
        return None
    
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        return verify_token(credentials.credentials, credentials_exception)
    except HTTPException:
        return None
