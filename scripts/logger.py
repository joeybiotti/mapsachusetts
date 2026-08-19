import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Creates a standardized logger instance across scripts.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if imported repeatedly
    if not logging.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Stream to standard output
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return handler