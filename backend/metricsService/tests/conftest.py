import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def test_client():
    """Fixture to provide a test client for FastAPI"""
    return TestClient(app)

@pytest.fixture
def mock_credibility_request():
    """Fixture to provide a sample credibility request"""
    return {
        "domain": "example.com",
        "citation_doi": "10.1234/example",
        "journal": "Example Journal",
        "publication_date": "2023-01-01",
        "author_id": "0000-0001-2345-6789",
        "author_name": "John Doe"
    }
