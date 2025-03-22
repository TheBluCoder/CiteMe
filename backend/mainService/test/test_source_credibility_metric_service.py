import pytest
from unittest.mock import patch, AsyncMock
from src.services.source_credibility_metric_service import get_credibility_metrics, calculate_overall_score

@pytest.mark.asyncio
async def test_get_credibility_metrics_success():
    # Arrange
    sources = [
        {
            "title": "Test Source",
            "link": "http://test.com",
            "domain": "test.com",
            "journal": "Test Journal",
            "citation_doi": "10.1234/test",
            "citation_references": ["ref1", "ref2"],
            "publication_date": "2024-01-01",
            "author_name": "Test Author",
            "abstract": "Test abstract",
            "issn": "1234-5678",
            "type": "journal"
        }
    ]
    
    mock_response = [
        {
            "status": "success",
            "data": {
                "credibility_score": 0.85,
                "metrics": {
                    "authority": 0.9,
                    "reliability": 0.8
                }
            }
        }
    ]

    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)

        # Act
        result = await get_credibility_metrics(sources)

        # Assert
        assert result == mock_response
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_get_credibility_metrics_api_error():
    # Arrange
    sources = [{"title": "Test Source"}]

    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 500

        # Act
        result = await get_credibility_metrics(sources)

        # Assert
        assert result == []

@pytest.mark.asyncio
async def test_get_credibility_metrics_exception():
    # Arrange
    sources = [{"title": "Test Source"}]

    with patch('aiohttp.ClientSession.post', side_effect=Exception("API Error")):

        # Act
        result = await get_credibility_metrics(sources)

        # Assert
        assert result == []

def test_calculate_overall_score_success():
    # Arrange
    credibility_metrics = [
        {
            "status": "success",
            "data": {
                "credibility_score": 0.85
            }
        },
        {
            "status": "success",
            "data": {
                "credibility_score": 0.75
            }
        }
    ]

    # Act
    result = calculate_overall_score(credibility_metrics)

    # Assert
    assert result == 0.80  # (0.85 + 0.75) / 2

def test_calculate_overall_score_empty():
    # Arrange
    credibility_metrics = []

    # Act
    result = calculate_overall_score(credibility_metrics)

    # Assert
    assert result == 0.0

def test_calculate_overall_score_mixed_status():
    # Arrange
    credibility_metrics = [
        {
            "status": "success",
            "data": {
                "credibility_score": 0.85
            }
        },
        {
            "status": "error",
            "data": {
                "credibility_score": 0.75
            }
        }
    ]

    # Act
    result = calculate_overall_score(credibility_metrics)

    # Assert
    assert result == 0.85  # Only considers successful responses

def test_calculate_overall_score_missing_data():
    # Arrange
    credibility_metrics = [
        {
            "status": "success"
        }
    ]

    # Act
    result = calculate_overall_score(credibility_metrics)

    # Assert
    assert result == 0.0

def test_calculate_overall_score_exception():
    # Arrange
    credibility_metrics = [
        {
            "status": "success",
            "data": {
                "credibility_score": "invalid"  # Invalid score type
            }
        }
    ]

    # Act
    result = calculate_overall_score(credibility_metrics)

    # Assert
    assert result == 0.0 