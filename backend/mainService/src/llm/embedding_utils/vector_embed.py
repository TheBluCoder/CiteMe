import os, re
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
from typing import List, Optional
from src.llm.Instructions import  *
from src.config.log_config import setup_logging
from src.custom_exceptions.api_exceptions import MissingApiKeyException,InvalidApiKeyException
from azure.core.exceptions import HttpResponseError
from azure.ai.inference.models import EmbeddingsResult
import logging


"""Currently using the pinecone embedding model. This will be replacing the Pinecone embedding model(Maybe)"""

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)


def vector_embed(text: List[str], model:Optional[str]=None) -> List[float]:
    """Embed a text using the Azure LLM."""

    embedding_model ="text-embedding-3-small"
    api_key = get_azure_api_key("AZURE_CREDENTIAL")

    client = EmbeddingsClient(
        endpoint= os.getenv("AZURE_MODELS_ENDPOINT",""),
        credential=AzureKeyCredential(api_key),
    )
    try:
        response:EmbeddingsResult = client.embed(
            input=text, 
            model=model or embedding_model,
            dimensions=1536
        )
        doc_embeds = [r.embedding for r in response.data] 
        return doc_embeds 

    except HttpResponseError as e:
        logger.exception(f"Error in establishing azure client: {e}")
        raise e 
        
def validate_azure_api_key(api_key: str) -> bool:
        """
        Validate Azure API key format.
        
        Args:
            api_key (str): The API key to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Note: This is a basic validation - adjust pattern based on your Azure key format
        """
        # Basic pattern for Azure API keys - adjust as needed
        pattern = r'^[a-zA-Z0-9]{32,}$'
        return bool(re.match(pattern, api_key))
    
def get_azure_api_key(key:str) -> str:
    """
    Retrieve and validate Azure API key from environment variables.
    
    Returns:
        str: Valid API key
        
    Raises:
        MissingApiKeyException: If API key is not set in environment
        InvalidApiKeyException: If API key format is invalid
    """
    api_key = os.getenv(key,"")

    if not api_key:
        raise MissingApiKeyException(
            "AZURE_PHI_CREDENTIAL key missing from environment variables"
        )

    if not validate_azure_api_key(api_key):
        raise InvalidApiKeyException(
            "AZURE_PHI_CREDENTIAL has invalid format. Please check your API key"
        )
    return api_key