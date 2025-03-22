"""
Base Scraper Module

This module provides the foundational class for web scraping operations using Playwright.
It implements core functionality for browser interactions and file downloads while
allowing specific implementations to be defined in child classes.

The BasePlaywrightScraper class provides:
- Browser context management
- File download handling
- Error handling and logging
- Abstract methods for child class implementation

Classes:
    BasePlaywrightScraper: Abstract base class for Playwright-based web scrapers
"""

from playwright.async_api import BrowserContext
from typing import  Optional
import os
from abc import ABC, abstractmethod
import  asyncio
from src.config.playwright_driver import PlaywrightDriver
from urllib3.util import parse_url
from src.config.log_config import setup_logging
from src.config.config import scraper_config

filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)

class BasePlaywrightScraper(ABC):
    """
    Abstract base class for implementing Playwright-based web scraping operations.

    This class provides core functionality for handling browser interactions and file downloads
    using Playwright's async API. It implements common scraping patterns and utilities while
    leaving specific implementation details to child classes.

    Attributes:
        context (BrowserContext): Playwright browser context for managing browser sessions
        PD (PlaywrightDriver): Custom Playwright driver instance for browser automation

    Methods:
        _handle_download: Internal method to handle file downloads
        download_pdf: Abstract method to be implemented by child classes for PDF downloads
    """

    
    def __init__(self, context: BrowserContext, playwright_driver:PlaywrightDriver):
        """
        Initialize the base scraper with browser context and playwright driver.

        Args:
            context (BrowserContext): Playwright browser context for managing browser sessions
            playwright_driver (PlaywrightDriver): Instance of custom Playwright driver
        """

        self.context = context
        self.PD = playwright_driver

    async def _handle_download(self, storage_dir: str, url: str = None, timeout: int = None) -> str | bool:
        """
        Handle file download with Playwright's built-in download capabilities.

        This method manages the download process including page creation, download triggering,
        and file saving with proper error handling and timeout management.

        Args:
            storage_dir (str): Directory path where the downloaded file will be saved
            url (str, optional): URL to download the file from
            timeout (int, optional): Custom timeout duration for the download operation

        Returns:
            str: Path to the downloaded file if successful
            bool: False if download fails

        Raises:
            asyncio.TimeoutError: If download exceeds timeout duration
            Exception: For any other errors during download process
        """

        try:
            logger.info(f"Starting download from: {url}")
            page = await self.PD.get_new_page(self.context)

            async with page.expect_download(timeout= scraper_config.TIMEOUT_DURATION) as download_info:
                await page.evaluate(f"window.open('{url}')")  

            logger.info("Download triggered, waiting for file...")
            download = await asyncio.wait_for(download_info.value, timeout= timeout or scraper_config.TIMEOUT_DURATION)  # Prevent indefinite hang

            suggested_filename = download.suggested_filename or parse_url(url).path.split('/')[-1]

            download_path = os.path.join(storage_dir, suggested_filename)
            logger.info(f"Saving file to: {download_path}")

            await download.save_as(download_path)  
            logger.info("Download completed successfully.")

            if os.path.exists(download_path) and os.path.getsize(download_path)>0:
                return download_path
            logger.error("Error occured during file saving")
            return False

        except asyncio.TimeoutError:
            logger.exception("Download timed out")
            return False

        except Exception as e:
            logger.exception(f"Error during download: {e}", exc_info=True)
            return False

        finally:
            if 'page' in locals():
                await page.close()


    @abstractmethod
    async def download_pdf(self, url: str, download_path: str) -> Optional[str]:
        """
        Abstract method to download PDF from the given URL.

        This method must be implemented by child classes to provide specific PDF
        download functionality.

        Args:
            url (str): URL of the PDF to download
            download_path (str): Path where the PDF should be saved

        Returns:
            Optional[str]: Path to the downloaded PDF if successful, None otherwise

        Raises:
            NotImplementedError: If the child class doesn't implement this method
        """

        pass
