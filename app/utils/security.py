from datetime import datetime, timedelta
from typing import Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password (str): Plain text password
        hashed_password (str): Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (timedelta, optional): Custom expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return encoded_jwt


def verify_token(token: str) -> Union[dict, None]:
    """
    Verify and decode a JWT token
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        dict or None: Decoded token data if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token (for future use)
    
    Args:
        email (str): User email
        
    Returns:
        str: Password reset token
    """
    data = {"sub": email, "type": "password_reset"}
    expires_delta = timedelta(hours=1)  # Reset tokens expire in 1 hour
    return create_access_token(data, expires_delta)


def verify_password_reset_token(token: str) -> Union[str, None]:
    """
    Verify a password reset token and return email
    
    Args:
        token (str): Password reset token
        
    Returns:
        str or None: Email if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "password_reset":
        return payload.get("sub")
    return None