from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any

from app.schemas import UserCreate, UserResponse, Token, APIResponse, UserRole
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user, get_current_active_user, get_admin_user

router = APIRouter()


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    
    Args:
        user_data (UserCreate): User registration data
        
    Returns:
        APIResponse: Success response with user data
        
    Raises:
        HTTPException: If user already exists or registration fails
    """
    try:
        # Create the user
        user = AuthService.create_user(user_data)
        
        return APIResponse(
            success=True,
            message="User registered successfully",
            data={
                "user": user,
                "next_step": "Please login with your credentials"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login endpoint
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login form data with username and password
        
    Returns:
        Token: Access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = AuthService.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = AuthService.create_user_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=APIResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    User login endpoint (alternative to /token with more detailed response)
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login form data
        
    Returns:
        APIResponse: Success response with token and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = AuthService.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = AuthService.create_user_token(user)
    
    return APIResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        }
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user data
    """
    return current_user


@router.get("/verify-token", response_model=APIResponse)
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verify if the current token is valid
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        APIResponse: Token verification result
    """
    return APIResponse(
        success=True,
        message="Token is valid",
        data={
            "user": {
                "id": current_user["id"],
                "email": current_user["email"],
                "full_name": current_user["full_name"],
                "role": current_user["role"],
                "is_active": current_user["is_active"]
            }
        }
    )


@router.post("/logout", response_model=APIResponse)
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user (token invalidation would be handled client-side or with token blacklisting)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        APIResponse: Logout confirmation
    """
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data={
            "message": "Please remove the token from client storage"
        }
    )


# Admin endpoints for user management
@router.get("/users", response_model=APIResponse)
async def list_all_users(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """
    List all users (admin only)
    
    Args:
        admin_user: Current admin user
        
    Returns:
        APIResponse: List of all users
    """
    users = AuthService.get_all_users()
    
    return APIResponse(
        success=True,
        message=f"Retrieved {len(users)} users",
        data={
            "users": users,
            "total_count": len(users)
        }
    )


@router.put("/users/{user_email}/status", response_model=APIResponse)
async def update_user_status(
    user_email: str,
    is_active: bool,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Update user active status (admin only)
    
    Args:
        user_email (str): Email of user to update
        is_active (bool): New active status
        admin_user: Current admin user
        
    Returns:
        APIResponse: Update confirmation
        
    Raises:
        HTTPException: If user not found
    """
    success = AuthService.update_user_status(user_email, is_active)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    action = "activated" if is_active else "deactivated"
    return APIResponse(
        success=True,
        message=f"User {user_email} has been {action}",
        data={
            "user_email": user_email,
            "is_active": is_active
        }
    )


# Development/Testing endpoints
@router.delete("/users/{user_email}", response_model=APIResponse)
async def delete_user(
    user_email: str,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """
    Delete a user (admin only, for development/testing)
    
    Args:
        user_email (str): Email of user to delete
        admin_user: Current admin user
        
    Returns:
        APIResponse: Deletion confirmation
        
    Raises:
        HTTPException: If user not found
    """
    success = AuthService.delete_user(user_email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return APIResponse(
        success=True,
        message=f"User {user_email} has been deleted",
        data={
            "deleted_user_email": user_email
        }
    )