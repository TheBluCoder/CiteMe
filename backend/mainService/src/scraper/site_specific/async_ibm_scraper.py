"""
IBM Research Scraper Module

This module provides functionality for scraping and downloading PDFs from IBM Research publications.
It extends the BasePlaywrightScraper class to implement site-specific scraping logic for IBM's research portal.

The scraper handles:
- PDF download link detection
- File size validation
- Error handling and logging
- Playwright-based browser automation

Classes:
    IBMScraper: Implements IBM-specific PDF download functionality
"""

from src.scraper.async_base_scraper import BasePlaywrightScraper   
from src.utils.web_utils import WebUtils
from src.utils.file_utils import FileUtils
from src.config.log_config import setup_logging
from src.config.config import scraper_config
import os


filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)


class IBMScraper(BasePlaywrightScraper):
    element_timeout = scraper_config.TIMEOUT_DURATION
    
    async def download_pdf(self, url: str, download_path: str) -> str | bool:
        page = None
        try:
            logger.info(f"Attempting to download PDF from IBM: {url}")
            
            page = await self.context.new_page()
            await page.goto(url, wait_until='networkidle')
            
            # Try multiple strategies to find the download link
            download_element = None
            try:
                # First try specific CSS selector
                download_element = page.locator('#main-content > article > div > div.aVLxf > header > div > a')

                if not await download_element.count():
                    # Try by text content
                    download_element = page.get_by_role('link', name="Download paper")
                
                if await download_element.count():
                    download_link = await download_element.get_attribute('href')
                    if not download_link:
                        raise ValueError("Download link attribute is empty")
                    
                    logger.info(f"Found download link: {download_link}")
                    
                    # Check file size if needed
                    try:
                        # Implement file size check using Playwright
                        size = WebUtils.get_file_size(download_link)
                        if size > FileUtils.MAX_FILE_SIZE:
                            logger.warning(f"File size {size} exceeds maximum limit")
                            return False
                    except Exception as e:
                        logger.warning(f"Could not check file size: {e}")
                    
                    # Close page before starting download
                    await page.close()
                    page = None
                    
                    # Handle the download
                    return await self._handle_download(url=download_link,storage_dir= download_path)
                else:
                    raise ValueError("No download element found")
                    
            except Exception as e:
                logger.exception(f"Failed to get download link")
                return False
                
        except Exception as e:
            logger.exception(f"Error in IBM PDF download")
            return False
            
        finally:
            if page:
                await page.close()
