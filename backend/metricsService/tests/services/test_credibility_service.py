import pytest
from unittest.mock import AsyncMock, patch
from src.services.credibility_service import (
    calculate_credibility,
    get_credibility_level,
    get_domain_reputation,
    get_citation_data,
    get_journal_impact,
    calculate_recency_score,
    get_authorship_reputation
)
from src.models.schemas import CredibilityRequest

@pytest.mark.asyncio
async def test_calculate_credibility_basic():
    """Test basic credibility calculation"""
    with patch('src.services.credibility_service.get_domain_reputation', new_callable=AsyncMock) as mock_domain, \
         patch('src.services.credibility_service.get_citation_data', new_callable=AsyncMock) as mock_citation, \
         patch('src.services.credibility_service.get_journal_impact', new_callable=AsyncMock) as mock_journal, \
         patch('src.services.credibility_service.calculate_recency_score', new_callable=AsyncMock) as mock_recency, \
         patch('src.services.credibility_service.get_authorship_reputation', new_callable=AsyncMock) as mock_author:
        
        mock_domain.return_value = 80.0
        mock_citation.return_value = 70.0
        mock_journal.return_value = 90.0
        mock_recency.return_value = 50.0
        mock_author.return_value = 80.0
        
        request = CredibilityRequest(
            domain="example.com",
            citation_doi="10.1234/example",
            journal="Example Journal",
            publication_date="2023-01-01",
            author_id="0000-0001-2345-6789"
        )
        
        result = await calculate_credibility(request)
        
        assert result["authorship_reputation"]== 80.0  

@pytest.mark.parametrize("score,expected_level", [
    (95, "Very High"),
    (80, "High"),
    (65, "Moderate"),
    (50, "Low"),
    (30, "Very Low"),
    (100, "Very High"),
    (0, "Very Low")
])
def test_get_credibility_level(score, expected_level):
    """Test credibility level mapping"""
    assert get_credibility_level(score) == expected_level

@pytest.mark.asyncio
async def test_get_domain_reputation():
    """Test domain reputation calculation"""
    with patch('src.services.domain_reputation.requests.get') as mock_get, \
         patch('src.services.domain_reputation.rate_limit', new_callable=AsyncMock):
        
        # Mock Tranco API response
        mock_get.return_value.json.return_value = {"example.com": 500}
        
        # Mock Observatory API responses
        mock_get.side_effect = [
            # First call - start scan
            type('MockResponse', (), {'status_code': 200, 'json': lambda: {"scan_id": "123"}}),
            # Second call - get results
            type('MockResponse', (), {'status_code': 200, 'json': lambda: {"state": "FINISHED", "grade": "A"}})
        ]
        
        score = await get_domain_reputation("example.com")
        assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_get_domain_reputation_invalid_domain():
    """Test domain reputation with invalid domain"""
    with patch('src.services.domain_reputation.requests.get') as mock_get, \
         patch('src.services.domain_reputation.rate_limit', new_callable=AsyncMock):
        
        # Mock Tranco API response
        mock_get.return_value.json.return_value = {}
        
        score = await get_domain_reputation("invalid-domain")
        assert score == 0

@pytest.mark.asyncio
async def test_get_domain_reputation_api_error():
    """Test domain reputation when APIs fail"""
    with patch('src.services.domain_reputation.requests.get') as mock_get, \
        patch('src.services.domain_reputation.rate_limit', new_callable=AsyncMock),\
        patch('src.services.domain_reputation.tranco_data') :
        
        # Mock API failure
        mock_get.side_effect = Exception("API error")
        
        with pytest.raises(Exception, match="API error"):
            await get_domain_reputation("example.com")





