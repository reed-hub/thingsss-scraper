# 🚀 Deployment Guide

Complete guide for deploying the Thingsss Scraping API Service to various platforms.

## 📋 Prerequisites

- Git
- GitHub account
- Platform account (Railway, Docker Hub, etc.)
- Basic understanding of environment variables

## Railway Deployment (Recommended)

Railway provides the easiest deployment path with automatic builds and scaling.

### Step 1: Repository Setup

```bash
# Clone the repository
git clone https://github.com/reed-hub/thingsss-scraper.git
cd thingsss-scraper

# Or fork and clone your fork
gh repo fork reed-hub/thingsss-scraper
git clone https://github.com/YOUR_USERNAME/thingsss-scraper.git
cd thingsss-scraper
```

### Step 2: Railway Project Creation

1. **Sign Up/Login to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `thingsss-scraper` repository
   - Click "Deploy Now"

3. **Initial Build**
   - Railway automatically detects `Dockerfile`
   - First build takes 10-15 minutes (Playwright installation)
   - Monitor build logs for any issues

### Step 3: Environment Configuration

Set these environment variables in Railway dashboard:

**Required Variables:**
```env
DEBUG=false
BROWSER_HEADLESS=true
MAX_CONCURRENT_REQUESTS=3
```

**Optional Variables:**
```env
BROWSER_TIMEOUT=30000
REQUEST_DELAY_MS=1000
MAX_RETRIES=3
RETRY_DELAY=2.0
```

**Security Variables (Optional):**
```env
ALLOWED_DOMAINS=cb2.com,walmart.com,wayfair.com
```

### Step 4: Domain Setup

1. **Custom Domain (Optional)**
   - Go to Settings → Domains
   - Add custom domain: `scraper.yourdomain.com`
   - Configure DNS CNAME record

2. **Default Domain**
   - Railway provides: `your-project-name.up.railway.app`
   - Use this URL for integration

### Step 5: Verification

```bash
# Test health endpoint
curl https://your-project-name.up.railway.app/health

# Expected response
{"status": "healthy", "service": "thingsss-scraping", "version": "1.0.0"}

# Test scraping
curl -X POST "https://your-project-name.up.railway.app/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "strategy": "http"}'
```

---

## Docker Deployment

Deploy using Docker for maximum control and portability.

### Local Docker Build

```bash
# Build image
docker build -t thingsss-scraper .

# Run container
docker run -d \
  --name thingsss-scraper \
  -p 8080:8080 \
  -e DEBUG=false \
  -e BROWSER_HEADLESS=true \
  -e MAX_CONCURRENT_REQUESTS=3 \
  thingsss-scraper

# Test deployment
curl http://localhost:8080/health
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  thingsss-scraper:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DEBUG=false
      - BROWSER_HEADLESS=true
      - MAX_CONCURRENT_REQUESTS=3
      - BROWSER_TIMEOUT=30000
    restart: unless-stopped
    
  # Optional: Add reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - thingsss-scraper
```

Run with:
```bash
docker-compose up -d
```

### Container Registry

**Push to Docker Hub:**
```bash
# Tag image
docker tag thingsss-scraper your-username/thingsss-scraper:latest

# Push to registry
docker push your-username/thingsss-scraper:latest
```

**Deploy from Registry:**
```bash
docker run -d \
  --name thingsss-scraper \
  -p 8080:8080 \
  your-username/thingsss-scraper:latest
```

---

## Cloud Platform Deployment

### Google Cloud Run

1. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Build and Deploy**
   ```bash
   # Build with Cloud Build
   gcloud builds submit --tag gcr.io/PROJECT_ID/thingsss-scraper
   
   # Deploy to Cloud Run
   gcloud run deploy thingsss-scraper \
     --image gcr.io/PROJECT_ID/thingsss-scraper \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="DEBUG=false,BROWSER_HEADLESS=true"
   ```

3. **Configure**
   ```bash
   # Update environment variables
   gcloud run services update thingsss-scraper \
     --region us-central1 \
     --set-env-vars="MAX_CONCURRENT_REQUESTS=3"
   ```

