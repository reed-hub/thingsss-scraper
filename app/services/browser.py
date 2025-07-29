"""Browser management service using Playwright."""
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
import structlog
from playwright.async_api import async_playwright, Browser, BrowserContext
from app.core.config import settings

logger = structlog.get_logger()

class BrowserService:
    """Manages browser instances for scraping."""
    
    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._lock = asyncio.Lock()
    
    async def _ensure_browser(self):
        """Ensure browser is initialized."""
        if self._browser is None:
            async with self._lock:
                if self._browser is None:
                    logger.info("Initializing browser")
                    self._playwright = await async_playwright().start()
                    self._browser = await self._playwright.chromium.launch(
                        headless=settings.browser_headless,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--no-first-run',
                            '--no-zygote',
                            '--disable-gpu'
                        ]
                    )
                    logger.info("Browser initialized successfully")
    
    @asynccontextmanager
    async def get_browser_context(self):
        """Get a browser context for scraping."""
        await self._ensure_browser()
        
        context = await self._browser.new_context(
            user_agent=settings.browser_user_agent,
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True,
            java_script_enabled=True
        )
        
        try:
            yield context
        finally:
            await context.close()
    
    async def close(self):
        """Close browser and cleanup resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        logger.info("Browser service closed")
    
    async def health_check(self) -> bool:
        """Check if browser service is healthy."""
        try:
            await self._ensure_browser()
            return self._browser is not None and self._browser.is_connected()
        except Exception as e:
            logger.error("Browser health check failed", error=str(e))
            return False 