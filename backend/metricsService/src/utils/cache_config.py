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
import os
from redis import asyncio as aioredis
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Redis connection settings from environment variables
redis_client: Optional[aioredis.Redis] = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = aioredis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {str(e)}")
        raise

async def close_redis():
    """Close Redis connection"""
    if redis_client:
        await redis_client.close()
