import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.citation_service import CitationService
from src.llm.Pinecone import PineconeOperations
from src.scraper.async_content_scraper import AsyncContentScraper
from src.llm.chat_llm.Groq_llm import Summarize_llm
from src.llm.chat_llm.Azure_llm import Citation
from src.custom_exceptions.llm_exceptions import CitationGenerationError
from src.models.schema import Source
from src.scraper.async_searchApi import SearchApi
from src.llm.embedding_utils.reranker import rerank
from src.utils.format_rerank_result import filter_mixbread_results
from src.services.source_credibility_metric_service import get_credibility_metrics, calculate_overall_score

@pytest.fixture
def mock_pinecone():
    mock_pc = AsyncMock(spec=PineconeOperations)
    mock_pc.hybrid_query = AsyncMock()
    mock_pc.create_index = AsyncMock(return_value=True)
    mock_pc.get_idx_stat = AsyncMock(return_value=0)
    mock_pc.upsert_documents = AsyncMock()
    mock_pc.set_current_index = AsyncMock(return_value=False)
    return mock_pc

@pytest.fixture
def mock_scraper():
    mock_scraper = AsyncMock(spec=AsyncContentScraper)
    mock_scraper.get_pdfs = AsyncMock()
    return mock_scraper

@pytest.fixture
def mock_summarize_llm():
    mock_llm = MagicMock(spec=Summarize_llm)
    mock_llm.getKeywordSearchTerm = MagicMock(return_value="test-keyword")
    return mock_llm

@pytest.fixture
def mock_citation_llm():
    mock_llm = MagicMock(spec=Citation)
    mock_llm.cite = AsyncMock(return_value=["Test Citation"])
    return mock_llm

@pytest.fixture
def citation_service(mock_pinecone, mock_scraper, mock_summarize_llm, mock_citation_llm):
    return CitationService(
        PC=mock_pinecone,
        scraper=mock_scraper,
        summarize_llm=mock_summarize_llm,
        citation_llm=mock_citation_llm
    )

@pytest.mark.asyncio
@patch('src.services.citation_service.rerank')
async def test_process_single_query_success(mock_rerank, citation_service, mock_pinecone):
    # Arrange
    query = "test query"
    mock_pinecone.hybrid_query.return_value = {
        "matches": [
            {"id": "1", "score": 0.9, "metadata": {"content": "test content"}}
        ]
    }
    mock_rerank.return_value = [{"id": "1", "score": 0.95, "content": "test content"}]

    # Act
    result = await citation_service.process_single_query(query)

    # Assert
    assert result is not None
    mock_pinecone.hybrid_query.assert_called_once_with(query=query, top_k=5)
    mock_rerank.assert_called_once()

@pytest.mark.asyncio
@patch('src.services.citation_service.rerank')
async def test_process_queries_success(mock_rerank, citation_service, mock_pinecone):
    # Arrange
    queries = ["query1", "query2"]
    mock_pinecone.hybrid_query.side_effect = [
        {"matches": [{"id": "1", "score": 0.9}]},
        {"matches": [{"id": "2", "score": 0.8}]}
    ]
    mock_rerank.return_value = [{"id": "1", "score": 0.95}]

    # Act
    results = await citation_service.process_queries(queries)

    # Assert
    assert len(results) == 2
    assert mock_pinecone.hybrid_query.call_count == 2
    assert mock_rerank.call_count == 2

@pytest.mark.asyncio
@patch('src.services.citation_service.rerank')
async def test_process_queries_retry(mock_rerank, citation_service, mock_pinecone):
    # Arrange
    queries = ["query1"]
    mock_pinecone.hybrid_query.side_effect = [
        Exception("First attempt fails"),
        {"matches": [{"id": "1", "score": 0.9}]}
    ]
    mock_rerank.return_value = [{"id": "1", "score": 0.95}]

    # Act
    results = await citation_service.process_queries(queries)

    # Assert
    assert len(results) == 1
    assert mock_pinecone.hybrid_query.call_count == 2
    assert mock_rerank.call_count == 1

