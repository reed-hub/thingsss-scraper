"""Main API endpoints for scraping service."""
import asyncio
import time
from typing import List
from datetime import datetime
import structlog
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.requests import ScrapeRequest, BulkScrapeRequest, ScrapingStrategy
from app.models.responses import ScrapeResponse, BulkScrapeResponse, HealthResponse
from app.services.scraper import ScrapingService
from app.utils.validators import is_safe_url, validate_url_domain
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

# Global scraping service instance
scraping_service = ScrapingService()

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest) -> ScrapeResponse:
    """
    Scrape a single URL and return structured data.
    
    This endpoint handles complex websites with JavaScript, bot detection,
    and anti-scraping measures using various strategies.
    """
    url = str(request.url)
    
    # Validate URL safety
    if not is_safe_url(url):
        raise HTTPException(status_code=400, detail="URL is not safe to scrape")
    
    # Validate domain restrictions if configured
    if settings.allowed_domains:
        allowed_domains = [d.strip() for d in settings.allowed_domains.split(',')]
        if not validate_url_domain(url, allowed_domains):
            raise HTTPException(status_code=403, detail="Domain not allowed")
    
    logger.info("Received scrape request", url=url, strategy=request.strategy)
    
    try:
        result = await scraping_service.scrape_url(request)
        
        if result.success:
            logger.info("Scraping successful", url=url, processing_time=result.processing_time)
        else:
            logger.warning("Scraping failed", url=url, error=result.error)
        
        return result
        
    except Exception as e:
        logger.error("Scraping endpoint error", url=url, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.post("/bulk-scrape", response_model=BulkScrapeResponse)
async def bulk_scrape_urls(request: BulkScrapeRequest) -> BulkScrapeResponse:
    """
    Scrape multiple URLs concurrently.
    
    Limited to 10 URLs per request to prevent abuse.
    Uses semaphore to limit concurrent connections.
    """
    start_time = time.time()
    urls = [str(url) for url in request.urls]
    
    logger.info("Received bulk scrape request", url_count=len(urls))
    
    # Validate all URLs
    for url in urls:
        if not is_safe_url(url):
            raise HTTPException(status_code=400, detail=f"URL is not safe to scrape: {url}")
    
    # Validate domain restrictions if configured
    if settings.allowed_domains:
        allowed_domains = [d.strip() for d in settings.allowed_domains.split(',')]
        for url in urls:
            if not validate_url_domain(url, allowed_domains):
                raise HTTPException(status_code=403, detail=f"Domain not allowed: {url}")
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
    
    async def scrape_with_semaphore(url: str) -> ScrapeResponse:
        """Scrape URL with rate limiting."""
        async with semaphore:
            scrape_request = ScrapeRequest(
                url=url,
                strategy=request.strategy,
                timeout=request.timeout,
                extract_fields=request.extract_fields
            )
            result = await scraping_service.scrape_url(scrape_request)
            # Add delay between requests
            await asyncio.sleep(settings.request_delay_ms / 1000)
            return result
    
    try:
        # Execute all scraping tasks concurrently
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Convert exception to failed response
                processed_results.append(ScrapeResponse(
                    url=urls[i],
                    success=False,
                    error=str(result),
                    strategy_used=request.strategy,
                    processing_time=0.0,
                    timestamp=datetime.utcnow()
                ))
                failed += 1
            else:
                processed_results.append(result)
                if result.success:
                    successful += 1
                else:
                    failed += 1
        
        processing_time = time.time() - start_time
        
        return BulkScrapeResponse(
            total_urls=len(urls),
            successful=successful,
            failed=failed,
            results=processed_results,
            processing_time=processing_time,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Bulk scraping error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bulk scraping failed: {str(e)}")

@router.get("/strategies")
async def get_available_strategies():
    """Get list of available scraping strategies."""
    return {
        "strategies": [
            {
                "name": ScrapingStrategy.AUTO,
                "description": "Automatically select best strategy (HTTP first, fallback to browser)"
            },
            {
                "name": ScrapingStrategy.HTTP,
                "description": "HTTP-only scraping (faster, limited JavaScript support)"
            },
            {
                "name": ScrapingStrategy.BROWSER,
                "description": "Browser-based scraping (slower, full JavaScript support)"
            },
            {
                "name": ScrapingStrategy.HYBRID,
                "description": "Custom hybrid approach (not yet implemented)"
            }
        ]
    }

@router.get("/health")
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring and Railway deployment.
    
    Checks browser service health and returns system status.
    """
    try:
        browser_ready = await scraping_service.browser_service.health_check()
        
        return HealthResponse(
            status="healthy" if browser_ready else "degraded",
            service="thingsss-scraping",
            version="1.0.0",
            timestamp=datetime.utcnow(),
            browser_ready=browser_ready,
            active_connections=0  # TODO: Implement connection tracking
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthResponse(
            status="unhealthy",
            service="thingsss-scraping", 
            version="1.0.0",
            timestamp=datetime.utcnow(),
            browser_ready=False,
            active_connections=0
        )

@router.post("/test")
async def test_scraping():
    """
    Test endpoint for validating scraping functionality.
    
    Tests with known working URLs to verify service health.
    """
    test_urls = [
        "https://httpbin.org/html",  # Simple test page
        "https://example.com",       # Basic HTML
    ]
    
    results = []
    
    for url in test_urls:
        try:
            request = ScrapeRequest(
                url=url,
                strategy=ScrapingStrategy.HTTP,
                timeout=10,
                extract_fields=["title", "description"]
            )
            result = await scraping_service.scrape_url(request)
            results.append({
                "url": url,
                "success": result.success,
                "title": result.data.title if result.data else None,
                "error": result.error
            })
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
    
    return {
        "test_results": results,
        "timestamp": datetime.utcnow()
    }

# Cleanup on shutdown
@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on service shutdown."""
    await scraping_service.close()
    logger.info("Scraping service shutdown complete") 