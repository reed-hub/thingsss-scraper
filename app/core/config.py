"""Configuration management for scraping service."""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Basic settings
    app_name: str = "Thingsss Scraping API"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Browser settings
    browser_timeout: int = 30000  # 30 seconds
    browser_headless: bool = True
    browser_user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    # Rate limiting
    max_concurrent_requests: int = 5
    request_delay_ms: int = 1000  # 1 second between requests
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 2.0
    
    # Security
    allowed_domains: Optional[str] = None  # Comma-separated list
    
    # External service URLs (for integration)
    main_api_url: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 