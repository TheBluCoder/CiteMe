import azure.functions as func
import logging
from app import app as fastapi_app  # Import the FastAPI app from app.py 
from src.config.startup import startup_event
from src.llm.Pinecone import PineconeOperations
from src.llm.chat_llm.Groq_llm import Summarize_llm
from src.llm.chat_llm.Azure_llm import Citation
from src.scraper.async_content_scraper import AsyncContentScraper
from src.config.playwright_driver import PlaywrightDriver as ASD
from src.config.async_http_session import AsyncHTTPClient
from src.utils.concurrent_resources import cleanup_resources
import nltk
from dotenv import load_dotenv
import asyncio
from contextlib import asynccontextmanager

# Initialize NLTK data and environment variables (these are safe to do at module level)
load_dotenv()
nltk.download('punkt')
nltk.download('punkt_tab')

@asynccontextmanager
async def get_resources():
    # Initialize resources
    playwright_driver = await ASD.create()
    pc = await PineconeOperations.create()
    summarize_llm = Summarize_llm()
    citation_llm = Citation()
    
    try:
        async with AsyncContentScraper(playwright_driver=playwright_driver) as content_scraper:
            # Set up app state
            fastapi_app.state.playwright_driver = playwright_driver
            fastapi_app.state.pc = pc
            fastapi_app.state.summarize_llm = summarize_llm
            fastapi_app.state.citation_llm = citation_llm
            fastapi_app.state.async_content_scraper = content_scraper
            yield
    finally:
        # Ensure resources are cleaned up
        await asyncio.gather(
            playwright_driver.quit(),
            pc.cleanup(),
            return_exceptions=True
        )
        cleanup_resources()
        logging.info("Resources cleaned up successfully")

async def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        async with get_resources():
            response = await func.AsgiMiddleware(fastapi_app).handle_async(req)
            res.set(response)
            logging.info('Request processed successfully')
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        res.set(func.HttpResponse(
            "Internal server error",
            status_code=500
        ))
