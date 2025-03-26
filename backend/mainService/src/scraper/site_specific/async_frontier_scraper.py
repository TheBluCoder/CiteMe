from typing import Union
from src.scraper.async_base_scraper import BasePlaywrightScraper
from urllib.parse import urljoin
from src.utils.web_utils import WebUtils
from src.utils.file_utils import FileUtils
import os
from src.config.log_config import setup_logging
from typing import Optional
from playwright.async_api import Page
from playwright.async_api import TimeoutError
from src.config.config import scraper_config

filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)


class FrontierScraper(BasePlaywrightScraper):
    element_timeout = scraper_config.TIMEOUT_DURATION

    async def download_pdf(
            self, url: str, download_path: str) -> Union[str, bool]:
        try:
            logger.info(f"Attempting to download PDF from Frontier: {url}")
            download_link = await self._get_download_link(url)
            if not download_link:
                return False

            if not await self._check_file_size(download_link):
                return False

            return await self._handle_download(url=download_link, storage_dir=download_path)
        except Exception as e:
            logger.error(f"Error in Frontier PDF download: {e}", exc_info=True)
            return False

    async def _get_download_link(self, url: str) -> Optional[str]:
        page = None
        try:
            page = await self.context.new_page()
            if not url.endswith("pdf"):
                await page.goto(url, wait_until='networkidle', timeout=self.element_timeout)
                await self._interact_with_dropdown(page)
                download_link = await self._extract_download_link(page)
            else:
                download_link = url

            return download_link
        finally:
            if page:
                await page.close()

    async def _interact_with_dropdown(self, page: Page):
        dropdown = page.locator("css=#FloatingButtonsEl > button")
        if await dropdown.count() > 0:
            try:
                await dropdown.click(timeout=self.element_timeout)
                logger.info("Successfully clicked dropdown")
            except TimeoutError as timeout_e:
                logger.warning(
                    f"Timeout while interacting with dropdown: {timeout_e}")
            except Exception as e:
                logger.warning(
                    f"Unexpected error while interacting with dropdown: {e}")

    async def _extract_download_link(self, page: Page) -> str:
        download_element = page.get_by_role('link', name="Download PDF")

        if await download_element.count() == 0:
            raise ValueError("Element for href extraction not found")
        download_link = await download_element.get_attribute('href')
        if not download_link:
            raise ValueError("Download link attribute is empty")
        logger.info("Found download link successfully")
        return urljoin(page.url, download_link)

    async def _check_file_size(self, download_link: str) -> bool:
        """
        Verify if the file size is within acceptable limits.

        Args:
            download_link (str): URL of the file to check

        Returns:
            bool: True if file size is acceptable, False otherwise
        """
        try:
            file_size = WebUtils.get_file_size(download_link)
        except Exception as e:
            logger.warning(f"Could not check file size: {e}")
            return False

        if file_size > FileUtils.MAX_FILE_SIZE:
            logger.warning(
                f"""File size {file_size} bytes exceeds maximum limit of {
                    FileUtils.MAX_FILE_SIZE} bytes""")
            return False

        return True
