"""
Author Reputation Service Module

This module handles the calculation of author reputation scores by aggregating data
from multiple academic sources. It provides a unified interface for assessing
author credibility based on their publication history and impact.

Key Functions:
- get_authorship_reputation: Main function that calculates reputation score
- get_openalex_author_reputation: Fetches data from OpenAlex
- get_semantic_scholar_author_reputation: Fetches data from Semantic Scholar
- get_google_scholar_author_reputation: Fetches data from Google Scholar

Data Sources:
- ORCID API
- OpenAlex API
- Semantic Scholar API
- Google Scholar (via scholarly package)

Scoring Methodology:
- Combines h-index and publication count from multiple sources
- Uses weighted average favoring h-index (70% weight)
- Ensures minimum score for any author with an ID or name
- Takes maximum values across sources for robustness

Features:
- Asynchronous API calls for better performance
- Rate limiting to prevent API abuse
- Comprehensive error handling and logging
- Fallback mechanism when sources fail
"""

import asyncio
import requests
from typing import Optional, List
from scholarly import scholarly
from ..utils.api_config import (
    ORCID_API,
    SEMANTIC_SCHOLAR_AUTHOR_SEARCH_API,
    OPEN_ALEX_AUTHOR_API,
    DEFAULT_TIMEOUT
)
from ..utils.api_utils import rate_limit
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

async def get_authorship_reputation(author_id: Optional[str] = None, author_name: Optional[str | List[str]] = None) -> float:
    """
    Fetch author reputation from ORCID (if available) and concurrently from OpenAlex, 
    Semantic Scholar, and Google Scholar using the author's name. If one source fails, 
    the others serve as fallback. When all are available, combine their outputs by averaging 
    h-index values and taking the maximum publication count.
    """
    if not author_id and not author_name:
        return 0

    h_index_values = []
    pub_count_values = []

    # ORCID lookup if available
    if author_id:
        await rate_limit()
        try:
            orcid_response = requests.get(
                f"{ORCID_API}{author_id}/works",
                headers={"Accept": "application/json"},
                timeout=DEFAULT_TIMEOUT
            )
            if orcid_response.status_code == 200:
                orcid_data = orcid_response.json()
                works = orcid_data.get("group", [])
                pub_count_values.append(len(works))
                # Add a base score for having an ORCID
                h_index_values.append(20)
        except Exception as e:
            logger.exception(f"ORCID API error: {e}")

    # Concurrent calls for OpenAlex, Semantic Scholar, and Google Scholar
    if author_name and isinstance(author_name, list):
        author_name = author_name[0] # Use the first name in the list for now
    if author_name:
        tasks = [
            asyncio.create_task(get_openalex_author_reputation(author_name)),
            asyncio.create_task(get_semantic_scholar_author_reputation(author_name)),
            asyncio.create_task(get_google_scholar_author_reputation(author_name))
        ]
        results = await asyncio.gather(*tasks)
        error_count = 0
        for result in results:
            if isinstance(result, Exception):
                logger.exception(f"Error in author reputation fetch: {result}")
                error_count += 1
                if error_count == 3:
                    raise Exception("Multiple errors in author reputation fetch")
            if result:
                if result.get("h_index", 0):
                    h_index_values.append(result["h_index"])
                if result.get("pub_count", 0):
                    pub_count_values.append(result["pub_count"])

    # Combine the results: take the highest h-index and publication count values
    combined_h_index = max(h_index_values) if h_index_values else 0
    combined_pub_count = max(pub_count_values) if pub_count_values else 0

    # Compute scores with more generous scaling
    h_index_score = min(100, combined_h_index * 10)  # h-index of 10+ yields max score
    pub_count_score = min(100, combined_pub_count * 1)  # 100+ publications yields max score
    
    # Weighted average favoring h-index
    final_reputation = (h_index_score * 0.7) + (pub_count_score * 0.3)
    
    # Ensure minimum score of 20 for any author with an ID or name
    if author_id or author_name:
        final_reputation = max(20, final_reputation)
        
    return final_reputation

async def get_openalex_author_reputation(author_name: str):
    """Fetch author reputation from OpenAlex using the authors endpoint."""
    await rate_limit()
    try:
        response = requests.get(f"{OPEN_ALEX_AUTHOR_API}?search={author_name}", timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                first_author = data["results"][0]
                h_index = first_author.get("h_index", 0)
                works_count = first_author.get("works_count", 0)
                return {"h_index": h_index, "pub_count": works_count}
    except Exception as e:
        logger.exception(f"OpenAlex API error: {e}")
        raise Exception(str(e)) from e

    return None

async def get_semantic_scholar_author_reputation(author_name: str):
    """Fetch author reputation from Semantic Scholar using the author search endpoint."""
    await rate_limit()
    try:
        params = {"query": author_name, "fields": "hIndex,paperCount", "limit": 1}
        response = requests.get(SEMANTIC_SCHOLAR_AUTHOR_SEARCH_API, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                first_author = data["data"][0]
                h_index = first_author.get("hIndex", 0)
                paper_count = first_author.get("paperCount", 0)
                return {"h_index": h_index, "pub_count": paper_count}
    except Exception as e:
        logger.exception(f"Semantic Scholar API error: {e}")
        raise Exception(str(e)) from e

    return None

async def get_google_scholar_author_reputation(author_name: str):
    """Fetch author reputation from Google Scholar using the scholarly package."""
    try:
        # Wrap the synchronous scholarly call in asyncio.to_thread for non-blocking execution
        result = await asyncio.to_thread(lambda: next(scholarly.search_author(author_name), None))
        if result:
            author_data = await asyncio.to_thread(lambda: scholarly.fill(result))
            h_index = author_data.get("hindex", 0)  # scholarly returns 'hindex' in lowercase
            pub_count = len(author_data.get("publications", []))
            return {"h_index": h_index, "pub_count": pub_count}
        else:
            return None
    except Exception as e:
        logger.exception(f"Google Scholar error: {e}")
        raise Exception(str(e)) from e
