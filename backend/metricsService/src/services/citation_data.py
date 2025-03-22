"""
Citation Data Service Module

This module handles the retrieval and processing of citation data for academic
publications. It aggregates citation counts from multiple sources to provide
a more comprehensive assessment of a publication's impact.

Key Functions:
- get_citation_data: Main function that fetches and processes citation data

Data Sources:
- Crossref API
- OpenCitations API

Scoring Methodology:
- Takes maximum citation count from available sources
- Applies logarithmic scaling to normalize scores
- Caps maximum score at 100
- Returns 0 if no citations found

Features:
- Retry mechanism for failed API calls
- Rate limiting to prevent API abuse
- Comprehensive error handling and logging
- Fallback mechanism when sources fail
"""

import requests
from typing import Optional
from ..utils.api_config import CROSSREF_API, OPEN_CITATIONS_API
from ..utils.api_utils import rate_limit
from ..utils.api_utils import retry_on_failure
from ..utils.logging_config import get_logger
import asyncio

logger = get_logger(__name__)


@retry_on_failure(max_retries=3, delay=1)
async def get_citation_data(doi: str) -> float:
    """Fetch citation count from Crossref and OpenCitations concurrently."""
    if not doi:
        return 0
    
    async def fetch_crossref():
        try:
            await rate_limit()
            response = requests.get(f"{CROSSREF_API}/{doi}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("is-referenced-by-count", 0)
        except Exception as e:
            logger.warning(f"Crossref API error: {e}")
        return 0

    async def fetch_opencitations():
        try:
            await rate_limit()
            response = requests.get(
                f"{OPEN_CITATIONS_API}citations/{doi}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return len(data)
        except Exception as e:
            logger.warning(f"OpenCitations API error: {e}")
        return 0

    try:
        # Run both API calls concurrently
        crossref_count, opencitations_count = await asyncio.gather(
            fetch_crossref(),
            fetch_opencitations()
        )

        citation_count = max(crossref_count, opencitations_count)
        if citation_count == 0:
            return 0
            
        # Optimized scoring calculation
        if citation_count < 10:
            return citation_count * 2
        elif citation_count < 100:
            return min(100, 20 + citation_count)
        elif citation_count < 1000:
            return min(100, 50 + (citation_count // 10))
        else:
            return 100
    except Exception as e:
        logger.error(f"Error in get_citation_data: {e}")
        raise
