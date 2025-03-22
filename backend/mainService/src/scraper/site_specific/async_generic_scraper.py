"""
Generic Web Scraper Module

This module provides a generic web scraper implementation that can handle PDF downloads
from various websites. It includes functionality for:
- PDF detection and download
- Web content extraction
- PDF generation from web content
- Error handling and logging

The GenericScraper class serves as a fallback when site-specific scrapers are not available.
It uses Playwright for browser automation and ReportLab for PDF generation.

Classes:
    GenericScraper: Implements generic PDF download and generation functionality
"""

from src.scraper.async_base_scraper import BasePlaywrightScraper
from src.utils.web_utils import WebUtils
from src.utils.file_utils import FileUtils
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from urllib3.util import parse_url
from src.config.log_config import setup_logging
import asyncio
from src.config.config import scraper_config

filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)

class GenericScraper(BasePlaywrightScraper):
    async def download_pdf(self, url: str, download_path: str) -> str | bool:
        try:
            if not url.lower().endswith('.pdf'):
                logger.info("URL does not point to a PDF file")
                logger.info(f"Attempting to make a PDF in {download_path}" )
                return await self.make_pdf(url, download_path)

            if WebUtils.get_file_size(url) > FileUtils.MAX_FILE_SIZE:
                logger.warning("File size exceeds limit")
                return False

            return await self._handle_download(url=url, storage_dir=download_path)
        except Exception as e:
            logger.exception(f"Error downloading PDF from generic source: {e}")
            return False
    
    def generate_pdf_sync(self,full_path: str, content: str) -> str:
        """
        Generate a PDF from the given content using ReportLab's Platypus.

        :param full_path: The full file path where the PDF will be saved.
        :param content: The text content to include in the PDF.
        :return: The path to the generated PDF.
        """
        # Create a document template with letter page size.
        doc = SimpleDocTemplate(full_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Create a Paragraph which handles text wrapping.
        paragraph = Paragraph(content, styles["Normal"])
        story.append(paragraph)
        
        # Optionally, add some spacing.
        story.append(Spacer(1, 0.2 * inch))
        
        # Build the PDF.
        doc.build(story)
        return full_path

    # Asynchronous method: Generate a PDF from a URL using Playwright for content extraction.
    async def make_pdf(self, url: str, download_path: str) -> str | bool:
        """
        Generate a PDF from a webpage's content.

        :param url: The URL of the webpage.
        :param download_path: Directory where the PDF will be saved.
        :return: The full path to the saved PDF, or False if an error occurred.
        """
        try:
            page = await self.PD.get_new_page(self.context)
            logger.info("New page created for PDF generation.")

            # Navigate to the URL and wait for DOM content to be loaded (faster than waiting for full network idle).
            await page.goto(url, wait_until="domcontentloaded",timeout=scraper_config.TIMEOUT_DURATION)
            content = await page.locator("body").inner_text()

            await page.close()

            # Parse the URL to create a sensible filename.
            parsed = parse_url(url)
            base = parsed.path.split('/')[0] or parsed.host
            filename = f"{base}.pdf"
            full_path = os.path.join(download_path, filename)

            # Offload the synchronous PDF generation to avoid blocking the event loop.
            loop = asyncio.get_running_loop()
            pdf_path = await loop.run_in_executor(None, self.generate_pdf_sync, full_path, content)
            logger.info(f"PDF saved to {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.exception(f"Error making PDF")
            return False
