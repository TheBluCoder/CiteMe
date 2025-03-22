from mixedbread_ai.client import AsyncMixedbreadAI,RerankingResponse
import os
from typing import Dict,List
from src.custom_exceptions.api_exceptions import MissingApiKeyException

model = "mixedbread-ai/mxbai-rerank-large-v1"
api_key = os.getenv("MIXBREAD_API_KEY","")
if not api_key:
    raise MissingApiKeyException("MIXBREAD_API_KEY is required to initialize MixedbreadAI.")

async def rerank(query: str, matches: List[Dict[str,str]], rank_fields:List=[],top_n:int=3) -> list[Dict]:
    mxbai = AsyncMixedbreadAI(api_key=api_key)
    
    reranked_docs:RerankingResponse = await mxbai.reranking(
        model=model,
        query=query,
        input=matches,
        return_input=True,
        top_k=top_n,
        rank_fields=rank_fields,
    )
    
    # reranked_result = [r.input for r in reranked_docs.data]
    return reranked_docs


def format_for_rerank(matches: List[Dict[str, str]]) -> list[Dict]:
    return [{
        "page_content": metadata.get('page_content'),
        "metadata": metadata
    } for match in matches if (metadata := match.get('metadata'))]


