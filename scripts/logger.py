import logging
import sys
from pathlib import Path

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "pipeline.log"

def get_logger(name: str) -> logging.Logger:
    """
    Creates a standardized logger instance across scripts.
    """
    logger = logging.getLogger(name)
    
    # Check handlers on the instance, not the logging module
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler (logs/pipeline.log)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

if __name__ == '__main__':
    test_log = get_logger("test")
    test_log.info("Logger operational! Writing to console and logs/pipeline.log")