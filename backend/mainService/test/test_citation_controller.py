import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.models.schema import CitationInput

def test_get_citation_auto(test_client, mock_pinecone, mock_summarize_llm, mock_citation_llm, mock_scraper):
    # Mock the app state
    test_client.app.state.pc = mock_pinecone
    test_client.app.state.summarize_llm = mock_summarize_llm
    test_client.app.state.citation_llm = mock_citation_llm
    test_client.app.state.async_content_scraper = mock_scraper

    # Test data
    test_payload = {
        "title": "Test Title",
        "content": "Test content",
        "citationStyle": "APA",
        "formType": "auto"
    }

    # Mock the service response
    mock_response = {
        "citations": ["Test Citation"],
        "metadata": {"source": "test"}
    }

    with patch('src.services.citation_service.CitationService.process_citation', 
               new_callable=AsyncMock) as mock_process:
        mock_process.return_value = mock_response

        response = test_client.post("/citation/get_citation", json=test_payload)
        
        assert response.status_code == 200
        assert response.json() == mock_response

def test_get_citation_web_with_invalid_sources(test_client, mock_pinecone, mock_summarize_llm, mock_citation_llm, mock_scraper):
    # Mock the app state
    test_client.app.state.pc = mock_pinecone
    test_client.app.state.summarize_llm = mock_summarize_llm
    test_client.app.state.citation_llm = mock_citation_llm
    test_client.app.state.async_content_scraper = mock_scraper

    # Test data
    test_payload = {
        "title": "Test Title",
        "content": "Test content",
        "citationStyle": "APA",
        "formType": "web",
        "sources": ["source1", "source2"],
        "supplementUrls": ["url1", "url2"]
    }

    # Mock the service response
    mock_response = {
        "citations": ["Test Citation"],
        "metadata": {"source": "test"}
    }

    with patch('src.services.citation_service.CitationService.process_citation', 
               new_callable=AsyncMock) as mock_process:
        mock_process.return_value = mock_response

        response = test_client.post("/citation/get_citation", json=test_payload)
        
        assert response.status_code == 422


def test_get_citation_invalid_form_type(test_client):
    # Test data with invalid form type
    test_payload = {
        "title": "Test Title",
        "content": "Test content",
        "citationStyle": "APA",
        "formType": "invalid"
    }

    response = test_client.post("/citation/get_citation", json=test_payload)
    
    assert response.status_code == 422

def test_get_citation_missing_title(test_client):
    # Test data without title
    test_payload = {
        "content": "Test content",
        "citationStyle": "APA",
        "formType": "auto"
    }

    response = test_client.post("/citation/get_citation", json=test_payload)
    
    assert response.status_code == 422