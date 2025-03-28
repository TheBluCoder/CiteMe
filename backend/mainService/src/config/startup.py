from src.llm.Pinecone import PineconeOperations
from src.llm.chat_llm.Groq_llm import Summarize_llm
from src.llm.chat_llm.Azure_llm import Citation
from dotenv import load_dotenv
from src.scraper.async_content_scraper import AsyncContentScraper
import nltk
from src.utils.concurrent_resources import cleanup_resources
from contextlib import asynccontextmanager
from src.config.playwright_driver import PlaywrightDriver as ASD
from src.config.async_http_session import AsyncHTTPClient
from fastapi import FastAPI 

@asynccontextmanager
async def startup_event(app: FastAPI):
    load_dotenv()
    nltk.download('punkt')
    nltk.download('punkt_tab')

    app.state.playwright_driver = await ASD.create()
    app.state.pc = await PineconeOperations.create()
    app.state.summarize_llm = Summarize_llm()
    app.state.citation_llm = Citation()
   # Initialize the async content scraper using its async context manager
    async with AsyncContentScraper(playwright_driver=app.state.playwright_driver) as content_scraper:
        app.state.async_content_scraper = content_scraper
        yield
    # Exiting the async with block automatically calls __aexit__
    await app.state.playwright_driver.quit()
    await app.state.pc.cleanup()
    await AsyncHTTPClient.close_session()
    cleanup_resources()  # Clean up thread pool and other concurrent resources
