"""Rate limiting configuration using slowapi.

Provides a limiter instance and a custom key function to rate limit
based on user ID for authenticated users and IP for unauthorized users.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from jose import jwt, JWTError
from config import settings

def get_user_or_ip_key(request: Request) -> str:
    """Generate a unique key for rate limiting.
    
    Uses sub (email) from JWT if available, otherwise falls back to client IP.
    This avoids database lookups for every request just to get the rate limit key.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        str: Unique identifier for the client (user email or IP address)
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except (JWTError, IndexError):
            # If token is invalid, fall back to IP
            pass
            
    return f"ip:{get_remote_address(request)}"

# Initialize Limiter with our custom key function
# By default, we use memory storage. For production with multiple workers/instances,
# this should be changed to use Redis.
limiter = Limiter(key_func=get_user_or_ip_key)