### AWS ECS (Fargate)

1. **Create Task Definition**
   ```json
   {
     "family": "thingsss-scraper",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "thingsss-scraper",
         "image": "your-username/thingsss-scraper:latest",
         "portMappings": [
           {
             "containerPort": 8080,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "DEBUG", "value": "false"},
           {"name": "BROWSER_HEADLESS", "value": "true"}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/thingsss-scraper",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

2. **Create Service**
   ```bash
   aws ecs create-service \
     --cluster default \
     --service-name thingsss-scraper \
     --task-definition thingsss-scraper \
     --desired-count 1 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

### Azure Container Instances

```bash
# Create resource group
az group create --name thingsss-scraper --location eastus

# Deploy container
az container create \
  --resource-group thingsss-scraper \
  --name thingsss-scraper \
  --image your-username/thingsss-scraper:latest \
  --dns-name-label thingsss-scraper \
  --ports 8080 \
  --environment-variables DEBUG=false BROWSER_HEADLESS=true \
  --cpu 2 \
  --memory 4
```

---

## Kubernetes Deployment

### Basic Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thingsss-scraper
  labels:
    app: thingsss-scraper
spec:
  replicas: 2
  selector:
    matchLabels:
      app: thingsss-scraper
  template:
    metadata:
      labels:
        app: thingsss-scraper
    spec:
      containers:
      - name: thingsss-scraper
        image: your-username/thingsss-scraper:latest
        ports:
        - containerPort: 8080
        env:
        - name: DEBUG
          value: "false"
        - name: BROWSER_HEADLESS
          value: "true"
        - name: MAX_CONCURRENT_REQUESTS
          value: "3"
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: thingsss-scraper-service
spec:
  selector:
    app: thingsss-scraper
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

### With Ingress

Create `k8s-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: thingsss-scraper-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - scraper.yourdomain.com
    secretName: thingsss-scraper-tls
  rules:
  - host: scraper.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: thingsss-scraper-service
            port:
              number: 80
```

---

## Environment Variables Reference

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Server port (set by platform) |
| `DEBUG` | `false` | Enable debug logging |
| `BROWSER_HEADLESS` | `true` | Run browsers in headless mode |

### Performance Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_CONCURRENT_REQUESTS` | `5` | Max simultaneous requests |
| `REQUEST_DELAY_MS` | `1000` | Delay between requests (ms) |
| `BROWSER_TIMEOUT` | `30000` | Browser timeout (ms) |
| `MAX_RETRIES` | `3` | Max retry attempts |
| `RETRY_DELAY` | `2.0` | Delay between retries (seconds) |

### Security Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_DOMAINS` | `None` | Comma-separated allowed domains |

---

## Health Checks

Configure health checks for your deployment platform:

### Railway
```toml
# railway.toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
```

### Docker
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1
```

### Kubernetes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

## Monitoring Setup

### Basic Monitoring

1. **Health Endpoint**
   ```bash
   # Monitor service health
   curl https://your-service-url/health
   ```

2. **Uptime Monitoring**
   - Use services like UptimeRobot, Pingdom
   - Monitor `/health` endpoint every 5 minutes

3. **Application Logs**
   ```bash
   # Railway
   railway logs
   
   # Docker
   docker logs thingsss-scraper -f
   
   # Kubernetes
   kubectl logs -f deployment/thingsss-scraper
   ```

### Advanced Monitoring

1. **Prometheus Metrics** (Future Enhancement)
   ```python
   # Add to main.py
   from prometheus_client import Counter, Histogram
   
   REQUEST_COUNT = Counter('scraper_requests_total', 'Total requests')
   REQUEST_DURATION = Histogram('scraper_request_duration_seconds', 'Request duration')
   ```

2. **Grafana Dashboard**
   - Import Playwright metrics
   - Monitor response times
   - Track success rates

3. **Alerting**
   ```yaml
   # Example alert rule
   - alert: ScraperDown
     expr: up{job="thingsss-scraper"} == 0
     for: 5m
     annotations:
       summary: "Scraper service is down"
   ```

---

## Performance Optimization

### Resource Allocation

**Railway:**
- Automatic scaling based on load
- No configuration needed

**Docker:**
```bash
docker run -d \
  --memory="2g" \
  --cpus="1.0" \
  thingsss-scraper
