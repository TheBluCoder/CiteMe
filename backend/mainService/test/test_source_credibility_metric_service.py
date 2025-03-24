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

@pytest.mark.asyncio
async def test_calculate_overall_score_success():
    # Test data
    credibility_metrics = [
        {
            "status": "success",
            "data": {"credibility_score": 0.8}
        }
    ]
    sources_with_scores = [
        {
            "rerank_score": 0.9
        }
    ]

    result = await calculate_overall_score(credibility_metrics, sources_with_scores)
    assert isinstance(result, dict)
    assert "overall_score" in result
    assert "source_scores" in result
    assert result["overall_score"] == 86.00  # (0.9 * 0.6 + 0.8 * 0.4) * 100

@pytest.mark.asyncio
async def test_calculate_overall_score_empty():
    result = await calculate_overall_score([], [])
    assert result["overall_score"] == 0.00
    assert result["source_scores"] == []

@pytest.mark.asyncio
async def test_calculate_overall_score_mixed_status():
    credibility_metrics = [
        {"status": "success", "data": {"credibility_score": 0.8}},
        {"status": "failed", "data": {"credibility_score": 0.5}}
    ]
    sources_with_scores = [
        {"rerank_score": 0.9},
        {"rerank_score": 0.7}
    ]

    result = await calculate_overall_score(credibility_metrics, sources_with_scores)
    print(result)
    assert len(result["source_scores"]) == 2
    assert result["source_scores"][0] == 86.00

@pytest.mark.asyncio
async def test_calculate_overall_score_missing_data():
    credibility_metrics = [
        {"status": "success", "data": {}}
    ]
    sources_with_scores = [
        {"rerank_score": 0.9}
    ]

    result = await calculate_overall_score(credibility_metrics, sources_with_scores)
    assert result["overall_score"] == 0.00

@pytest.mark.asyncio
async def test_calculate_overall_score_exception():
    credibility_metrics = [
        {"status": "success", "data": None}
    ]
    sources_with_scores = [
        {"rerank_score": 0.9}
    ]

    result = await calculate_overall_score(credibility_metrics, sources_with_scores)
    assert result["overall_score"] == 0.00 