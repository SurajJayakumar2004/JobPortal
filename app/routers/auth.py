"""
Authentication router for user registration and login.

This module handles all authentication-related endpoints including
user registration, login, token refresh, and logout functionality.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import uuid
import json
import os
from datetime import datetime

from app.schemas import (
    UserCreate, UserLogin, UserOut, User, Token, UserProfile,
    EmployerRegistration, StudentRegistration, UserRole,
    SuccessResponse, ErrorResponse
)
from app.utils.security import (
    verify_password, get_password_hash, create_token_response
)
from app.utils.dependencies import get_current_active_user, TokenData

router = APIRouter()

# Persistent storage files
USERS_DB_FILE = "users_db.json"
USERS_BY_EMAIL_FILE = "users_by_email.json"

def load_users_db():
    """Load users database from file."""
    try:
        if os.path.exists(USERS_DB_FILE):
            with open(USERS_DB_FILE, 'r') as f:
                data = json.load(f)
                # Convert dict data back to User objects
                users_db = {}
                for user_id, user_data in data.items():
                    # Convert datetime strings back to datetime objects
                    if 'created_at' in user_data:
                        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    if 'updated_at' in user_data:
                        user_data['updated_at'] = datetime.fromisoformat(user_data['updated_at'])
                    
                    # Convert profile dict to UserProfile object if it exists
                    if 'profile' in user_data and user_data['profile']:
                        user_data['profile'] = UserProfile(**user_data['profile'])
                    
                    users_db[user_id] = User(**user_data)
                return users_db
        return {}
    except Exception as e:
        print(f"Error loading users database: {e}")
        return {}

def save_users_db(users_db):
    """Save users database to file."""
    try:
        # Convert User objects to dict for JSON serialization
        data = {}
        for user_id, user in users_db.items():
            user_dict = user.dict()
            # Convert datetime objects to strings
            if 'created_at' in user_dict:
                user_dict['created_at'] = user_dict['created_at'].isoformat()
            if 'updated_at' in user_dict:
                user_dict['updated_at'] = user_dict['updated_at'].isoformat()
            
            # Ensure _id field is present for loading
            if 'id' in user_dict and '_id' not in user_dict:
                user_dict['_id'] = user_dict['id']
            
            data[user_id] = user_dict
        
        with open(USERS_DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving users database: {e}")

def load_users_by_email():
    """Load email to user_id mapping from file."""
    try:
        if os.path.exists(USERS_BY_EMAIL_FILE):
            with open(USERS_BY_EMAIL_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading users by email: {e}")
        return {}

def save_users_by_email(users_by_email):
    """Save email to user_id mapping to file."""
    try:
        with open(USERS_BY_EMAIL_FILE, 'w') as f:
            json.dump(users_by_email, f, indent=2)
    except Exception as e:
        print(f"Error saving users by email: {e}")

# Load persistent user storage
users_db: Dict[str, User] = load_users_db()
users_by_email: Dict[str, str] = load_users_by_email()  # email -> user_id mapping


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    
    This endpoint allows new users (students or employers) to create an account
    by providing their email, password, role, and profile information.
    
    Args:
        user_data: User registration data including email, password, role, and profile
        
    Returns:
        Dict containing success message and user information
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if user already exists
    if user_data.email in users_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate user ID and hash password
    user_id = str(uuid.uuid4())
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
    
    # Store user in persistent storage
    users_db[user_id] = user
    users_by_email[user_data.email] = user_id
    
    # Save to files
    save_users_db(users_db)
    save_users_by_email(users_by_email)
    
    # Create response without sensitive data
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
        "message": "User registered successfully",
        "data": {
            "user": user_out.dict(),
            "next_steps": [
                "Verify your email address",
                "Complete your profile",
                "Upload your resume" if user_data.role == "student" else "Set up your company profile"
            ]
        }
    }


@router.post("/register/employer", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_employer(employer_data: EmployerRegistration):
    """
    Register a new employer account with organization details.
    
    This endpoint allows employers to create an account with their organization
    information including full name, organization name, organization email, and phone.
    
    Args:
        employer_data: Employer registration data
        
    Returns:
        Dict containing success message and user information
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if user already exists by organization email
    if employer_data.organization_email in users_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization email already registered"
        )
    
    # Generate user ID and hash password
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(employer_data.password)
    
    # Create user profile with employer-specific data
    profile = UserProfile(
        name=employer_data.full_name,
        phone=employer_data.phone_number,
        organization_name=employer_data.organization_name,
        organization_email=employer_data.organization_email
    )
    
    # Create user object
    user = User(
        _id=user_id,
        email=employer_data.organization_email,
        hashed_password=hashed_password,
        role=UserRole.EMPLOYER,
        profile=profile,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Store user in persistent storage
    users_db[user_id] = user
    users_by_email[employer_data.organization_email] = user_id
    
    # Save to files
    save_users_db(users_db)
    save_users_by_email(users_by_email)
    
    # Create response without sensitive data
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
        "message": "Employer account registered successfully",
        "data": {
            "user": user_out.dict(),
            "next_steps": [
                "Verify your organization email address",
                "Complete your company profile",
                "Start posting job opportunities"
            ]
        }
    }