@pytest.mark.asyncio
async def test_get_citation_data():
    """Test citation data retrieval"""
    with patch('src.services.citation_data.requests.get') as mock_get, \
         patch('src.services.citation_data.rate_limit', new_callable=AsyncMock):
        
        # Mock Crossref API response
        mock_get.return_value.json.return_value = {"message": {"is-referenced-by-count": 10}}
        
        score = await get_citation_data("10.1234/example")
        assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_get_citation_data_no_doi():
    """Test citation data with no DOI"""
    score = await get_citation_data(None)
    assert score == 0

@pytest.mark.asyncio
async def test_get_citation_data_api_error():
    """Test citation data when APIs fail"""
    with patch('src.services.citation_data.requests.get') as mock_get, \
         patch('src.services.citation_data.rate_limit', new_callable=AsyncMock):
        
        # Mock API failure
        mock_get.side_effect = Exception("API error")
        
        score = await get_citation_data("10.1234/example")
        assert score == 0

@pytest.mark.asyncio
async def test_get_journal_impact_with_issn():
    """Test journal impact calculation with ISSN"""
    with patch('src.services.journal_impact.requests.get') as mock_get, \
        patch('src.services.journal_impact.get_by_issn') as mock_issn, \
        patch('src.services.journal_impact.parse_item') as mock_parse, \
        patch('src.services.journal_impact.rate_limit', new_callable=AsyncMock) as mock_rate_limit:
            
        # Mock DOAJ API response
        mock_rate_limit.return_value = None

        mock_get.return_value.json.return_value = {"total": 1, "results": [{"bibjson": {"title": "Example Journal"}}]}
        mock_issn.return_value = """{
            'data': {
                'Country': 'Switzerland',
                'CountryCode': 'sz',
                'KeyTitle': 'Frontiers in public health',
                'ISSN': {'status': 'Valid', 'value': '2296-2565'},
                'Organization': '40',
                'Record': {'modified': '20210207002300.0', 'status': 'Register'},
                'errors': [],
                'issn': '2296-2565', } 
                'resource': {'URL': 'https://www.frontiersin.org/journals/public-health#articles'},
                }
            }
            """
        mock_parse.return_value = {
            'data': {
                'Country': 'Switzerland',
                'CountryCode': 'sz',
                'ISSN': {'status': 'Valid', 'value': '2296-2565'},
                'KeyTitle': 'Frontiers in public health',
                'Organization': '40',
                'Record': {'modified': '20210207002300.0', 'status': 'Register'},
                'errors': [],
                'issn': '2296-2565', } ,
                'resource': {'URL': 'https://www.frontiersin.org/journals/public-health#articles'},
                }
        score = await get_journal_impact(issn="1234-5678")
        assert 0 <= score <= 100
        assert mock_rate_limit.called

@pytest.mark.asyncio
async def test_get_journal_impact_with_journal_name():
    """Test journal impact calculation with journal name"""
    with patch('src.services.journal_impact.requests.get') as mock_get, \
         patch('src.services.journal_impact.rate_limit', new_callable=AsyncMock):
        
        # Mock DOAJ API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"total": 1, "results": [{"bibjson": {"title": "Example Journal"}}]}
        score = await get_journal_impact(journal="Example Journal")
        assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_get_journal_impact_with_both():
    """Test journal impact calculation with both ISSN and journal name"""
    with patch('src.services.journal_impact.requests.get') as mock_get, \
        patch('src.services.journal_impact.get_by_issn') as mock_issn, \
        patch('src.services.journal_impact.parse_item') as mock_parse, \
        patch('src.services.journal_impact.rate_limit', new_callable=AsyncMock) as mock_rate_limit:
            
        # Mock DOAJ API response
        mock_rate_limit.return_value = None

        mock_get.return_value.json.return_value = {"total": 1, "results": [{"bibjson": {"title": "Example Journal"}}]}
        mock_issn.return_value = """{
            'data': {
                'Country': 'Switzerland',
                'CountryCode': 'sz',
                'KeyTitle': 'Frontiers in public health',
                'ISSN': {'status': 'Valid', 'value': '2296-2565'},
                'Organization': '40',
                'Record': {'modified': '20210207002300.0', 'status': 'Register'},
                'errors': [],
                'issn': '2296-2565', } 
                'resource': {'URL': 'https://www.frontiersin.org/journals/public-health#articles'},
                }
            """
        mock_parse.return_value = {
            'data': {
                'Country': 'Switzerland',
                'CountryCode': 'sz',
                'ISSN': {'status': 'Valid', 'value': '2296-2565'},
                'KeyTitle': 'Frontiers in public health',
                'Organization': '40',
                'Record': {'modified': '20210207002300.0', 'status': 'Register'},
                'errors': [],
                'issn': '2296-2565', } ,
                'resource': {'URL': 'https://www.frontiersin.org/journals/public-health#articles'},
                }
        score = await get_journal_impact(issn="1234-5678", journal="Example Journal")
        assert 0 <= score <= 100
        assert mock_rate_limit.called

