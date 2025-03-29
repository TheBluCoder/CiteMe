import azure.functions as func
import logging
from app import app as fastapi_app  # Import FastAPI app
from src.config.playwright_driver import PlaywrightDriver as ASD
from src.llm.Pinecone import PineconeOperations
from src.llm.chat_llm.Groq_llm import Summarize_llm
from src.llm.chat_llm.Azure_llm import Citation
from src.scraper.async_content_scraper import AsyncContentScraper
from dotenv import load_dotenv
import nltk
import asyncio

# Load environment variables and NLTK data
load_dotenv()
nltk.download('punkt')
nltk.download('punkt_tab')

# Global variables for resources
playwright_driver = None
pc = None
summarize_llm = None
citation_llm = None
async_content_scraper = None
resource_lock = asyncio.Lock()  # Prevent race conditions

async def initialize_resources():
    """
    Initializes global resources only once and prevents multiple concurrent initializations.
    """
    global playwright_driver, pc, summarize_llm, citation_llm, async_content_scraper

    async with resource_lock:  # Prevent multiple requests from initializing Playwright at the same time
        if playwright_driver is None:
            logging.info("Initializing Playwright and other global resources...")

            playwright_driver = await ASD.create()
            pc = await PineconeOperations.create()
            summarize_llm = Summarize_llm()
            citation_llm = Citation()
            async_content_scraper = await AsyncContentScraper(playwright_driver).__aenter__()

            # Set FastAPI state
            fastapi_app.state.playwright_driver = playwright_driver
            fastapi_app.state.pc = pc
            fastapi_app.state.summarize_llm = summarize_llm
            fastapi_app.state.citation_llm = citation_llm
            fastapi_app.state.async_content_scraper = async_content_scraper

            logging.info("Global resources initialized.")

async def main(req: func.HttpRequest, res: func.Out[func.HttpResponse]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        if playwright_driver is None:
            await initialize_resources()  # Make sure Playwright is running

        response = await func.AsgiMiddleware(fastapi_app).handle_async(req)
        res.set(response)
        logging.info('Request processed successfully')

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        res.set(func.HttpResponse("Internal server error", status_code=500))