```

**Kubernetes:**
```yaml
resources:
  limits:
    memory: "2Gi"
    cpu: "1000m"
  requests:
    memory: "1Gi"
    cpu: "500m"
```

### Scaling Configuration

1. **Horizontal Scaling**
   - Multiple instances for high load
   - Load balancer distribution

2. **Vertical Scaling**
   - Increase memory for browser operations
   - Increase CPU for concurrent processing

3. **Auto-scaling Rules**
   ```yaml
   # Kubernetes HPA
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: thingsss-scraper-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: thingsss-scraper
     minReplicas: 1
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
   ```

---

## Security Configuration

### Network Security

1. **Firewall Rules**
   ```bash
   # Allow only HTTP/HTTPS traffic
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw deny 8080/tcp  # Block direct access
   ```

2. **Reverse Proxy**
   ```nginx
   # nginx configuration
   server {
       listen 80;
       server_name scraper.yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Access Control

1. **API Key Authentication** (Future Enhancement)
   ```python
   # Add to app/api/scraping.py
   from fastapi import Header, HTTPException
   
   async def verify_api_key(x_api_key: str = Header(...)):
       if x_api_key != expected_api_key:
           raise HTTPException(status_code=401, detail="Invalid API key")
   ```

2. **Rate Limiting**
   ```python
   # Add rate limiting middleware
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/v1/scrape")
   @limiter.limit("10/minute")
   async def scrape_url(request: Request, ...):
       # Implementation
   ```

---

## Backup and Recovery

### Configuration Backup

```bash
# Backup environment variables
railway variables > backup-env.txt

# Backup Docker configuration
docker inspect thingsss-scraper > backup-docker.json
```

### Database Backup (If Added)

```bash
# Future: If database is added
pg_dump thingsss_scraper > backup.sql
```

### Disaster Recovery

1. **Service Recreation**
   ```bash
   # Railway: Redeploy from GitHub
   railway up
   
   # Docker: Recreate container
   docker run -d --env-file backup-env.txt thingsss-scraper
   ```

2. **Data Recovery**
   - Configuration via environment variables
   - No persistent data loss (stateless service)

---

## Troubleshooting Deployment

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   railway logs --build
   
   # Common causes:
   # - Missing dependencies
   # - Playwright installation timeout
   # - Memory limits exceeded
   ```

2. **Health Check Failures**
   ```bash
   # Test locally
   curl http://localhost:8080/health
   
   # Check logs
   railway logs
   ```

3. **Performance Issues**
   ```bash
   # Monitor resource usage
   railway ps
   
   # Check for memory leaks
   docker stats thingsss-scraper
   ```

### Debug Mode

Enable debugging:
```env
DEBUG=true
```

This provides:
- Detailed request/response logs
- Browser automation steps
- Performance metrics
- Error stack traces

---

## Production Checklist

### Pre-Deployment

- [ ] Code reviewed and tested
- [ ] Environment variables configured
- [ ] Health checks implemented
- [ ] Resource limits set
- [ ] Security measures in place

### Post-Deployment

- [ ] Health endpoint accessible
- [ ] Test scraping functionality
- [ ] Monitor logs for errors
- [ ] Verify performance metrics
- [ ] Test integration with main API

### Ongoing Maintenance

- [ ] Monitor health checks
- [ ] Review error logs weekly
- [ ] Update dependencies monthly
- [ ] Performance optimization quarterly
- [ ] Security updates as needed

---

For deployment issues or questions, refer to:
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Configuration Guide](CONFIGURATION.md)
- [GitHub Issues](https://github.com/reed-hub/thingsss-scraper/issues) 