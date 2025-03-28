"""
Logging Configuration Module

This module handles the configuration of the application's logging system.
It sets up both file(optional) and stream handlers with a standardized format for
consistent logging throughout the application.

Key Functions:
- get_logger: Returns a configured logger instance

Configuration:
- Log level: INFO
- Log format: Timestamp - Logger Name - Level - Message
- Handlers: File handler

Features:
- Centralized logging configuration
- Easy logger instance creation
- Both file and stream output
- Standardized log format
"""

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
        filename (str): Base filename for log files (default: 'log')
        logToFile (bool): Whether to log to file (default: False)
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

