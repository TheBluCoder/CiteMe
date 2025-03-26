from typing import Dict, List, Any, Optional
from src.scraper.async_searchApi import SearchApi
from src.llm.chat_llm.Groq_llm import Summarize_llm
from src.scraper.async_content_scraper import AsyncContentScraper as ACS
from src.llm.Async_prepare_data_for_embedding import create_batches, chunk_text, create_batches_from_doc
import asyncio
import os
from src.llm.Pinecone import PineconeOperations
from src.utils.format_rerank_result import filter_mixbread_results
from src.config.log_config import setup_logging
from src.llm.chat_llm.Azure_llm import Citation
from src.config.config import LlmConfig as LLMEC
from src.config.config import concurrency_config, search_config
from src.custom_exceptions.llm_exceptions import CitationGenerationError
from src.llm.embedding_utils.reranker import rerank, format_for_rerank
from src.utils.index_operation import add_index_to_memory
from concurrent.futures import ThreadPoolExecutor
from langchain_core.documents import Document
from src.services.source_credibility_metric_service import get_credibility_metrics, calculate_overall_score
from src.models.schema import Source
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

log_filename = os.path.basename(__file__)
logger = setup_logging(filename=log_filename)

_index_executor = ThreadPoolExecutor(
    max_workers=concurrency_config.HANDLE_INDEX_DELETE_WORKERS)


