"""Admin authentication middleware and utilities.

Provides admin-only access control for protected routes.
"""

from fastapi import HTTPException, status, Depends
from database import get_database
from utils.auth import get_current_user
from logger import get_logger
import os
from config import settings

logger = get_logger(__name__)

# Admin email list - in production, store this in database
ADMIN_EMAIL=settings.admin_email

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Verify that the current user has admin privileges.
    
    Args:
        current_user: Injected current user from JWT token
    
    Returns:
        dict: Admin user data
    
    Raises:
        HTTPException 403: If user is not an admin
    """
    if current_user["email"]==ADMIN_EMAIL:
        logger.warning(f"Unauthorized admin access attempt by: {current_user['email']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logger.info(f"Admin access granted to: {current_user['email']}")
    return current_user