# @pytest.mark.skip(reason="Skipping test due to making actual API calls")
@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_auto_success(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service, 
    mock_scraper
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(return_value={
        "matches": [{"id": "1", "score": 0.9}]
    })
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=False)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance
    
    # Mock Scraper
    mock_scraper.get_pdfs.return_value = {
        "paths": {"url1": "path1"},
        "storage_path": "test_path"
    }
    
    # Mock Citation LLM
    mock_citation_instance = AsyncMock()
    mock_citation_instance.cite = AsyncMock(return_value=["Test Citation"])
    mock_citation_class.return_value = mock_citation_instance
    
    # Mock Summarize LLM
    mock_summarize_instance = MagicMock()
    mock_summarize_instance.getKeywordSearchTerm = MagicMock(return_value="test-keyword")
    mock_genai_cite.merge_citation.return_value = ["Test Citation"]
    
    # Replace the citation_service's LLM instances with our mocks
    citation_service.citation_llm = mock_citation_instance
    citation_service.summarize_llm = mock_summarize_instance
    
    # Mock rerank and filter results
    mock_rerank.return_value = [{"id": "1", "score": 0.95}]
    mock_filter_mixbread_results.return_value = [{"id": "1", "score": 0.95}]
    
    # Mock credibility metrics
    mock_get_credibility_metrics.return_value = [{"status": "success", "data": {"title": "Test Source"}}]
    mock_calculate_overall_score.return_value = 0.8

    # Mock document processing
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"source": "path1"}
    mock_load_document.return_value = [mock_doc]
    mock_split_document.return_value = [mock_doc]
    mock_append_metadata.return_value = [mock_doc]

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is not None
    assert "result" in result
    assert "overall_score" in result
    assert "sources" in result
    assert result["result"] == ["Test Citation"]
    assert result["overall_score"] == 0.8
    assert len(result["sources"]) == 1

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_web_success(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service, 
    mock_scraper
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    sources = [
        Source(
            url="http://test.com",
            title="Test Source",
            content="Test source content",
            authors="Test Author"
        )
    ]
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(return_value={
        "matches": [{"id": "1", "score": 0.9}]
    })
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=False)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance
    
    # Mock Scraper
    mock_scraper.get_pdfs.return_value = {
        "paths": {"url1": "path1"},
        "storage_path": "test_path"
    }
    
    # Mock Citation LLM
    mock_citation_instance = AsyncMock()
    mock_citation_instance.cite = AsyncMock(return_value=["Test Citation"])
    mock_citation_class.return_value = mock_citation_instance
    
    # Mock Summarize LLM
    mock_summarize_instance = MagicMock()
    mock_summarize_instance.getKeywordSearchTerm = MagicMock(return_value="test-keyword")
    mock_genai_cite.merge_citation.return_value = ["Test Citation"]
    
    # Replace the citation_service's LLM instances with our mocks
    citation_service.citation_llm = mock_citation_instance
    citation_service.summarize_llm = mock_summarize_instance
    
    # Mock rerank and filter results
    mock_rerank.return_value = [{"id": "1", "score": 0.95}]
    mock_filter_mixbread_results.return_value = [{"id": "1", "score": 0.95}]
    
    # Mock credibility metrics
    mock_get_credibility_metrics.return_value = [{"status": "success", "data": {"title": "Test Source"}}]
    mock_calculate_overall_score.return_value = 0.8

    # Mock document processing
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"source": "path1"}
    mock_load_document.return_value = [mock_doc]
    mock_split_document.return_value = [mock_doc]
    mock_append_metadata.return_value = [mock_doc]

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="web",
        style=style,
        sources=sources,
        supplement_urls=True
    )

    # Assert
    assert result is not None
    assert "result" in result
    assert "overall_score" in result
    assert "sources" in result
    assert result["result"] == ["Test Citation"]
    assert result["overall_score"] == 0.8
    assert len(result["sources"]) == 1

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_source_success(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    sources = [
        Source(
            url="http://test.com",
            title="Test Source",
            content="Test source content",
            authors="Test Author"
        )
    ]
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(return_value={
        "matches": [{"id": "1", "score": 0.9}]
    })
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=False)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance
    
    # Mock Citation LLM
    mock_citation_instance = AsyncMock()
    mock_citation_instance.cite = AsyncMock(return_value=["Test Citation"])
    mock_citation_class.return_value = mock_citation_instance
    
    # Mock Summarize LLM
    mock_summarize_instance = MagicMock()
    mock_summarize_instance.getKeywordSearchTerm = MagicMock(return_value="test-keyword")
    mock_genai_cite.merge_citation.return_value = ["Test Citation"]
    
    # Replace the citation_service's LLM instances with our mocks
    citation_service.citation_llm = mock_citation_instance
    citation_service.summarize_llm = mock_summarize_instance
    
    # Mock rerank and filter results
    mock_rerank.return_value = [{"id": "1", "score": 0.95}]
    mock_filter_mixbread_results.return_value = [{"id": "1", "score": 0.95}]
    
    # Mock credibility metrics
    mock_get_credibility_metrics.return_value = [{"status": "success", "data": {"title": "Test Source"}}]
    mock_calculate_overall_score.return_value = 0.8

    # Mock document processing
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"source": "path1"}
    mock_load_document.return_value = [mock_doc]
    mock_split_document.return_value = [mock_doc]
    mock_append_metadata.return_value = [mock_doc]

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="source",
        style=style,
        sources=sources
    )

    # Assert
    assert result is not None
    assert "result" in result
    assert "overall_score" in result
    assert "sources" in result
    assert result["result"] == ["Test Citation"]
    assert result["overall_score"] == 0.8
    assert len(result["sources"]) == 1

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_existing_index(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(return_value={
        "matches": [{"id": "1", "score": 0.9}]
    })
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=True)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance
    
    # Mock Citation LLM
    mock_citation_instance = AsyncMock()
    mock_citation_instance.cite = AsyncMock(return_value=["Test Citation"])
    mock_citation_class.return_value = mock_citation_instance
    
    # Mock Summarize LLM
    mock_summarize_instance = MagicMock()
    mock_summarize_instance.getKeywordSearchTerm = MagicMock(return_value="test-keyword")
    mock_genai_cite.merge_citation.return_value = ["Test Citation"]
    
    # Replace the citation_service's LLM instances with our mocks
    citation_service.citation_llm = mock_citation_instance
    citation_service.summarize_llm = mock_summarize_instance
    
    # Mock rerank and filter results
    mock_rerank.return_value = [{"id": "1", "score": 0.95}]
    mock_filter_mixbread_results.return_value = [{"id": "1", "score": 0.95}]
    
    # Mock credibility metrics
    mock_get_credibility_metrics.return_value = [{"status": "success", "data": {"title": "Test Source"}}]
    mock_calculate_overall_score.return_value = 0.8

    # Mock document processing
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"source": "path1"}
    mock_load_document.return_value = [mock_doc]
    mock_split_document.return_value = [mock_doc]
    mock_append_metadata.return_value = [mock_doc]

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is not None
    assert "result" in result
    assert "overall_score" in result
    assert "sources" in result
    assert result["result"] == ["Test Citation"]
    assert result["overall_score"] == 0.8
    assert len(result["sources"]) == 1