@pytest.mark.asyncio
async def test_get_journal_impact_no_issn_or_journal():
    """Test journal impact with no ISSN or journal name"""
    score = await get_journal_impact()
    assert score == 0

@pytest.mark.asyncio
async def test_get_journal_impact_invalid_journal_name():
    """Test journal impact with invalid journal name"""
    with patch('src.services.journal_impact.requests.get') as mock_get, \
         patch('src.services.journal_impact.rate_limit', new_callable=AsyncMock):
        
        # Mock DOAJ API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"total": 0}
        
        score = await get_journal_impact(journal="Invalid Journal")
        assert score == 0

# @pytest.mark.skip(reason="DOAJ API is not working")
@pytest.mark.asyncio
async def test_get_journal_impact_api_error():
    """Test journal impact when APIs fail"""
    with patch('src.services.journal_impact.requests.get') as mock_get, \
         patch('src.services.journal_impact.rate_limit', new_callable=AsyncMock) as mock_issn,\
         patch('src.services.journal_impact.get_by_issn', new_callable=AsyncMock):
        
        # Mock API failure
        mock_get.side_effect = Exception("API error")
        mock_issn.side_effect = Exception("API error")
        
        with pytest.raises(Exception ):
            await get_journal_impact("example.com")
        


@pytest.mark.asyncio
async def test_calculate_recency_score():
    """Test recency score calculation"""
    # Test various date formats
    assert await calculate_recency_score("2023-01-01") > 0
    assert await calculate_recency_score(2023) > 0
    assert await calculate_recency_score("January 2023") > 0

@pytest.mark.asyncio
async def test_calculate_recency_score_invalid_date():
    """Test recency score with invalid date"""
    assert await calculate_recency_score("invalid-date") == 0

@pytest.mark.asyncio
async def test_calculate_recency_score_future_date():
    """Test recency score with future date"""
    assert await calculate_recency_score("2030-01-01") == 0

@pytest.mark.asyncio
async def test_get_authorship_reputation():
    """Test author reputation calculation"""
    with patch('src.services.author_reputation.requests.get') as mock_get, \
         patch('src.services.author_reputation.rate_limit', new_callable=AsyncMock):
        
        # Mock ORCID API response
        mock_get.return_value.json.return_value = {"group": [{}]}
        
        score = await get_authorship_reputation(author_id="0000-0001-2345-6789")
        assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_get_authorship_reputation_no_author():
    """Test author reputation with no author info"""
    score = await get_authorship_reputation()
    assert score == 0

@pytest.mark.asyncio
async def test_get_authorship_reputation_api_error():
    """Test author reputation when APIs fail"""
    with patch('src.services.author_reputation.requests.get') as mock_get, \
         patch('src.services.author_reputation.rate_limit', new_callable=AsyncMock):
        
        # Mock API failure
        mock_get.side_effect = Exception("API error")
        
        score = await get_authorship_reputation(author_id="0000-0001-2345-6789")
        assert score >= 20  # Minimum score for having author info
