"""Input validation utilities."""
from typing import List
from urllib.parse import urlparse

def validate_url_domain(url: str, allowed_domains: List[str] = None) -> bool:
    """Validate if URL domain is allowed."""
    if not allowed_domains:
        return True
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix for comparison
        if domain.startswith('www.'):
            domain = domain[4:]
        
        for allowed in allowed_domains:
            allowed = allowed.lower()
            if allowed.startswith('www.'):
                allowed = allowed[4:]
            
            if domain == allowed or domain.endswith('.' + allowed):
                return True
        
        return False
    except Exception:
        return False

def is_safe_url(url: str) -> bool:
    """Check if URL is safe to scrape (not localhost, internal IPs, etc.)."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return False
        
        # Block localhost
        if hostname in ['localhost', '127.0.0.1', '::1']:
            return False
        
        # Block private IP ranges
        import ipaddress
        try:
            ip = ipaddress.ip_address(hostname)
            return not ip.is_private
        except ValueError:
            # Not an IP address, assume it's a domain name
            pass
        
        # Block file:// and other non-http schemes
        if parsed.scheme not in ['http', 'https']:
            return False
        
        return True
    except Exception:
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    import re
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    return filename[:255] 