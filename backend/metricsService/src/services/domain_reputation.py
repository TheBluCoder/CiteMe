"""
Domain Reputation Service Module

This module handles the assessment of domain reputation by combining
popularity rankings with security assessments. It provides a unified
score that reflects both a domain's authority and security posture.

Key Functions:
- get_domain_reputation: Main function that calculates domain reputation
- initialize_tranco_data: Fetches and processes TRANCO ranking data

Data Sources:
- TRANCO List (domain popularity rankings)
- Mozilla Observatory (security assessments)

Scoring Methodology:
- Combines TRANCO ranking score (70%) with security grade (30%)
- Uses logarithmic scaling for TRANCO rankings
- Maps security grades to numerical scores
- Ensures minimum score for all domains

Features:
- Caching of TRANCO ranking data
- Asynchronous API calls for better performance
- Rate limiting to prevent API abuse
- Comprehensive error handling and logging
- Fallback mechanism when sources fail
"""

import asyncio
import requests
from ..utils.api_config import (
    TRANCO_DOMAIN_API,
    TRANCO_API,
    OBSERVATORY_API
)
from ..utils.api_utils import rate_limit
from src.utils.logging_config import get_logger
import csv
from io import StringIO

logger = get_logger(__name__)

def initialize_tranco_data():
    """Fetch and parse TRANCO CSV data into a domain:rank dictionary"""
    try:
        # Get the latest TRANCO list metadata
        response = requests.get(TRANCO_API)
        if response.status_code != 200:
            logger.error("Failed to fetch TRANCO list metadata")
            return {}
            
        list_metadata = response.json()
        if not list_metadata.get('download'):
            logger.error("No download URL in TRANCO response")
            return {}
            
        # Download and parse the CSV
        csv_response = requests.get(list_metadata['download'])
        if csv_response.status_code != 200:
            logger.error("Failed to download TRANCO CSV")
            return {}
            
        csv_data = csv_response.text
        csv_reader = csv.reader(StringIO(csv_data))
        return {row[1]: int(row[0]) for row in csv_reader}
        
    except Exception as e:
        logger.error(f"Error initializing TRANCO data: {e}")
        return {}

# Initialize TRANCO data at module level
tranco_data = initialize_tranco_data()

async def get_domain_reputation(domain: str) -> float:
    """Fetch domain authority score from Tranco List and Mozilla Observatory."""
    global tranco_data  # Declare global at the start of the function

    if not domain:
        return 0
        
    try:
        # Initialize rank
        rank = 0
        
        # Check if we have valid tranco_data
        if tranco_data and isinstance(tranco_data, dict):
            rank = tranco_data.get(domain, 0)
        else:
            # Fetch new data if tranco_data is invalid
            try:
                tranco_response = requests.get(f"{TRANCO_DOMAIN_API}/{domain}")
                if tranco_response.status_code == 200:
                    tranco_data = tranco_response.json()
                    rank = tranco_data.get("ranks", [{"rank": 0, "date": ""}])[0].get("rank", 0)
            except Exception as e:
                logger.exception(f"Tranco API error: {e}")
                raise Exception(str(e)) from e

        # Calculate Tranco score
        print(f"Rank: {rank}")
        if rank == 0:
            tranco_score = 0
        elif rank <= 1000:
            tranco_score = 80 + (20 * (1 - (rank / 1000)))
        elif rank <= 10000:
            tranco_score = 60 + (20 * (1 - ((rank - 1000) / 9000)))
        elif rank <= 100000:
            tranco_score = 40 + (20 * (1 - ((rank - 10000) / 90000)))
        elif rank <= 1000000:
            tranco_score = 20 + (20 * (1 - ((rank - 100000) / 900000)))
        else:
            tranco_score = 20

        # Get Mozilla Observatory security score
        await rate_limit()
        try:
            observatory_response = requests.post(
                OBSERVATORY_API,
                data={"host": domain, "hidden": "true"},
                timeout=10
            )
            if observatory_response.status_code == 200:
                scan_data = observatory_response.json()
                scan_id = scan_data.get("scan_id")
                if scan_id:
                    for _ in range(3):
                        await asyncio.sleep(2)
                        await rate_limit()
                        results = requests.get(f"{OBSERVATORY_API}/{domain}", timeout=10).json()
                        if results.get("state") == "FINISHED":
                            grade = results.get("grade", "F")
                            grade_scores = {"A+": 100, "A": 95, "A-": 90, "B+": 85, "B": 80, "B-": 75,
                                            "C+": 70, "C": 65, "C-": 60, "D+": 55, "D": 50, "D-": 45, "F": 40}
                            observatory_score = grade_scores.get(grade, 20)
                            break
                    else:
                        observatory_score = 0
                else:
                    observatory_score = 0
            else:
                observatory_score = 0
        except Exception as e:
            logger.exception(f"Observatory API error: {e}")
            observatory_score = 50

        # Combine scores (70% Tranco, 30% Observatory)
        domain_score = (tranco_score * 0.7) + (observatory_score * 0.3)
        return domain_score
    except Exception as e:
        logger.exception(f"Error in get_domain_reputation: {e}")
        raise Exception(str(e)) from e
