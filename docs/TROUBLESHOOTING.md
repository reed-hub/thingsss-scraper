# 🚨 Troubleshooting Guide

Complete troubleshooting guide for the Thingsss Scraping API Service covering common issues, debugging techniques, and solutions.

## 📋 Quick Diagnostics

### Health Check

First, verify basic service health:

```bash
# Check service health
curl https://your-service-url/health

# Expected healthy response
{
  "status": "healthy",
  "service": "thingsss-scraping",
  "version": "1.0.0"
}

# Unhealthy response
{
  "status": "unhealthy",
  "error": "Browser service unavailable"
}
```

### Service Status

```bash
# Railway
railway status
railway logs

# Docker
docker ps
docker logs thingsss-scraper

# Kubernetes
kubectl get pods
kubectl logs -f deployment/thingsss-scraper
```

---

## 🏗️ Deployment Issues

### Docker Build Failures

#### Issue: User Creation Fails
```bash
Error: process "/bin/sh -c useradd -m -u 1000 scraper" did not complete successfully: exit code: 4
```

**Solution:**
The Dockerfile has been updated to remove user creation. Update your code:
```dockerfile
# Remove this line (old)
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app

# Use this instead (fixed)
# Railway runs containers securely, no need for custom user
```

#### Issue: Playwright Installation Timeout
```bash
Error: Failed to download browser binaries
```

**Solutions:**
1. **Increase build timeout** (Railway: 15+ minutes)
2. **Use pre-built image** with Playwright
3. **Check network connectivity** during build

```dockerfile
# Alternative: Use smaller browser set
RUN playwright install --with-deps chromium
# Instead of: playwright install --with-deps chromium firefox webkit
```

#### Issue: Memory Limit Exceeded
```bash
Error: Killed (OOM)
```

**Solutions:**
1. **Railway**: Upgrade plan or optimize memory usage
2. **Docker**: Increase memory limit
   ```bash
   docker run --memory="2g" thingsss-scraper
   ```
3. **Kubernetes**: Increase resource limits
   ```yaml
   resources:
     limits:
       memory: "2Gi"
   ```

### Railway-Specific Issues

#### Issue: PORT Environment Variable
```bash
Error: Invalid value for '--port': '$PORT' is not a valid integer
```

**Solution:**
Use `python3 main.py` instead of direct uvicorn command:
```toml
# railway.toml - Remove this
[deploy]
startCommand = "python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT"

# Let Dockerfile handle it
CMD ["python3", "main.py"]
```

#### Issue: Build Not Triggering
**Symptoms:** No build after git push

**Solutions:**
1. Check Railway GitHub connection
2. Verify webhook is active
3. Manual trigger: Railway dashboard → Deploy → Trigger Deploy

#### Issue: Environment Variables Not Applied
**Symptoms:** Service uses default values

**Solutions:**
1. Verify variables in Railway dashboard
2. Check variable names (case-sensitive)
3. Restart service after changes

---

## 🤖 Browser Automation Issues

### Browser Startup Failures

#### Issue: Browser Won't Start
```bash
Error: Failed to launch browser
```

**Debugging Steps:**
1. **Check headless mode:**
   ```env
   BROWSER_HEADLESS=true  # Required for production
   ```

2. **Verify Playwright installation:**
   ```bash
   python3 -m playwright install --with-deps chromium
   ```

3. **Check system dependencies:**
   ```bash
   # Docker: Ensure base image includes dependencies
   FROM mcr.microsoft.com/playwright/python:v1.40.0
   ```

#### Issue: Browser Crashes
```bash
Error: Target page, context or browser has been closed
```

**Solutions:**
1. **Increase timeout:**
   ```json
   {
     "url": "https://example.com",
     "timeout": 60,
     "strategy": "browser"
   }
   ```

2. **Check memory limits:**
   - Each browser instance uses ~100-200MB
   - Limit concurrent requests if memory-constrained

3. **Monitor resource usage:**
   ```bash
   # Railway
   railway ps
   
   # Docker
   docker stats thingsss-scraper
   ```

### Browser Timeout Issues

#### Issue: Page Load Timeout
```bash
Error: Timeout 30000ms exceeded
```

**Solutions:**
1. **Increase timeout:**
   ```json
   {
     "timeout": 60,
     "strategy": "browser"
   }
   ```