class CitationService:
    """
    A service class that handles the end-to-end process of generating citations for given content.

    This class orchestrates the citation generation process including document search, content scraping,
    document processing, vector indexing, and citation formatting. It utilizes multiple external services
    including search APIs, content scrapers, and language models.

    Attributes:
        PC (PineconeOperations): Instance for vector database operations
        scraper_driver (PlaywrightDriver): Browser automation driver for content scraping
        summarize_llm (Summarize_llm): Language model for content summarization
        citation_llm (Citation): Language model for citation generation

    Methods:
        process_single_query: Process a single search query
        process_queries: Handle multiple queries concurrently
        process_citation: Main method for generating citations
    """

    def __init__(
            self,
            PC: PineconeOperations,
            scraper: ACS,
            summarize_llm: Summarize_llm,
            citation_llm: Citation):
        self.PC = PC
        self.summarize_llm = summarize_llm
        self.citation_llm = citation_llm
        self.scraper = scraper

    async def process_single_query(self, query: str) -> Dict[str, Any]:
        """
        Process a single query and return the results.
        We query the pinecone index with the query and get the top 5 results.
        We then rerank the results using the llm and return the top result.

        Args:
            query (str): The query to process

        Returns:
            Dict[str, Any]: The processed results

        """
        logger.info(f"Processing query {query[:15]}")
        search_results = await self.PC.hybrid_query(query=query, top_k=5)
        formatted_results = format_for_rerank(search_results['matches'])
        reranked_results = await rerank(matches=formatted_results, query=query, top_n=1, rank_fields=["page_content"])
        return reranked_results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def process_queries(
            self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple queries concurrently.

        Args:
            queries (List[str]): List of queries to process

        Returns:
            List[Dict[str, Any]]: List of processed results

        """
        logger.info("Processing queries concurrently")
        try:
            # Create tasks for all queries
            tasks = [self.process_single_query(query) for query in queries]

            # Process all queries concurrently
            results = await asyncio.gather(*tasks)
            return results

        except Exception as e:
            logger.exception(f"Error in batch query processing: {str(e)}")
            raise CitationGenerationError(
                "Failed to process queries after multiple retries") from e

    async def process_citation(self,
                               title: str,
                               content: str,
                               form_type: str,
                               style: str = "APA",
                               sources: List[Dict] = None,
                               supplement_urls: bool = False) -> Dict[str,
                                                                      Any] | False:
        """
        Main orchestrator for citation generation process.

        Args:
            title (str): Title of the content
            content (str): Content to generate citations for
            style (str, optional): Citation style. Defaults to "APA".

        Returns:
            Dict[str, Any] | False: Citation results or False if error occurs

        """
        try:
            # Step 0: Generate index name
            title = self.summarize_llm.getKeywordSearchTerm(content, proposed_title=title)
            index_name = self._generate_index_name(title)
            logger.info(f"index_name = {index_name}")
            if await self.PC.set_current_index(index_name):
                logger.info(f"Index set to {index_name}")
                return await self._generate_citations(content, style)

            # Step 1: Get sources
            processed_docs = None
            if form_type == "auto":
                search_results = await self._get_search_results(title)
                processed_docs = await self._process_documents(search_results)
            elif form_type == "web":
                processed_docs = await self.process_web_sources(title=title, sources=sources, supplement_urls=supplement_urls)
            elif form_type == "source":
                processed_docs = await self.process_direct_sources(sources)

            # Step 2: Create and populate index
            index_success = await self._create_and_populate_index(processed_docs, index_name=index_name)
            if not index_success:
                return False

            # Step 3: Generate citations
            return await self._generate_citations(content, style)

        except Exception as e:
            logger.exception(f"Error in citation process: {str(e)}")
            return False

    async def process_web_sources(self,
                                  sources: List[Source],
                                  supplement_urls: bool,
                                  title: str) -> Dict[str,
                                                      Any]:
        """Handle web form sources with optional supplementary URLs"""
        max_sources = search_config.TOP_N
        if supplement_urls:
            remaining_slots = max_sources - len(sources)
            logger.info(f"fetching {remaining_slots} additional sources")
            additional_results = await self._get_search_results(search_key=title, top_n=remaining_slots)
            sources_dict = additional_results.copy()
            for item in sources:
                key = item.url
                sources_dict["cleaned_result"]["meta"][key] = item.model_dump()
                sources_dict["cleaned_result"]["links"].append(key)

        return await self._process_documents(sources_dict)

    async def process_direct_sources(
            self, sources: List[Source]) -> Dict[str, Any]:
        """Handle direct source content without searching"""

        sources_as_docs = [
            Document(
                page_content=source.content,
                metadata={key: value for key, value in source.model_dump().items() if key != "content" and value is not None}
            )
            for source in sources
        ]

        # Await batch creation for efficient processing
        batches = await create_batches_from_doc(sources_as_docs, LLMEC.BATCH_SIZE)

        return {"batches": batches}

    async def _get_search_results(
            self, search_key: str, top_n: Optional[int] = None) -> Dict[str, Any] | False:
        """
        Get search terms and perform initial search.
        Here we use the google search_api to find sources that are relevant to the content.

        Args:
            search_key (str): The keyword term used by the Google Search Api to find relevant source.
        Returns:
            Dict[str, Any] | False: Search results dictionary or False if error occurs
        """

        try:

            cleaned_result = await SearchApi.clean_search(search_key, top_n=top_n)
            return {"search_key": search_key, "cleaned_result": cleaned_result}
        except Exception as e:
            logger.exception(f"Error getting search results: {str(e)}")
            return False

    async def _process_documents(
            self, search_results: Dict[str, Any]) -> Dict[str, Any] | False:
        """
        Process and download documents from search results.

        Args:
            search_results (Dict[str, Any]): Results from the search operation

        Returns:
            Dict[str, Any] | False: Processed document batches or False if error occurs
        """

        try:
            cleaned_result = search_results["cleaned_result"]
            async with asyncio.timeout(15):  # 15 second timeout
                download_results = await self.scraper.get_pdfs(
                    target_urls=cleaned_result.get("links"),
                    storage_path=search_results["search_key"]
                )

            return await self._prepare_document_batches(
                download_results,
                cleaned_result["meta"]
            )
        except Exception as e:
            logger.exception(f"Error processing documents: {str(e)}")
            return False

    async def _prepare_document_batches(
        self,
        download_results: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare document batches for processing.

        Args:
            download_results (Dict[str, Any]): Results from the download operation
            metadata (Dict[str, Any]): Metadata for the documents

        Returns:
            Dict[str, Any]: Document batches and storage path

        """
        filtered_results = {}

        # Update metadata with file paths
        for url, meta in metadata.items():
            if url in download_results["paths"]:
                meta["file_path"] = download_results["paths"][url]
                filtered_results[url] = meta

        # Create document batches
        batches = create_batches(
            download_results["storage_path"],
            filtered_results,
            LLMEC.BATCH_SIZE
        )

        return {
            "batches": batches,
            "storage_path": download_results["storage_path"]
        }

    async def _create_and_populate_index(
        self,
        processed_docs: Dict[str, Any],
        index_name: str
    ) -> bool:
        """
        Create and populate the search index.

        Args:
            processed_docs (Dict[str, Any]): Processed document batches
            index_name (str): Name of the index

        Returns:
            bool: True if index creation and population is successful, False otherwise

        """
        try:
            # Create index
            index = await self.PC.create_index(index_name=index_name)
            if not index:
                logger.exception("Index creation failed")
                return False
            # Add index to memory
            _index_executor.submit(add_index_to_memory, index_name)

            # Populate index
            return await self._populate_index(processed_docs["batches"])
        except Exception as e:
            logger.exception(f"Error creating/populating index: {e}")
            return False

    def _generate_index_name(self, search_key: str) -> str:
        """
        Generate a valid index name.

        Args:
            search_key (str): Search key for the index
        Returns:
            str: Valid index name

        """
        return (search_key.strip()[:LLMEC.INDEX_NAME_LEN]
                .replace(" ", "-")
                .lower() + "a")

    async def _populate_index(self, batches: List[Any]) -> bool:
        """
        Populate the index with document batches.

        Args:
            batches (List[Any]): List of document batches
        Returns:
            bool: True if index population is successful, False otherwise

        """
        try:
            initial_count = current_count = await self.PC.get_idx_stat()
            await self.PC.upsert_documents(batches=batches)

            # Wait for documents to be indexed
            while current_count < initial_count + len(batches):
                await asyncio.sleep(1)
                current_count = await self.PC.get_idx_stat()
                logger.info("Upserting document to pinecone...")

            return current_count >= initial_count + len(batches)
        except Exception as e:
            logger.exception(f"Error populating index: {str(e)}")
            return False

    async def _generate_citations(
            self, content: str, style: str) -> Dict[str, Any] | False:
        """Generate citations from processed content.

        Args:
            content (str): Processed content
            style (str): Citation style

        Returns:
            Dict[str, Any] | False: Citation results or False if error occurs


        """
        try:
            queries = chunk_text(
                content,
                max_tokens=LLMEC.QUERY_TOKEN_SIZE,
                overlap_percent=5
            )
            # RAG + Rerank
            results = await self.process_queries(queries)
            filtered_results = filter_mixbread_results(results)

            sources_with_scores = [
                {
                    "title": result.get("title", ""),
                    "link": result.get("link", "") or result.get("url", ""),
                    "domain": result.get("domain", ""),
                    "journal": result.get("journal_title", ""),
                    "citation_doi": result.get("citation_doi", ""),
                    "citation_references": result.get("references", [""]),
                    "publication_date": result.get("publication_date", ""),
                    "author_name": result.get("author_name", "") or result.get("author", "") or result.get("authors", ""),
                    "abstract": result.get("abstract", ""),
                    "issn": result.get("issn", ""),
                    "type": result.get("type", ""),
                    "rerank_score": result.get("score", 0)
                } for result in filtered_results
            ]

            credibility_task = get_credibility_metrics(sources_with_scores)
            citation_task = Citation(source=filtered_results).cite(
                text=queries,
                citation_style=style
            )

            # Start both tasks but handle credibility metrics first
            credibility_metrics = await asyncio.gather(credibility_task, return_exceptions=True)
            
            if isinstance(credibility_metrics[0], Exception):
                logger.exception(f"Credibility metrics failed: {str(credibility_metrics[0])}")
                credibility_metrics = []
            else:
                credibility_metrics = credibility_metrics[0]

            # Calculate scores immediately after getting credibility metrics
            scores = await calculate_overall_score(credibility_metrics, sources_with_scores, 
                                          rerank_weight=0.6, credibility_weight=0.4)

            sources = [
                item["data"] for item in credibility_metrics if item["status"] == "success"
            ] if credibility_metrics else []

            citation_result = await citation_task
            if isinstance(citation_result, Exception):
                logger.exception(f"Citation generation failed: {str(citation_result)}")
                raise CitationGenerationError("Failed to generate citations")

            return {
                "result": citation_result,
                "overall_score": scores["overall_score"],
                "sources": sources
            }

        except CitationGenerationError as e:
            logger.exception(f"Error generating citation: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error in citation generation: {str(e)}")
            return False

