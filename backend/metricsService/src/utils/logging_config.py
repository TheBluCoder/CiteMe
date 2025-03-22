"""
Logging Configuration Module

This module handles the configuration of the application's logging system.
It sets up both file and stream handlers with a standardized format for
consistent logging throughout the application.

Key Functions:
- get_logger: Returns a configured logger instance

Configuration:
- Log level: INFO
- Log format: Timestamp - Logger Name - Level - Message
- Handlers: File handler (app.log)

Features:
- Centralized logging configuration
- Easy logger instance creation
- Both file and stream output
- Standardized log format
"""

import logging

file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, stream_handler]
)

def get_logger(name):
    return logging.getLogger(name)
