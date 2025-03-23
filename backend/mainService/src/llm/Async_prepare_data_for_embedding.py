from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Optional, Dict
import os
import nltk
from concurrent.futures import ThreadPoolExecutor
from src.config.config import concurrency_config, LlmConfig as LLMEC
import glob
from src.config.log_config import setup_logging

log_filename = os.path.basename(__file__)
logger = setup_logging(filename=log_filename)

shared_executor = ThreadPoolExecutor(
    max_workers=concurrency_config.DEFAULT_CONCURRENT_WORKERS)


def load_document(docs_path: str) -> List[Document]:
    """Load PDF documents from a directory path.

    Args:
        docs_path (str): Path to directory containing PDF files

    Returns:
        List[Document]: List of loaded document objects

    Raises:
        FileNotFoundError: If the provided path does not exist
    """
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"{docs_path} does not exist")

    # List PDF files in a sorted order (alphabetically, for example)
    pdf_paths = sorted(
        glob.glob(
            os.path.join(
                docs_path,
                "**/*.pdf"),
            recursive=True))
    all_docs = []

    for pdf in pdf_paths:
        try:
            loader = PyPDFLoader(pdf)
            docs = loader.load()  # Each document represents one page.
        except Exception as e:
            logger.exception(f"Error loading {pdf}")
            continue

        # Sort pages by metadata (if available)
        docs.sort(key=lambda doc: doc.metadata.get("page_number", 0))

        # Now filter pages: after encountering "conclusion", stop at the first
        # page that mentions "reference" or "bibliography"
        filtered_pages = []
        conclusion_found = False
        for page in docs:
            content = page.page_content.lower()
            if not conclusion_found and "conclusion" in content:
                conclusion_found = True
            # Once we've passed conclusion, if a page signals references, stop
            # processing further pages
            if conclusion_found and (
                    "reference" in content or "bibliography" in content):
                break
            filtered_pages.append(page)

        all_docs.extend(filtered_pages)

    return all_docs


def split_document(
        documents: List[Document],
        max_tokens: Optional[int] = LLMEC.MAX_TOKENS) -> List[Document]:
    """Split documents into smaller chunks based on token size.

    Args:
        documents (List[Document]): Documents to split
        max_tokens (Optional[int], optional): Maximum tokens per chunk.
            Defaults to LLMEC.MAX_TOKENS.

    Returns:
        List[Document]: List of split document chunks
    """
    split_docs = []

    def process_doc(doc: Document) -> List[Document]:
        chunks = chunk_text(
            doc.page_content,
            max_tokens=max_tokens,
            overlap_percent=LLMEC.DEFAULT_OVERLAP_PERCENT
        )
        return [
            Document(
                page_content=chunk,
                metadata=doc.metadata.copy()) for chunk in chunks]

    results = shared_executor.map(process_doc, documents)

    for result in results:
        split_docs.extend(result)

    return split_docs


def append_metadata(
        documents: list[Document], metadata: Dict[str, Dict[str, str]]) -> list[Document]:
    """
    Append metadata to documents based on file path matching.

    Args:
        documents (list[Document]): List of documents to update
        metadata (Dict[str, Dict[str, str]]): Dictionary of metadata keyed by file path

    Returns:
        list[Document]: Documents with updated metadata
    """

    metadata_lookup = {
        value.get("file_path"): value for value in metadata.values()}
    for document in documents:
        if document.metadata.get("source") in metadata_lookup:
            document.metadata = metadata_lookup[document.metadata.get(
                "source")]
    return documents


def split_and_append_metadata(
        docs_path: str, metadata: Dict[str, Dict[str, str]]) -> list[Document]:
    """
    Load documents, append metadata, and split them into smaller chunks.

    Args:
        docs_path (str): Path to the documents
        metadata (Dict[str, Dict[str, str]]): Dictionary of metadata to append

    Returns:
        list[Document]: List of processed and split documents with metadata
    """

    documents = load_document(docs_path)
    documents = append_metadata(documents, metadata)
    documents = split_document(documents)
    return documents


def create_batches(docs_path: str,
                   metadata: Dict[str,
                                  Dict[str,
                                       str]],
                   batch_element_size: int) -> List[List[Document]]:
    """
    Create batches of documents with metadata for processing.

    Args:
        docs_path (str): Path to the documents
        metadata (Dict[str, Dict[str, str]]): Dictionary of metadata to append
        batch_element_size (int): Size of each batch

    Returns:
        List[List[Document]]: List of document batches
    """

    documents = split_and_append_metadata(docs_path, metadata)
    batches = []
    for i in range(0, len(documents), batch_element_size):
        batches.append(documents[i:i + batch_element_size])
    return batches


async def create_batches_from_doc(
        documents: List[Document], batch_element_size: int) -> List[List[Document]]:
    """
    Create batches of documents from a list of texts.

    args:
        documents (List[Document]): List of documents to split into batches

    returns:
        List[List[Document]]: List of document batches
    """
    batches = []

    split_documents = split_document(documents)

    for i in range(0, len(split_documents), batch_element_size):
        batches.append(split_documents[i:i + batch_element_size])
    return batches


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string.

    Args:
        text (str): Text to count tokens for

    Returns:
        int: Number of tokens in the text
    """
    """Roughly estimates number of tokens based on word count.
    This is a conservative estimate that tends to overestimate rather than underestimate."""
    # Most tokenizers average 1.3-1.5 tokens per word
    # amazonq-ignore-next-line
    return int(len(text.split()) * 1.5)


def process_chunk(
        sentences: List[str],
        max_tokens: int = LLMEC.MAX_TOKENS,
        overlap_percent: int = LLMEC.DEFAULT_OVERLAP_PERCENT) -> List[str]:
    """Process a list of sentences into overlapping chunks.

    Args:
        sentences (List[str]): List of sentences to process
        max_tokens (int, optional): Maximum tokens per chunk.
            Defaults to LLMEC.MAX_TOKENS.
        overlap_percent (int, optional): Percentage of overlap between chunks.
            Defaults to LLMEC.DEFAULT_OVERLAP_PERCENT.

    Returns:
        List[str]: List of processed text chunks
    """
    """Processes a set of sentences into properly formatted text chunks."""
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        # If a single sentence is too large, split it
        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0

            # Force split using RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=max_tokens, chunk_overlap=min(
                    overlap_percent, int(
                        max_tokens * 0.1)))
            sub_chunks = splitter.split_text(sentence)
            chunks.extend(sub_chunks)
            continue

        # If adding this sentence exceeds chunk size, save current chunk
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))

            # Apply overlap
            overlap_size = max(
                1, int(len(current_chunk) * (overlap_percent / 100)))
            # Retain overlap context
            current_chunk = current_chunk[-overlap_size:]
            current_tokens = count_tokens(" ".join(current_chunk))

        # Add sentence to chunk
        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    # Add last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def chunk_text(
        text: str,
        max_tokens: int = LLMEC.MAX_TOKENS,
        overlap_percent: int = LLMEC.DEFAULT_OVERLAP_PERCENT) -> List[str]:
    """Split text into chunks with specified overlap.

    Args:
        text (str): Text to split into chunks
        max_tokens (int, optional): Maximum tokens per chunk.
            Defaults to LLMEC.MAX_TOKENS.
        overlap_percent (int, optional): Percentage of overlap between chunks.
            Defaults to LLMEC.DEFAULT_OVERLAP_PERCENT.

    Returns:
        List[str]: List of text chunks
    """
    """Splits text into chunks in parallel, ensuring consistent sizes."""
    sentences = nltk.sent_tokenize(text)
    return process_chunk(sentences, max_tokens, overlap_percent)
