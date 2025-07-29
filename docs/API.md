# 📡 API Documentation

Complete reference for the Thingsss Scraping API Service endpoints, request/response formats, and usage examples.

## Base URLs

- **Production**: `https://thingsss-scraper-production.up.railway.app`
- **Local Development**: `http://localhost:8080`

## Authentication

Currently, the API is open and does not require authentication. For production use, consider implementing:
- API key authentication
- Rate limiting per client
- Domain whitelist restrictions

## Common Headers

All requests should include:

```http
Content-Type: application/json
Accept: application/json
```

---

## Endpoints

### Health Check

Check service health and availability.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "thingsss-scraping", 
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### Single URL Scraping

Scrape a single URL and extract structured data.

```http
POST /api/v1/scrape
```

**Request Body:**
```json
{
  "url": "https://www.cb2.com/product-url",
  "strategy": "browser",
  "timeout": 60,
  "extract_fields": ["title", "description", "images", "price"],
  "wait_for": ".product-details",
  "options": {
    "scroll_to_bottom": true,
    "wait_for_images": true
  }
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | string | ✅ | - | URL to scrape |
| `strategy` | string | ❌ | `"auto"` | Scraping strategy (`auto`, `http`, `browser`) |
| `timeout` | integer | ❌ | `30` | Timeout in seconds (5-120) |
| `extract_fields` | array | ❌ | `["title", "description", "images", "price"]` | Fields to extract |
| `wait_for` | string | ❌ | `null` | CSS selector to wait for (browser mode) |
| `options` | object | ❌ | `{}` | Additional options |

**Response:**
```json
{
  "url": "https://www.cb2.com/product-url",
  "success": true,
  "data": {
    "title": "Burl 35.5\" Rotating Coffee Table",
    "description": "Authentic burl wood coffee table...",
    "images": [
      "https://cb2.scene7.com/is/image/CB2/image1.jpg",
      "https://cb2.scene7.com/is/image/CB2/image2.jpg"
    ],
    "price": "999.00",
    "currency": "USD", 
    "brand": "CB2",
    "model": "Burl Coffee Table",
    "specifications": {
      "Material": "Italian Mappa Burl Wood",
      "Dimensions": "35.5\"W x 35.5\"D x 15\"H"
    },
    "meta_tags": {
      "description": "Shop Burl 35.5\" Rotating Coffee Table...",
      "og_price:amount": "$999.00"
    }
  },
  "error": null,
  "strategy_used": "browser",
  "processing_time": 12.45,
  "timestamp": "2024-01-15T10:30:00Z",
  "status_code": 200,
  "content_type": "text/html",
  "final_url": "https://www.cb2.com/product-url"
}
```

**Error Response:**
```json
{
  "url": "https://example.com",
  "success": false,
  "data": null,
  "error": "Target page, context or browser has been closed",
  "strategy_used": "browser", 
  "processing_time": 5.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Request processed (check `success` field)
- `400 Bad Request`: Invalid request parameters
- `403 Forbidden`: Domain not allowed
- `422 Unprocessable Entity`: URL validation failed
- `500 Internal Server Error`: Service error

---

### Bulk URL Scraping

Scrape multiple URLs concurrently (max 10 URLs per request).

```http
POST /api/v1/bulk-scrape
```

**Request Body:**
```json
{
  "urls": [
    "https://www.cb2.com/product1",
    "https://www.wayfair.com/product2",
    "https://example.com"
  ],
  "strategy": "auto",
  "timeout": 30,
  "extract_fields": ["title", "price", "images"]
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `urls` | array | ✅ | - | Array of URLs (max 10) |
| `strategy` | string | ❌ | `"auto"` | Strategy for all URLs |
| `timeout` | integer | ❌ | `30` | Timeout per URL |
| `extract_fields` | array | ❌ | `["title", "description", "images"]` | Fields to extract |

**Response:**
```json
{
  "total_urls": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {
      "url": "https://www.cb2.com/product1",
      "success": true,
      "data": { /* extracted data */ },
      "strategy_used": "browser",
      "processing_time": 8.5
    },
    {
      "url": "https://www.wayfair.com/product2", 
      "success": true,
      "data": { /* extracted data */ },
      "strategy_used": "browser",
      "processing_time": 12.1
    },
    {
      "url": "https://example.com",
      "success": false,
      "error": "Timeout exceeded",
      "strategy_used": "http",
      "processing_time": 30.0
    }
  ],
  "processing_time": 25.3,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Available Strategies

Get list of available scraping strategies and their descriptions.

```http
GET /api/v1/strategies
```

**Response:**
```json
{
  "strategies": [
    {
      "name": "auto",
      "description": "Automatically select best strategy (HTTP first, fallback to browser)"
    },
    {
      "name": "http", 
      "description": "HTTP-only scraping (faster, limited JavaScript support)"
    },
    {
      "name": "browser",
      "description": "Browser-based scraping (slower, full JavaScript support)"
    },
    {
      "name": "hybrid",
      "description": "Custom hybrid approach (not yet implemented)"
    }
  ]
}
```

---

### Test Endpoint

Test scraping functionality with known working URLs.

```http
POST /api/v1/test
```

**Response:**
```json
{
  "test_results": [
    {
      "url": "https://httpbin.org/html",
      "success": true,
      "title": "Herman Melville - Moby-Dick",
      "error": null
    },
    {
      "url": "https://example.com",
      "success": true, 
      "title": "Example Domain",
      "error": null
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Strategy Details

### AUTO Strategy
- **Use Case**: Default for unknown sites
- **Behavior**: Tries HTTP first, falls back to browser if needed
- **Performance**: Adaptive (2-15 seconds)
- **JavaScript**: Fallback support

### HTTP Strategy
- **Use Case**: Simple sites without bot detection
- **Behavior**: Fast HTTP requests with user-agent rotation
- **Performance**: Fast (2-5 seconds)
- **JavaScript**: Not supported

### BROWSER Strategy
- **Use Case**: Complex sites with JavaScript/bot detection
- **Behavior**: Full browser automation with Playwright
- **Performance**: Slower (8-15 seconds)
- **JavaScript**: Full support

---

## Extract Fields

Available fields for extraction:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Product/page title |
| `description` | string | Product description |
| `images` | array | Image URLs |
| `price` | string | Price amount |
| `currency` | string | Currency code |
| `brand` | string | Brand name |
| `model` | string | Model/SKU |
| `specifications` | object | Technical specifications |
| `meta_tags` | object | Meta tag data |

---

## Error Handling

### Common Error Types

| Error | Description | Solution |
|-------|-------------|----------|
| `Timeout exceeded` | Request took too long | Increase timeout or use browser strategy |
| `Target page closed` | Browser closed unexpectedly | Retry with same strategy |
| `403 Forbidden` | Site blocked the request | Use browser strategy |
| `Invalid URL` | URL format is incorrect | Check URL format |
| `Domain not allowed` | Domain restrictions in effect | Contact administrator |

### Rate Limiting

- **Concurrent Requests**: Max 5 simultaneous requests
- **Request Delay**: 1 second between requests
- **Bulk Limit**: Max 10 URLs per bulk request
- **Timeout Limits**: 5-120 seconds per request

---

## Usage Examples

### Basic Scraping
```bash
curl -X POST "https://thingsss-scraper-production.up.railway.app/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "strategy": "http"
  }'
