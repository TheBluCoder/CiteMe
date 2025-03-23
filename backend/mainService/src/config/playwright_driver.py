from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page, Route, Request
from typing import List
import threading
import asyncio
import os
from src.config.config import scraper_config
from src.config.log_config import setup_logging

"""
A singleton wrapper module for Playwright browser automation that provides managed browser contexts and pages.

This module implements a thread-safe singleton pattern for managing Playwright browser instances,
contexts, and pages with built-in stealth mode capabilities. It handles browser lifecycle management
and provides methods for creating and managing browser contexts and pages with custom configurations.

Classes:
    PlaywrightDriver: A singleton class that manages Playwright browser instances and contexts.

Features:
    - Thread-safe singleton browser instance management
    - Async-compatible browser initialization and operations
    - Automatic stealth mode implementation for pages
    - Custom header injection for all requests
    - Multiple browser context support
    - Managed browser lifecycle (initialization, context creation, cleanup)

Example:
    async def main():
        driver = await PlaywrightDriver.create()
        try:
            context = await driver.get_new_context()
            page = await driver.get_new_page(context)
            await page.goto("https://example.com")
        finally:
            await driver.quit()

Dependencies:
    - playwright.async_api
    - playwright_stealth
    - threading
    - asyncio

Note:
    This implementation uses Chromium as the default browser with specific
    arguments to disable various features that might expose automation.
"""

log_filename = os.path.basename(__file__)
logger = setup_logging(filename=log_filename)


class PlaywrightDriver:
    """
    A singleton class that manages Playwright browser instances and contexts.

    This class provides thread-safe browser management with stealth capabilities
    and custom header injection. It ensures only one browser instance exists
    across the application.

    Attributes:
        _instance (PlaywrightDriver): Singleton instance of the class
        _playwright (Playwright): Playwright instance
        _browser (Browser): Browser instance
        _contexts (List[BrowserContext]): List of active browser contexts
        _current_context (BrowserContext): Currently active browser context
    """

    _instance = None
    _playwright: Playwright = None
    _browser: Browser = None
    _lock = threading.Lock()
    _async_lock = asyncio.Lock()
    _contexts: List[BrowserContext] = []
    _current_context: BrowserContext = None

    def __new__(cls):
        with cls._lock:
            if not hasattr(cls, 'instance'):
                cls.instance: PlaywrightDriver = super().__new__(cls)
                cls.instance._browser = None
            return cls.instance

    def __init__(self):
        pass

    @classmethod
    async def create(cls):
        """
        Factory method for creating or retrieving the singleton instance.

        Returns:
            PlaywrightDriver: Singleton instance of the PlaywrightDriver class

        Example:
            driver = await PlaywrightDriver.create()
        """

        # Factory method for async initialization
        if not cls._instance:
            cls._instance = cls()
            await cls._instance.__initialize_browser()
        return cls._instance

    async def __initialize_browser(self) -> Browser:
        """
         Initialize the browser instance with custom configurations.

         Returns:
             Browser: Configured browser instance

         Raises:
             Exception: If browser initialization fails

         Note:
             Configures browser with specific arguments to disable automation detection
         """

        async with self._async_lock:
            if self._browser:
                return self._browser

            args = [
                "--disable-gpu",
                "--disable-extensions",
                "--disable-infobars",
                "--disable-software-rasterizer",
                "--disable-dns-prefetch",
                '--disable-notification'
                "--disable-blink-features=AutomationControlled",
            ]
            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(headless=True, args=args)
            except Exception as e:
                logger.critical(f"Error while initializing browser: {e}")
                raise e
            return self._browser

    async def get_new_context(self) -> BrowserContext:
        """
        Create and return a new browser context.

        Returns:
            BrowserContext: New browser context with downloads enabled

        Note:
            Automatically adds the new context to internal context tracking
        """

        if not self._browser:
            await self.__initialize_browser()
        context = await self._browser.new_context(accept_downloads=True)
        self._contexts.append(context)
        self._current_context = context
        return context

    async def get_browser(self) -> Playwright:
        """
        Get the current browser instance, initializing it if necessary.

        Returns:
            Playwright: Current browser instance
        """

        if not self._browser:
            self._browser = await self.__initialize_browser()
        return self._browser

    async def close_browser(self):
        """
        Close all browser contexts and the browser instance.

        Closes all active contexts before closing the browser instance.

        Raises:
            Exception: If there's an error during browser closure
        """

        try:
            if self._browser:
                for context in self._contexts:
                    await context.close()
                await self._browser.close()
        except Exception as e:
            logger.exception(f"Error while closing browser: {e}")

    async def get_new_page(self, context: BrowserContext) -> Page:
        """
        Create a new page in the specified browser context with stealth mode.

        Args:
            context (BrowserContext): Browser context to create the page in

        Returns:
            Page: New page instance with stealth mode and custom routing enabled
        """

        page = await context.new_page()
        await page.route("**/*", self.handle)
        return page

    async def handle(self, route: Route, request: Request):
        """
        Handle browser requests by injecting custom headers.

        Args:
            route (Route): Playwright route object
            request (Request): Request being made

        Note:
            Injects custom headers defined in scraper_config.HTTP_HEADERS
        """

        # override headers
        headers = {
            **request.headers,
            **scraper_config.HTTP_HEADERS,
            "SEC_CH_UA": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        }
        await route.continue_(headers=headers)

    async def quit(self):
        """
        Clean up all browser resources.

        Closes the browser and stops the playwright instance.

        Raises:
            Exception: If there's an error during cleanup
        """

        try:
            if self._browser:
                await self.close_browser()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.exception(f"Error while quitting driver: {e}")

    async def get_context(self) -> BrowserContext:
        """
        Get the current context or create a new one if none exists.

        Returns:
            BrowserContext: Current or new browser context
        """

        if not self._contexts:
            return await self.get_new_context()
        return self._current_context

    async def get_current_context(self) -> BrowserContext | None:
        """
        Get the currently active browser context.

        Returns:
            BrowserContext | None: Current browser context or None if no context exists
        """

        return self._current_context

    async def set_current_context(self, context: BrowserContext):
        """
        Set the current active browser context.

        Args:
            context (BrowserContext): Browser context to set as current
        """

        self._current_context = context
