"""URL parsing and normalization utilities."""
from urllib.parse import urlparse, urljoin, urlunparse
from typing import Optional
import re

def normalize_url(url: str) -> str:
    """Normalize a URL by removing fragments and unnecessary query parameters."""
    parsed = urlparse(url)
    
    # Remove fragment
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        None  # Remove fragment
    ))
    
    # Ensure scheme
    if not parsed.scheme:
        normalized = "https://" + normalized
    
    return normalized

def get_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc.lower()

def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_base_url(url: str) -> str:
    """Get base URL (scheme + netloc)."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def resolve_relative_url(base_url: str, relative_url: str) -> str:
    """Resolve relative URL against base URL."""
    return urljoin(base_url, relative_url)

def clean_url(url: str) -> str:
    """Clean URL by removing tracking parameters and fragments."""
    # Common tracking parameters to remove
    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'ref', 'source', 'campaign'
    }
    
    parsed = urlparse(url)
    if parsed.query:
        # Parse query parameters
        from urllib.parse import parse_qs, urlencode
        params = parse_qs(parsed.query)
        # Remove tracking parameters
        clean_params = {k: v for k, v in params.items() if k not in tracking_params}
        clean_query = urlencode(clean_params, doseq=True)
    else:
        clean_query = parsed.query
    
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        None  # Remove fragment
    )) 