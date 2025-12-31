"""Authentication routes for user signup and login.

Provides endpoints for:
- User registration (signup)
- User login with JWT token generation
- Getting current user information
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from database import get_database
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from config import settings
from logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """Register a new user and return access token.
    
    Creates a new user account with hashed password and generates a JWT token.
    
    Args:
        user: User registration data (email, password, full_name, selected_role)
    
    Returns:
        Token: JWT access token and token type
    
    Raises:
        HTTPException 400: If email is already registered
    """
    db = get_database()
    
    logger.info(f"Signup attempt for email: {user.email}")
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        logger.warning(f"Signup failed - email already registered: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "full_name": user.full_name,
        "selected_role": user.selected_role,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    result = await db.users.insert_one(user_data)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """Authenticate user and return JWT token.
    
    Verifies credentials and generates a new JWT token.
    Updates user's last login timestamp.
    
    Args:
        user_login: Login credentials (email, password)
    
    Returns:
        Token: JWT access token and token type
    
    Raises:
        HTTPException 401: If credentials are incorrect
    """
    db = get_database()
    
    # Find user
    user = await db.users.find_one({"email": user_login.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information.
    
    Returns the profile information of the currently logged-in user.
    
    Args:
        current_user: Injected current user from JWT token
    
    Returns:
        UserResponse: User profile information
    """
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "selected_role": current_user.get("selected_role"),
        "created_at": current_user["created_at"],
        "last_login": current_user.get("last_login")
    }