2. **Use specific wait conditions:**
   ```json
   {
     "wait_for": ".product-details",
     "strategy": "browser"
   }
   ```

3. **Check site responsiveness:**
   ```bash
   curl -I https://target-site.com
   ```

#### Issue: Element Not Found
```bash
Error: Waiting for selector ".product-title" failed
```

**Solutions:**
1. **Update selectors** in `app/services/extractors.py`
2. **Add fallback selectors:**
   ```python
   selectors = [
       '.product-title h1',     # Primary
       'h1[data-testid="title"]', # Fallback 1
       'h1',                    # Fallback 2
   ]
   ```

3. **Check site changes:**
   - Inspect element on target site
   - Update extraction rules

---

## 🌐 HTTP Client Issues

### Connection Failures

#### Issue: HTTP 403 Forbidden
```bash
Error: HTTP 403 Forbidden
```

**Solutions:**
1. **Switch to browser strategy:**
   ```json
   {
     "url": "https://complex-site.com",
     "strategy": "browser"
   }
   ```

2. **Check user agent rotation:**
   - Implemented in `app/services/scraper.py`
   - Uses `fake-useragent` library

3. **Add to complex sites list:**
   ```python
   # app/services/strategies.py
   BROWSER_REQUIRED_DOMAINS.add('new-problematic-site.com')
   ```

#### Issue: HTTP Timeout
```bash
Error: httpx.ConnectTimeout
```

**Solutions:**
1. **Increase timeout:**
   ```json
   {
     "timeout": 30,
     "strategy": "http"
   }
   ```

2. **Check network connectivity:**
   ```bash
   curl -I https://target-site.com
   ```

3. **Switch to browser strategy:**
   - More reliable for problematic sites

### SSL/TLS Issues

#### Issue: SSL Certificate Verification
```bash
Error: SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**
1. **Check if site has valid SSL:**
   ```bash
   openssl s_client -connect target-site.com:443
   ```

2. **Update httpx configuration** if needed:
   ```python
   # In app/services/scraper.py
   async with httpx.AsyncClient(verify=False) as client:
       # Only for development/testing
   ```

---

## 📊 Data Extraction Issues

### Empty Results

#### Issue: No Data Extracted
```json
{
  "success": true,
  "data": {
    "title": null,
    "description": null,
    "images": []
  }
}
```

**Debugging Steps:**
1. **Check selectors:**
   ```bash
   # Test with browser strategy
   curl -X POST "https://your-service/api/v1/scrape" \
     -d '{"url": "https://target-site.com", "strategy": "browser"}'
   ```

2. **Inspect HTML structure:**
   - View page source
   - Check for dynamic content loading

3. **Update extraction rules:**
   ```python
   # app/services/extractors.py
   selectors = [
       'h1[data-testid="product-title"]',  # Add new selectors
       '.product-title h1',
       '#product-name'
   ]
   ```

#### Issue: Incorrect Data Extracted
**Symptoms:** Wrong title, price, or description

**Solutions:**
1. **Review site structure changes**
2. **Update selectors for specific sites:**
   ```python
   # Add site-specific extraction in extractors.py
   if 'example.com' in domain:
       title_selectors = ['.custom-title-selector']
   ```

3. **Test with manual inspection:**
   ```bash
   curl https://target-site.com | grep -i "title\|price"
   ```

### Price Extraction Issues

#### Issue: Price Not Detected
**Symptoms:** `"price": null` in response

**Solutions:**
1. **Check price format patterns:**
   ```python
   # app/services/extractors.py - Add new patterns
   patterns = [
       r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $123.45
       r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD',  # 123.45 USD
       # Add more patterns as needed
   ]
   ```

2. **Update price selectors:**
   ```python
   price_selectors = [
       '.price-current',
       '[data-testid="price"]',
       '.sale-price',  # Add new selectors
   ]
   ```

---

## ⚡ Performance Issues

### Slow Response Times

#### Issue: Requests Taking Too Long
**Symptoms:** Response times > 30 seconds

**Debugging:**
1. **Check processing times:**
   ```json
   {
     "processing_time": 45.2,  # Too slow
     "strategy_used": "browser"
   }
   ```

2. **Analyze bottlenecks:**
   - Browser startup time
   - Page load time
   - Element waiting time

**Solutions:**
1. **Optimize browser settings:**
   ```python
   # app/services/browser.py
   context = await browser.new_context(
       user_agent=settings.browser_user_agent,
       java_script_enabled=False,  # Disable JS if not needed
       images_enabled=False,       # Skip images for speed
   )
   ```

2. **Use HTTP strategy when possible:**
   - Faster for simple sites
   - Automatic fallback to browser

3. **Implement caching** (future enhancement):
   ```python
   # Cache results for repeated requests
   @lru_cache(maxsize=100)
   async def cached_scrape(url: str):
       # Implementation
   ```

### Memory Issues

#### Issue: High Memory Usage
**Symptoms:** Service crashes, OOM errors

**Debugging:**
```bash
# Monitor memory usage
docker stats thingsss-scraper

