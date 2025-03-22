import pytest
from src.custom_exceptions.llm_exceptions import SearchKeyGenerationError, CitationGenerationError

def test_search_key_generation_error():
    error_message = "Failed to generate search key"
    error = SearchKeyGenerationError(error_message)
    
    assert str(error) == error_message
    assert isinstance(error, Exception)

def test_citation_generation_error():
    error_message = "Error processing LLM request"
    error = CitationGenerationError(error_message)
    
    assert str(error) == error_message
    assert isinstance(error, Exception) 