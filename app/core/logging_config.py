import logging
import sys
from app.config import settings

def setup_logging():
    # Configure root logger
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Optional: silence noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger("app")
    logger.info("Logging setup complete")
    return logger

logger = logging.getLogger("app")
