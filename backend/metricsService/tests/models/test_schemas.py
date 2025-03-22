from src.models.schemas import ComponentScore, CredibilityRequest, CredibilityResponse


def test_credibility_request_validation():
    """Test validation of CredibilityRequest model"""
    
    # Test valid request
    valid_data = {
        "domain": "example.com",
        "citation_doi": "10.1234/example",
        "journal": "Example Journal",
        "publication_date": "2023-01-01",
        "author_id": "0000-0001-2345-6789",
        "author_name": "John Doe"
    }
    request = CredibilityRequest(**valid_data)
    assert request.domain == "example.com"
    assert request.citation_doi == "10.1234/example"
    
    # Test minimum required fields
    minimal_data = {
        "publication_date": "2023-01-01"
    }
    request = CredibilityRequest(**minimal_data)
    assert request.publication_date == "2023-01-01"
    assert request.domain is None

def test_component_score_validation():
    """Test validation of ComponentScore model"""
    
    # Test valid component score
    valid_data = {
        "score": 80.0,
        "weighted_score": 16.0,
        "weight": 0.2,
        "available": True
    }
    component = ComponentScore(**valid_data)
    assert component.score == 80.0
    assert component.weighted_score == 16.0
    assert component.weight == 0.2
    assert component.available is True
    
    # Test with default values
    minimal_data = {
        "score": 50.0,
        "weighted_score": 25.0,
        "weight": 0.5
    }
    component = ComponentScore(**minimal_data)
    assert component.available is False

def test_credibility_response_validation():
    """Test validation of CredibilityResponse model"""
    
    # Test valid response
    valid_data = {
        "status": "success",
        "data": {
            "total_score": 85.0,
            "components": {
                "domain_reputation": {
                    "score": 80.0,
                    "weighted_score": 16.0,
                    "weight": 0.2,
                    "available": True
                }
            }
        }
    }
    response = CredibilityResponse(**valid_data)
    assert response.status == "success"
    assert response.data["total_score"] == 85.0
    assert response.data["components"]["domain_reputation"]["score"] == 80.0
    
    # Test with minimal data
    minimal_data = {
        "data": {
            "total_score": 50.0,
            "components": {}
        }
    }
    response = CredibilityResponse(**minimal_data)
    assert response.status == "success"  # Default value
    assert response.data["total_score"] == 50.0
