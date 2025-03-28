import os
import logging
from datetime import datetime
from typing import Optional
from logging import Logger


def setup_logging(
        log_level=logging.INFO,
        log_dir: str = 'logs',
        filename: Optional[str] = 'log',
        logToFile: Optional[bool] = False,
        ) -> Logger:
        
    """
    Set up a standardized logging configuration for the entire project.

    Args:
        log_level (int): Logging level (default: logging.INFO)
        log_dir (str): Directory to store log files (default: 'logs')
    """
    # Create a unique log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%U")

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Also log to console
        ]
    )
    logger = logging.getLogger(filename)

    if logToFile:
        # Ensure logs directory exists
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, f'{filename}_{timestamp}.log')
        logger.addHandler(logging.FileHandler(log_filename))
        
    
    return logger