# Check browser instances
ps aux | grep chromium
```

**Solutions:**
1. **Limit concurrent requests:**
   ```env
   MAX_CONCURRENT_REQUESTS=2  # Reduce from 5
   ```

2. **Increase memory allocation:**
   ```bash
   # Docker
   docker run --memory="2g" thingsss-scraper
   ```

3. **Implement browser pooling** (future enhancement):
   ```python
   # Reuse browser instances
   class BrowserPool:
       def __init__(self, size=3):
           self.pool = asyncio.Queue(maxsize=size)
   ```

### Concurrent Request Issues

#### Issue: Rate Limiting Errors
**Symptoms:** Requests queued or rejected

**Solutions:**
1. **Adjust concurrency settings:**
   ```env
   MAX_CONCURRENT_REQUESTS=3
   REQUEST_DELAY_MS=2000  # Increase delay
   ```

2. **Implement proper queuing:**
   - Built-in semaphore limits concurrent requests
   - Monitor queue length

3. **Scale horizontally:**
   - Deploy multiple instances
   - Use load balancer

---

## 🔧 Configuration Issues

### Environment Variable Problems

#### Issue: Settings Not Applied
**Symptoms:** Default values used instead of environment variables

**Debugging:**
1. **Check variable names:**
   ```bash
   # Correct
   BROWSER_HEADLESS=true
   
   # Incorrect
   HEADLESS=true  # Wrong name
   ```

2. **Verify variable loading:**
   ```python
   # Add debug logging to app/core/config.py
   print(f"DEBUG: {os.getenv('DEBUG')}")
   print(f"BROWSER_HEADLESS: {os.getenv('BROWSER_HEADLESS')}")
   ```

3. **Check .env file format:**
   ```env
   # Correct
   DEBUG=false
   
   # Incorrect
   DEBUG = false  # No spaces around =
   ```

### URL Validation Issues

#### Issue: URL Rejected
```bash
Error: URL is not safe to scrape
```

**Solutions:**
1. **Check URL format:**
   ```python
   # Valid URLs
   https://example.com
   http://example.com
   
   # Invalid URLs
   localhost:8080
   127.0.0.1
   file:///path/to/file
   ```

2. **Update domain allowlist:**
   ```env
   ALLOWED_DOMAINS=example.com,other-site.com
   ```

3. **Review safety checks:**
   ```python
   # app/utils/validators.py
   def is_safe_url(url: str) -> bool:
       # Customize safety rules
   ```

---

## 🔍 Debugging Techniques

### Enable Debug Mode

```env
DEBUG=true
```

This provides:
- Detailed request/response logs
- Browser automation steps
- Performance metrics
- Error stack traces

### Request Tracing

Add correlation IDs for tracking:
```python
# Future enhancement
import uuid

correlation_id = str(uuid.uuid4())
logger.info("Request started", correlation_id=correlation_id, url=url)
```

### Browser Debugging

For local development:
```python
# app/core/config.py - Temporarily set
browser_headless: bool = False  # See browser window
```

View browser actions:
```python
# app/services/browser.py - Add slow motion
await self._playwright.chromium.launch(
    headless=False,
    slow_mo=1000  # 1 second delay between actions
)
```

### API Testing

Test individual endpoints:
```bash
# Health check
curl https://your-service/health

# Strategy listing
curl https://your-service/api/v1/strategies

# Test endpoint
curl -X POST https://your-service/api/v1/test

# Simple scraping
curl -X POST "https://your-service/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "strategy": "http"}'
```

---

## 📈 Monitoring and Alerting

### Log Analysis

**Common error patterns:**
```bash
# Browser crashes
grep "Target page.*closed" logs.txt

