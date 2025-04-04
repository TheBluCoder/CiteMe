import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app import app
from unittest.mock import AsyncMock, MagicMock
from dotenv import load_dotenv
import nltk
from nltk.data import find

load_dotenv()
try:    
    find('tokenizers/punkt')
    find('punkt_tab')

except LookupError as e:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    
@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_pinecone():
    mock_pc = AsyncMock()
    mock_pc.cleanup = AsyncMock()
    return mock_pc

@pytest.fixture
def mock_summarize_llm():
    return MagicMock()

@pytest.fixture
def mock_citation_llm():
    return MagicMock()

@pytest.fixture
def mock_scraper():
    mock_scraper = AsyncMock()
    mock_scraper.__aenter__.return_value = mock_scraper
    mock_scraper.__aexit__.return_value = None
    return mock_scraper

@pytest.fixture
def mock_playwright_driver():
    mock_driver = AsyncMock()
    mock_driver.quit = AsyncMock()
    return mock_driver 

pytest_plugins = ['pytest_asyncio'] 