"""
Recency Score Service Module

This module handles the calculation of recency scores for academic publications.
Newer publications receive higher scores, reflecting their timeliness and relevance.

Key Functions:
- calculate_recency_score: Main function that computes recency score

Scoring Methodology:
- Scores based on years since publication:
  - 0-1 years: 100
  - 1-2 years: 90
  - 2-3 years: 80
  - 3-5 years: 50
  - 5-7 years: 40
  - 7-10 years: 10
  - 10+ years: 0
- Handles both string and integer date formats
- Extracts year from strings using regex

Features:
- Comprehensive error handling and logging
- Default scores for invalid dates
- Flexible date parsing
"""

import re
from datetime import datetime
from typing import Union
from ..utils.logging_config import get_logger
logger = get_logger(__name__)
async def calculate_recency_score(publication_date: Union[str, int]) -> float:
    """Calculate recency score - newer publications get higher scores."""
    if not publication_date:
        logger.info("No publication date provided")
        return 0
    try:
        current_year = datetime.now().year
        year = None
        if isinstance(publication_date, int):
            year = publication_date
        elif isinstance(publication_date, str):
            year_match = re.search(r'(\d{4})', publication_date)
            if year_match:
                year = int(year_match.group(1))
        if not year or year > current_year:
            raise ValueError("Invalid publication date")
        years_ago = current_year - year
        if years_ago <= 1:
            return 100
        elif years_ago <= 2:
            return 90
        elif years_ago <= 3:
            return 80
        elif years_ago <= 5:
            return 50
        elif years_ago <= 7:
            return 40
        elif years_ago <= 10:
            return 10
        else:
            return 0
    except ValueError as e:
        logger.exception(f"Invalid publication date: {e}")
        return 0
    except Exception as e:
        logger.exception(f"Error in calculate_recency_score: {e}")
        return 50
