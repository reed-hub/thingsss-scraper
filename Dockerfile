# ==============================================================================
# Thingsss Scraping API Service - Production Dockerfile
# ==============================================================================
# 
# This Dockerfile creates a production-ready container for the Thingsss Scraping
# API Service. It uses the official Playwright Python image to ensure all browser
# dependencies are properly installed.
#
# Features:
# - Pre-installed Playwright browsers (Chromium, Firefox, WebKit)
# - Optimized for Railway and other cloud platforms
# - Secure by default (Railway handles user management)
# - Supports environment variable configuration
#
# Build: docker build -t thingsss-scraper .
# Run:   docker run -p 8080:8080 thingsss-scraper
#
# Environment Variables:
#   PORT=8080                    # Server port (auto-set by Railway)
#   DEBUG=false                  # Enable debug logging
#   BROWSER_HEADLESS=true        # Run browsers in headless mode
#   MAX_CONCURRENT_REQUESTS=5    # Limit concurrent scraping requests
# ==============================================================================

# Use official Playwright Python image with pre-installed browsers
# This image includes all necessary system dependencies for browser automation
FROM mcr.microsoft.com/playwright/python:v1.40.0

# Set working directory
WORKDIR /app

# Install Python dependencies first (better Docker layer caching)
# This step is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers with all dependencies
# This ensures browsers work correctly in the container environment
RUN playwright install --with-deps chromium firefox webkit

# Copy application code
# Done after dependency installation for better layer caching
COPY . .

# Railway runs containers securely - no need for custom user creation
# Previous versions created custom users but this caused deployment issues
# Railway handles container security automatically

# Expose port 8080 (Railway will set PORT environment variable)
# The application reads this dynamically in main.py
EXPOSE 8080

# Start the application
# Use python3 directly to handle PORT environment variable properly
# This avoids issues with $PORT not being properly interpolated
CMD ["python3", "main.py"]

# ==============================================================================
# Deployment Notes:
# 
# 1. Railway Deployment:
#    - Automatically detects this Dockerfile
#    - Sets PORT environment variable
#    - Handles SSL termination and domain mapping
#    - Build time: ~10-15 minutes (due to browser installation)
#
# 2. Local Development:
#    - docker build -t thingsss-scraper .
#    - docker run -p 8080:8080 -e DEBUG=true thingsss-scraper
#
# 3. Production Configuration:
#    - Set BROWSER_HEADLESS=true
#    - Set DEBUG=false
#    - Monitor memory usage (browsers use ~100-200MB each)
#    - Consider limiting MAX_CONCURRENT_REQUESTS based on resources
#
# 4. Troubleshooting:
#    - If browsers fail to start, ensure headless mode is enabled
#    - Check logs for Playwright installation issues
#    - Verify environment variables are set correctly
# ============================================================================== 