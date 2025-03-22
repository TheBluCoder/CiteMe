from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Check the health status of the API.

    Returns:
        Dict[str, str]: Health status indicating the API is running
    """
    return {"status": "Healthy"}
