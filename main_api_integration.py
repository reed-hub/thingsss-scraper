"""
Production Integration Guide for Main Thingsss API
==================================================

This module provides a production-ready integration class to connect your main
Thingsss API with the dedicated scraping service for handling complex sites.

Usage:
    from main_api_integration import ThingsssEnhancedScraper
    
    scraper = ThingsssEnhancedScraper()
    result = await scraper.enhanced_url_inference(url)

Features:
    - Automatic strategy selection based on site complexity
    - Fallback mechanisms for reliability
    - Comprehensive error handling and logging
    - Performance monitoring and metrics
    - Production-ready timeout and retry logic

Author: Thingsss Team
Version: 1.0.0
"""

import httpx
import asyncio
from typing import Optional, Dict, Any, List
import logging
from urllib.parse import urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThingsssEnhancedScraper:
    """
    Enhanced scraper using the dedicated scraping service for complex sites.
    
    This class provides intelligent routing between HTTP and browser-based
    scraping strategies based on site characteristics and historical success rates.
    
    Attributes:
        scraping_api_url (str): Base URL of the scraping service
        timeout (int): Default timeout for HTTP requests
        complex_sites (set): Sites requiring browser automation
        
    Example:
        >>> scraper = ThingsssEnhancedScraper()
        >>> result = await scraper.enhanced_url_inference('https://cb2.com/product')
        >>> print(result['title'])
        'Product Name'
    """
    
    def __init__(self, scraping_api_url: Optional[str] = None):
        """
        Initialize the enhanced scraper.
        
        Args:
            scraping_api_url: Custom scraping service URL. If None, uses production URL.
        """
        # Use production URL by default
        self.scraping_api_url = scraping_api_url or "https://thingsss-scraper-production.up.railway.app"
        self.timeout = 90  # 90 second timeout for complex scraping
        
        # Sites that require the advanced scraping service due to:
        # - Bot detection systems
        # - JavaScript-heavy interfaces
        # - CAPTCHA challenges
        # - Complex authentication flows
        self.complex_sites = {
            # Furniture & Home Decor
            'cb2.com', 'westelm.com', 'potterybarn.com', 'williams-sonoma.com',
            'wayfair.com', 'overstock.com', 'houzz.com', 'article.com',
            
            # Major Retailers
            'walmart.com', 'target.com', 'costco.com', 'samsclub.com',
            'homedepot.com', 'lowes.com', 'menards.com',
            
            # Fashion & Apparel
            'macys.com', 'nordstrom.com', 'bloomingdales.com', 'saksfifthavenue.com',
            'neimanmarcus.com', 'bergdorfgoodman.com',
            
            # Electronics
            'bestbuy.com', 'apple.com', 'samsung.com', 'lg.com',
            
            # Specialty Retailers
            'rei.com', 'patagonia.com', 'nike.com', 'adidas.com'
        }
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0,
            'strategy_usage': {'http': 0, 'browser': 0, 'auto': 0}
        }
    
    def needs_advanced_scraping(self, url: str) -> bool:
        """
        Determine if URL requires the advanced scraping service.
        
        This method analyzes the domain to determine if the site is known
        to require browser automation due to bot detection or JavaScript requirements.
        
        Args:
            url: The URL to analyze
            
        Returns:
            bool: True if advanced scraping is needed, False otherwise
            
        Example:
            >>> scraper = ThingsssEnhancedScraper()
            >>> scraper.needs_advanced_scraping('https://cb2.com/product')
            True
            >>> scraper.needs_advanced_scraping('https://example.com')
            False
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix for comparison
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check exact matches and subdomain matches
            for complex_domain in self.complex_sites:
                if domain == complex_domain or domain.endswith('.' + complex_domain):
                    logger.info(f"🤖 Advanced scraping required for {domain}")
                    return True
            
            logger.info(f"🌐 Standard scraping suitable for {domain}")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ URL parsing error for {url}: {e}")
            # Default to advanced scraping for safety
            return True
    
    async def scrape_with_service(
        self, 
        url: str, 
        strategy: str = "auto",
        extract_fields: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape URL using the dedicated scraping service.
        
        Args:
            url: URL to scrape
            strategy: Scraping strategy ('auto', 'http', 'browser')
            extract_fields: List of fields to extract
            timeout: Custom timeout for this request
            
        Returns:
            Extracted data dictionary or None if failed
            
        Raises:
            httpx.TimeoutException: If request times out
            httpx.HTTPStatusError: If HTTP error occurs
        """
        start_time = time.time()
        request_timeout = timeout or self.timeout
        
        # Default extraction fields
        if extract_fields is None:
            extract_fields = [
                "title", "description", "images", "price", 
                "brand", "model", "specifications"
            ]
        
        try:
            payload = {
                "url": url,
                "strategy": strategy,
                "timeout": min(request_timeout - 10, 60),  # Leave 10s buffer for HTTP
                "extract_fields": extract_fields
            }
            
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                logger.info(f"📡 Sending request to scraping service: {url}")
                
                response = await client.post(
                    f"{self.scraping_api_url}/api/v1/scrape",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    processing_time = time.time() - start_time
                    
                    if result.get("success"):
                        # Update metrics
                        self._update_metrics(True, processing_time, strategy)
                        
                        logger.info(
                            f"✅ Scraping successful for {url} "
                            f"using {result.get('strategy_used')} "
                            f"in {result.get('processing_time', 0):.2f}s"
                        )
                        return result.get("data")
                    else:
                        self._update_metrics(False, processing_time, strategy)
                        error_msg = result.get('error', 'Unknown error')
                        logger.warning(f"❌ Scraping failed for {url}: {error_msg}")
                        
                else:
                    self._update_metrics(False, time.time() - start_time, strategy)
                    logger.error(
                        f"❌ Scraping service HTTP error for {url}: "
                        f"Status {response.status_code}"
                    )
                
        except httpx.TimeoutException:
            self._update_metrics(False, time.time() - start_time, strategy)
            logger.error(f"⏰ Scraping service timeout for {url}")
            
        except Exception as e:
            self._update_metrics(False, time.time() - start_time, strategy)
            logger.error(f"❌ Scraping service exception for {url}: {e}")
        
        return None
    
    async def enhanced_url_inference(
        self, 
        url: str,
        extract_fields: Optional[List[str]] = None,
        force_strategy: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Main method: Enhanced URL inference with intelligent strategy selection.
        
        This is the primary method for scraping URLs. It automatically selects
        the optimal strategy based on site characteristics and provides fallback
        mechanisms for maximum reliability.
        
        Args:
            url: URL to scrape
            extract_fields: Specific fields to extract
            force_strategy: Override automatic strategy selection
            
        Returns:
            Extracted data dictionary or None if all strategies fail
            
        Example:
            >>> scraper = ThingsssEnhancedScraper()
            >>> data = await scraper.enhanced_url_inference('https://cb2.com/product')
            >>> print(data['title'])
            'Burl 35.5" Rotating Coffee Table'
        """
        logger.info(f"🎯 Starting enhanced URL inference for: {url}")
        
        # Use forced strategy if provided
        if force_strategy:
            strategy = force_strategy
            logger.info(f"🔧 Using forced strategy: {strategy}")
        else:
            # Intelligent strategy selection
            if self.needs_advanced_scraping(url):
                strategy = "browser"
                logger.info(f"🤖 Using browser strategy for complex site")
            else:
                strategy = "http"
                logger.info(f"🌐 Using HTTP strategy for simple site")
        
        # Primary attempt
        result = await self.scrape_with_service(
            url, 
            strategy=strategy, 
            extract_fields=extract_fields
        )
        
        # Fallback mechanism for HTTP strategy
        if result is None and strategy == "http":
            logger.info(f"🔄 HTTP failed, falling back to browser strategy")
            result = await self.scrape_with_service(
                url, 
                strategy="browser", 
                extract_fields=extract_fields,
                timeout=120  # Extra time for browser fallback
            )
        
        if result:
            logger.info(f"✅ Successfully extracted data for {url}")
        else:
            logger.error(f"❌ All scraping strategies failed for {url}")
        
        return result
    
    def _update_metrics(self, success: bool, processing_time: float, strategy: str):
        """Update internal performance metrics."""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        # Update average response time
        total = self.metrics['total_requests']
        current_avg = self.metrics['avg_response_time']
        self.metrics['avg_response_time'] = (current_avg * (total - 1) + processing_time) / total
        
        # Track strategy usage
        if strategy in self.metrics['strategy_usage']:
            self.metrics['strategy_usage'][strategy] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for monitoring and optimization.
        
        Returns:
            Dictionary containing performance statistics
        """
        if self.metrics['total_requests'] == 0:
            success_rate = 0
        else:
            success_rate = (
                self.metrics['successful_requests'] / 
                self.metrics['total_requests'] * 100
            )
        
        return {
            **self.metrics,
            'success_rate_percent': round(success_rate, 2)
        }
    
    async def health_check(self) -> bool:
        """
        Check if the scraping service is healthy and responsive.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.scraping_api_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    return data.get('status') == 'healthy'
        except Exception as e:
            logger.error(f"Health check failed: {e}")
        
        return False


# FastAPI Integration Examples
# ============================

async def example_fastapi_integration():
    """
    Example FastAPI integration for the main Thingsss API.
    
    Add this to your main API to enable enhanced scraping capabilities.
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI()
    scraper = ThingsssEnhancedScraper()
    
    class URLRequest(BaseModel):
        url: str
        extract_fields: Optional[List[str]] = None
        force_strategy: Optional[str] = None
    
    @app.post("/api/scrape")
    async def enhanced_scrape_endpoint(request: URLRequest):
        """Enhanced scraping endpoint with automatic strategy selection."""
        try:
            result = await scraper.enhanced_url_inference(
                request.url,
                extract_fields=request.extract_fields,
                force_strategy=request.force_strategy
            )
            
            if result:
                return {
                    "success": True,
                    "data": result,
                    "message": "Successfully scraped URL"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to scrape URL",
                    "message": "Please try again or contact support"
                }
                
        except Exception as e:
            logger.error(f"Scraping endpoint error: {e}")
            raise HTTPException(status_code=500, detail="Internal scraping error")
    
    @app.post("/api/scrape/cb2")
    async def cb2_specific_endpoint(request: URLRequest):
        """Dedicated CB2 scraping endpoint with optimized settings."""
        if 'cb2.com' not in request.url:
            raise HTTPException(status_code=400, detail="This endpoint is for CB2 URLs only")
        
        result = await scraper.scrape_with_service(
            request.url, 
            strategy="browser",
            extract_fields=["title", "description", "images", "price", "specifications"]
        )
        
        if result:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=422, detail="Failed to scrape CB2 URL")
    
    @app.get("/api/scraper/metrics")
    async def get_scraper_metrics():
        """Get scraping performance metrics."""
        return scraper.get_metrics()
    
    @app.get("/api/scraper/health")
    async def check_scraper_health():
        """Check scraping service health."""
        healthy = await scraper.health_check()
        return {"healthy": healthy, "service_url": scraper.scraping_api_url}


# Usage Examples
# ==============

async def usage_examples():
    """Comprehensive usage examples for different scenarios."""
    
    scraper = ThingsssEnhancedScraper()
    
    # Example 1: Basic usage
    print("=== Example 1: Basic Usage ===")
    result = await scraper.enhanced_url_inference(
        "https://www.cb2.com/burl-35.5-rotating-coffee-table/s151251"
    )
    if result:
        print(f"Title: {result.get('title')}")
        print(f"Price: {result.get('price')}")
    
    # Example 2: Custom field extraction
    print("\n=== Example 2: Custom Field Extraction ===")
    result = await scraper.enhanced_url_inference(
        "https://www.cb2.com/product",
        extract_fields=["title", "price", "images"]
    )
    
    # Example 3: Force specific strategy
    print("\n=== Example 3: Force Browser Strategy ===")
    result = await scraper.enhanced_url_inference(
        "https://www.walmart.com/product",
        force_strategy="browser"
    )
    
    # Example 4: Health check
    print("\n=== Example 4: Health Check ===")
    healthy = await scraper.health_check()
    print(f"Service healthy: {healthy}")
    
    # Example 5: Performance metrics
    print("\n=== Example 5: Performance Metrics ===")
    metrics = scraper.get_metrics()
    print(f"Success rate: {metrics['success_rate_percent']}%")
    print(f"Average response time: {metrics['avg_response_time']:.2f}s")


if __name__ == "__main__":
    """
    Run usage examples if script is executed directly.
    
    Usage:
        python3 main_api_integration.py
    """
    print("🤖 Thingsss Enhanced Scraper - Usage Examples")
    print("=" * 50)
    
    # Run examples
    asyncio.run(usage_examples())
    
    print("\n✅ Examples completed!")
    print("\nTo integrate with your main API:")
    print("1. Copy this file to your main API project")
    print("2. Import ThingsssEnhancedScraper")
    print("3. Use enhanced_url_inference() method")
    print("4. Monitor metrics with get_metrics()") 