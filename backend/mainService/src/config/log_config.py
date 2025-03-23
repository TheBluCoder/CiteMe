import os
import logging
from datetime import datetime
from typing import Optional
from logging import Logger


def setup_logging(
        log_level=logging.INFO,
        log_dir: str = 'logs',
        filename: Optional[str] = 'log') -> Logger:
    """
    Set up a standardized logging configuration for the entire project.

    Args:
        log_level (int): Logging level (default: logging.INFO)
        log_dir (str): Directory to store log files (default: 'logs')
    """
    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create a unique log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%U")
    log_filename = os.path.join(log_dir, f'{filename}_{timestamp}.log')

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),  # Log to file
            logging.StreamHandler()  # Also log to console
        ]
    )
    return logging.getLogger(filename)
