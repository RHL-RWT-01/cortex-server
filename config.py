"""Application configuration management.

This module handles all application settings loaded from environment variables.
Settings are cached for performance using LRU cache.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings can be overridden via .env file or environment variables.
    """
    
    # MongoDB Configuration
    mongodb_url: str  # MongoDB connection string (required)
    database_name: str = "cortex"  # Database name (default: cortex)
    
    # JWT Authentication Configuration
    secret_key: str  # Secret key for JWT signing (required)
    algorithm: str = "HS256"  # JWT algorithm (default: HS256)
    access_token_expire_minutes: int = 43200  # Token expiry: 30 days
    
    # Gemini AI Configuration
    gemini_api_key: str  # Google Gemini API key (required)
    gemini_model: str = "gemini-2.5-flash-lite"  # Default Gemini model
    
    # Server Configuration
    host: str = "0.0.0.0"  # Server host (default: all interfaces)
    port: int = 8000  # Server port (default: 8000)
    
    # Admin Configuration
    admin_email: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Create and cache settings instance.
    
    Uses LRU cache to ensure settings are only loaded once,
    improving performance and consistency across the application.
    
    Returns:
        Settings: Cached settings instance
    """
    return Settings()


# Global settings instance used throughout the application
settings = get_settings()
