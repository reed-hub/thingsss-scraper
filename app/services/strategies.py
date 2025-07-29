"""Site-specific scraping strategies."""
from typing import Dict
from app.models.requests import ScrapingStrategy
from app.utils.url_parser import get_domain

class StrategySelector:
    """Selects appropriate scraping strategy based on site characteristics."""
    
    # Sites known to require browser-based scraping
    BROWSER_REQUIRED_DOMAINS = {
        'cb2.com',
        'walmart.com', 
        'wayfair.com',
        'overstock.com',
        'homedepot.com',
        'lowes.com',
        'target.com',
        'bestbuy.com',
        'macys.com',
        'nordstrom.com'
    }
    
    # Sites that work well with HTTP scraping
    HTTP_FRIENDLY_DOMAINS = {
        'amazon.com',
        'ebay.com',
        'etsy.com',
        'craigslist.org',
        'facebook.com',
        'instagram.com'
    }
    
    def select_strategy(self, domain: str) -> ScrapingStrategy:
        """Select best strategy for the given domain."""
        domain = domain.lower()
        
        # Remove www. prefix for comparison
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check exact matches first
        if domain in self.BROWSER_REQUIRED_DOMAINS:
            return ScrapingStrategy.BROWSER
        
        if domain in self.HTTP_FRIENDLY_DOMAINS:
            return ScrapingStrategy.HTTP
        
        # Check domain suffixes
        for browser_domain in self.BROWSER_REQUIRED_DOMAINS:
            if domain.endswith('.' + browser_domain) or domain == browser_domain:
                return ScrapingStrategy.BROWSER
        
        for http_domain in self.HTTP_FRIENDLY_DOMAINS:
            if domain.endswith('.' + http_domain) or domain == http_domain:
                return ScrapingStrategy.HTTP
        
        # Default to HTTP first (faster), fallback to browser if needed
        return ScrapingStrategy.AUTO
    
    def get_site_specific_options(self, domain: str) -> Dict[str, any]:
        """Get site-specific options for scraping."""
        domain = domain.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        options = {}
        
        # CB2 specific options
        if 'cb2.com' in domain:
            options.update({
                'wait_for': '.product-details',
                'scroll_to_bottom': True,
                'wait_for_images': True
            })
        
        # Walmart specific options
        elif 'walmart.com' in domain:
            options.update({
                'wait_for': '[data-testid="product-title"]',
                'handle_captcha': True
            })
        
        # Wayfair specific options
        elif 'wayfair.com' in domain:
            options.update({
                'wait_for': '.ProductDetailInfoBlock',
                'scroll_to_bottom': True
            })
        
        return options 