"""
Credibility Service Module

This module contains the core business logic for calculating credibility scores
of academic sources. It combines multiple factors into a weighted score and
provides caching for improved performance.

Key Functions:
- calculate_credibility: Main function that computes credibility score
- get_credibility_level: Converts numeric score to qualitative level

Scoring Methodology:
The credibility score is calculated as a weighted sum of these factors:
- Domain Reputation (20%)
- Citation Count (20%)
- Journal Impact (25%)
- Recency (10%)
- Authorship Reputation (25%)

Features:
- Asynchronous execution of scoring components
- Caching of results to improve performance
- Comprehensive error handling and logging
- Weighted scoring system
- Normalization of final score

Implementation Details:
- Uses asyncio for concurrent processing of scoring components
- Implements caching using src.utils.cache
- Provides detailed logging through src.utils.logging_config
"""

import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from src.models.schemas import CredibilityRequest
from src.services.domain_reputation import get_domain_reputation
from src.services.citation_data import get_citation_data
from src.services.journal_impact import get_journal_impact
from src.services.recency_score import calculate_recency_score
from src.services.author_reputation import get_authorship_reputation
from src.utils.cache import get_cache, set_cache
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

async def calculate_credibility(request: CredibilityRequest) -> Dict[str, Any]:
    """Calculate credibility score based on multiple factors"""
    try:
        # Check cache first
        cache_key = f"credibility:{request.model_dump()}"
        cached_result = await get_cache(cache_key)
        if cached_result:
            return cached_result

        # Extract and validate parameters
        domain = request.domain or (lambda u: (not u.hostname.startswith("www.") and u.hostname) or u.hostname[4:])(urlparse(request.link))
        doi = request.citation_doi
        issn = request.issn
        journal = request.journal
        publication_date = request.publication_date
        author_id = request.author_id
        author_name = request.author_name

        # Create and execute tasks concurrently
        tasks = [
            ('domain', get_domain_reputation(domain), 0.20) if domain else None,
            ('citation', get_citation_data(doi), 0.20) if doi else None,
            ('journal', get_journal_impact(issn, journal), 0.25) if issn else None,
            ('recency', calculate_recency_score(publication_date), 0.10),
            ('author', get_authorship_reputation(author_id, author_name), 0.25) if (author_id or author_name) else None
        ]

        # Filter out None tasks
        valid_tasks = [task for task in tasks if task is not None]
        results = {}
        total_score = 0
        total_weight = 0

        if valid_tasks:
            async with asyncio.TaskGroup() as tg:
                # Create all tasks concurrently
                running_tasks = {
                    key: tg.create_task(coro) for key, coro, _ in valid_tasks
                }

            # Process results
            for key, _, weight in valid_tasks:
                try:
                    score = await running_tasks[key]
                    if score is not None:
                        results[key] = score
                        total_score += score * weight
                        total_weight += weight
                except Exception as e:
                    logger.warning(f"Error processing {key}: {str(e)}")
                    results[key] = 0
        
        # Prepare result
        result = {
            "total_score": round(total_score, 2),
            "domain_reputation": round(results.get('domain', 0),2),
            "citation_count": results.get('citation', 0),
            "journal_impact": results.get('journal', 0),
            "recency": results.get('recency', 0),
            "authorship_reputation": results.get('author', 0)
        }

        # Debug logging
        logger.info(f"Final result before caching: {result}")
        logger.info(f"Total score calculation: {total_score} (total_weight: {total_weight})")

        # Cache the result
        await set_cache(cache_key, result)
        
        return result
    except Exception as e:
        logger.error(f"Error calculating credibility: {str(e)}")
        raise

def get_credibility_level(score: float) -> str:
    """Get credibility level based on score"""
    if score > 85:
        return "Very High"
    elif score >= 75:
        return "High"
    elif score >= 60:
        return "Moderate"
    elif score >= 50:
        return "Low"
    else:
        return "Very Low"
