# 🤖 Thingsss Scraping API Service

A production-ready web scraping service designed to handle complex websites with bot detection, JavaScript requirements, and anti-scraping measures.

## 🎯 Overview

This independent service solves the challenge of scraping modern e-commerce and retail websites that return 403 Forbidden errors or require JavaScript execution. It's specifically designed to work with sites like CB2, Walmart, Wayfair, and other complex retail platforms.

### Key Features

- **🌐 Multi-Strategy Scraping**: HTTP-first with browser fallback
- **🤖 Browser Automation**: Playwright-powered for JavaScript-heavy sites
- **🚀 High Performance**: Concurrent processing with rate limiting
- **🔒 Security**: URL validation, domain restrictions, safety checks
- **📊 Structured Data**: Automatic extraction of product metadata
- **🔄 Auto-Retry**: Intelligent fallback strategies
- **📈 Production Ready**: Health checks, logging, monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Main API      │    │  Scraping API    │    │   Target Site   │
│  (Thingsss)     │───▶│   (This Service) │───▶│   (CB2, etc.)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Strategy Selection

1. **AUTO**: Try HTTP first, fallback to browser if needed
2. **HTTP**: Fast scraping for simple sites (Amazon, eBay)
3. **BROWSER**: Full JavaScript execution for complex sites (CB2, Walmart)
4. **HYBRID**: Custom approach (future enhancement)

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd thingsss-scraping

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run development server
uvicorn main:app --reload --port 8080
```

### Docker

```bash
# Build image
docker build -t thingsss-scraping .

# Run container
docker run -p 8080:8080 thingsss-scraping
```

### Railway Deployment

1. Connect Railway to your GitHub repository
2. Set environment variables:
   ```
   DEBUG=false
   BROWSER_HEADLESS=true
   MAX_CONCURRENT_REQUESTS=3
   ```
3. Deploy and verify health endpoint

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scrape` | POST | Scrape single URL |
| `/api/v1/bulk-scrape` | POST | Scrape multiple URLs |
| `/api/v1/strategies` | GET | List available strategies |
| `/api/v1/test` | POST | Test scraping functionality |
| `/health` | GET | Health check |

### Example Usage

#### Single URL Scraping

```bash
curl -X POST "http://localhost:8080/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.cb2.com/burl-35.5-rotating-coffee-table/s151251",
    "strategy": "browser",
    "timeout": 30,
    "extract_fields": ["title", "description", "images", "price"]
  }'
```

#### Response Format

```json
{
  "url": "https://www.cb2.com/burl-35.5-rotating-coffee-table/s151251",
  "success": true,
  "data": {
    "title": "Burl 35.5\" Rotating Coffee Table",
    "description": "Authentic burl wood coffee table with rotating top...",
    "images": ["https://images.cb2.com/product1.jpg", "..."],
    "price": "899.00",
    "currency": "USD",
    "brand": "CB2",
    "specifications": {...}
  },
  "strategy_used": "browser",
  "processing_time": 12.5,
  "timestamp": "2024-01-15T10:30:00Z",
  "status_code": 200
}
```

#### Bulk Scraping

```bash
curl -X POST "http://localhost:8080/api/v1/bulk-scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.cb2.com/product1",
      "https://www.wayfair.com/product2"
    ],
    "strategy": "auto"
  }'
```

## 🔧 Configuration

### Environment Variables

```bash
# Application settings
DEBUG=false
APP_NAME="Thingsss Scraping API"

# Browser settings
BROWSER_TIMEOUT=30000
BROWSER_HEADLESS=true

# Rate limiting
MAX_CONCURRENT_REQUESTS=5
REQUEST_DELAY_MS=1000

# Security (optional)
ALLOWED_DOMAINS=cb2.com,walmart.com,wayfair.com
```

### Site-Specific Configuration

The service automatically configures optimal settings for known sites:

- **CB2**: Browser mode, wait for `.product-details`, scroll to bottom
- **Walmart**: Browser mode, wait for product title, handle CAPTCHA
- **Wayfair**: Browser mode, wait for product info block

## 🎯 Integration with Main API

Add to your main Thingsss API:

```python
# app/services/enhanced_url_inference.py
import httpx

class EnhancedScraper:
    def __init__(self):
        self.scraping_api_url = "https://thingsss-scraping.railway.app"
    
    async def handle_complex_site(self, url: str):
        """Use scraping service for complex sites."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.scraping_api_url}/api/v1/scrape",
                json={
                    "url": url,
                    "strategy": "auto",
                    "extract_fields": ["title", "description", "images", "price"]
                }
            )
            return response.json()
```

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8080/health
```

### Test Endpoint

```bash
curl -X POST http://localhost:8080/api/v1/test
```

### Manual Testing URLs

Test with these known problematic sites:
- CB2: `https://www.cb2.com/burl-35.5-rotating-coffee-table/s151251`
- Walmart: Any product URL (should handle 403 gracefully)
- Amazon: Should work with HTTP strategy

## 📊 Monitoring

### Key Metrics

- Success/failure rates by domain
- Average response times by strategy
- Browser service health
- Concurrent request handling

### Logs

Structured JSON logging with:
- Request/response details
- Error categorization
- Performance metrics
- Strategy selection reasoning

## 🔒 Security

### Built-in Protections

- URL safety validation (no localhost, internal IPs)
- Domain allowlist support
- Rate limiting and concurrency controls
- Input sanitization
- Safe browser configuration

### Production Considerations

- Configure CORS for specific origins
- Set domain restrictions via `ALLOWED_DOMAINS`
- Monitor resource usage
- Implement request authentication if needed

## 🚀 Deployment

### Railway

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically
4. Monitor via Railway dashboard

### Docker Production

```dockerfile
# Use production Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0
# ... (see Dockerfile for full configuration)
```

### Health Checks

- Railway: `GET /health`
- Kubernetes: Configure liveness/readiness probes
- Load Balancer: Monitor health endpoint

## 📈 Performance

### Benchmarks

- HTTP scraping: ~2-5 seconds
- Browser scraping: ~8-15 seconds
- Concurrent requests: Up to 5 simultaneous
- Memory usage: ~200MB baseline + 100MB per browser

### Optimization Tips

1. Use HTTP strategy when possible
2. Configure site-specific wait selectors
3. Limit concurrent browser instances
4. Monitor memory usage
5. Implement caching for repeated requests

## 🛠️ Development

### Project Structure

```
thingsss-scraping/
├── app/
│   ├── api/         # FastAPI endpoints
│   ├── core/        # Configuration and logging
│   ├── models/      # Pydantic models
│   ├── services/    # Core scraping logic
│   └── utils/       # Utilities
├── Dockerfile       # Container configuration
├── requirements.txt # Python dependencies
└── main.py         # Application entry point
```

### Adding New Sites

1. Update strategy selector in `app/services/strategies.py`
2. Add site-specific extractors in `app/services/extractors.py`
3. Test with sample URLs
4. Update documentation

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 🆘 Troubleshooting

### Common Issues

**Browser fails to start**
- Ensure Playwright browsers are installed
- Check system dependencies
- Verify Docker image includes browsers

**403 Errors persist**
- Switch to browser strategy
- Check if site requires CAPTCHA solving
- Verify user agent rotation

**Timeout errors**
- Increase timeout settings
- Check network connectivity
- Monitor resource usage

### Support

For issues and questions:
1. Check health endpoint
2. Review application logs
3. Test with `/api/v1/test` endpoint
4. Verify configuration settings

---

**🎯 Success Criteria**: When CB2 URLs return structured product data instead of 403 errors, and the main Thingsss API can seamlessly integrate with this service for complex sites. 