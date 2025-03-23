"""
Content Scraper Module

This module provides the main implementation for scraping and processing content
from various sources. It handles both PDF downloads and content extraction,
providing a unified interface for different types of content.

The AsyncContentScraper class provides:
- PDF download management
- Content extraction and processing
- Site-specific scraper integration
- Error handling and logging

Classes:
    AsyncContentScraper: Main class for handling content scraping operations
"""

from urllib3.util import parse_url
from typing import Dict, Optional, Union
import os
from src.scraper.site_specific.async_ibm_scraper import IBMScraper
from src.scraper.site_specific.async_frontier_scraper import FrontierScraper
from src.scraper.site_specific.async_generic_scraper import GenericScraper
from src.scraper.async_base_scraper import BasePlaywrightScraper
from src.utils.web_utils import WebUtils
from src.utils.file_utils import FileUtils
from src.config.playwright_driver import PlaywrightDriver
import asyncio
from datetime import datetime
from playwright.async_api import Browser, BrowserContext
from src.config.log_config import setup_logging
from datetime import timezone as tz


log_filename = os.path.basename(__file__)
logger = setup_logging(filename=log_filename)

"""
Citation Content Scraper Module

This module provides asynchronous functionality for scraping citation content from various sources.
It handles concurrent requests and content extraction efficiently using asyncio.

Classes:
    AsyncContentScraper: Main class for handling asynchronous content scraping operations
"""


class AsyncContentScraper:
    """
    A class to handle asynchronous content scraping operations.

    This class provides methods to concurrently fetch and process content from multiple URLs,
    optimizing performance through asynchronous operations.

    Attributes:
        session (aiohttp.ClientSession): Async session for making HTTP requests
        timeout (int): Maximum time in seconds to wait for a response
        max_retries (int): Maximum number of retry attempts for failed requests

    Methods:
        get_content(url: str) -> str:
            Asynchronously retrieves content from a given URL

        process_urls(urls: List[str]) -> List[Dict]:
            Processes multiple URLs concurrently and returns their content
    """

    def __init__(self, playwright_driver: PlaywrightDriver = None):
        """
        Initialize the AsyncContentScraper with an optional playwright driver.

        This constructor sets up the initial state of the scraper, including browser and context
        attributes that will be initialized when the scraper is used as a context manager.

        Args:
            playwright_driver (PlaywrightDriver, optional): Instance of PlaywrightDriver for browser automation.
                If not provided, a new instance will be created when entering the context manager.

        Attributes:
            scraper_driver (PlaywrightDriver): The playwright driver instance
            _browser (Browser): Playwright browser instance, initialized in context manager
            _context (BrowserContext): Playwright browser context, initialized in context manager
            current_download_path (str): Path where downloads are currently being stored
        """

        self.scraper_driver: PlaywrightDriver = playwright_driver
        self._browser: Browser = None
        self._context: BrowserContext = None
        self.current_download_path: str = None

    async def __aenter__(self):
        self.scraper_driver = self.scraper_driver or await PlaywrightDriver.create()
        self._browser = await self.scraper_driver.get_browser()
        self._context = await self.scraper_driver.get_context()
        await self._setup_scrapers()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._context:
                self.scraper_driver.quit()
                await self._context.close()
        except Exception as e:
            # Log the exception even if it occurred during cleanup
            logger.critical(f"Exception while closing context: {e}",exc_info=True)

            if exc_type:
                logger.error("Exception in context manager", exc_info=(exc_type, exc_val, exc_tb))

    async def _setup_scrapers(self):
        self.scrapers: Dict[BasePlaywrightScraper] = {
            "research.ibm.com": IBMScraper(
                self._context, self.scraper_driver), "www.frontiersin.org": FrontierScraper(
                self._context, self.scraper_driver), "default": GenericScraper(
                self._context, self.scraper_driver)}

    async def get_pdf(self,
                      target_url: str,
                      storage_path: Optional[str] = None) -> tuple[str,
                                                                   Optional[str],
                                                                   str] | bool:
        """Download a PDF from the specified URL.

        Args:
            target_url (str): The URL of the PDF to download
            storage_path (Optional[str], optional): Path where to store the PDF.
                If not provided, a default path will be generated. Defaults to None.

        Returns:
            tuple[str, Optional[str], str]: A tuple containing:
                - The original target URL
                - The path where the PDF was saved (None if failed)
                - The storage directory path
        """
        try:
            parsed_url = parse_url(target_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.host}"

            # Set up download path
            if not storage_path:
                default_path = parsed_url.host + \
                    str(datetime.now(tz.utc).strftime("%d_%m_%Y_%H_%M_%S"))
                storage_path = os.path.join(
                    os.getcwd(), "downloads", default_path)
            else:
                storage_path = os.path.abspath(storage_path)

            self.current_download_path = storage_path

            # Check robots.txt
            can_fetch, _ = WebUtils.check_robots_txt(
                base_url, target_url, "Mozilla/5.0")
            if not can_fetch:
                logger.warning(f"can't fetch {target_url}")
                return False

            # Ensure download directory exists
            if not FileUtils.ensure_directory(storage_path):
                logger.critical("Failed to create download directory")
                raise OSError("Failed to create download directory")

            # Get appropriate scraper and download
            scraper: BasePlaywrightScraper = self.scrapers.get(
                parsed_url.host, self.scrapers["default"])
            file_path = await scraper.download_pdf(target_url, storage_path)
            return target_url, file_path, storage_path

        except Exception as e:
            logger.exception(f"Error in get_pdf: {e}")
            return False

    async def get_pdfs(self,
                       target_urls: list[str],
                       storage_path: Optional[str] = None) -> Dict[str,Union[int,Dict[str, str],Optional[str]]]:
        """Download multiple PDFs concurrently from the provided URLs.

        Args:
            target_urls (list[str]): List of URLs to download PDFs from
            storage_path (Optional[str], optional): Base path for storing the PDFs.
                If not provided, a default path will be generated. Defaults to None.

        Returns:
            Dict[str, Union[int, Dict[str, str], Optional[str]]]: A dictionary containing:
                - 'count': Number of successfully downloaded PDFs
                - 'paths': Mapping of URLs to their local file paths
                - 'storage_path': The base storage directory path used
        """
        results = {"count": 0, "paths": {}, "storage_path": None}

        storage_path = storage_path + \
            str(datetime.now(tz.utc).strftime("%d_%m_%Y_%H_%M_%S")) if storage_path else None

        # Create tasks for all downloads
        tasks = [self.get_pdf(url, storage_path) for url in target_urls]

        # Execute downloads concurrently
        async_result = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in async_result:
            if isinstance(result, bool):
                continue
            url, path, storage_path, = result
            if path:
                results["count"] += 1
                results["paths"][url] = path
                results["storage_path"] = storage_path
            else:
                logger.exception(f"Failed to get pdf from {url}")

        if results["count"] == 0:
            logger.warning("No PDFs were successfully downloaded.")

        return results
