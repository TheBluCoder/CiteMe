import json
import os
import re
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from typing import List, Optional, Dict, Union, Any
from src.llm.Instructions import *
from src.llm.chat_llm.Gemini_llm import Genai_cite
import asyncio
from src.config.log_config import setup_logging
from src.custom_exceptions.api_exceptions import MissingApiKeyException, InvalidApiKeyException, MissingEndpointException
from azure.core.exceptions import HttpResponseError
from azure.ai.inference.models import ChatCompletions
from src.custom_exceptions.llm_exceptions import CitationGenerationError
import logging
from concurrent.futures import ThreadPoolExecutor
from src.config.config import concurrency_config, model_config

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING)


filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)
RESPONSE_CLEANUP_PATTERN = re.compile(r'^(```json\n|```|json|\n)|(```|\n)$')


_executor = ThreadPoolExecutor(
    max_workers=concurrency_config.DEFAULT_CONCURRENT_WORKERS)


class Citation:
    model = "Phi-4"
    embedding_model = "text-embedding-3-small"

    def __init__(
            self,
            source: List[str] = None,
            api_key: str = None,
            model: Optional[str] = None,
            endpoint: Optional[str] = None) -> None:
        """Initialize the Azure hosted LLM client.

        Args:
            source (str, optional): Source identifier. Defaults to None.
            api_key (str, optional): Azure API key. Defaults to global api_key.
            model (Optional[str], optional): Name of the model to use. Defaults to None.
            endpoint (Optional[str], optional): Azure endpoint URL. Defaults to None.
        """
        self.api_key = api_key or get_azure_api_key("AZURE_CREDENTIAL")
        self.model_name = model or self.model
        self.source = source
        self.client = ChatCompletionsClient(
            endpoint=endpoint or get_azure_endpoint("AZURE_MODELS_ENDPOINT"),
            credential=AzureKeyCredential(self.api_key),
        )
        self.merger = Genai_cite()

    async def cite(self,
                   text: List[str],
                   citation_style: str) -> Dict[str,
                                                Union[str,
                                                      List[Dict[str,
                                                                str]]]]:
        """Generate citations for given text passages.

        Args:
            text (List[str]): List of text passages to generate citations for
            format (str): Citation format (e.g., "APA", "MLA")

        Returns:
            Dict[str, Union[str, List[Dict[str, str]]]]: Dictionary containing citations and metadata
        """
        # amazonq-ignore-next-line
        batch_size = max(1, len(text) // 10)
        try:
            tasks = [self._cite(text[i:i + batch_size], citation_style)
                     for i in range(0, len(text), batch_size)]
            citations = await asyncio.gather(*tasks)
            merged_citations = await self.merger.merge_citation(citations, format=citation_style)
        except Exception as e:
            logger.exception(f"Error in citation generation: {e}")
            raise CitationGenerationError(
                f"""Citation generation failed for {
                    len(text)} text passages: {e}""") from e

        return merged_citations

    async def _cite(self, text: str |
                    List[str], format: str) -> Dict[str, Any]:
        """Internal method to process citation requests.

        Args:
            text (Union[str, List[str]]): Text or list of texts to generate citations for
            format (str): Citation format (e.g., "APA", "MLA")

        Returns:
            Dict[str, Any]: Processed citation results
        """
        messages = [
            SystemMessage(
                content=SYSTEM_INSTRUCTION.format(
                    format=format)), UserMessage(
                content=USER_INSTRUCTION.format(
                    text=text, sources=self.source, format=format)), ]
        model = self.model_name
        # Offload blocking work to a thread
        logger.info(f"Sending request to Azure API with messages")
        result = await asyncio.get_running_loop().run_in_executor(
            _executor,
            self._blocking_citation_request,
            messages,
            model
        )

        return result

    def _blocking_citation_request(
            self, messages: List[str], model_name: str = None) -> Dict[str, Any]:
        """Make a blocking citation request to the Azure API.

        Args:
            messages (List[str]): List of messages to process
            model_name (str, optional): Model to use for citation. Defaults to None.

        Returns:
            Dict[str, Any]: Raw API response containing citation data
        """
        try:
            response: ChatCompletions = self.client.complete(
                messages=messages, 
                model=(model_name or self.model_name), 
                temperature=model_config.CITE_LLM_TEMPERATURE, 
                top_p=model_config.DEFAULT_TOP_P)
            response_content = response.choices[0].message.content
            # amazonq-ignore-next-line
            response_content = response_content.strip()
            response_content = re.sub(
                RESPONSE_CLEANUP_PATTERN, '', response_content)
            result = json.loads(response_content)
        except HttpResponseError as e:
            logger.exception(f"Error in establishing azure client: {e}")
            raise e
        except json.JSONDecodeError as e:
            logger.warning(f"Error in decoding json: {e}")
            return {"unformatted_response": response}
        return result


def validate_azure_api_key(api_key: str) -> bool:
    """
    Validate Azure API key format.

    Args:
        api_key (str): The API key to validate

    Returns:
        bool: True if valid, False otherwise

    """
    # Basic pattern for Azure API keys - adjust as needed
    pattern = r'^[a-zA-Z0-9]{32,}$'
    return bool(re.match(pattern, api_key))


def get_azure_api_key(key: str) -> str:
    """
    Retrieve and validate Azure API key from environment variables.

    Returns:
        str: Valid API key

    Raises:
        MissingApiKeyException: If API key is not set in environment
        InvalidApiKeyException: If API key format is invalid
    """
    api_key = os.getenv(key, "")

    if not api_key:
        raise MissingApiKeyException(
            "AZURE_PHI_CREDENTIAL key missing from environment variables"
        )

    if not validate_azure_api_key(api_key):
        raise InvalidApiKeyException(
            "AZURE_PHI_CREDENTIAL has invalid format. Please check your API key"
        )
    return api_key


def get_azure_endpoint(endpoint: str) -> str:
    """
    Retrieve and validate Azure endpoint from environment variables.

    Returns:
        str: Valid endpoint

    Raises:
        MissingEndpointException: If endpoint is not set in environment
        InvalidEndpointException: If endpoint format
    """

    endpoint = os.getenv(endpoint, "")
    if not endpoint:
        raise MissingEndpointException(
            "AZURE_ENDPOINT key missing from environment variables"
        )
    return endpoint


def __del__(self):
    """
    Cleanup resources when the object is destroyed.
    """
    _executor.shutdown(wait=True)
