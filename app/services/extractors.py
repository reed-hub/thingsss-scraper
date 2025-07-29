"""Data extraction logic for web pages."""
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import structlog
from bs4 import BeautifulSoup

from app.models.responses import ExtractedData
from app.utils.url_parser import resolve_relative_url, get_base_url

logger = structlog.get_logger()

class DataExtractor:
    """Extracts structured data from HTML content."""
    
    def extract_data(self, raw_data: Dict[str, Any], url: str, extract_fields: List[str]) -> ExtractedData:
        """Extract structured data from raw HTML."""
        html = raw_data.get('html', '')
        if not html:
            return ExtractedData()
        
        soup = BeautifulSoup(html, 'html.parser')
        base_url = get_base_url(url)
        
        data = ExtractedData()
        
        try:
            if 'title' in extract_fields:
                data.title = self._extract_title(soup)
            
            if 'description' in extract_fields:
                data.description = self._extract_description(soup)
            
            if 'images' in extract_fields:
                data.images = self._extract_images(soup, base_url)
            
            if 'price' in extract_fields:
                price_data = self._extract_price(soup)
                data.price = price_data.get('price')
                data.currency = price_data.get('currency')
            
            if 'brand' in extract_fields:
                data.brand = self._extract_brand(soup)
            
            if 'model' in extract_fields:
                data.model = self._extract_model(soup)
            
            # Always extract meta tags for additional context
            data.meta_tags = self._extract_meta_tags(soup)
            
            # Extract specifications/features
            data.specifications = self._extract_specifications(soup)
            
        except Exception as e:
            logger.error("Data extraction error", error=str(e), url=url)
        
        return data
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        # Try various selectors in order of preference
        selectors = [
            'h1[data-testid="product-title"]',  # Walmart
            '.product-title h1',  # CB2
            '.ProductDetailInfoBlock h1',  # Wayfair
            '[data-testid="product-title"]',
            '.product-name',
            '.product-title',
            '#productTitle',  # Amazon
            'h1',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 3:  # Basic validation
                    return title
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description."""
        selectors = [
            '.product-description',
            '.product-details',
            '[data-testid="product-description"]',
            '.ProductDetailInfoBlock .description',
            '#feature-bullets',  # Amazon
            '.product-summary',
            '.description'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                if desc and len(desc) > 10:
                    return desc
        
        # Fallback to meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        return None
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract product images."""
        images = []
        
        # Try product-specific image selectors
        selectors = [
            '.product-images img',
            '.product-gallery img',
            '[data-testid="product-image"] img',
            '.ProductDetailImages img',
            '#landingImage',  # Amazon
            '.carousel img'
        ]
        
        for selector in selectors:
            for img in soup.select(selector):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    # Resolve relative URLs
                    if src.startswith('/'):
                        src = urljoin(base_url, src)
                    elif not src.startswith('http'):
                        continue
                    
                    # Filter out tiny images (likely icons)
                    if self._is_valid_product_image(img, src):
                        images.append(src)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)
        
        return unique_images[:10]  # Limit to 10 images
    
    def _extract_price(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """Extract price information."""
        price_selectors = [
            '.price',
            '.price-current',
            '[data-testid="price"]',
            '.ProductDetailPricing',
            '.a-price-whole',  # Amazon
            '.sr-only:contains("current price")',
            '.current-price'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                parsed_price = self._parse_price(price_text)
                if parsed_price['price']:
                    return parsed_price
        
        return {'price': None, 'currency': None}
    
    def _parse_price(self, price_text: str) -> Dict[str, Optional[str]]:
        """Parse price string to extract amount and currency."""
        if not price_text:
            return {'price': None, 'currency': None}
        
        # Common price patterns
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $123.45 or $1,234.56
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$',  # 123.45$
            r'USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # USD 123.45
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD',  # 123.45 USD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, price_text)
            if match:
                price = match.group(1).replace(',', '')
                currency = 'USD' if '$' in price_text or 'USD' in price_text else None
                return {'price': price, 'currency': currency}
        
        return {'price': None, 'currency': None}
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand information."""
        selectors = [
            '[data-testid="brand"]',
            '.brand',
            '.product-brand',
            '.manufacturer',
            '[itemprop="brand"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                brand = element.get_text(strip=True)
                if brand:
                    return brand
        
        return None
    
    def _extract_model(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract model information."""
        selectors = [
            '[data-testid="model"]',
            '.model',
            '.product-model',
            '[itemprop="model"]',
            '.sku'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                model = element.get_text(strip=True)
                if model:
                    return model
        
        return None
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract useful meta tags."""
        meta_tags = {}
        
        # Common meta tags of interest
        meta_names = ['description', 'keywords', 'author', 'robots']
        
        for name in meta_names:
            meta = soup.find('meta', attrs={'name': name})
            if meta and meta.get('content'):
                meta_tags[name] = meta['content']
        
        # Open Graph tags
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        for tag in og_tags:
            if tag.get('content'):
                key = tag['property'].replace('og:', '')
                meta_tags[f'og_{key}'] = tag['content']
        
        return meta_tags
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications."""
        specs = {}
        
        # Look for specification tables or lists
        spec_selectors = [
            '.specifications table',
            '.product-specs table',
            '.details table',
            '.features ul',
            '.specs dl'
        ]
        
        for selector in spec_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'table':
                    specs.update(self._parse_spec_table(element))
                elif element.name == 'ul':
                    specs.update(self._parse_spec_list(element))
                elif element.name == 'dl':
                    specs.update(self._parse_spec_dl(element))
        
        return specs
    
    def _parse_spec_table(self, table) -> Dict[str, str]:
        """Parse specifications from a table."""
        specs = {}
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key and value:
                    specs[key] = value
        return specs
    
    def _parse_spec_list(self, ul) -> Dict[str, str]:
        """Parse specifications from a list."""
        specs = {}
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            if ':' in text:
                key, value = text.split(':', 1)
                specs[key.strip()] = value.strip()
        return specs
    
    def _parse_spec_dl(self, dl) -> Dict[str, str]:
        """Parse specifications from a definition list."""
        specs = {}
        dts = dl.find_all('dt')
        dds = dl.find_all('dd')
        
        for dt, dd in zip(dts, dds):
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            if key and value:
                specs[key] = value
        
        return specs
    
    def _is_valid_product_image(self, img_element, src: str) -> bool:
        """Check if image is likely a product image."""
        # Skip tiny images (likely icons)
        width = img_element.get('width')
        height = img_element.get('height')
        
        if width and height:
            try:
                w, h = int(width), int(height)
                if w < 50 or h < 50:
                    return False
            except ValueError:
                pass
        
        # Skip common icon/UI image patterns
        skip_patterns = [
            'icon', 'logo', 'button', 'arrow', 'star', 'rating',
            'social', 'badge', 'banner', 'ad', 'placeholder'
        ]
        
        src_lower = src.lower()
        for pattern in skip_patterns:
            if pattern in src_lower:
                return False
        
        return True 