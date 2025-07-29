"""Response models for scraping API."""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExtractedData(BaseModel):
    """Extracted data from a webpage."""
    title: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = []
    price: Optional[str] = None
    currency: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    specifications: Dict[str, Any] = {}
    meta_tags: Dict[str, str] = {}
    
class ScrapeResponse(BaseModel):
    """Response model for URL scraping."""
    url: str
    success: bool
    data: Optional[ExtractedData] = None
    error: Optional[str] = None
    strategy_used: str
    processing_time: float
    timestamp: datetime
    
    # Technical details
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    final_url: Optional[str] = None  # After redirects
    
class BulkScrapeResponse(BaseModel):
    """Response model for bulk URL scraping."""
    total_urls: int
    successful: int
    failed: int
    results: List[ScrapeResponse]
    processing_time: float
    timestamp: datetime

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: datetime
    browser_ready: bool
    active_connections: int 