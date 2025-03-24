from typing import List, Dict, Any
import aiohttp
from src.config.log_config import setup_logging
import os
from functools import partial
import asyncio
from src.config.config import concurrency_config
from src.utils.concurrent_resources import credibility_executor, credibility_semaphore

filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)

def _calculate_source_score(metric: Dict, source: Dict, 
                          rerank_weight: float, credibility_weight: float) -> tuple[float, Dict]:
    """
    Calculate weighted score for a single source in a separate thread.
    Uses semaphore to limit concurrent calculations.
    
    Args:
        metric (Dict): Credibility metric for the source
        source (Dict): Source with rerank score
        rerank_weight (float): Weight for rerank score
        credibility_weight (float): Weight for credibility score
    
    Returns:
        tuple[float, Dict]: Tuple of (weighted_score, updated_metric)
    """
    with credibility_semaphore:
        if metric["status"] != "success":
            return 0.00, metric
        
        credibility_score = metric["data"]["credibility_score"]
        rerank_score = source["rerank_score"]
        
        # Normalize rerank score to 0-1 range
        normalized_rerank = min(max(rerank_score, 0), 1)
        
        # Calculate weighted score and normalize to 0-100 range
        weighted_score = round((normalized_rerank * rerank_weight + 
                              credibility_score * credibility_weight) * 100, 2)
        
        # Update the credibility score in the metric data
        metric["data"]["credibility_score"] = weighted_score
        return weighted_score, metric

async def get_credibility_metrics(sources: List[Dict]) -> List[Dict]:
    """
    Call the credibility API to get metrics for sources.
    Uses timeout handling for better reliability.
    """
    credibility_metrics_api = os.getenv('CREDIBILITY_API_URL','')
    if not credibility_metrics_api:
        logger.error("CREDIBILITY_API_URL is not set")
        return []
    
    # Configure timeout
    timeout = aiohttp.ClientTimeout(total=10)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
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
    except asyncio.TimeoutError:
        logger.error("Credibility API request timed out")
        return []
    except Exception:
        logger.exception("Error calling credibility API")
        return []

async def calculate_overall_score(credibility_metrics: List[Dict], sources_with_scores: List[Dict],
                                rerank_weight: float = 0.6, credibility_weight: float = 0.4) -> Dict[str, Any]:
    """
    Calculate weighted scores for each source and overall mean score using parallel processing.
    Uses configured thread pool and semaphore for concurrent calculations.
    
    Args:
        credibility_metrics (List[Dict]): List of credibility metrics for each source
        sources_with_scores (List[Dict]): List of sources with their rerank scores
        rerank_weight (float): Weight for rerank score (default 0.6)
        credibility_weight (float): Weight for credibility score (default 0.4)
    
    Returns:
        Dict[str, Any]: Dictionary containing source scores and overall mean score
    """
    if not credibility_metrics or not sources_with_scores:
        return {"overall_score": 0.00, "source_scores": []}

    try:
        calculate_score = partial(_calculate_source_score, 
                                rerank_weight=rerank_weight, 
                                credibility_weight=credibility_weight)
        
        # Process in batches using configured size
        source_scores = []
        for i in range(0, len(sources_with_scores), concurrency_config.CREDIBILITY_BATCH_SIZE):
            batch_metrics = credibility_metrics[i:i + concurrency_config.CREDIBILITY_BATCH_SIZE]
            batch_sources = sources_with_scores[i:i + concurrency_config.CREDIBILITY_BATCH_SIZE]
            
            # Calculate batch scores
            batch_results = list(credibility_executor.map(
                lambda x: calculate_score(x[0], x[1]), 
                zip(batch_metrics, batch_sources)
            ))
            
            scores, updated_metrics = zip(*batch_results) if batch_results else ([], [])
            source_scores.extend(scores)
            credibility_metrics[i:i + concurrency_config.CREDIBILITY_BATCH_SIZE] = updated_metrics
        
        overall_mean = round(sum(source_scores) / len(source_scores), 2) if source_scores else 0.00
        
        return {
            "overall_score": overall_mean,
            "source_scores": source_scores
        }
        
    except Exception as e:
        logger.exception(f"Error in score calculation: {str(e)}")
        return {"overall_score": 0.00, "source_scores": []}
