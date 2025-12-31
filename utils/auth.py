"""Authentication and authorization utilities.

Provides functions for:
- Password hashing and verification (bcrypt)
- JWT token creation and validation
- User authentication from JWT tokens
- Current user dependency injection
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from database import get_database
from bson import ObjectId

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# HTTP Bearer token security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version.
    
    Args:
        plain_password: The password to verify
        hashed_password: The bcrypt hashed password from database
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for a password.
    
    Args:
        password: The plain text password
    
    Returns:
        str: Bcrypt hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token.
    
    Generates a signed JWT token with expiration time.
    
    Args:
        data: Payload data to encode in token (typically {"sub": email})
        expires_delta: Optional custom expiration time
    
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


def decode_access_token(token: str):
    """Decode and validate a JWT token.
    
    Args:
        token: The JWT token string
    
    Returns:
        dict: Decoded token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token.
    
    Dependency function that:
    1. Extracts JWT token from Authorization header
    2. Validates and decodes the token
    3. Fetches user from database
    4. Returns user document for use in endpoints
    
    Args:
        credentials: HTTP Bearer token from request header
    
    Returns:
        dict: User document from MongoDB
    
    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    db = get_database()
    user = await db.users.find_one({"email": email})
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> ObjectId:
    """Extract ObjectId from current user.
    
    Convenience dependency for endpoints that only need the user ID.
    
    Args:
        current_user: Injected current user document
    
    Returns:
        ObjectId: MongoDB ObjectId of the user
    """
    return current_user["_id"]
