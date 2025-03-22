from typing import List, Dict
import aiohttp
from src.config.log_config import setup_logging
import os

filename= os.path.basename(__file__)
logger = setup_logging(filename=filename)

async def get_credibility_metrics(sources: List[Dict]) -> List[Dict]:
    """
    Call the credibility API to get metrics for sources.
    
    Args:
        sources (List[Dict]): List of source metadata
        
    Returns:
        List[Dict]: Credibility metrics for each source
    """
    credibility_metrics_api = 'http://localhost:9050/api/v1/credibility/batch'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                credibility_metrics_api,
                json={'sources': sources},
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Credibility API error: {response.status}")
                    return []
    except Exception as e:
        logger.exception(f"Error calling credibility API")
        return []


def calculate_overall_score(credibility_metrics: List[Dict]) -> float:
    """
    Calculate the weighted average of credibility scores.
    
    Args:
        credibility_metrics (List[Dict]): List of credibility metric responses
        
    Returns:
        float: Weighted average score rounded to 2 decimal places
    """
    try:
        # Filter successful responses and extract scores
        valid_scores = [
            item["data"]["credibility_score"] 
            for item in credibility_metrics 
            if item["status"] == "success" and "data" in item
        ]
        
        if not valid_scores:
            return 0.0
            
        # Calculate simple average (can be modified to use weights if needed)
        average_score = sum(valid_scores) / len(valid_scores)
        
        return round(average_score, 2)
        
    except Exception as e:
        logger.exception(f"Error calculating overall score")
        return 0.0

