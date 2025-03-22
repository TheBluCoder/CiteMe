"""
Cache Configuration Module

This module handles the configuration and management of the Redis cache
connection. It provides functions for initializing and closing the Redis
connection, which is used throughout the application for caching.

Key Functions:
- init_redis: Initializes the Redis connection
- close_redis: Closes the Redis connection

Configuration:
- REDIS_URL: Redis server connection URL
- redis_client: Global Redis client instance

Features:
- Asynchronous connection management
- Comprehensive error handling and logging
- Type hints for better code clarity
"""

from typing import Optional
import aioredis
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Redis connection settings
REDIS_URL = "redis://localhost:6379"
redis_client: Optional[aioredis.Redis] = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = await aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {str(e)}")
        raise

async def close_redis():
    """Close Redis connection"""
    if redis_client:
        await redis_client.close()