@pytest.mark.asyncio
async def test_process_citation_error_handling(citation_service, mock_pinecone):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    
    mock_pinecone.hybrid_query.side_effect = Exception("Test error")

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_generate_index_name(citation_service):
    # Arrange
    search_key = "Test Search Key With Spaces"

    # Act
    index_name = citation_service._generate_index_name(search_key)

    # Assert
    assert isinstance(index_name, str)
    assert len(index_name) <= 64  # Assuming LLMEC.INDEX_NAME_LEN is 64
    assert "-" in index_name
    assert index_name.endswith("a")

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_mla_style(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "MLA"
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(return_value={
        "matches": [{"id": "1", "score": 0.9}]
    })
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=False)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance
    
    # Mock Citation LLM
    mock_citation_instance = AsyncMock()
    mock_citation_instance.cite = AsyncMock(return_value=["Test MLA Citation"])
    mock_citation_class.return_value = mock_citation_instance
    
    # Mock Summarize LLM
    mock_summarize_instance = MagicMock()
    mock_summarize_instance.getKeywordSearchTerm = MagicMock(return_value="test-keyword")
    mock_genai_cite.merge_citation.return_value = ["Test MLA Citation"]
    
    # Replace the citation_service's LLM instances with our mocks
    citation_service.citation_llm = mock_citation_instance
    citation_service.summarize_llm = mock_summarize_instance
    
    # Mock rerank and filter results
    mock_rerank.return_value = [{"id": "1", "score": 0.95}]
    mock_filter_mixbread_results.return_value = [{"id": "1", "score": 0.95}]
    
    # Mock credibility metrics
    mock_get_credibility_metrics.return_value = [{"status": "success", "data": {"title": "Test Source"}}]
    mock_calculate_overall_score.return_value = 0.8

    # Mock document processing
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"source": "path1"}
    mock_load_document.return_value = [mock_doc]
    mock_split_document.return_value = [mock_doc]
    mock_append_metadata.return_value = [mock_doc]

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is not None
    assert "result" in result
    assert result["result"] == ["Test MLA Citation"]

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_empty_content(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = ""
    style = "APA"
    
    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is False

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_llm_error(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(return_value={
        "matches": [{"id": "1", "score": 0.9}]
    })
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=False)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance
    
    # Mock Citation LLM to raise an error
    mock_citation_instance = AsyncMock()
    mock_citation_instance.cite = AsyncMock(side_effect=CitationGenerationError("Test error"))
    mock_citation_class.return_value = mock_citation_instance
    
    # Replace the citation_service's LLM instance with our mock
    citation_service.citation_llm = mock_citation_instance

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is False

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_supplement_urls_failure(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service,
    mock_scraper
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    sources = [
        Source(
            url="http://test.com",
            title="Test Source",
            content="Test source content",
            authors="Test Author"
        )
    ]
    
    # Mock SearchApi to raise an error
    mock_search_api.clean_search = AsyncMock(side_effect=Exception("Search API error"))
    
    # Mock Scraper to raise an error
    mock_scraper.get_pdfs = AsyncMock(side_effect=Exception("Scraper error"))

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="web",
        style=style,
        sources=sources,
        supplement_urls=True
    )

    # Assert
    assert result is False

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_search_api_error(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    
    # Mock SearchApi to raise an error
    mock_search_api.clean_search = AsyncMock(side_effect=Exception("Search API error"))

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is False
    assert mock_search_api.clean_search.call_count == 1

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_pinecone_error(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone to raise an error
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(side_effect=Exception("Pinecone error"))
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=False)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is False

@pytest.mark.asyncio
@patch('src.services.citation_service.SearchApi')
@patch('src.services.citation_service.rerank')
@patch('src.services.citation_service.filter_mixbread_results')
@patch('src.services.citation_service.get_credibility_metrics')
@patch('src.services.citation_service.calculate_overall_score')
@patch('src.llm.Async_prepare_data_for_embedding.load_document')
@patch('src.llm.Async_prepare_data_for_embedding.split_document')
@patch('src.llm.Async_prepare_data_for_embedding.append_metadata')
@patch('src.llm.Pinecone.PineconeOperations')
@patch('src.services.citation_service.Citation')
@patch('src.llm.chat_llm.Azure_llm.Genai_cite')
async def test_process_citation_document_processing_error(
    mock_genai_cite,
    mock_citation_class,
    mock_pinecone_class,
    mock_append_metadata,
    mock_split_document,
    mock_load_document,
    mock_calculate_overall_score,
    mock_get_credibility_metrics,
    mock_filter_mixbread_results,
    mock_rerank,
    mock_search_api,
    citation_service
):
    # Arrange
    title = "Test Title"
    content = "Test content"
    style = "APA"
    
    # Mock SearchApi
    mock_search_api.clean_search = AsyncMock(return_value={
        "links": ["url1"],
        "meta": {"url1": {"title": "Test Source"}}
    })
    
    # Mock Pinecone
    mock_pinecone_instance = AsyncMock()
    mock_pinecone_instance.hybrid_query = AsyncMock(return_value={
        "matches": [{"id": "1", "score": 0.9}]
    })
    mock_pinecone_instance.set_current_index = AsyncMock(return_value=False)
    mock_pinecone_instance.create_index = AsyncMock(return_value=True)
    mock_pinecone_instance.get_idx_stat = AsyncMock(side_effect=[0, 1])
    mock_pinecone_instance.upsert_documents = AsyncMock()
    mock_pinecone_class.return_value = mock_pinecone_instance
    
    # Replace the citation_service's Pinecone instance with our mock
    citation_service.PC = mock_pinecone_instance
    
    # Mock document processing to raise an error
    mock_load_document.side_effect = Exception("Document processing error")

    # Act
    result = await citation_service.process_citation(
        title=title,
        content=content,
        form_type="auto",
        style=style
    )

    # Assert
    assert result is False 