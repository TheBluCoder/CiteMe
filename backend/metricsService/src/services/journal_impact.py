"""
Journal Impact Service Module

This module handles the assessment of journal impact by combining
data from multiple sources. It provides a unified score that reflects
a journal's quality and reputation in the academic community.

Key Functions:
- get_journal_impact: Main function that calculates journal impact score

Data Sources:
- DOAJ (Directory of Open Access Journals)
- ISSN API (International Standard Serial Number database)

Scoring Methodology:
- Primary source: DOAJ (70% weight)
- Fallback source: ISSN API (30% weight)
- Considers factors like peer review status, journal age, and registration
- Caps maximum score at 100
- Returns 0 if no data available

Features:
- Retry mechanism for failed API calls
- Rate limiting to prevent API abuse
- Comprehensive error handling and logging
- Fallback mechanism when primary source fails
"""

from typing import Optional
from datetime import datetime
import requests
from issn.issn_api import get_by_issn, parse_item
from ..utils.api_config import DOAJ_API, DOAJ_API_WITH_ISSN
from ..utils.api_utils import rate_limit
from ..utils.api_utils import retry_on_failure
from ..utils.logging_config import get_logger
import asyncio

logger = get_logger(__name__)

@retry_on_failure(max_retries=3, delay=1)
async def get_journal_impact(issn: Optional[str] = None, journal: Optional[str] = None) -> float:
    """Fetch journal impact factor using DOAJ as primary and ISSN API as fallback."""
    if not issn and not journal:
        return 0
    
    async def fetch_doaj():
        try:
            await rate_limit()
            url = DOAJ_API_WITH_ISSN.format(issn=issn) if issn else DOAJ_API.format(journal=journal)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("total", 0) > 0:
                    journal_data = data.get("results", [])[0]
                    score = 50  # Base score for being in DOAJ
                    
                    # Check peer review process
                    review_process = journal_data.get("bibjson", {}).get("editorial", {}).get("review_process", "")
                    if review_process and "peer review" in review_process:
                        score += 30
                        
                    # Check journal age
                    created_date = journal_data.get("created_date", "")
                    if created_date and len(created_date) >= 4:
                        try:
                            journal_year = int(created_date[:4])
                            if journal_year <= datetime.now().year - 10:
                                score += 20
                        except ValueError:
                            pass
                    return score
                else:
                    return 0
        except Exception as e:
            logger.exception(f"DOAJ API error: {e}")
            return None

    async def fetch_issn():
        if not issn:
            return None
        try:
            await rate_limit()
            issn_data = get_by_issn(issn)
            if not issn_data:
                return None
                
            issn_data = parse_item(issn_data)
            if not issn_data.get('data'):
                return None
                
            data = issn_data['data']
            score = 50  # Base score for valid ISSN
            
            # Additional scoring factors
            if data.get('CountryCode'):
                score += 5
            if data.get('resource', {}).get('URL'):
                score += 5
            if data.get('KeyTitle',''):
                score += 10
            if (record:=data.get('Record'), {}) and record.get('status','').lower() == 'register':
                score += 10
            if data.get('ISSN', {}).get('status') == 'Valid':
                score += 20
            else:
                score -= 20
                
            return score
        except Exception as e:
            logger.exception(f"ISSN API error")
            return None

    try:
        # Fetch both scores concurrently
        doaj_score, issn_score = await asyncio.gather(
            fetch_doaj(),
            fetch_issn()
        )

        if doaj_score is None and issn_score is None:
            raise Exception("Both DOAJ and ISSN API calls failed")
        
        # Calculate final score
        if doaj_score and issn_score:
            return min(100, (doaj_score * 0.6) + (issn_score * 0.4))
        elif doaj_score and doaj_score > 0:
            return min(100, doaj_score)
        elif issn_score and issn_score > 0:
            return min(100, issn_score)
        else:
            return 0
            
    except Exception as e:
        logger.exception(f"Error in get_journal_impact: {e}")
        raise Exception(str(e)) from e
