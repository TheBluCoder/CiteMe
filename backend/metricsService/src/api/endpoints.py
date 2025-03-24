"""
API Endpoints Module

This module contains all the API endpoints for the Citation Credibility Service.
It handles both single and batch requests for credibility analysis, with support
for detailed results and controlled concurrency.

Endpoints:
- POST /credibility: Calculate credibility score for a single source
- POST /credibility/batch: Calculate credibility scores for multiple sources
- GET /health: Health check endpoint

Features:
- Type validation using Pydantic models
- Detailed and summary response formats
- Controlled concurrency for batch processing
- Configurable timeout per request
- Comprehensive error handling

Implementation Details:
- Uses FastAPI's APIRouter for endpoint organization
- Leverages asyncio for concurrent processing
- Implements semaphore-based concurrency control
- Provides timeout protection for individual requests
- Logs all errors for debugging and monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import asyncio
from src.models.schemas import CredibilityRequest, BatchCredibilityRequest
from src.services.credibility_service import calculate_credibility
from src.utils.logging_config import get_logger
from src.utils.api_config import MAX_CONCURRENT_WORKERS, DEFAULT_CONCURRENT_WORKERS

logger = get_logger(__name__)
router = APIRouter()

@router.post("/credibility", response_model=Dict[str, Any])
async def compute_credibility(
    request: CredibilityRequest,
    detailed: bool = Query(default=False, description="Return detailed results")
):
    """Calculate credibility score for a single source"""
    try:
        result = await calculate_credibility(request)
        # Store the total score before modifying the result
        total_score = result.get("total_score", 0)
        
        if detailed:
            # Don't pop the total_score, just create a new dict without it for components
            components = {k: v for k, v in result.items() if k != "total_score"}
            return {
                "status": "success", 
                "data": {
                    "credibility_score": total_score,
                    "component": components,
                    "url": request.domain,
                    "title": request.title,
                    "type": request.type
                }
            }
        else:
            return {
                "status": "success",
                "data": {
                    "credibility_score": total_score,
                    "url": request.domain,
                    "title": request.title,
                    "type": request.type
                }
            }
    except Exception as e:
        logger.exception(f"Error calculating credibility: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error calculating credibility score"
        )

@router.post("/credibility/batch", response_model=List[Dict[str, Any]])
async def compute_credibility_batch(
    requests: BatchCredibilityRequest,
    detail: bool = Query(default=False, description="Return detailed results"),
    max_concurrent: int = Query(default=10, description="Maximum concurrent requests"),
    timeout: float = Query(default=30.0, description="Timeout per request in seconds")
):
    """Calculate credibility scores for multiple sources with controlled concurrency"""
    try:
        logger.info(f"Received batch of {len(requests.sources)} requests")
        logger.info(f"requests: {requests}")
        
        # Create semaphore for controlled concurrency
        semaphore = asyncio.Semaphore(min(max(max_concurrent, DEFAULT_CONCURRENT_WORKERS), MAX_CONCURRENT_WORKERS))
        
        async def process_request_with_semaphore(req):
            async with semaphore:
                try:
                    async with asyncio.timeout(timeout*3):
                        result = await calculate_credibility(req)
                        if detail:
                            return {
                                "status": "success",
                                "data": result
                            }
                        else:
                            return {
                                "status": "success",
                                "data": {
                                    "credibility_score": result["total_score"],
                                    "url": req.link,
                                    "title": req.title,
                                    "type": req.type
                                }
                            }
                except asyncio.TimeoutError:
                    return {
                        "status": "error",
                        "data": {
                            "credibility_score": 0,
                            "url": req.link,
                            "title": req.title,
                            "type": req.type,
                            "error": "Request timed out"
                        }
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "data": {
                            "credibility_score": 0,
                            "url": req.link,
                            "title": req.title,
                            "type": req.type,
                            "error": str(e)
                        }
                    }

        # Process all requests concurrently
        results = await asyncio.gather(
            *(process_request_with_semaphore(req) for req in requests.sources)
        )
        
        logger.info(f"Completed batch processing of {len(results)} requests")
        return results

    except Exception as e:
        logger.exception(f"Error processing batch request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing batch request"
        )

@router.get("/health")
async def health_check():
    #"""API health check endpoint"""
    return {"status": "healthy"}
