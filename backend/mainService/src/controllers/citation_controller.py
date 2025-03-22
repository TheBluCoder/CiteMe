from fastapi import APIRouter, Form, Request,status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from src.services.citation_service import CitationService
from src.config.log_config import setup_logging
import os
from src.custom_exceptions.llm_exceptions import SearchKeyGenerationError
from src.models.schema import CitationInput


filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)   

router = APIRouter()

@router.post("/get_citation",status_code=status.HTTP_200_OK)
async def get_citation(request: Request, payload: CitationInput) -> Dict[str, Any]:
    """Generate citations for the provided content.

    Args:
        request (Request): FastAPI request object containing app state
        title (str): Title of the content
        content (str): Text content to generate citations for
        format (str): Citation format (e.g., "APA", "MLA")

    Returns:
        Dict[str, Any]: Generated citations and metadata
    """
    citation_service = CitationService(PC=request.app.state.pc, summarize_llm=request.app.state.summarize_llm, citation_llm=request.app.state.citation_llm, scraper=request.app.state.async_content_scraper)
    try:
        title = payload.title
        content = payload.content
        citation_style = payload.citationStyle or "APA"
        
        # Handle each form type accordingly
        if payload.formType == "auto":
            result = await citation_service.process_citation(
                title, content, form_type=payload.formType, style=citation_style
            )
        elif payload.formType == "web":
            result = await citation_service.process_citation(
                title, content, form_type=payload.formType, style=citation_style,
                sources=payload.sources, supplement_urls=payload.supplementUrls
            )
        elif payload.formType == "source":
            result = await citation_service.process_citation(
                title, content, form_type=payload.formType, style=citation_style,
                sources=payload.sources
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"error": "Invalid formType"}
            )
            
        if not result:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Cannot generate citation at this time"}
            )
        return result
    except SearchKeyGenerationError as e:
        logger.error(f"Error in processing citation: {e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Title required to process citation at this time"}
        )
    except Exception as e:
        logger.exception(f"Error in processing citation: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error"}
        )

