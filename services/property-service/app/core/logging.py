import logging
import sys
from .config import settings

def setup_logging() -> logging.Logger:
    """Configure and return a logger instance."""

    # create logger with service name 
    logger = logging.getLogger("bet360.property_service")

    # Set log level based on debug setting
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logger.setLevel(log_level)

    # Remove existing handlers to avoid deplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handler that outputs to terminal
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Define the log message format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# Create a single instance
logger = setup_logging()