import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import AsyncMock, patch


def test_root_endpoint(test_client):
    """Test the root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    
@pytest.mark.asyncio
async def test_credibility_endpoint_default_response(test_client):
    test_data = {
        "domain": "example.com",
        "citation_doi": "10.1234/example",
        "journal": "Example Journal",
        "publication_date": "2023-01-01",
        "author_id": "0000-0001-2345-6789",
        "title": "Test Title",
        "type": "article"
    }
    
    expected_response = {
        "status": "success",
        "data": {
            "credibility_score": 85.0,
            "url": "example.com",
            "title": "Test Title",
            "type": "article"
        }
    }
    
    with patch('src.api.endpoints.calculate_credibility', new_callable=AsyncMock) as mock_calculate:
        mock_calculate.return_value = {
            "total_score": 85.0,
            "credibility_level": "High",
            "domain_reputation": {
                "score": 80.0,
                "weighted_score": 16.0,
                "weight": 0.2,
                "available": True
            }
        }
        
        response = test_client.post("/api/v1/credibility", json=test_data)
        assert response.status_code == 200
        assert response.json() == expected_response



def test_credibility_endpoint_detailed_response(test_client):
    """Test the credibility endpoint with detailed response"""
    test_data = {
        "domain": "example.com",
        "citation_doi": "10.1234/example",
        "journal": "Example Journal",
        "publication_date": "2023-01-01",
        "author_id": "0000-0001-2345-6789",
        "title": "Test Title",
        "type": "article"
    }
    
    with patch('src.api.endpoints.calculate_credibility', new_callable=AsyncMock) as mock_calculate:
            
        mock_calculate.return_value = {
            "total_score": 85.0,
            "credibility_level": "High",
            "domain_reputation": {
                "score": 80.0,
                "weighted_score": 16.0,
                "weight": 0.2,
                "available": True
            },
            "citation_count": {
                "score": 75.0,
                "weighted_score": 15.0,
                "weight": 0.2,
                "available": True
            },
            "journal_impact": {
                "score": 90.0,
                "weighted_score": 22.5,
                "weight": 0.25,
                "available": True
            },
            "recency": {
                "score": 100.0,
                "weighted_score": 10.0,
                "weight": 0.1,
                "available": True
            },
            "authorship_reputation": {
                "score": 80.0,
                "weighted_score": 20.0,
                "weight": 0.25,
                "available": True
            }
        }
        
        response = test_client.post("http://127.0.0.1:9050/api/v1/credibility?detailed=true", json=test_data)
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "success"
        assert "data" in response_data
        assert "credibility_score" in response_data["data"]
        assert "domain_reputation" in response_data["data"]["component"]
        assert "citation_count" in response_data["data"]["component"]
        assert "journal_impact" in response_data["data"]["component"]
        assert "recency" in response_data["data"]["component"]
        assert "authorship_reputation" in response_data["data"]["component"]

def test_credibility_endpoint_with_none_score(test_client):
    test_data = {
        "domain": "example.com",
        "citation_doi": "10.1234/example",
        "journal": "Example Journal",
        "publication_date": "2023-01-01",
        "author_id": "0000-0001-2345-6789"
    }
    
    with patch('src.api.endpoints.calculate_credibility', new_callable=AsyncMock) as mock_calculate:
        mock_calculate.return_value = {
            "total_score": 60.0,
            "credibility_level": "Moderate",
            "domain_reputation": {
                "score": None,
                "weighted_score": 0.0,
                "weight": 0.2,
                "available": True
            }
        }
        
        response = test_client.post("/api/v1/credibility", json=test_data)
        assert response.status_code == 200
        response_json = response.json()
        assert "data" in response_json
        assert "credibility_score" in response_json["data"]  # Note lowercase
        assert response_json["data"]["credibility_score"] == 60.0