```

### CB2 Product Scraping
```bash
curl -X POST "https://thingsss-scraper-production.up.railway.app/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.cb2.com/burl-35.5-rotating-coffee-table/s151251",
    "strategy": "browser",
    "timeout": 60,
    "extract_fields": ["title", "description", "images", "price"]
  }'
```

### Bulk Scraping
```bash
curl -X POST "https://thingsss-scraper-production.up.railway.app/api/v1/bulk-scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.cb2.com/product1",
      "https://www.wayfair.com/product2"
    ],
    "strategy": "auto"
  }'
```

### Python Integration
```python
import httpx
import asyncio

async def scrape_url(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://thingsss-scraper-production.up.railway.app/api/v1/scrape",
            json={"url": url, "strategy": "auto"}
        )
        return response.json()

# Usage
result = asyncio.run(scrape_url("https://example.com"))
print(result['data']['title'])
```

---

## Performance Guidelines

### Optimization Tips

1. **Choose Right Strategy**:
   - Use `http` for simple sites (2-5x faster)
   - Use `browser` only for complex sites
   - Use `auto` when unsure

2. **Field Selection**:
   - Only request needed fields
   - Avoid `specifications` for faster extraction
   - Use `images` sparingly (can be slow)

3. **Timeout Management**:
   - Start with 30s timeout
   - Increase to 60s for complex sites
   - Use 120s maximum only when necessary

4. **Bulk Requests**:
   - Group similar sites together
   - Use same strategy for bulk requests
   - Monitor concurrent limits

### Performance Benchmarks

| Strategy | Avg Time | Success Rate | Memory Usage |
|----------|----------|--------------|--------------|
| HTTP | 2-5s | 95% | ~50MB |
| Browser | 8-15s | 90% | ~200MB |
| Auto | 3-12s | 92% | ~100MB |

---

## Integration Patterns

### FastAPI Integration
```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.post("/scrape")
async def scrape_endpoint(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://thingsss-scraper-production.up.railway.app/api/v1/scrape",
            json={"url": url, "strategy": "auto"}
        )
        return response.json()
```

### Error Handling Pattern
```python
async def safe_scrape(url: str):
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                "https://thingsss-scraper-production.up.railway.app/api/v1/scrape",
                json={"url": url, "strategy": "auto"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    return result['data']
                else:
                    print(f"Scraping failed: {result['error']}")
            else:
                print(f"HTTP error: {response.status_code}")
                
    except httpx.TimeoutException:
        print("Request timeout")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None
```

---

## Monitoring

### Health Monitoring
```bash
# Check service health
curl https://thingsss-scraper-production.up.railway.app/health

# Expected response
{"status": "healthy", "service": "thingsss-scraping", "version": "1.0.0"}
```

### Performance Monitoring
Monitor these metrics:
- Response times by strategy
- Success rates by domain
- Error patterns and frequency
- Concurrent request handling
- Memory usage trends

---

## Support

- **GitHub Issues**: [thingsss-scraper/issues](https://github.com/reed-hub/thingsss-scraper/issues)
- **API Status**: Monitor `/health` endpoint
- **Documentation**: This guide and inline code comments 