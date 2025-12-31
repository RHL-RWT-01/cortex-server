"""Singleton AI client for Google Gemini.

This module provides a single, reusable AI client instance following the singleton pattern.
The client is configured once from environment variables and reused throughout the application.
"""

import google.generativeai as genai
from config import settings
from logger import get_logger

logger = get_logger(__name__)


class GeminiAI:
    """Singleton class for Google Gemini AI client.
    
    Ensures only one AI client instance is created and reused across the application.
    Uses configuration from environment variables via settings.
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super(GeminiAI, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Gemini AI client (called once)."""
        if self._model is None:
            logger.info(f"Initializing Gemini AI with model: {settings.gemini_model}")
            
            # Validate API key
            if not settings.gemini_api_key:
                logger.error("GEMINI_API_KEY is not set in environment variables")
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            
            # Configure Gemini
            genai.configure(api_key=settings.gemini_api_key)
            
            # Create model instance
            self._model = genai.GenerativeModel(settings.gemini_model)
            
            logger.info("Gemini AI client initialized successfully")
    
    @property
    def model(self):
        """Get the Gemini model instance.
        
        Returns:
            GenerativeModel: Configured Gemini model
        """
        return self._model
    
    def generate_content(self, contents):
        """Generate content using the Gemini model.
        
        Args:
            contents: Text prompt or list of contents (text, images) for generation
            
        Returns:
            Response from Gemini model
        """
        return self._model.generate_content(contents)


# Singleton instance - import and use this everywhere
gemini_ai = GeminiAI()

# Export for easy access
__all__ = ['gemini_ai']
