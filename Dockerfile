FROM mcr.microsoft.com/playwright/python:v1.40.0

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium firefox webkit

# Copy application code
COPY . .

# Railway runs containers securely, no need for custom user

# Expose port (Railway will set PORT env var)
EXPOSE 8080

# Start server - main.py handles PORT env var properly
CMD ["python3", "main.py"] 