# Timeout errors
grep "Timeout.*exceeded" logs.txt

# HTTP errors
grep "HTTP.*error" logs.txt

# Memory issues
grep -i "memory\|oom" logs.txt
```

### Performance Monitoring

**Key metrics to track:**
- Response time percentiles (p50, p95, p99)
- Success rate by strategy
- Error rate by domain
- Memory usage trends
- Concurrent request counts

**Basic monitoring script:**
```python
#!/usr/bin/env python3
import httpx
import time
import asyncio

async def monitor_health():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://your-service/health")
                if response.status_code != 200:
                    print(f"❌ Health check failed: {response.status_code}")
                else:
                    print(f"✅ Service healthy")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(monitor_health())
```

### Alerting Rules

**Set up alerts for:**
1. **Service Down**: Health check fails for 5+ minutes
2. **High Error Rate**: >10% errors in 10-minute window
3. **Slow Response**: P95 response time >30 seconds
4. **Memory Usage**: Memory usage >80% for 10+ minutes

---

## 🆘 Emergency Procedures

### Service Down

1. **Check service status:**
   ```bash
   curl https://your-service/health
   ```

2. **Review recent logs:**
   ```bash
   railway logs --tail 100
   ```

3. **Quick restart:**
   ```bash
   # Railway
   railway restart
   
   # Docker
   docker restart thingsss-scraper
   
   # Kubernetes
   kubectl rollout restart deployment/thingsss-scraper
   ```

### High Error Rate

1. **Identify error patterns:**
   ```bash
   railway logs | grep ERROR
   ```

2. **Check specific domain issues:**
   - Test problematic URLs manually
   - Review site changes

3. **Temporary mitigation:**
   - Force browser strategy for all requests
   - Increase timeouts
   - Reduce concurrent requests

### Memory Issues

1. **Immediate action:**
   ```bash
   # Restart service
   railway restart
   ```

2. **Adjust settings:**
   ```env
   MAX_CONCURRENT_REQUESTS=2
   BROWSER_TIMEOUT=20000
   ```

3. **Monitor recovery:**
   ```bash
   railway ps  # Check memory usage
   ```

---

## 📞 Getting Help

### Self-Service Resources

1. **Documentation:**
   - [API Documentation](API.md)
   - [Deployment Guide](DEPLOYMENT.md)
   - [Configuration Guide](CONFIGURATION.md)

2. **Testing Tools:**
   ```bash
   # Run comprehensive tests
   python3 test_deployment.py
   ```

3. **Debug Mode:**
   ```env
   DEBUG=true
   ```

### Community Support

1. **GitHub Issues:**
   - [Report bugs](https://github.com/reed-hub/thingsss-scraper/issues)
   - Search existing issues
   - Include logs and configuration

2. **Issue Template:**
   ```markdown
   ## Bug Description
   Brief description of the issue
   
   ## Environment
   - Platform: Railway/Docker/Kubernetes
   - URL being scraped: https://example.com
   - Strategy used: browser/http/auto
   
   ## Steps to Reproduce
   1. Step one
   2. Step two
   
   ## Expected Behavior
   What should happen
   
   ## Actual Behavior
   What actually happens
   
   ## Logs
   ```
   Paste relevant logs here
   ```
   
   ## Configuration
   ```
   Paste environment variables (mask sensitive data)
   ```
   ```

### Professional Support

For mission-critical deployments:
- Consider professional support services
- Implement comprehensive monitoring
- Set up automated alerting
- Regular maintenance schedules

---

## 🔄 Regular Maintenance

### Weekly Tasks

- [ ] Review error logs
- [ ] Check response time trends
- [ ] Monitor memory usage
- [ ] Test health endpoints

### Monthly Tasks

- [ ] Update dependencies
- [ ] Review and update extraction rules
- [ ] Performance optimization review
- [ ] Security updates

### Quarterly Tasks

- [ ] Comprehensive performance analysis
- [ ] Capacity planning review
- [ ] Disaster recovery testing
- [ ] Documentation updates

---

Remember: Most issues can be resolved by:
1. Checking the health endpoint
2. Reviewing recent logs
3. Verifying environment variables
4. Testing with browser strategy
5. Restarting the service

For persistent issues, enable debug mode and gather comprehensive logs before seeking support. 