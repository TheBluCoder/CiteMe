"""
Citation Credibility Service API

This is the main entry point for the Citation Credibility Service API, which provides
endpoints for analyzing and scoring the credibility of academic citations and sources.

Key Features:
- RESTful API endpoints for credibility analysis
- CORS support for cross-origin requests
- Versioned API endpoints (/api/v1)
- Health check endpoint
- Configurable through environment variables

Configuration:
- Environment variables are loaded from .env file
- CORS is configured to allow all origins
- Logging is configured through src.utils.logging_config

Example Usage:
    $ uvicorn src.main:app --reload

Deployment:
    The service can be deployed using any ASGI server (e.g. uvicorn, hypercorn)
    and is configured to run on port 8000 by default.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.logging_config import get_logger
from src.api.endpoints import router as api_router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get logger
logger = get_logger(__name__)


app = FastAPI(
    title="Citation Credibility Service",
    description="API for calculating credibility scores of academic sources",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include versioned routers
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Citation Credibility Service is running"}

# Uncomment to run via uvicorn directly
# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
