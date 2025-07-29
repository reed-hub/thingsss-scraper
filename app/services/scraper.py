"""Main scraping service implementation."""
import time
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from datetime import datetime
import structlog

from app.models.requests import ScrapeRequest, ScrapingStrategy
from app.models.responses import ScrapeResponse, ExtractedData
from app.services.browser import BrowserService
from app.services.strategies import StrategySelector
from app.services.extractors import DataExtractor
from app.utils.url_parser import normalize_url, get_domain
from app.core.config import settings

logger = structlog.get_logger()

class ScrapingService:
    """Main scraping service orchestrator."""
    
    def __init__(self):
        self.browser_service = BrowserService()
        self.strategy_selector = StrategySelector()
        self.data_extractor = DataExtractor()
        
    async def scrape_url(self, request: ScrapeRequest) -> ScrapeResponse:
        """Scrape a single URL with the specified strategy."""
        start_time = time.time()
        url = str(request.url)
        
        logger.info("Starting scrape", url=url, strategy=request.strategy)
        
        try:
            # Normalize URL
            normalized_url = normalize_url(url)
            domain = get_domain(normalized_url)
            
            # Select strategy
            if request.strategy == ScrapingStrategy.AUTO:
                strategy = self.strategy_selector.select_strategy(domain)
            else:
                strategy = request.strategy
                
            # Execute scraping
            if strategy == ScrapingStrategy.BROWSER:
                raw_data = await self._scrape_with_browser(normalized_url, request)
            else:
                raw_data = await self._scrape_with_http(normalized_url, request)
                
            # Extract structured data
            extracted_data = self.data_extractor.extract_data(
                raw_data, normalized_url, request.extract_fields
            )
            
            processing_time = time.time() - start_time
            
            return ScrapeResponse(
                url=url,
                success=True,
                data=extracted_data,
                strategy_used=strategy,
                processing_time=processing_time,
                timestamp=datetime.utcnow(),
                status_code=raw_data.get("status_code"),
                content_type=raw_data.get("content_type"),
                final_url=raw_data.get("final_url", normalized_url)
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error("Scraping failed", url=url, error=str(e), exc_info=True)
            
            return ScrapeResponse(
                url=url,
                success=False,
                error=str(e),
                strategy_used=request.strategy,
                processing_time=processing_time,
                timestamp=datetime.utcnow()
            )
    
    async def _scrape_with_browser(self, url: str, request: ScrapeRequest) -> Dict[str, Any]:
        """Scrape URL using browser automation."""
        async with self.browser_service.get_browser_context() as context:
            page = await context.new_page()
            
            try:
                # Navigate to page
                response = await page.goto(url, timeout=request.timeout * 1000)
                
                # Wait for specific element if requested
                if request.wait_for:
                    await page.wait_for_selector(request.wait_for, timeout=10000)
                else:
                    # Wait for network idle
                    await page.wait_for_load_state("networkidle", timeout=10000)
                
                # Get page content and metadata
                html = await page.content()
                title = await page.title()
                final_url = page.url
                
                return {
                    "html": html,
                    "title": title,
                    "final_url": final_url,
                    "status_code": response.status if response else None,
                    "content_type": "text/html"
                }
                
            finally:
                await page.close()
    
    async def _scrape_with_http(self, url: str, request: ScrapeRequest) -> Dict[str, Any]:
        """Scrape URL using HTTP client."""
        import httpx
        from fake_useragent import UserAgent
        
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        async with httpx.AsyncClient(timeout=request.timeout, headers=headers) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            return {
                "html": response.text,
                "final_url": str(response.url),
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", "")
            }
    
    async def close(self):
        """Close all services and cleanup resources."""
        await self.browser_service.close()
        logger.info("Scraping service closed") 