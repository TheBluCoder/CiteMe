import pytest
from unittest.mock import AsyncMock, patch
from src.utils.cache import get_cache, set_cache

@pytest.mark.asyncio
async def test_get_cache_miss():
    """Test get_cache when cache miss occurs"""
    # Test with a non-existent key
    result = await get_cache("non_existent_key")
    assert result is None

@pytest.mark.asyncio
async def test_set_get_cache():
    """Test setting and getting cache values"""
    # Test data
    test_key = "test_key"
    test_value = {"data": "test_value"}
    
    # Set the cache value
    await set_cache(test_key, test_value)
    
    # Get the cached value
    result = await get_cache(test_key)
    
    # Verify the result
    assert result is not None
    assert result == test_value
    assert isinstance(result, dict)
    assert result["data"] == "test_value"

@pytest.mark.asyncio
async def test_set_get_cache_with_expiry():
    """Test setting and getting cache values with expiration"""
    test_key = "test_key_expiry"
    test_value = {"data": "test_value"}
    expiry = 60  # 60 seconds
    
    # Set the cache value with expiry
    await set_cache(test_key, test_value, expiry)
    
    # Get the cached value
    result = await get_cache(test_key)
    
    # Verify the result
    assert result is not None
    assert result == test_value

@pytest.mark.asyncio
async def test_set_cache_invalid_value():
    """Test setting cache with invalid value"""
    test_key = "test_key_invalid"
    test_value = None
    
    # Set the cache value
    await set_cache(test_key, test_value)
    
    # Get the cached value
    result = await get_cache(test_key)
    
    # Verify the result
    assert result is None

@pytest.mark.asyncio
async def test_set_get_cache_multiple_values():
    """Test setting and getting multiple cache values"""
    test_data = [
        ("key1", {"data": "value1"}),
        ("key2", {"data": "value2"}),
        ("key3", {"data": "value3"})
    ]
    
    # Set multiple cache values
    for key, value in test_data:
        await set_cache(key, value)
    
    # Get and verify each cached value
    for key, expected_value in test_data:
        result = await get_cache(key)
        assert result == expected_value
