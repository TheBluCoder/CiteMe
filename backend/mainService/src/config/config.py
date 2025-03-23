from typing import Dict, Any
from dataclasses import dataclass, field
import os


@dataclass
class ScraperConfig:
    """Configuration class for web scraping settings.

    Contains various settings and parameters used for configuring web scraping behavior."""
    """Configuration for web scraping operations."""

    # HTTP Headers
    HTTP_HEADERS: Dict[str, str] = field(default_factory=lambda: {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "SEC_CH_UA": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "SEC_CH_UA_MOBILE": "?0",
        "SEC_FETCH_SITE": "cross-site",
        "ACCEPT_ENCODING": "gzip, deflate, br, zstd",
    })

    # File and Processing Limits
    # This is the maximum size of a file that we are willing to download and
    # process as a source document for citation.
    MB = 1024 * 1024

    """
    This is the maximum size of a file that we are willing to download and process as a source document for citation.
    """
    MAX_FILE_SIZE: int = 3 * MB  # 3 MB

    """
    This is the timeout duration for the requests made to the web scraper
    """
    TIMEOUT_DURATION: int = 8000

    def __post_init__(self):
        if self.MAX_FILE_SIZE <= 0:
            raise ValueError("MAX_FILE_SIZE must be positive")
        if self.TIMEOUT_DURATION <= 0:
            raise ValueError("TIMEOUT_DURATION must be positive")


@dataclass
class LlmConfig:
    """Configuration class for LLM and embedding settings.

    Contains settings related to LLM models, embeddings, and related parameters."""

    """
        This is the number of tokens that the source documents are split into to generate their embeddings.
        507 is the maximum number of tokens that can be processed by the multilingual-e5-large model.
        380 seem to be a good balance between how large each chunk should be in order to reduce the number of request made to pinecone for embeddings,
    """
    MAX_TOKENS: int = 380

    """
        This is the number of tokens that the query(the user's thesis) is split into to generate its embeddings.
        half of the MAX_TOKENS is a good balance between how large each chunk should be in order to reduce the number of request made to pinecone for embeddings,
        as well as being as accurate as possible for the eventual intext citation.
    """
    QUERY_TOKEN_SIZE: int = MAX_TOKENS // 1.5  # if using mixbread remember the max token for a query is 250

    """
        This is the percentage of overlap between the chunks of the source documents.
        15 was an arbitrary number that seemed to work well.
        Feel free to experiment with this value to see what works best for your use case.
    """
    DEFAULT_OVERLAP_PERCENT: int = 10

    """
        This is the number of tokens that are processed in a single batch.
        Each request to pinecone for embeddings is limited to 90  because the inference API can only handle 96 tokens in one batch request and each token
        can have a maximum size of 507.
    """
    BATCH_SIZE: int = 90

    """
        This is the maximum character lenght our pincone index name can be.
    """
    INDEX_NAME_LEN: int = 42

    """
    This is the number of documents that are processed in a single batch.
    """
    UPSERT_BATCH_SIZE: int = 1000

    """
    This is the llm that open router uses for generating the intext citation and reference list for each query
    """
    OPEN_ROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"

    """
    This is the azure model api endpoint
    """


# Concurrency and Performance
@dataclass
class ConcurrencyConfig:
    """Configuration class for concurrency settings.

    Contains settings that control parallel processing and thread management."""
    """Configuration for concurrency and performance settings."""

    """
        This is the number of concurrent workers that will be used for parallel and concurrent operations.
    """
    DEFAULT_CONCURRENT_WORKERS: int = (os.cpu_count() // 2) + 1

    HANDLE_INDEX_DELETE_WORKERS: int = 2


@dataclass
class ModelConfig:
    """Configuration class for AI model settings.

    Contains settings specific to AI models and their deployment."""
    """Configuration for ML models and APIs."""

    MODEL_ID: str = "BAAI/bge-m3"
    MODEL_API_URL: str = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_ID}"

    # LLM Generation Parameters
    DEFAULT_TEMPERATURE: float = 0.5
    DEFAULT_TOP_P: float = 1.0
    DEFAULT_MAX_TOKENS: int = 1024


@dataclass
class SearchConfig:
    """Configuration class for search settings.

    Contains settings related to search functionality and parameters."""
    """Configuration for search-related operations."""

    DATE_RESTRICT: str = "y5"
    TOP_N: int = 5
    SEARCH_URL: str = "https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}&dateRestrict={DATE_RESTRICT}&num={TOP_N}"


# Main configuration object
scraper_config = ScraperConfig()
concurrency_config = ConcurrencyConfig()
model_config = ModelConfig()
search_config = SearchConfig()
LlmConfig = LlmConfig()
