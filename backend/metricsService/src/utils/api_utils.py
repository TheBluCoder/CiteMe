"""
API Utilities Module

This module provides utility functions for handling API interactions,
including rate limiting and retry mechanisms. These utilities help
ensure reliable and efficient API communication throughout the application.

Key Functions:
- rate_limit: Ensures API calls don't exceed rate limits
- retry_on_failure: Decorator for retrying failed API calls

Features:
- Global rate limiting across all API calls
- Configurable retry mechanism with exponential backoff
- Asynchronous implementation for non-blocking operations
- Comprehensive logging for debugging and monitoring
"""

import asyncio
import time
import functools
from src.utils.logging_config import get_logger
from typing import Callable, Any

logger = get_logger(__name__)

# Rate limiting parameters
API_RATE_LIMIT = 1  # Minimum seconds between API calls
last_api_call_time = 0

async def rate_limit():
    """Ensure we don't exceed API rate limits."""
    global last_api_call_time
    current_time = time.time()
    time_since_last_call = current_time - last_api_call_time
    if time_since_last_call < API_RATE_LIMIT:
        await asyncio.sleep(API_RATE_LIMIT - time_since_last_call)
    last_api_call_time = time.time()

def retry_on_failure(max_retries: int = 3, delay: float = 1):
    """Decorator to retry a function on failure."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
