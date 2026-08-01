import logging
import sys
from .config import settings


def setup_logging() -> logging.Logger:
    """Set up logging configuration based on the application settings."""
    #create logger with sevice name
    logger = logging.getLogger("bet360_user_service")

    #set log level based on debug setting
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logger.setLevel(log_level)

    #remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    #create handler that outputs to terminal (stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    #define the log format and set it for the handler
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
 #create a single instance
logger = setup_logging()