@router.post("/register/student", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_student(student_data: StudentRegistration):
    """
    Register a new student account.
    
    This endpoint allows students to create an account with their personal
    information including full name, email, and phone number.
    
    Args:
        student_data: Student registration data
        
    Returns:
        Dict containing success message and user information
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if user already exists
    if student_data.email in users_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate user ID and hash password
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(student_data.password)
    
    # Create user profile
    profile = UserProfile(
        name=student_data.full_name,
        phone=student_data.phone_number
    )
    
    # Create user object
    user = User(
        _id=user_id,
        email=student_data.email,
        hashed_password=hashed_password,
        role=UserRole.STUDENT,
        profile=profile,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Store user in persistent storage
    users_db[user_id] = user
    users_by_email[student_data.email] = user_id
    
    # Save to files
    save_users_db(users_db)
    save_users_by_email(users_by_email)
    
    # Create response without sensitive data
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
        "message": "Student account registered successfully",
        "data": {
            "user": user_out.dict(),
            "next_steps": [
                "Verify your email address",
                "Complete your profile",
                "Upload your resume"
            ]
        }
    }


@router.post("/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """
    Authenticate user and return access token.
    
    This endpoint authenticates users with their email and password,
    returning a JWT access token for subsequent API calls.
    
    Args:
        login_data: User login credentials (email and password)
        
    Returns:
        Dict containing access token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Check if user exists
    if login_data.email not in users_by_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user_id = users_by_email[login_data.email]
    
    # Check if user exists in users_db (handle data consistency)
    if user_id not in users_db:
        # Remove from users_by_email to fix inconsistency
        del users_by_email[login_data.email]
        save_users_by_email(users_by_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found. Please register again."
        )
    
    user = users_db[user_id]
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create token response
    token_response = create_token_response(user_id, user.email, user.role)
    
    return {
        "success": True,
        "message": "Login successful",
        "data": token_response
    }


@router.post("/logout", response_model=SuccessResponse)
async def logout_user(current_user: TokenData = Depends(get_current_active_user)):
    """
    Logout the current user.
    
    In a stateless JWT implementation, logout is typically handled client-side
    by removing the token. This endpoint can be used for logging purposes
    or token blacklisting in more advanced implementations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success response confirming logout
    """
    # In a production app, you might:
    # 1. Add token to blacklist
    # 2. Log the logout event
    # 3. Clear any server-side sessions
    
    return SuccessResponse(
        message=f"User {current_user.email} logged out successfully"
    )


@router.post("/refresh-token", response_model=Dict[str, Any])
async def refresh_token(current_user: TokenData = Depends(get_current_active_user)):
    """
    Refresh the access token for the current user.
    
    This endpoint allows users to get a new access token using their
    current valid token, extending their session.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict containing new access token
    """
    # Create new token response
    token_response = create_token_response(
        current_user.user_id, 
        current_user.email, 
        current_user.role
    )
    
    return {
        "success": True,
        "message": "Token refreshed successfully",
        "data": token_response
    }


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: TokenData = Depends(get_current_active_user)):
    """
    Get information about the currently authenticated user.
    
    This endpoint returns the current user's profile information
    and account details.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If user not found
    """
    # Get user from database
    if current_user.user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = users_db[current_user.user_id]
    
    # Create response without sensitive data
    user_out = UserOut(
        _id=current_user.user_id,
        email=user.email,
        role=user.role,
        profile=user.profile,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return {
        "success": True,
        "message": "User information retrieved successfully",
        "data": {"user": user_out.dict()}
    }
