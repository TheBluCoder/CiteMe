import pytest
import time
from unittest.mock import AsyncMock
from src.utils.api_utils import rate_limit, retry_on_failure

@pytest.mark.asyncio
async def test_rate_limit():
    """Test rate limiting functionality"""
    # First call should proceed immediately
    start_time = time.time()
    await rate_limit()
    first_call_duration = time.time() - start_time
    assert first_call_duration < 0.1  # Should be almost instant

    # Second call should be delayed
    start_time = time.time()
    await rate_limit()
    second_call_duration = time.time() - start_time
    assert second_call_duration >= 1.0  # Should be delayed by at least 1 second

@pytest.mark.asyncio
async def test_retry_on_failure_success():
    """Test retry_on_failure decorator with successful operation"""
    mock_func = AsyncMock(return_value="success")
    
    @retry_on_failure(max_retries=3, delay=0.1)
    async def test_func():
        return await mock_func()
    
    result = await test_func()
    
    assert result == "success"
    mock_func.assert_called_once()  # Should succeed on first try

@pytest.mark.asyncio
async def test_retry_on_failure_failure():
    """Test retry_on_failure decorator with failing operation"""
    mock_func = AsyncMock(side_effect=[Exception("Failed"), Exception("Failed"), "success"])
    
    @retry_on_failure(max_retries=3, delay=0.1)
    async def test_func():
        return await mock_func()
    
    result = await test_func()
    
    assert result == "success"
    assert mock_func.call_count == 3  # Should succeed on third try
