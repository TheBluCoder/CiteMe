from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.config.playwright_driver import PlaywrightDriver as ASD
from src.config.async_http_session import AsyncHTTPClient
from src.controllers.citation_controller import router as citation_router
from src.controllers.health_controller import router as health_router
from src.llm.Pinecone import PineconeOperations
from src.llm.chat_llm.Groq_llm import Summarize_llm
from src.llm.chat_llm.Azure_llm import Citation
from src.utils.index_operation import start
from dotenv import load_dotenv
from src.scraper.async_content_scraper import AsyncContentScraper
from fastapi.middleware.cors import CORSMiddleware
import nltk
from src.utils.concurrent_resources import cleanup_resources



origins = [
    "http://localhost:5173",  # Frontend running on localhost (React, Vue, etc.)
]


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
        start()
        yield
    # Exiting the async with block automatically calls __aexit__
    await app.state.playwright_driver.quit()
    await app.state.pc.cleanup()
    await AsyncHTTPClient.close_session()
    cleanup_resources()  # Clean up thread pool and other concurrent resources


app = FastAPI(lifespan=startup_event)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,  # Allow cookies & authentication headers
    allow_methods=["POST", "GET", "OPTIONS", "HEAD"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers with prefixes
app.include_router(health_router, tags=["Health"])
app.include_router(citation_router, prefix="/citation", tags=["Citation"])
