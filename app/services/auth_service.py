"""
Authentication service for user management and session handling.

This service handles user authentication, registration, and session management
including password hashing, token generation, and user validation.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.schemas import User, UserCreate, UserLogin, UserOut, Token
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory user storage (this would be replaced with actual database in production)
users_store: Dict[str, User] = {}
email_to_user_id: Dict[str, str] = {}


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self):
        """Initialize the authentication service."""
        pass
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Dict containing success status and user information
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        try:
            # Check if email already exists
            if user_data.email in email_to_user_id:
                raise ValueError("Email already registered")
            
            # Generate user ID
            user_id = str(uuid.uuid4())
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user object
            user = User(
                _id=user_id,
                email=user_data.email,
                hashed_password=hashed_password,
                role=user_data.role,
                profile=user_data.profile,
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store user
            users_store[user_id] = user
            email_to_user_id[user_data.email] = user_id
            
            logger.info(f"Successfully registered user {user_id} with email {user_data.email}")
            
            # Create user output (without sensitive data)
            user_out = UserOut(
                _id=user_id,
                email=user.email,
                role=user.role,
                profile=user.profile,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            return {
                "success": True,
                "user": user_out,
                "message": "User registered successfully"
            }
            
        except Exception as e:
            logger.error(f"Error registering user with email {user_data.email}: {str(e)}")
            raise ValueError(f"Registration failed: {str(e)}")
    
    async def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """
        Authenticate a user and return token.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Dict containing authentication token and user info
            
        Raises:
            ValueError: If authentication fails
        """
        try:
            # Check if user exists
            if login_data.email not in email_to_user_id:
                raise ValueError("Invalid email or password")
            
            user_id = email_to_user_id[login_data.email]
            user = users_store[user_id]
            
            # Verify password
            if not verify_password(login_data.password, user.hashed_password):
                raise ValueError("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                raise ValueError("Account is deactivated")
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": user.email, "user_id": user_id, "role": user.role},
                expires_delta=access_token_expires
            )
            
            logger.info(f"Successfully authenticated user {user_id}")
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.access_token_expire_minutes * 60,
                "user": {
                    "id": user_id,
                    "email": user.email,
                    "role": user.role,
                    "name": user.profile.name
                }
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user with email {login_data.email}: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            User object if found, None otherwise
        """
        return users_store.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.
        
        Args:
            email: The user's email address
            
        Returns:
            User object if found, None otherwise
        """
        user_id = email_to_user_id.get(email)
        if user_id:
            return users_store.get(user_id)
        return None
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user's profile information.
        
        Args:
            user_id: The user's unique identifier
            profile_data: Updated profile data
            
        Returns:
            Dict containing success status and updated user info
            
        Raises:
            ValueError: If user not found or update fails
        """
        try:
            if user_id not in users_store:
                raise ValueError("User not found")
            
            user = users_store[user_id]
            
            # Update profile fields
            for field, value in profile_data.items():
                if hasattr(user.profile, field):
                    setattr(user.profile, field, value)
            
            # Update timestamp
            user.updated_at = datetime.utcnow()
            
            # Save changes
            users_store[user_id] = user
            
            logger.info(f"Successfully updated profile for user {user_id}")
            
            # Create user output
            user_out = UserOut(
                _id=user_id,
                email=user.email,
                role=user.role,
                profile=user.profile,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            return {
                "success": True,
                "user": user_out,
                "message": "Profile updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {str(e)}")
            raise ValueError(f"Profile update failed: {str(e)}")
    
    async def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """
        Deactivate a user account.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dict containing success status
            
        Raises:
            ValueError: If user not found
        """
        try:
            if user_id not in users_store:
                raise ValueError("User not found")
            
            user = users_store[user_id]
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            users_store[user_id] = user
            
            logger.info(f"Successfully deactivated user {user_id}")
            
            return {
                "success": True,
                "message": "User account deactivated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {str(e)}")
            raise ValueError(f"Account deactivation failed: {str(e)}")
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change a user's password.
        
        Args:
            user_id: The user's unique identifier
            old_password: Current password
            new_password: New password
            
        Returns:
            Dict containing success status
            
        Raises:
            ValueError: If user not found or old password is incorrect
        """
        try:
            if user_id not in users_store:
                raise ValueError("User not found")
            
            user = users_store[user_id]
            
            # Verify old password
            if not verify_password(old_password, user.hashed_password):
                raise ValueError("Current password is incorrect")
            
            # Hash new password
            new_hashed_password = get_password_hash(new_password)
            
            # Update password
            user.hashed_password = new_hashed_password
            user.updated_at = datetime.utcnow()
            
            users_store[user_id] = user
            
            logger.info(f"Successfully changed password for user {user_id}")
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {str(e)}")
            raise ValueError(f"Password change failed: {str(e)}")
    
    async def verify_user_email(self, user_id: str) -> Dict[str, Any]:
        """
        Mark a user's email as verified.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dict containing success status
            
        Raises:
            ValueError: If user not found
        """
        try:
            if user_id not in users_store:
                raise ValueError("User not found")
            
            user = users_store[user_id]
            user.is_verified = True
            user.updated_at = datetime.utcnow()
            
            users_store[user_id] = user
            
            logger.info(f"Successfully verified email for user {user_id}")
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
            
        except Exception as e:
            logger.error(f"Error verifying email for user {user_id}: {str(e)}")
            raise ValueError(f"Email verification failed: {str(e)}")
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """
        Get overall user statistics.
        
        Returns:
            Dict containing user statistics
        """
        total_users = len(users_store)
        active_users = sum(1 for user in users_store.values() if user.is_active)
        verified_users = sum(1 for user in users_store.values() if user.is_verified)
        student_users = sum(1 for user in users_store.values() if user.role == "student")
        employer_users = sum(1 for user in users_store.values() if user.role == "employer")
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "student_users": student_users,
            "employer_users": employer_users,
            "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
        }
