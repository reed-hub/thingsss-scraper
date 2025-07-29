"""Request models for scraping API."""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ScrapingStrategy(str, Enum):
    """Available scraping strategies."""
    AUTO = "auto"          # Try HTTP first, fallback to browser
    HTTP = "http"          # HTTP-only scraping
    BROWSER = "browser"    # Browser-based scraping
    HYBRID = "hybrid"      # Custom hybrid approach

class ScrapeRequest(BaseModel):
    """Request model for URL scraping."""
    url: HttpUrl = Field(..., description="URL to scrape")
    strategy: ScrapingStrategy = Field(
        default=ScrapingStrategy.AUTO,
        description="Scraping strategy to use"
    )
    timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout in seconds"
    )
    wait_for: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for (browser mode)"
    )
    extract_fields: List[str] = Field(
        default=["title", "description", "images", "price"],
        description="Fields to extract"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional scraping options"
    )

class BulkScrapeRequest(BaseModel):
    """Request model for bulk URL scraping."""
    urls: List[HttpUrl] = Field(..., max_items=10, description="URLs to scrape")
    strategy: ScrapingStrategy = Field(default=ScrapingStrategy.AUTO)
    timeout: int = Field(default=30, ge=5, le=120)
    extract_fields: List[str] = Field(default=["title", "description", "images"]) 