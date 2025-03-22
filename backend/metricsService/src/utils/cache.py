"""
Cache Management Module

This module provides caching functionality using Redis as the backend.
When Redis is unavailable, it falls back to an in-memory cache with TTL support.
It includes functions for getting, setting, and clearing cache, as well
as a decorator for caching function results.

Key Functions:
- get_cache: Retrieves cached data
- set_cache: Stores data in cache
- clear_cache: Clears all cached data
- cache_decorator: Decorator for caching function results

Caching Strategy:
- Uses Redis as the primary caching backend when available
- Falls back to in-memory cache with TTL support when Redis is unavailable
- Default TTL (Time To Live) of 1 hour
- Automatic serialization/deserialization of data
- Cache key generation based on function arguments

Features:
- Asynchronous operations
- Comprehensive error handling and logging
- Configurable TTL for cached items
- Decorator for easy function caching
"""

import json
import time
from typing import Any, Dict, Optional, Tuple
import hashlib
from src.utils.logging_config import get_logger
from src.utils.cache_config import redis_client

logger = get_logger(__name__)
CACHE_TTL = 3600  # Cache time-to-live in seconds

# In-memory cache to use when Redis is unavailable
# Structure: {key: (value, expiration_timestamp)}
memory_cache: Dict[str, Tuple[Any, float]] = {}

def _generate_cache_key(*args, **kwargs) -> str:
    """Generate a unique cache key based on function arguments"""
    key_str = f"{args}{kwargs}"
    return hashlib.md5(key_str.encode()).hexdigest()

def _clean_expired_cache_entries() -> None:
    """Remove expired entries from the in-memory cache"""
    current_time = time.time()
    expired_keys = [key for key, (_, expiry) in memory_cache.items() if current_time > expiry]
    for key in expired_keys:
        del memory_cache[key]

async def get_cache(key: str) -> Optional[Any]:
    """Get cached value by key"""
    try:
        # Try Redis first if available
        if redis_client:
            cached_data = await redis_client.get(key)
            return json.loads(cached_data) if cached_data else None
        
        # Fall back to in-memory cache when Redis is not available
        _clean_expired_cache_entries()  # Clean expired entries
        if key in memory_cache:
            value, expiry = memory_cache[key]
            if time.time() <= expiry:
                return value
            # Remove expired entry
            del memory_cache[key]
        return None
    except Exception as e:
        logger.error(f"Error getting cache for key {key}: {str(e)}")
        return None

async def set_cache(key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
    """Set cache value with optional TTL"""
    try:
        # Try Redis first if available
        if redis_client:
            serialized_value = json.dumps(value)
            return await redis_client.set(key, serialized_value, ex=ttl)
        
        # Fall back to in-memory cache when Redis is not available
        expiry_time = time.time() + ttl
        memory_cache[key] = (value, expiry_time)
        return True
    except Exception as e:
        logger.error(f"Error setting cache for key {key}: {str(e)}")
        return False

async def clear_cache() -> None:
    """Clear all cached values"""
    try:
        # Clear Redis cache if available
        if redis_client:
            await redis_client.flushdb()
        
        # Clear in-memory cache
        memory_cache.clear()
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")

def cache_decorator(ttl: int = CACHE_TTL):
    """Decorator for caching function results"""
    def wrapper(func):
        async def wrapped(*args, **kwargs):
            cache_key = _generate_cache_key(func.__name__, *args, **kwargs)
            cached_result = await get_cache(cache_key)
            
            if cached_result is not None:
                return cached_result
                
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, ttl)
            return result
        return wrapped
    return wrapper