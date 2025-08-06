from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import verify_token
from app.services.auth_service import AuthService
from app.schemas import UserRole

# OAuth2 scheme for token authentication
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        dict: Current user data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # Extract email from token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Get user from database
        user = AuthService.get_user_by_email(email)
        if user is None:
            raise credentials_exception
        
        # Check if user is active
        if not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
        
    except Exception as e:
        raise credentials_exception


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current active user
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        dict: Current active user data
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_employer(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Dependency to get current user if they are an employer
    
    Args:
        current_user: Current user from get_current_active_user dependency
        
    Returns:
        dict: Current employer user data
        
    Raises:
        HTTPException: If user is not an employer
    """
    if current_user.get("role") != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Employer role required."
        )
    return current_user


async def get_current_job_seeker(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Dependency to get current user if they are a job seeker
    
    Args:
        current_user: Current user from get_current_active_user dependency
        
    Returns:
        dict: Current job seeker user data
        
    Raises:
        HTTPException: If user is not a job seeker
    """
    if current_user.get("role") != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Job seeker role required."
        )
    return current_user


async def get_current_counselor(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Dependency to get current user if they are a counselor
    
    Args:
        current_user: Current user from get_current_active_user dependency
        
    Returns:
        dict: Current counselor user data
        
    Raises:
        HTTPException: If user is not a counselor
    """
    if current_user.get("role") != UserRole.COUNSELOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Counselor role required."
        )
    return current_user


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Dependency to get current user if they have admin privileges
    (For now, admin is any employer - can be refined later)
    
    Args:
        current_user: Current user from get_current_active_user dependency
        
    Returns:
        dict: Current admin user data
        
    Raises:
        HTTPException: If user doesn't have admin privileges
    """
    if current_user.get("role") not in [UserRole.EMPLOYER, UserRole.COUNSELOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin privileges required."
        )
    return current_user


# Optional dependencies (don't raise exceptions if user is not authenticated)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user (doesn't raise exception if not authenticated)
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        
    Returns:
        dict or None: Current user data if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
        
        email: str = payload.get("sub")
        if email is None:
            return None
        
        user = AuthService.get_user_by_email(email)
        if user is None or not user.get("is_active", False):
            return None
        
        return user
        
    except Exception:
        return None