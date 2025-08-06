from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas import UserCreate, UserResponse, UserRole
from app.utils.security import get_password_hash, verify_password, create_access_token

# In-memory database simulation (replace with actual database in later phases)
users_db: Dict[str, Dict[str, Any]] = {}
user_id_counter = 1


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address
        
        Args:
            email (str): User email
            
        Returns:
            dict or None: User data if found, None otherwise
        """
        return users_db.get(email.lower())
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict or None: User data if found, None otherwise
        """
        for user_data in users_db.values():
            if user_data.get("id") == user_id:
                return user_data
        return None
    
    @staticmethod
    def create_user(user_data: UserCreate) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            user_data (UserCreate): User creation data
            
        Returns:
            dict: Created user data
            
        Raises:
            ValueError: If user already exists
        """
        global user_id_counter
        
        email_lower = user_data.email.lower()
        
        # Check if user already exists
        if email_lower in users_db:
            raise ValueError("User with this email already exists")
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user record
        user_record = {
            "id": user_id_counter,
            "email": email_lower,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "phone": None,
            "location": None,
            "bio": None
        }
        
        # Store user
        users_db[email_lower] = user_record
        user_id_counter += 1
        
        # Return user data without password
        return {k: v for k, v in user_record.items() if k != "hashed_password"}
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password
        
        Args:
            email (str): User email
            password (str): Plain text password
            
        Returns:
            dict or None: User data if authentication successful, None otherwise
        """
        user = AuthService.get_user_by_email(email)
        
        if not user:
            return None
        
        if not user.get("is_active"):
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        # Return user data without password
        return {k: v for k, v in user.items() if k != "hashed_password"}
    
    @staticmethod
    def create_user_token(user: Dict[str, Any]) -> str:
        """
        Create access token for user
        
        Args:
            user (dict): User data
            
        Returns:
            str: JWT access token
        """
        token_data = {
            "sub": user["email"],
            "user_id": user["id"],
            "role": user["role"]
        }
        return create_access_token(token_data)
    
    @staticmethod
    def get_all_users() -> list:
        """
        Get all users (for development/testing purposes)
        
        Returns:
            list: List of all users without passwords
        """
        return [
            {k: v for k, v in user.items() if k != "hashed_password"}
            for user in users_db.values()
        ]
    
    @staticmethod
    def update_user_status(email: str, is_active: bool) -> bool:
        """
        Update user active status
        
        Args:
            email (str): User email
            is_active (bool): New active status
            
        Returns:
            bool: True if updated successfully, False if user not found
        """
        user = AuthService.get_user_by_email(email)
        if user:
            users_db[email.lower()]["is_active"] = is_active
            return True
        return False
    
    @staticmethod
    def delete_user(email: str) -> bool:
        """
        Delete user (for development/testing purposes)
        
        Args:
            email (str): User email
            
        Returns:
            bool: True if deleted successfully, False if user not found
        """
        email_lower = email.lower()
        if email_lower in users_db:
            del users_db[email_lower]
            return True
        return False


# Create some default users for testing
def create_default_users():
    """Create default users for testing purposes"""
    try:
        # Create admin/employer user
        admin_user = UserCreate(
            email="admin@jobportal.com",
            full_name="Admin User",
            role=UserRole.EMPLOYER,
            password="admin123"
        )
        AuthService.create_user(admin_user)
        
        # Create job seeker user
        job_seeker = UserCreate(
            email="jobseeker@example.com",
            full_name="John Doe",
            role=UserRole.JOB_SEEKER,
            password="jobseeker123"
        )
        AuthService.create_user(job_seeker)
        
        # Create counselor user
        counselor = UserCreate(
            email="counselor@jobportal.com",
            full_name="Career Counselor",
            role=UserRole.COUNSELOR,
            password="counselor123"
        )
        AuthService.create_user(counselor)
        
        print("✅ Default users created successfully")
        
    except ValueError as e:
        # Users already exist
        print(f"ℹ️ Default users already exist: {e}")


# Initialize default users
create_default_users()