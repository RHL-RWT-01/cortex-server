"""Logging configuration for the application.

Provides structured logging with:
- Console output with color-coded levels
- File output for persistent logs
- Request/response tracing
- Database operation tracking
- Custom CRON level for cron job tracking
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Define custom CRON log level (between INFO=20 and WARNING=30)
CRON_LEVEL = 25
logging.addLevelName(CRON_LEVEL, "CRON")


def cron(self, message, *args, **kwargs):
    """Log a message with CRON level."""
    if self.isEnabledFor(CRON_LEVEL):
        self._log(CRON_LEVEL, message, *args, **kwargs)


# Add cron method to Logger class
logging.Logger.cron = cron

# Define log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create formatter
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

# Console handler - always output to terminal
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Show all levels in terminal
console_handler.setFormatter(formatter)

# File handler for all logs
file_handler = logging.FileHandler(
    log_dir / f"cortex_{datetime.now().strftime('%Y%m%d')}.log"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Error file handler
error_handler = logging.FileHandler(
    log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Cron file handler - dedicated log file for cron jobs
cron_handler = logging.FileHandler(
    log_dir / f"cron_{datetime.now().strftime('%Y%m%d')}.log"
)
cron_handler.setLevel(CRON_LEVEL)
cron_handler.setFormatter(formatter)
# Only log CRON level messages to this file
cron_handler.addFilter(lambda record: record.levelno == CRON_LEVEL)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__ of the module)
    
    Returns:
        logging.Logger: Configured logger instance with cron() method
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(cron_handler)
    
    return logger

